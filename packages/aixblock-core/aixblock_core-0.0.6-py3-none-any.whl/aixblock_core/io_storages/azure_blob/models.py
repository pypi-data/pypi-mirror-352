"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
import logging
import json
import re

from core.redis import start_job_async_or_sync
from datetime import datetime, timedelta
from urllib.parse import urlparse

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.db.models.signals import post_save

from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from django.dispatch import receiver
from core.utils.params import get_env
from io_storages.base_models import ImportStorage, ImportStorageLink, ExportStorage, ExportStorageLink
from plugins.plugin_centrifuge import publish_message
from tasks.models import Annotation

import os
import io
import threading
from io import BytesIO
from pydub import AudioSegment

logger = logging.getLogger(__name__)
logging.getLogger('azure.core.pipeline.policies.http_logging_policy').setLevel(logging.WARNING)


class AzureBlobStorageMixin(models.Model):
    container = models.TextField(
        _('container'), null=True, blank=True,
        help_text='Azure blob container')
    prefix = models.TextField(
        _('prefix'), null=True, blank=True,
        help_text='Azure blob prefix name')
    regex_filter = models.TextField(
        _('regex_filter'), null=True, blank=True,
        help_text='Cloud storage regex for filtering objects')
    use_blob_urls = models.BooleanField(
        _('use_blob_urls'), default=False,
        help_text='Interpret objects as BLOBs and generate URLs')
    account_name = models.TextField(
        _('account_name'), null=True, blank=True,
        help_text='Azure Blob account name')
    account_key = models.TextField(
        _('account_key'), null=True, blank=True,
        help_text='Azure Blob account key')

    def get_account_name(self):
        return str(self.account_name) if self.account_name else get_env('AZURE_BLOB_ACCOUNT_NAME')

    def get_account_key(self):
        return str(self.account_key) if self.account_key else get_env('AZURE_BLOB_ACCOUNT_KEY')

    def get_client_and_container(self):
        account_name = self.get_account_name()
        account_key = self.get_account_key()
        if not account_name or not account_key:
            raise ValueError('Azure account name and key must be set using '
                             'environment variables AZURE_BLOB_ACCOUNT_NAME and AZURE_BLOB_ACCOUNT_KEY')
        connection_string = "DefaultEndpointsProtocol=https;AccountName=" + account_name + \
                            ";AccountKey=" + account_key + ";EndpointSuffix=core.windows.net"
        client = BlobServiceClient.from_connection_string(conn_str=connection_string)
        container = client.get_container_client(str(self.container))
        return client, container

    def get_container(self):
        _, container = self.get_client_and_container()
        return container


