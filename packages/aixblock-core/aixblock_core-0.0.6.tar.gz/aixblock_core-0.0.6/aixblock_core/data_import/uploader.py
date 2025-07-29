"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
import os
import io
import csv
import ssl
# import time
import uuid
import base64
# import pickle
# import shutil
import logging
import mimetypes
# from core.audio import get_audio_info
from core.utils.common import split_into_chunks
from django_dbq.models import Job
# from plugins.plugin_centrifuge import publish_message
from tasks.models import Task

try:
    import ujson as json
except:
    import json

# from dateutil import parser
from rest_framework.exceptions import ValidationError
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from urllib.request import urlopen, Request

from .models import FileUpload
from core.utils.io import url_is_local
from core.utils.exceptions import ImportFromLocalIPError
# from projects.services.project_cloud_storage import project_minio_no_prefix

import zipfile
# from projects.services.project_cloud_storage import dataset_minio
import tempfile

# import threading
# from PIL import Image
# from pydub import AudioSegment
import datetime
from projects.services.project_cloud_storage import ProjectCloudStorage

logger = logging.getLogger(__name__)
csv.field_size_limit(131072 * 10)


def is_binary(f):
    return isinstance(f, (io.RawIOBase, io.BufferedIOBase))


def csv_generate_header(file):
    """ Generate column names for headless csv file """
    file.seek(0)
    names = []
    line = file.readline()

    num_columns = len(line.split(b',' if isinstance(line, bytes) else ','))
    for i in range(num_columns):
        names.append('column' + str(i+1))
    file.seek(0)
    return names


def check_max_task_number(tasks):
    # max tasks
    if len(tasks) > settings.TASKS_MAX_NUMBER:
        raise ValidationError(f'Maximum task number is {settings.TASKS_MAX_NUMBER}, '
                              f'current task number is {len(tasks)}')


def check_file_sizes_and_number(files):
    total = sum([file.size for _, file in files.items()])

    if total >= settings.TASKS_MAX_FILE_SIZE:
        raise ValidationError(f'Maximum total size of all files is {settings.TASKS_MAX_FILE_SIZE} bytes, '
                              f'current size is {total} bytes')

# def create_image_thumbnails(project_minio_no_prefix, project, image_path, user, original_file=None):
#     try:
#         image = Image.open(image_path)
#
#         ratios = {'small': 6, 'middle': 4, 'large': 2}
#         for size_name, ratio in ratios.items():
#             thumbnail = image.copy()
#             image_dir, image_name = os.path.split(image_path)
#             thumbnail_path = os.path.join(image_dir, f'{size_name}_{image_name}')
#
#             if size_name == 'large':
#                 # Nếu size_name là 'large', giảm chất lượng ảnh mà không thay đổi kích thước
#                 thumbnail.save(thumbnail_path, quality=30)
#             else:
#                 width, height = thumbnail.size
#                 new_width = width // ratio
#                 new_height = height // ratio
#
#                 thumbnail.thumbnail((new_width, new_height))
#
#                 thumbnail.save(thumbnail_path)
#
#             object_name = f'{size_name}_{image_name}'
#             # file_path = f'{settings.UPLOAD_DIR}/{project.id}/{size_name}_{image_name}'
#             # FileUpload.objects.create(user=user, project=project, file=file_path)
#
#             from io_storages.functions import get_all_project_storage
#             storages = get_all_project_storage(project.pk)
#             for storage in storages:
#                 storage.upload_file(object_name, thumbnail_path, f'convert_files_{project.pk}', scan_link=True, remove_link=True, user=user, original_file=original_file)
#                 break
#
#         os.remove(image_path)
#     except Exception as e:
#         os.remove(image_path)
#
# def create_audio_ogg(project_minio_no_prefix, project, audio_path, user, original_file=None):
#     try:
#         # audio = AudioSegment.from_file(audio_path)
#         # audio = audio.set_frame_rate(24000)
#         # duration_seconds = audio.duration_seconds
#         # duration_seconds = None
#
#         audio_dir, audio_name = os.path.split(audio_path)
#         audio_name_without_ext, ext = os.path.splitext(audio_name)
#         new_audio_name = f"{audio_name_without_ext}.ogg"
#         output_audio_path = os.path.join(audio_dir, new_audio_name)
#
#         stdout = convert_audio(audio_path=audio_path, output_audio_path=output_audio_path, codec="libopus", bitrate="32k")
#
#         if not stdout:
#             raise Exception("Error while converting audio")
#
#         duration_seconds = grab_audio_duration_from_ffmpeg_output(stdout)
#
#         # Xuất file âm thanh với định dạng OGG và bộ mã hóa Opus
#         # start_time = datetime.datetime.now()
#         # audio.export(output_audio_path, format="ogg", codec="libopus")
#         # The ffmpeg command with the vorbis codec can reduce the conversion time by half
#         # stdout = subprocess.check_output(['ffmpeg', '-i', audio_path, '-c:a', 'libopus', '-b:a', '32k', output_audio_path], stderr=subprocess.STDOUT)
#         # end_time = datetime.datetime.now()
#         # print(f"Conversion time: {end_time - start_time}")
#         # stdout = stdout.decode('utf-8')
#         # duration_match = re.search(r' Duration: (\d+:\d+:\d+\.\d+)', stdout)
#         #
#         # if duration_match:
#         #     duration = duration_match.group(1)
#         #     duration_parts = duration.split(',' if "," in duration else '.')
#         #     vals = duration_parts[0].split(':')
#         #     duration_seconds = round(
#         #         int(vals[0]) * 3600 + int(vals[1]) * 60 + int(vals[2]) + (float(f"0.{duration_parts[1]}") if len(duration_parts) > 1 else 0),
#         #         2)
#         #     print(f"Audio duration: {duration_seconds}")
#
#         object_name = f'{new_audio_name}'
#         # file_path = f'{settings.UPLOAD_DIR}/{project.id}/{new_audio_name}'
#         # FileUpload.objects.create(user=user, project=project, file=file_path)
#
#         from io_storages.functions import get_all_project_storage
#         storages = get_all_project_storage(project.pk)
#         for storage in storages:
#             storage.upload_file(
#                 object_name=object_name,
#                 file_path=output_audio_path,
#                 prefix=f'convert_files_{project.pk}',
#                 scan_link=True,
#                 remove_link=True,
#                 duration=duration_seconds,
#                 user=user,
#                 original_file=original_file,
#             )
#             break
#         os.remove(audio_path)
#     except Exception as e:
#         os.remove(audio_path)

