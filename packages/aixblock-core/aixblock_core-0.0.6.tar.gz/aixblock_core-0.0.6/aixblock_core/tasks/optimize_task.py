import os
import uuid
from urllib.parse import urljoin, urlparse

import requests
from PIL import Image
from core.audio import convert_audio, get_audio_info
from core.label_config import replace_task_data_undefined_with_config_field
from django.conf import settings
from django.utils.crypto import get_random_string
from io_storages.azure_blob.models import AzureBlobImportStorage, AzureBlobImportStorageLink
from io_storages.gcs.models import GCSImportStorage, GCSImportStorageLink
from io_storages.s3.models import S3ImportStorage, S3ImportStorageLink
from io_storages.gdriver.models import GDriverImportStorage, GDriverImportStorageLink
from tasks.models import Task


def optimize_task(task_id: int, storage_scheme: str, storage_pk: int):
    task = Task.objects.filter(pk=task_id).first()

    if not task:
        print(f"[Optimize Task #{task_id}] Not found")
        return False

    if task.is_data_optimized:
        return True

    # The original data in data. Cloud storage look like: s3://<bucket>/<path>
    original_data = task.data.copy()

    # The resolved data with cloud storage converted into http:// or https://
    resolved_data = task.data.copy()
    task.resolve_uri(resolved_data, task.project)
    replace_task_data_undefined_with_config_field(resolved_data, task.project)

    # Check cloud storage type
    storage = None
    storage_host = ""
    storage_class = None

    if storage_scheme == "s3":
        storage = S3ImportStorage.objects.filter(pk=storage_pk).first()
        storage_host = f"{storage.url_scheme}://{storage.bucket}"
        storage_class = S3ImportStorageLink
    elif storage_scheme == "gs":
        storage = GCSImportStorage.objects.filter(pk=storage_pk).first()
        storage_host = f"{storage.url_scheme}://{storage.bucket}"
        storage_class = GCSImportStorageLink
    elif storage_scheme == "azure-blob":
        storage = AzureBlobImportStorage.objects.filter(pk=storage_pk).first()
        storage_host = f"{storage.url_scheme}://{storage.container}"
        storage_class = AzureBlobImportStorageLink
    elif storage_scheme == "gdr":
        storage = GDriverImportStorage.objects.filter(pk=storage_pk).first()
        storage_host = f"{storage.url_scheme}://{storage.bucket}"
        storage_class = GDriverImportStorageLink
    # Request to remove URLs
    remove_urls = []

    # Processing data one-by-one
    for k, dt in list(task.project.data_types.items()):
        if dt not in ["Audio", "AudioPlus", "Image"]:
            continue

        ################################################################
        # STEP 1: Copy data to cloud storage if it is an external link #
        ################################################################

        # This var will have value if the data file was uploaded to cloud storage
        storage_file_path = task.storage_filename
        url = resolved_data[k]
        print(url)
        is_file_from_cloud_storage = True
        is_src_downloaded = False

        # Check data key
        data_key = k if k in original_data else settings.DATA_UNDEFINED_NAME if settings.DATA_UNDEFINED_NAME in original_data else ""

        # Local file
        if not url.startswith("http://") and not url.startswith("https://"):
            if settings.HOSTNAME:
                url = urljoin(settings.HOSTNAME, url)
            else:
                url = urljoin(f"https://127.0.0.1:{settings.INTERNAL_PORT}", url)

        # Don't have storage file path => File not in cloud storage
        if not storage_file_path:
            parsed_url = urlparse(url)
            base_file_name = os.path.basename(parsed_url.path)
            storage_file_path = f"raw_files_{task.project.pk}/{str(uuid.uuid4())[0:8]}_{base_file_name}"
            is_file_from_cloud_storage = False

            if "original_file" not in original_data:
                original_data["original_file"] = base_file_name

        # Create temp path to store source file
        storage_filename = storage_file_path.split("/")[-1]
        src_path = os.path.join(settings.BASE_DATA_DIR, get_random_string() + "_" + storage_filename)

        # Handle the source file download
        def download_source_file():
            nonlocal is_src_downloaded

            if is_src_downloaded:
                return

            print(f"[Optimize Task #{task_id}] Downloading source file: {url}")

            with requests.get(url, stream=True, verify=False) as response:
                response.raise_for_status()

                with open(src_path, 'wb') as src_file:
                    for chunk in response.iter_content(chunk_size=8192): 
                        src_file.write(chunk)

            is_src_downloaded = True
            print(f"[Optimize Task #{task_id}] Downloaded source file: {url}")

        # If the file is not in cloud storage, download source file and upload to cloud storage
        if not is_file_from_cloud_storage:
            download_source_file()

            print(f"[Optimize Task #{task_id}] Uploading to cloud storage: {src_path}")

            storage.upload_file(
                object_name=storage_filename,
                file_path=src_path,
                prefix=f"raw_files_{task.project.pk}",
                scan_link=False,
                remove_link=False,
            )

            storage_class.create(task=task, key=storage_file_path, storage=storage)
            original_data[data_key] = f"{storage_host}/{storage_file_path}"
            print(f"[Optimize Task #{task_id}] Uploaded to cloud storage: {src_path}")
            remove_urls.append(f"{url}{'&' if '?' in url else '?'}{settings.UPLOAD_TEMP_DELETE_KEY}={settings.UPLOAD_TEMP_DELETE_TOKEN}")

        #########################
        # STEP 2: Optimize data #
        #########################

        # Convert audio file to ogg
        if dt in ["Audio", "AudioPlus"]:
            download_source_file()
            ogg_filename = ".".join(storage_filename.split(".")[0:-1]) + ".ogg"
            tgt_ogg_path = os.path.join(settings.BASE_DATA_DIR, get_random_string() + "_" + ogg_filename)
            exception = None
            convert_result = convert_audio(src_path, tgt_ogg_path, codec="libopus", bitrate="32k")

            if convert_result:
                storage.upload_file(
                    object_name=ogg_filename,
                    file_path=tgt_ogg_path,
                    prefix=f'convert_files_{task.project.pk}',
                    scan_link=False,
                    remove_link=False,
                )

                new_data = f"{storage_host}/convert_files_{task.project.pk}/{ogg_filename}"
                print(f"[Optimize Task #{task_id}] Replace data key[{data_key}]: '{original_data[data_key]}' with '{new_data}'")
                original_data[data_key] = new_data
            else:
                exception = Exception("[Optimize Task #{task_id}] Failed to convert audio to OGG")

            if not task.is_data_has_audio_meta():
                try:
                    audio_info = get_audio_info(src_path)

                    if audio_info:
                        original_data = original_data | audio_info
                except Exception as e:
                    print(f"[Optimize Task #{task_id}] Can not get audio information. Error: {e}")

            try:
                os.remove(src_path)
                os.remove(tgt_ogg_path)
            except FileNotFoundError:
                pass

            if exception:
                raise exception
        # Make small image
        elif dt in ["Image"]:
            download_source_file()
            thumbnail = Image.open(src_path)
            thumbnail_path = os.path.join(settings.BASE_DATA_DIR, get_random_string() + "_" + storage_filename)
            thumbnail.save(thumbnail_path, quality=30)

            storage.upload_file(
                object_name=storage_filename,
                file_path=thumbnail_path,
                prefix=f'convert_files_{task.project.pk}',
                scan_link=False,
                remove_link=False,
            )

            new_data = f"{storage_host}/convert_files_{task.project.pk}/{storage_filename}"
            print(f"[Optimize Task #{task_id}] Replace data key[{data_key}]: '{original_data[data_key]}' with '{new_data}'")
            original_data[data_key] = new_data

            try:
                os.remove(src_path)
                os.remove(thumbnail_path)
            except FileNotFoundError:
                pass

        #############################
        # STEP 3: Cleanup temp file #
        #############################
        try:
            os.remove(src_path)
        except FileNotFoundError:
            pass
    
    if storage_scheme != "gdr":
        task.data = original_data
        
    task.is_data_optimized = True
    task.save(update_fields=["data", "is_data_optimized"])
    print(f"[Optimize Task #{task_id}] Done and saved")

    for remove_url in remove_urls:
        try:
            if storage_scheme != "gdr":
                requests.delete(remove_url)
                print(f"[Optimize Task #{task_id}] Requested to remove {remove_url}")
        except Exception:
            pass

    task.send_update_signal()
    print(f"[Optimize Task #{task_id}] Sent update signal")
    return True