class AzureBlobImportStorage(ImportStorage, AzureBlobStorageMixin):
    url_scheme = 'azure-blob'

    presign = models.BooleanField(
        _('presign'), default=True,
        help_text='Generate presigned URLs')
    presign_ttl = models.PositiveSmallIntegerField(
        _('presign_ttl'), default=60,
        help_text='Presigned URLs TTL (in minutes)'
    )
    is_global = models.BooleanField(
        _('is_global'), default=False,
        help_text=_('Perform recursive scan over the bucket content'), null=True, blank=True)
    export_storage = models.IntegerField(
        _('export_storage'), null=True, blank=True)
   
    user_id = models.IntegerField(
        _('user_id'), null=True, blank=True)
    org_id = models.IntegerField(
        _('org_id'), null=True, blank=True)
    
    def iterkeys(self):
        container = self.get_container()
        prefix = str(self.prefix) if self.prefix else ''
        files = container.list_blobs(name_starts_with=prefix)
        regex = re.compile(str(self.regex_filter)) if self.regex_filter else None
        # filtered_blobs = [
        #     blob.name for blob in files
        #     if regex.match(blob.name)
        # ]
        for file in files:
            # skip folder
            if file.name == (prefix.rstrip('/') + '/'):
                continue
            # check regex pattern filter
            if regex and not regex.match(file.name):
                logger.debug(file.name + ' is skipped by regex filter')
                continue

            yield file.name

    def get_data(self, key, raw_key=None):
        if 'json' not in key:
            if 'audio' in self.project.data_types or 'image' in self.project.data_types or 'video' in self.project.data_types:
                data_key = settings.DATA_UNDEFINED_NAME

                # try:
                #     self.create_convert_file(key)
                # except:
                #     pass
                
                if raw_key:
                    try:
                        # Truy cập container và tải file
                        container = self.get_container()
                        blob_client = container.get_blob_client(key)

                        # Tải file âm thanh từ Azure Blob Storage
                        stream = io.BytesIO()
                        blob_client.download_blob().readinto(stream)
                        stream.seek(0)

                        # Load file âm thanh với pydub
                        audio = AudioSegment.from_file(stream)
                        duration = len(audio) / 1000.0  # Tính thời lượng (giây)

                        return {data_key: f'{self.url_scheme}://{self.container}/{key}', 'duration': duration}
                    except Exception as e:
                        print(f"Error calculating duration for audio file {key}: {e}")

                return {data_key: f'{self.url_scheme}://{self.container}/{key}'}

        container = self.get_container()
        blob = container.download_blob(key)
        blob_str = blob.content_as_text()
        value = json.loads(blob_str)
        if not isinstance(value, dict):
            raise ValueError(f"Error on key {key}: For {self.__class__.__name__} your JSON file must be a dictionary with one task")  # noqa
        return value
    
    def validate_connection(self, client=None):
        logger.debug('validate_connection')
        if client is None:
            client = self.get_container()

        client.get_container_properties()  # Thử lấy thông tin container

    def scan_and_create_links(self, key=None, duration=None, user=None, original_file=None, extras_data=None):
        return self._scan_and_create_links(AzureBlobImportStorageLink, key, duration, user=user, original_file=original_file, extras_data=extras_data)

    def generate_http_url(self, url, exp_in=None):
        r = urlparse(url, allow_fragments=False)
        container = r.netloc
        blob = r.path.lstrip('/')

        expiry = datetime.utcnow() + timedelta(minutes=self.presign_ttl)

        sas_token = generate_blob_sas(account_name=self.get_account_name(),
                                      container_name=container,
                                      blob_name=blob,
                                      account_key=self.get_account_key(),
                                      permission=BlobSasPermissions(read=True),
                                      expiry=expiry)
        return 'https://' + self.get_account_name() + '.blob.core.windows.net/' + container + '/' + blob + '?' + sas_token

    def scan_export_storage(self):
        # Kiểm tra bản ghi đầu tiên
        export_storage = AzureBlobExportStorage.objects.filter(project_id=self.project_id).first()
        self.export_storage = export_storage.id

    def sync_export_storage(self):
        if not self.export_storage:
            self.scan_export_storage()

        export_storage = AzureBlobExportStorage.objects.filter(id=self.export_storage).first()
        export_storage.sync()
    
    def copy_storage(self, s3_prj, target=True):
        pass

    def alias_storage(self, s3_prj):
        pass
    
    def upload_obj(self, client, file_path, key):
        with open(file_path, "rb") as data:
            client.upload_blob(name=key, data=data, overwrite=True)

    def _upload_file(self, object_name, file_path, prefix="raw_files", scan_link=False, remove_link=False, duration=None, user=None, original_file=None, extras_data=None, publish_channel=None, upload_file_id=None):
        def send_message(msg, percent=None):
            if not publish_channel or not upload_file_id:
                return

            publish_message(
                channel=publish_channel,
                data=json.dumps({
                    "upload_file_id": upload_file_id,
                    "message": msg,
                    "percent": percent,
                }),
            )

        client = self.get_container()
        key = f'{prefix}/{object_name}'  # Tạo đường dẫn file trên S3

        send_message("Saving to cloud storage...")
        self.upload_obj(client, file_path, key)
        send_message("Saved to cloud storage")

        if scan_link:
            self.scan_and_create_links(key, duration, user=user, original_file=original_file, extras_data=extras_data)
            
        if remove_link:
            os.remove(file_path)

    def upload_file(self, object_name, file_path, prefix="raw_files", scan_link=False, remove_link=False, duration=None, user=None, original_file=None, extras_data=None, publish_channel=None, upload_file_id=None):
        # if not thread:
        self._upload_file(object_name, file_path, prefix, scan_link, remove_link, duration, user=user, original_file=original_file, extras_data=extras_data, publish_channel=publish_channel, upload_file_id=upload_file_id)
        # else:
        #     t = threading.Thread(target=self._upload_file, args=(object_name, file_path, prefix, scan_link, remove_link, duration), kwargs={"user": user, "original_file": original_file})
        #     manage_task_thread(t)

    def get_iterkeys(self, object_path=None):
        pass

    def extract_zip(self, object_key):
        pass

    def create_folder(self, folder_name="raw_files/"):
        client = self.get_container()
        client.upload_blob(name=folder_name, data=b"", overwrite=True)

    def _upload_folder(self, folder_path, prefix="raw_files"):
        if not os.path.isdir(folder_path):
            raise ValueError(f"The path {folder_path} is not a valid directory.")
        
        # Walk through the folder
        for root, _, files in os.walk(folder_path):
            for file in files:
                # Full path of the file
                file_path = os.path.join(root, file)
                # Blob name (prefix + relative path of the file from folder_path)
                blob_name = os.path.join(prefix, os.path.relpath(file_path, folder_path)).replace("\\", "/")
                
                # Upload the file
                with open(file_path, "rb") as data:
                    self.container_client.upload_blob(name=blob_name, data=data, overwrite=True)
                    print(f"Uploaded: {file_path} to blob: {blob_name}")

        print("Folder upload completed.")

    def upload_folder(self, folder_path, prefix="raw_files/"):
        t = threading.Thread(target=self._upload_folder, args=(folder_path, prefix))
        t.start()

    # def _create_convert_file(self, key):
    #     from PIL import Image
    #
    #     client = self.get_container()
    #     blob_client = client.get_blob_client(key)
    #     blob_data = blob_client.download_blob().readall()
    #     file_extension = key.split('.')[-1].lower()
    #     project_id = self.project.id
    #
    #     if file_extension in ['jpg', 'jpeg', 'png']:
    #         # Đọc dữ liệu từ S3 object
    #         image_data = blob_data
    #
    #         # Convert object thành đối tượng PIL.Image
    #         image = Image.open(BytesIO(image_data))
    #
    #         ratios = {'small': 6, 'middle': 4, 'large': 2}
    #         for size_name, ratio in ratios.items():
    #             thumbnail = image.copy()
    #
    #             if size_name == 'large':
    #                 # Nếu size_name là 'large', giảm chất lượng ảnh mà không thay đổi kích thước
    #                 thumbnail_io = BytesIO()
    #                 thumbnail.save(thumbnail_io, format=image.format, quality=30)
    #             else:
    #                 width, height = thumbnail.size
    #                 new_width = width // ratio
    #                 new_height = height // ratio
    #
    #                 thumbnail.thumbnail((new_width, new_height))
    #
    #                 # Lưu thumbnail vào BytesIO để upload trực tiếp lên S3
    #                 thumbnail_io = BytesIO()
    #                 thumbnail.save(thumbnail_io, format=image.format)
    #
    #             thumbnail_io.seek(0)  # Đặt lại con trỏ để upload từ đầu file
    #
    #             # Tạo tên file thumbnail
    #             original_image_name = key.split('/')[-1]
    #             thumbnail_key = f'convert_files_{project_id}/{size_name}_{original_image_name}'
    #
    #             client.upload_blob(name=thumbnail_key, data=thumbnail_io, overwrite=True)
    #
    #     elif file_extension in ['mp3', 'wav', 'flac', 'ogg', 'm4a']:
    #         # Xử lý audio
    #         audio_data = blob_data
    #         audio = AudioSegment.from_file(BytesIO(audio_data))
    #
    #         # Thiết lập frame rate
    #         audio = audio.set_frame_rate(24000)
    #
    #         # Tạo tên file mới cho audio
    #         audio_name = key.split('/')[-1]
    #         audio_name_without_ext, ext = os.path.splitext(audio_name)
    #         new_audio_name = f"{audio_name_without_ext}.ogg"
    #
    #         # Lưu audio vào BytesIO
    #         audio_io = BytesIO()
    #         audio.export(audio_io, format="ogg", codec="libopus")
    #         audio_io.seek(0)
    #
    #         # Tạo tên file cho S3
    #         audio_key = f'convert_files/{new_audio_name}'
    #
    #         client.upload_blob(name=audio_key, data=audio_io, overwrite=True)
    

    # def create_convert_file(self, key):
    #     import threading
    #     t = threading.Thread(target=self._create_convert_file, args=(key,))
    #     manage_task_thread(t)

    def download_and_save_folder(self, path, save_path, all_path=True):
        pass