def create_file_upload(request, project, file, file_content=None):
    from io_storages.functions import get_all_project_storage
    storages = get_all_project_storage(project.pk)

    if file_content:
        output_json, labels = convert_csv_ner(file_content)
        if len(labels) > 0:
            project = update_label_NER_ml(project, labels)

        project_dir = os.path.join(settings.MEDIA_ROOT, settings.UPLOAD_DIR, str(project.id))
        os.makedirs(project_dir, exist_ok=True)

        # Tạo đường dẫn cho tệp JSON
        if file and file.name:
            filename = file.name
        else:
            filename = str(uuid.uuid4())[0:8] + file.name + '-' + 'output.json'

        path = os.path.join(project_dir, filename)

        with open(path, 'w', encoding='utf-8') as json_file:
            json.dump(output_json, json_file, ensure_ascii=False, indent=4)

    if file.name.endswith('.json') or file.name.endswith('.txt') or file.name.endswith('.csv'):
        instance = FileUpload(user=request.user, project=project, file=file)
    
        if settings.SVG_SECURITY_CLEANUP:
            content_type, encoding = mimetypes.guess_type(str(instance.file.name))
            if content_type in ['image/svg+xml']:
                clean_xml = allowlist_svg(instance.file.read())
                instance.file.seek(0)
                instance.file.write(clean_xml)
                instance.file.truncate()
        instance.save()

        object_name = str(os.path.basename(instance.file.file.name))
        file_path = instance.file.path

        for storage in storages:
            storage.upload_file(
                object_name,
                file_path,
                prefix=f'raw_files_{project.pk}',
                user=request.user,
                original_file=file.name,
            )
            break

        return instance

    else:
        temp_dir = settings.UPLOAD_TEMP_DIR
        os.makedirs(temp_dir, exist_ok=True)
        # with tempfile.TemporaryDirectory() as temp_dir:
        # Tạo đường dẫn đầy đủ cho file trong thư mục tạm
        unique_suffix = str(uuid.uuid4())[0:8]
        original_file: str = os.path.basename(file.name)
        new_file_name = f"{unique_suffix}_{original_file}"
        
        # Tạo đường dẫn đầy đủ cho file trong thư mục tạm
        file_path = os.path.join(temp_dir, new_file_name)
        
        # Lưu nội dung của file vào file tạm
        with open(file_path, 'wb') as temp_file:
            for chunk in file.chunks():
                temp_file.write(chunk)

        # Tạo thư mục cố định cho file
        # fixed_dir = os.path.join(f"{settings.UPLOAD_DIR}/{project.id}", "fixed_storage")  # Thư mục cố định trong thư mục tạm
        # os.makedirs(fixed_dir, exist_ok=True)
        #
        # Copy file vào thư mục cố định
        # fixed_file_path = os.path.join(fixed_dir, new_file_name)
        # shutil.copy(file_path, fixed_file_path)
        #
        # Lấy object_name từ tên file
        # object_name = os.path.basename(file_path)
        #
        # data_types = project.data_types
        # will_create_thumb = 'image' in data_types
        # will_create_ogg = 'audio' in data_types and not original_file.endswith(".ogg")
        # remove_link = not will_create_ogg and not will_create_thumb

        # extras_data = None
        # publish_channel = request.data.get("publish_channel")
        # upload_file_id = request.data.get("upload_file_id")
        #
        # def send_message(msg):
        #     if not publish_channel or not upload_file_id:
        #         return
        #
        #     publish_message(
        #         channel=publish_channel,
        #         data=json.dumps({
        #             "upload_file_id": upload_file_id,
        #             "message": msg,
        #         }),
        #     )

        data_url = f"{settings.UPLOAD_TEMP_URL.rstrip('/')}/{new_file_name}"

        if not data_url.startswith("http://") and not data_url.startswith("https://"):
            data_url = f"{settings.HOSTNAME.rstrip('/')}/{data_url.lstrip('/')}"

        data = {
            settings.DATA_UNDEFINED_NAME: data_url,
            "original_file": original_file,
        }

        # if 'audio' in project.data_types:
        #     send_message("Reading audio information...")
        #     extras_data = get_audio_info(file_path)
        #     send_message("Finished reading audio information...")
        #
        #     if extras_data:
        #         data = data | extras_data

        task = Task.objects.create(
            data=data,
            project=project,
            created_by=request.user,
            is_data_optimized=False,
        )

        Job.objects.create(name="optimize_task", workspace={
            "task_pk": task.pk,
            "storage_scheme": storages[0].url_scheme,
            "storage_pk": storages[0].pk,
        })

        # Upload to local server then create a background job to move local file to cloud storage
        #
        # for storage in storages:
        #     storage.upload_file(
        #         object_name,
        #         file_path,
        #         prefix=f'raw_files_{project.pk}',
        #         scan_link=True,
        #         remove_link=True,
        #         user=request.user,
        #         original_file=original_file,
        #         extras_data=extras_data,
        #         publish_channel=publish_channel,
        #         upload_file_id=upload_file_id,
        #     )
        #     break

        # if will_create_thumb:
        #     thread = threading.Thread(target=create_image_thumbnails, args=(project_minio_no_prefix, project, fixed_file_path, request.user), kwargs={"original_file": original_file})
        #     manage_task_generator_thread(thread)
        # elif will_create_ogg:
        #     thread = threading.Thread(target=create_audio_ogg, args=(project_minio_no_prefix, project, fixed_file_path, request.user), kwargs={"original_file": original_file})
        #     manage_task_generator_thread(thread)
        
        return None
            # storage.scan_and_create_links()
 
# def create_file_upload(request, project, file, file_content=None):
#     if file_content:
#         output_json, labels = convert_csv_ner(file_content)
#         if len(labels) > 0:
#             project = update_label_NER_ml(project, labels)

#         project_dir = os.path.join(settings.MEDIA_ROOT, settings.UPLOAD_DIR, str(project.id))
#         os.makedirs(project_dir, exist_ok=True)

#         # Tạo đường dẫn cho tệp JSON
#         if file and file.name:
#             filename = file.name
#         else:
#             filename = str(uuid.uuid4())[0:8] + '-' + 'output.json'

#         path = os.path.join(project_dir, filename)

#         with open(path, 'w', encoding='utf-8') as json_file:
#             json.dump(output_json, json_file, ensure_ascii=False, indent=4)
        
#         # file = path

#     instance = FileUpload(user=request.user, project=project, file=file)
    
#     if settings.SVG_SECURITY_CLEANUP:
#         content_type, encoding = mimetypes.guess_type(str(instance.file.name))
#         if content_type in ['image/svg+xml']:
#             clean_xml = allowlist_svg(instance.file.read())
#             instance.file.seek(0)
#             instance.file.write(clean_xml)
#             instance.file.truncate()
#     instance.save()

#     object_name = str(os.path.basename(instance.file.file.name))
#     file_path = instance.file.path

#     data_types = project.data_types
#     if 'image' in data_types:
#         # object_name, file_path = create_image_thumbnails(project_minio_no_prefix, project, file_path)
#         thread = threading.Thread(target=create_image_thumbnails, args=(project_minio_no_prefix, project, file_path, request.user))
#         thread.start()
#     elif 'audio' in data_types:
#         # object_name, file_path = create_audio_ogg(project_minio_no_prefix, project, file_path)
#         thread = threading.Thread(target=create_audio_ogg, args=(project_minio_no_prefix, project, file_path, request.user))
#         thread.start()

#     from io_storages.functions import get_all_project_storage
#     storages = get_all_project_storage(project.pk)
#     for storage in storages:
#         storage.upload_file(object_name, file_path, f'raw_files_{project.pk}')