class AzureBlobExportStorage(ExportStorage, AzureBlobStorageMixin):

    def save_annotation(self, annotation):
        container = self.get_container()
        logger.debug(f'Creating new object on {self.__class__.__name__} Storage {self} for annotation {annotation}')
        ser_annotation = self._get_serialized_data(annotation)
        # get key that identifies this object in storage
        key = AzureBlobExportStorageLink.get_key(annotation)
        key = str(self.prefix) + '/' + key if self.prefix else key

        # put object into storage
        blob = container.get_blob_client(key)
        blob.upload_blob(json.dumps(ser_annotation), overwrite=True)

        # create link if everything ok
        AzureBlobExportStorageLink.create(annotation, self)


def async_export_annotation_to_azure_storages(annotation):
    project = annotation.task.project
    if hasattr(project, 'io_storages_azureblobexportstorages'):
        for storage in project.io_storages_azureblobexportstorages.all():
            logger.debug(f'Export {annotation} to Azure Blob storage {storage}')
            storage.save_annotation(annotation)


@receiver(post_save, sender=Annotation)
def export_annotation_to_azure_storages(sender, instance, **kwargs):
    start_job_async_or_sync(async_export_annotation_to_azure_storages, instance)


class AzureBlobImportStorageLink(ImportStorageLink):
    storage = models.ForeignKey(AzureBlobImportStorage, on_delete=models.CASCADE, related_name='links')


class AzureBlobExportStorageLink(ExportStorageLink):
    storage = models.ForeignKey(AzureBlobExportStorage, on_delete=models.CASCADE, related_name='links')