#     # from io_storages.s3.models import S3ImportStorage
#     # s3_minio = S3ImportStorage.objects.filter(project_id=project.pk)
#     # for s3 in s3_minio:
#     #     project_minio_no_prefix.upload_file(
#     #         project=project,
#     #         bucket_name=str(s3.bucket),
#     #         object_name=object_name,
#     #         file_path=file_path,
#     #         s3=s3
#     #     )

#     return instance


def allowlist_svg(dirty_xml):
    """Filter out malicious/harmful content from SVG files
    by defining allowed tags
    """
    from lxml.html import clean

    allow_tags = [
            'xml',
            'svg',
            'circle',
            'ellipse',
            'line',
            'path',
            'polygon',
            'polyline',
            'rect'
    ]

    cleaner = clean.Cleaner(
            allow_tags=allow_tags,
            style=True,
            links=True,
            add_nofollow=False,
            page_structure=True,
            safe_attrs_only=False,
            remove_unknown_tags=False)

    clean_xml = cleaner.clean_html(dirty_xml)
    return clean_xml


def str_to_json(data):
    try:
        json_acceptable_string = data.replace("'", "\"")
        return json.loads(json_acceptable_string)
    except ValueError:
        return None


def tasks_from_url(file_upload_ids, project, request, url):
    """ Download file using URL and read tasks from it
    """
    # process URL with tasks
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        req = Request(url, data=None, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
        })

        filename = url.rsplit('/', 1)[-1]
        with urlopen(req, context=ctx) as file:   # nosec
            # check size
            meta = file.info()
            try:
                file.size = int(meta.get("Content-Length"))
            except Exception as e:
                print(e)
                file.size = 0
                pass
            file.urlopen = True
            check_file_sizes_and_number({url: file})
            file_content = file.read()
            if isinstance(file_content, str):
                file_content = file_content.encode()
            file_upload = create_file_upload(request, project, SimpleUploadedFile(filename, file_content))
            file_upload_ids.append(file_upload.id)
            tasks, found_formats, data_keys = FileUpload.load_tasks_from_uploaded_files(project, file_upload_ids)

    except ValidationError as e:
        raise e
    except Exception as e:
        raise ValidationError(str(e))
    return data_keys, found_formats, tasks, file_upload_ids

def tasks_from_base64(file_upload_ids, project, request, base64_data):
    try:
        # Decode base64 data
        image_data = base64.b64decode(base64_data)
        filename = f"{uuid.uuid4()}.png"

        if isinstance(image_data, str):
            image_data = image_data.encode()
            
        file_upload = create_file_upload(request, project, SimpleUploadedFile(filename, image_data))
        file_upload_ids.append(file_upload.id)
        tasks, found_formats, data_keys = FileUpload.load_tasks_from_uploaded_files(project, file_upload_ids)

    except Exception as e:
        raise ValidationError(str(e))

    return data_keys, found_formats, tasks, file_upload_ids

def import_task_with_annotation(user, data, project=None):
    task = data["task"]

    if not project:
        project_id = task.get("project")
    else:
        project_id = project.id

    try:
        from tasks.models import Task, Annotation 
        if Task.objects.filter(pk=task["id"]).exists():
            task_instance = Task.objects.filter(pk=task["id"])
            task_instance.update(
                data=task.get("data"),
                meta=task.get("meta"),
                created_at=task.get("created_at"),
                updated_at=task.get("updated_at"),
                is_labeled=task.get("is_labeled"),
                overlap=task.get("overlap"),
                inner_id=task.get("inner_id"),
                total_annotations=task.get("total_annotations"),
                cancelled_annotations=task.get("cancelled_annotations"),
                total_predictions=task.get("total_predictions"),
                comment_count=task.get("comment_count"),
                unresolved_comment_count=task.get("unresolved_comment_count"),
                last_comment_updated_at=task.get("last_comment_updated_at"),
                reviewed_result=task.get("reviewed_result"),
                is_in_review=task.get("is_in_review"),
                is_in_qc=task.get("is_in_qc"),
                qualified_result=task.get("qualified_result"),
                project_id=task.get("project"),
                updated_by_id=task.get("updated_by"),
                file_upload=task.get("file_upload"),
                reviewed_by_id=task.get("reviewed_by"),
                qualified_by=task.get("qualified_by"),
                assigned_to=task.get("assigned_to"),
                # comment_authors=task.get("comment_authors")
            )

            task_instance = task_instance.first()

        else:
            if task.get("project") == project_id:
                task_instance = Task.objects.create(
                    id = task["id"],
                    data=task.get("data"),
                    meta=task.get("meta"),
                    created_at=task.get("created_at"),
                    updated_at=task.get("updated_at"),
                    is_labeled=task.get("is_labeled"),
                    overlap=task.get("overlap"),
                    inner_id=task.get("inner_id"),
                    total_annotations=task.get("total_annotations"),
                    cancelled_annotations=task.get("cancelled_annotations"),
                    total_predictions=task.get("total_predictions"),
                    comment_count=task.get("comment_count"),
                    unresolved_comment_count=task.get("unresolved_comment_count"),
                    last_comment_updated_at=task.get("last_comment_updated_at"),
                    reviewed_result=task.get("reviewed_result"),
                    is_in_review=task.get("is_in_review"),
                    is_in_qc=task.get("is_in_qc"),
                    qualified_result=task.get("qualified_result"),
                    project_id=project_id,
                    updated_by_id=task.get("updated_by"),
                    # file_upload=task.get("file_upload"),
                    reviewed_by_id=task.get("reviewed_by"),
                    qualified_by_id=task.get("qualified_by"),
                    assigned_to=task.get("assigned_to"),
                    # comment_authors = task["comment_authors"]
                    created_by_id=user.id,
                )
            else:
                task_instance = Task.objects.create(
                    id = task["id"],
                    data=task.get("data"),
                    # meta=task.get("meta"),
                    # created_at=task.get("created_at"),
                    # updated_at=task.get("updated_at"),
                    # is_labeled=task.get("is_labeled"),
                    # overlap=task.get("overlap"),
                    # inner_id=task.get("inner_id"),
                    # total_annotations=task.get("total_annotations"),
                    # cancelled_annotations=task.get("cancelled_annotations"),
                    # total_predictions=task.get("total_predictions"),
                    # comment_count=task.get("comment_count"),
                    # unresolved_comment_count=task.get("unresolved_comment_count"),
                    # last_comment_updated_at=task.get("last_comment_updated_at"),
                    # reviewed_result=task.get("reviewed_result"),
                    # is_in_review=task.get("is_in_review"),
                    # is_in_qc=task.get("is_in_qc"),
                    # qualified_result=task.get("qualified_result"),
                    project_id=project_id,
                    # updated_by_id=task.get("updated_by"),
                    # file_upload=task.get("file_upload"),
                    # reviewed_by_id=task.get("reviewed_by"),
                    # qualified_by_id=task.get("qualified_by"),
                    # assigned_to=task.get("assigned_to"),
                    # comment_authors = task["comment_authors"]
                    created_by_id=user.id,
                )
        
        comment_authors = task.get("comment_authors")
        if comment_authors is not None:
            task_instance.comment_authors.set(comment_authors)
        
        if task.get("project") == project_id:
            if Annotation.objects.filter(pk=data["id"]).exists():
                annotation = Annotation.objects.filter(pk=data["id"])
                annotation.update(
                    result=data["result"],
                    task=task_instance,
                    completed_by_id=data["completed_by"]["id"],
                    was_cancelled=data["was_cancelled"],
                    ground_truth=data["ground_truth"],
                    created_at=data["created_at"],
                    updated_at=data["updated_at"],
                    lead_time=data["lead_time"],
                    parent_prediction=data["parent_prediction"],
                    parent_annotation=data["parent_annotation"]
                )
            else:
                Annotation.objects.create(
                    pk=data["id"],
                    result=data["result"],
                    task=task_instance,
                    completed_by_id=data["completed_by"]["id"],
                    was_cancelled=data["was_cancelled"],
                    ground_truth=data["ground_truth"],
                    created_at=data["created_at"],
                    updated_at=data["updated_at"],
                    lead_time=data["lead_time"],
                    parent_prediction=data["parent_prediction"],
                    parent_annotation=data["parent_annotation"]
                )
        
    except Exception as e:
        print(e)

def validate_json_format(data):
    required_keys = ["id", "task", "result", "was_cancelled", "ground_truth", "created_at", "updated_at", "parent_prediction", "parent_annotation"]

    # Kiểm tra xem tất cả các khóa bắt buộc có trong data không
    for key in required_keys:
        if key not in data:
            return False
    return True

def load_tasks(request, project):
    """ Load tasks from different types of request.data / request.files
    """
    file_upload_ids, found_formats, data_keys = [], [], set()
    could_be_tasks_lists = False

    # take tasks from request FILES
    if len(request.FILES):
        check_file_sizes_and_number(request.FILES)
        import_type = request.data.get('type_import')
        for filename, file in request.FILES.items():
            filename, extension = os.path.splitext(file.name)

            if extension == '.json' and filename.split('_')[0].isdigit():
                file_content = file.read().decode('utf-8')
                data = json.loads(file_content)
                if validate_json_format(data):
                    import_task_with_annotation(request.user, data, project)
                    return None, None, None, None, None

            file_content = None

            if project.template is not None:
                if project.template.name == "Named Entity Recognition" and extension.lower() == '.csv' or project.template.name == "NER Slot Annotation" and extension.lower() == '.csv':
                    file_content = file.read().decode('utf-8')

                if project.template.name == "Named Entity Recognition" and extension.lower() == '.xlsx' or project.template.name == "NER Slot Annotation" and extension.lower() == '.xlsx':
                    print(f"[{file.name}] Converting to JSON")
                    tasks, labels = convert_xlsx(file.read(), file.name)
                    print(f"[{file.name}] Converted to JSON file")

                    if len(labels) > 0:
                        print(f"[{file.name}] Found {len(labels)} label(s)")
                        print(f"[{file.name}] Updating project labels")
                        update_label_NER_ml(project, labels)
                        print(f"[{file.name}] Updated project labels")

                    # project_dir = os.path.join(settings.MEDIA_ROOT, settings.UPLOAD_DIR, str(project.id))
                    # os.makedirs(project_dir, exist_ok=True)

                    print(f"[{file.name}] Found {len(tasks)} task(s)")
                    chunks = split_into_chunks(tasks, 10)

                    for tasks in chunks:
                        Job.objects.create(
                            name="create_tasks_with_annotation",
                            workspace={
                                "tasks": tasks,
                                "project_id": project.pk,
                                "user_id": request.user.pk,
                            },
                        )

                    #     try:
                    #         file_name = output["annotations"][0]["result"][0]["file_name"]
                    #         filename = str(file_name) + '.json'
                    #     except:
                    #         filename = str(uuid.uuid4())[0:8] + '-' + 'output.json'
                    #
                    #     path = os.path.join(project_dir, filename)
                    #
                    #     with open(path, 'w', encoding='utf-8') as json_file:
                    #         json.dump(output, json_file, ensure_ascii=False, indent=4)
                    #
                    #     instance = FileUpload(user=request.user, project=project, file=path)
                    #
                    #     if settings.SVG_SECURITY_CLEANUP:
                    #         content_type, encoding = mimetypes.guess_type(str(instance.file.name))
                    #         if content_type in ['image/svg+xml']:
                    #             clean_xml = allowlist_svg(instance.file.read())
                    #             instance.file.seek(0)
                    #             instance.file.write(clean_xml)
                    #             instance.file.truncate()
                    #     instance.save()
                    #
                    #     object_name = str(os.path.basename(instance.file.file.name))
                    #     file_path = instance.file.path
                    #
                    #     file_upload_ids.append(instance.id)

                    # tasks, found_formats, data_keys = FileUpload.load_tasks_from_uploaded_files(project, file_upload_ids)

                    return None, None, None, None, None
                
            if zipfile.is_zipfile(file):
                if import_type and import_type == "dataset":
                    instance = FileUpload(user=request.user, project=project, file=file)
                    instance.save()
                    object_name = str(os.path.basename(instance.file.file.name))
                    file_path = instance.file.path

                    now = datetime.datetime.now()
                    date_str = now.strftime("%Y%m%d")
                    time_str = now.strftime("%H%M%S")
                    
                    version = f'{date_str}-{time_str}'
                    dir_path = f"dataset_{project.id}/{version}/"
                    dataset_upload = ProjectCloudStorage(bucket_prefix="project-", object_prefix=dir_path)

                    # Lưu thư mục vào MinIO
                    # dataset_upload.upload_file(
                    #     project=project,
                    #     bucket_name=str(project.id),
                    #     object_name=object_name,
                    #     file_path=file_path,
                    #     new_thread=True
                    # )

                    from model_marketplace.models import DatasetModelMarketplace
                    user = request.user

                    try:
                        from io_storages.functions import get_all_project_storage_with_name
                        storages = get_all_project_storage_with_name(project.pk)
                        for storage in storages:
                            storage.upload_file(object_name, file_path, f'dataset_{project.pk}', user=user)
                            storage_name  = storage.storage_name
                            storage_id = storage.id
                            break

                        DatasetModelMarketplace.objects.create(name=version, owner_id=user.id, author_id=user.id, project_id=project.id, 
                                                            catalog_id=project.template.catalog_model_id, model_id=0, order=0, config=0, version=version,
                                                            dataset_storage_id=storage_id, dataset_storage_name=storage_name)
                    except Exception as e:
                        print(e)

                    return None, None, None, None, None
                else:
                    from django.core.files import File
                    check_import_task = True

                    with tempfile.TemporaryDirectory() as temp_dir:
                        with zipfile.ZipFile(file, 'r') as zip_ref:
                            zip_ref.extractall(temp_dir)
                        
                        for root, dirs, files in os.walk(temp_dir):
                            for file_name in files:
                                file_path = os.path.join(root, file_name)

                                if "__MACOSX" in file_path or file_name.startswith("."):
                                    continue
                                try:
                                    with open(file_path, 'rb') as f:
                                        django_file = File(f, name=file_name)
                                        filename, extension = os.path.splitext(file_name)

                                        if extension == '.json' and filename.isdigit():
                                            file_content = django_file.read().decode('utf-8')
                                            data = json.loads(file_content)
                                            if validate_json_format(data):
                                                check_import_task = False
                                                import_task_with_annotation(request.user, data)
                                        
                                        if check_import_task:
                                            # Đọc nội dung của từng file
                                            file_upload = create_file_upload(request, project, django_file, file_content)
                                            if file_upload.format_could_be_tasks_list:
                                                could_be_tasks_lists = True
                                                
                                            file_upload_ids.append(file_upload.id)
                                            tasks, found_formats, data_keys = FileUpload.load_tasks_from_uploaded_files(project, file_upload_ids)

                                except Exception as e:
                                    print(e)
                        
                        if not check_import_task:
                            return None, None, None, None, None
                         
                        return tasks, file_upload_ids, could_be_tasks_lists, found_formats, list(data_keys)
          
            else:
                file_upload = create_file_upload(request, project, file, file_content)
                if not file_upload:
                    return None, None, None, None, None
                if file_upload.format_could_be_tasks_list:
                    could_be_tasks_lists = True

                file_upload_ids.append(file_upload.id)
                tasks, found_formats, data_keys = FileUpload.load_tasks_from_uploaded_files(project, file_upload_ids)

    # take tasks from url address
    elif 'application/x-www-form-urlencoded' in request.content_type:
        # empty url
        url = request.data.get('url')
        image = request.data.get('image')
        if not url and not image:
            raise ValidationError('"url" is not found in request data')

        if image:
            data_keys, found_formats, tasks, file_upload_ids = tasks_from_base64(
                file_upload_ids, project, request, image
            )
        else:
            # try to load json with task or tasks from url as string
            json_data = str_to_json(url)
            if json_data:
                for _url in json_data:
                    if settings.SSRF_PROTECTION_ENABLED and url_is_local(_url):
                        raise ImportFromLocalIPError

                    if _url.strip().startswith('file://'):
                        raise ValidationError('"url" is not valid')

                    data_keys, found_formats, tasks, file_upload_ids = tasks_from_url(
                        file_upload_ids, project, request, _url
                    )
                # file_upload = create_file_upload(request, project, SimpleUploadedFile('inplace.json', url.encode()))
                # file_upload_ids.append(file_upload.id)
                # tasks, found_formats, data_keys = FileUpload.load_tasks_from_uploaded_files(project, file_upload_ids)
                
            # download file using url and read tasks from it
            else:
                if settings.SSRF_PROTECTION_ENABLED and url_is_local(url):
                    raise ImportFromLocalIPError

                if url.strip().startswith('file://'):
                    raise ValidationError('"url" is not valid')

                data_keys, found_formats, tasks, file_upload_ids = tasks_from_url(
                    file_upload_ids, project, request, url
                )

    # take one task from request DATA
    elif 'application/json' in request.content_type and isinstance(request.data, dict):
        tasks = [request.data]

    # take many tasks from request DATA
    elif 'application/json' in request.content_type and isinstance(request.data, list):
        for res in request.data:
            if 'image_64' in res:
                data_keys, found_formats, tasks, file_upload_ids = tasks_from_base64(
                    file_upload_ids, project, request, res['image_64']
                )
            else:
            #     _url = res['image']
            #     if settings.SSRF_PROTECTION_ENABLED and url_is_local(_url):
            #         raise ImportFromLocalIPError

            #     if _url.strip().startswith('file://'):
            #         raise ValidationError('"url" is not valid')

            #     data_keys, found_formats, tasks, file_upload_ids = tasks_from_url(
            #         file_upload_ids, project, request, _url
            #     )
            # elif 'text' in res:
            #     file_content = res['text']
            #     project_dir = os.path.join(settings.MEDIA_ROOT, settings.UPLOAD_DIR, str(project.id))
            #     os.makedirs(project_dir, exist_ok=True)

            #     # Tạo đường dẫn cho tệp JSON
            #     filename = str(uuid.uuid4())[0:8]+'.txt'
            #     path = os.path.join(project_dir, filename)
            #     with open(path, 'w') as file:
            #         file.write(file_content)

            #     file_upload = create_file_upload(request, project, path)
            #     file_upload_ids.append(file_upload.id)
            
                tasks = request.data

    # incorrect data source
    else:
        raise ValidationError('load_tasks: No data found in DATA or in FILES')

    # check is data root is list
    if not isinstance(tasks, list):
        raise ValidationError('load_tasks: Data root must be list')

    # empty tasks error
    if not tasks:
        raise ValidationError('load_tasks: No tasks added')

    # check_max_task_number(tasks)
    return tasks, file_upload_ids, could_be_tasks_lists, found_formats, list(data_keys)

def convert_csv_ner(file_content):
    import pandas as pd 
    import ast
    from io import StringIO
    df = pd.read_csv(StringIO(file_content))

    # Khởi tạo các biến
    text_data = []
    annotations = []
    labels = []
    current_position = 0

    for index, row in df.iterrows():
        text_line = row['text'].lower()
        if not 'slots' in row:
            text_data.append(text_line)
            continue
        
        slots = row['slots']
        
        # Kiểm tra nếu slots là chuỗi và không rỗng
        if isinstance(slots, str) and slots:
            slots = ast.literal_eval(slots)  # Chuyển đổi chuỗi JSON thành từ điển an toàn
        
            # Thêm dòng văn bản vào text_data
            text_data.append(text_line)
            text_line_length = len(text_line)
            index_slot = 0
            # Duyệt qua các mục trong slots
            for slot, value in slots.items():
                if value != 'NA':
                    start_pos = text_line.find(value.lower())
                    if start_pos != -1:
                        print(slot, value)
                        if slot not in labels:
                            labels.append(slot)
                        annotation = {
                            "value": {
                                "start": current_position + start_pos,
                                "end": current_position + start_pos + len(value),
                                "text": value,
                                "labels": [slot]
                            },
                            "id": index_slot,
                            "from_name": "label",
                            "to_name": "text",
                            "type": "labels"
                        }
                        annotations.append(annotation)
                        index_slot += 1
            
            # Cập nhật vị trí hiện tại
            current_position += text_line_length + 3

    final_text = '\n \n'.join(text_data)

    # Tạo cấu trúc JSON
    output_json = {
        "data": {
            "text": final_text
        }
    }
    
    if len(annotations)>0:
        output_json["annotations"] = [{
            "result": annotations
        }]

    return output_json, labels

def update_label_NER_ml(project, labels):
        import random
        import string
        parsed_label_config = project.parsed_label_config
        label_config_title = project.label_config
    
        existing_labels = parsed_label_config['label'].get('labels', [])  # Lấy danh sách nhãn hiện có
        existing_labels_attrs = parsed_label_config['label'].get('labels_attrs', {})  # Lấy attributes của các nhãn hiện có
        new_label_tags = []
        for label in labels:
            if label not in existing_labels:
                # Thêm nhãn mới vào danh sách nhãn
                existing_labels.append(label)
                color = ''.join([random.choice(string.hexdigits) for _ in range(6)])
                # Tạo một màu ngẫu nhiên cho nhãn mới
                random_color = f"#{color}"
                # Cập nhật attributes cho nhãn mới với màu ngẫu nhiên
                existing_labels_attrs[label] = {
                    "value": label,
                    "background": random_color
                }

                new_label_tag = f'<Label value="{label}" background="{random_color}"/>'
                new_label_tags.append(new_label_tag)
        
        # Cập nhật danh sách nhãn và attributes vào parsed_label_config
        parsed_label_config['label']['labels'] = existing_labels
        parsed_label_config['label']['labels_attrs'] = existing_labels_attrs
        new_label_tags_str = '\n'.join(new_label_tags)
        label_config_title = label_config_title.replace('</Labels>', f'\n{new_label_tags_str}\n</Labels>')

        # parsed_label_config['label']['labels'] = list(set(parsed_label_config['label'].get('labels', []) + labels))

        project.parsed_label_config = parsed_label_config
        project.label_config = label_config_title
        project.save()

        return project

def convert_xlsx(file_content, original_file_name):
    import pandas as pd
    excel_file = io.BytesIO(file_content)
    
    df = pd.read_excel(excel_file)

    # Khởi tạo các biến
    text_data = []
    labels = []
    available_labels = df['style'].dropna().unique().tolist()
    for label in available_labels:
        if label not in labels:
            labels.append(label)

    for index, row in df.iterrows():
        text_line = row['segment_transcript']
        
        if pd.isna(text_line) or not text_line.strip():
            continue

        label = row['style']
        file_name = row["unique_id"]

        if pd.isna(file_name) or not str(file_name).strip():
            file_name = ""

        text_data.append({
            "data": {
                "text": text_line,
                "original_file": original_file_name,
            },
            "result": [
                {
                    "value": {
                        "start": 0,
                        "end": len(text_line),
                        "text": text_line,
                        "labels": [label]
                    },
                    "file_name": file_name,
                    "from_name": "label",
                    "to_name": "text",
                    "type": "labels"
                },
            ],
        })

    return text_data, labels