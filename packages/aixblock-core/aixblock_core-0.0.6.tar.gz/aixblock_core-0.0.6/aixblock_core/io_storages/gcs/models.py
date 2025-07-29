"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
import logging
import json
import socket
import google.auth
import re
import os

from core.redis import start_job_async_or_sync
from google.auth import compute_engine
from google.cloud import storage as google_storage
from google.cloud.storage.client import _marker
from google.auth.transport import requests
from google.oauth2 import service_account
from googleapiclient.discovery import build
from urllib.parse import urlparse
from datetime import datetime, timedelta
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save

import threading
from io import BytesIO

from plugins.plugin_centrifuge import publish_message
from pydub import AudioSegment
import io

from io_storages.base_models import ImportStorage, ImportStorageLink, ExportStorage, ExportStorageLink
from tasks.models import Annotation

logger = logging.getLogger(__name__)

clients_cache = {}


class GCSStorageMixin(models.Model):
    bucket = models.TextField(
        _('bucket'), null=True, blank=True,
        help_text='GCS bucket name')
    prefix = models.TextField(
        _('prefix'), null=True, blank=True,
        help_text='GCS bucket prefix')
    regex_filter = models.TextField(
        _('regex_filter'), null=True, blank=True,
        help_text='Cloud storage regex for filtering objects')
    use_blob_urls = models.BooleanField(
        _('use_blob_urls'), default=False,
        help_text='Interpret objects as BLOBs and generate URLs')
    google_application_credentials = models.TextField(
        _('google_application_credentials'), null=True, blank=True,
        help_text='The content of GOOGLE_APPLICATION_CREDENTIALS json file')

    def get_client(self, raise_on_error=False):
        credentials = None
        project_id = _marker

        # gcs client initialization ~ 200 ms, for 30 tasks it's a 6 seconds, so we need to cache it
        cache_key = f'{self.google_application_credentials}'
        if self.google_application_credentials:
            if cache_key in clients_cache:
                return clients_cache[cache_key]
            try:
                service_account_info = json.loads(self.google_application_credentials)
                project_id = service_account_info.get('project_id', _marker)
                credentials = service_account.Credentials.from_service_account_info(service_account_info)
            except Exception as exc:
                if raise_on_error:
                    raise
                logger.error(f"Can't create GCS credentials", exc_info=True)
                credentials = None
                project_id = _marker

        client = google_storage.Client(project=project_id, credentials=credentials)
        # client = build('drive', 'v3', credentials=credentials)
        if credentials is not None:
            clients_cache[cache_key] = client
        return client

    def get_bucket(self, client=None, bucket_name=None):
        if not client:
            client = self.get_client()
        
        # query = f"mimeType='application/vnd.google-apps.folder' and name='{self.bucket}'"
        # results = client.files().list(q=query, fields="files(id, name)").execute()
        # items = results.get('files', [])
        # return items[0]
    
        return client.get_bucket(bucket_name or self.bucket)

    def validate_connection(self):
        logger.debug('Validating GCS connection')
        client = self.get_client(raise_on_error=True)
        logger.debug('Validating GCS bucket')
        self.get_bucket(client=client)


class GCSImportStorage(GCSStorageMixin, ImportStorage):
    url_scheme = 'gs'

    presign = models.BooleanField(
        _('presign'), default=True,
        help_text='Generate presigned URLs')
    presign_ttl = models.PositiveSmallIntegerField(
        _('presign_ttl'), default=60,
        help_text='Presigned URLs TTL (in minutes)'
    )

    export_storage = models.IntegerField(
        _('export_storage'), null=True, blank=True)
    is_global = models.BooleanField(
        _('is_global'), default=False,
        help_text=_('Perform recursive scan over the bucket content'), null=True, blank=True)
    user_id = models.IntegerField(
        _('user_id'), null=True, blank=True)
    org_id = models.IntegerField(
        _('org_id'), null=True, blank=True)

    def iterkeys(self):
        bucket = self.get_bucket()
        # query = f"'{bucket['id']}' in parents"
        # results = service.files().list(q=query, fields="files(id, name)").execute()
        # items = results.get('files', [])
        files = bucket.list_blobs(prefix=self.prefix)
        prefix = str(self.prefix) if self.prefix else ''
        regex = re.compile(str(self.regex_filter)) if self.regex_filter else None

        for file in files:
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
                # try:
                #     self.create_convert_file(key)
                # except:
                #     pass

                if raw_key:
                    try:
                        # Lấy bucket và tải file từ GCS
                        bucket = self.get_bucket()
                        blob = bucket.blob(key)
                        
                        # Tải dữ liệu nhị phân từ blob
                        audio_data = blob.download_as_string()
                        
                        # Load file âm thanh với pydub
                        audio = AudioSegment.from_file(io.BytesIO(audio_data))
                        duration = len(audio) / 1000.0  # Tính thời lượng (giây)

                        return {settings.DATA_UNDEFINED_NAME: f'{self.url_scheme}://{self.bucket}/{key}', 'duration':duration}
                    except Exception as e:
                        print(f"Error calculating duration for audio file {key}: {e}")

                
                return {settings.DATA_UNDEFINED_NAME: f'{self.url_scheme}://{self.bucket}/{key}'}
        bucket = self.get_bucket()
        blob = bucket.blob(key)
        blob_str = blob.download_as_string()
        value = json.loads(blob_str)
        if not isinstance(value, dict):
            raise ValueError(f"Error on key {key}: For {self.__class__.__name__} your JSON file must be a dictionary with one task.")  # noqa
        return value

    @classmethod
    def is_gce_instance(cls):
        """Check if it's GCE instance via DNS lookup to metadata server"""
        try:
            socket.getaddrinfo('metadata.google.internal', 80)
        except socket.gaierror:
            return False
        return True

    def generate_http_url(self, url, exp_in=None):
        r = urlparse(url, allow_fragments=False)
        bucket_name = r.netloc
        key = r.path.lstrip('/')
        if self.is_gce_instance() and not self.google_application_credentials:
            logger.debug('Generate signed URL for GCE instance')
            return self.python_cloud_function_get_signed_url(bucket_name, key)
        else:
            logger.debug('Generate signed URL for local instance')
            return self.generate_download_signed_url_v4(bucket_name, key)

    def generate_download_signed_url_v4(self, bucket_name, blob_name):
        """Generates a v4 signed URL for downloading a blob.

        Note that this method requires a service account key file. You can not use
        this if you are using Application Default Credentials from Google Compute
        Engine or from the Google Cloud SDK.
        """
        # bucket_name = 'your-bucket-name'
        # blob_name = 'your-object-name'

        client = self.get_client()
        bucket = self.get_bucket(client, bucket_name)
        blob = bucket.blob(blob_name)

        url = blob.generate_signed_url(
            version="v4",
            # This URL is valid for 15 minutes
            expiration=timedelta(minutes=self.presign_ttl),
            # Allow GET requests using this URL.
            method="GET",
        )

        logger.debug('Generated GCS signed url: ' + url)
        return url

    def python_cloud_function_get_signed_url(self, bucket_name, blob_name):
        # https://gist.github.com/jezhumble/91051485db4462add82045ef9ac2a0ec
        # Copyright 2019 Google LLC.
        # SPDX-License-Identifier: Apache-2.0
        # This snippet shows you how to use Blob.generate_signed_url() from within compute engine / cloud functions
        # as described here: https://cloud.google.com/functions/docs/writing/http#uploading_files_via_cloud_storage
        # (without needing access to a private key)
        # Note: as described in that page, you need to run your function with a service account
        # with the permission roles/iam.serviceAccountTokenCreator
        auth_request = requests.Request()
        credentials, project = google.auth.default()
        storage_client = google_storage.Client(project, credentials)
        # storage_client = self.get_client()
        data_bucket = storage_client.lookup_bucket(bucket_name)
        signed_blob_path = data_bucket.blob(blob_name)
        expires_at_ms = datetime.now() + timedelta(minutes=self.presign_ttl)
        # This next line is the trick!
        signing_credentials = compute_engine.IDTokenCredentials(auth_request, "",
                                                                service_account_email=None)
        signed_url = signed_blob_path.generate_signed_url(expires_at_ms, credentials=signing_credentials, version="v4")
        return signed_url

    def scan_and_create_links(self, key=None, duration=None, user=None, original_file=None, extras_data=None):
        return self._scan_and_create_links(GCSImportStorageLink, key, duration, user=user, original_file=original_file, extras_data=extras_data)

    def scan_export_storage(self):
        # Kiểm tra bản ghi đầu tiên
        export_storage = GCSExportStorage.objects.filter(project_id=self.project_id).first()
        self.export_storage = export_storage.id

    def sync_export_storage(self):
        if not self.export_storage:
            self.scan_export_storage()

        export_storage = GCSExportStorage.objects.filter(id=self.export_storage).first()
        export_storage.sync()
    
    def copy_storage(self, s3_prj, target=True):
        pass

    def alias_storage(self, s3_prj):
        pass
    
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

        client = self.get_client()
        bucket = self.get_bucket(client, self.bucket)

        # Tạo đường dẫn đến file (nếu cần thêm prefix vào)
        blob_name = f"{prefix}/{object_name}"  # Tạo blob name với prefix
        
        # Kiểm tra nếu file tồn tại
        if not os.path.exists(file_path):
            print(f"File {file_path} does not exist.")
            return

        # Mở file và upload
        blob = bucket.blob(blob_name)

        # Upload file lên GCS
        send_message("Saving to cloud storage...")
        blob.upload_from_filename(file_path)
        send_message("Saved to cloud storage")
        print(f"File {file_path} uploaded to {blob_name}.")

        # Optional: Scan and/or remove link
        if scan_link:
            self.scan_and_create_links(blob_name, duration, user=user, original_file=original_file, extras_data=extras_data)
            
        if remove_link:
            os.remove(file_path)
        
        return blob_name

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
    
    def create_folder(self, folder_name="raw_files"):
        """Tạo thư mục giả trong GCS bằng cách tạo một blob có tên kết thúc với dấu '/'."""
        client = self.get_client()
        bucket = client.get_bucket(self.bucket)

        # Tạo một blob giả, nơi chỉ cần tạo đối tượng với tên kết thúc bằng "/"
        blob = bucket.blob(f"{folder_name}/")  # Thêm dấu "/" vào cuối tên thư mục

        # Lưu đối tượng, nhưng đối tượng này sẽ trống
        blob.upload_from_string('')  # Nội dung không quan trọng, chỉ cần tạo đối tượng

        print(f"Folder {folder_name} created in bucket {self.bucket}.")

    def _upload_folder(self, folder_path, prefix="raw_files"):
        """Upload all files in a folder to GCS."""
        if not os.path.isdir(folder_path):
            print(f"The provided path {folder_path} is not a valid directory.")
            return

        for root, dirs, files in os.walk(folder_path):
            for file in files:
                # Get the relative path of the file and create the full GCS object name
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, folder_path)
                # Upload the file to GCS with the folder structure
                self._upload_file(relative_path, file_path, prefix)

    def upload_folder(self, folder_path, prefix="raw_files/"):
        t = threading.Thread(target=self._upload_folder, args=(folder_path, prefix))
        t.start()

    def download_and_save_folder(self, path, save_path, all_path=True):
        pass

    # def _create_convert_file(self, key):
    #     from PIL import Image
    #
    #     client = self.get_client()
    #     bucket = self.get_bucket(client, self.bucket)
    #
    #     # Lấy blob từ GCS bằng key
    #     blob = bucket.blob(key)
    #
    #     # Lấy dữ liệu của file từ GCS dưới dạng bytes
    #     blob_data = blob.download_as_string()
    #
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
    #         from pydub import AudioSegment
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
    #
    #
    # def create_convert_file(self, key):
    #     import threading
    #     t = threading.Thread(target=self._create_convert_file, args=(key,))
    #     manage_task_thread(t)

class GCSExportStorage(GCSStorageMixin, ExportStorage):

    def save_annotation(self, annotation):
        bucket = self.get_bucket()
        logger.debug(f'Creating new object on {self.__class__.__name__} Storage {self} for annotation {annotation}')
        ser_annotation = self._get_serialized_data(annotation)

        # get key that identifies this object in storage
        key = GCSExportStorageLink.get_key(annotation)
        key = str(self.prefix) + '/' + key if self.prefix else key

        # put object into storage
        blob = bucket.blob(key)
        blob.upload_from_string(json.dumps(ser_annotation))

        # create link if everything ok
        GCSExportStorageLink.create(annotation, self)


def async_export_annotation_to_gcs_storages(annotation):
    project = annotation.task.project
    if hasattr(project, 'io_storages_gcsexportstorages'):
        for storage in project.io_storages_gcsexportstorages.all():
            logger.debug(f'Export {annotation} to GCS storage {storage}')
            storage.save_annotation(annotation)


@receiver(post_save, sender=Annotation)
def export_annotation_to_s3_storages(sender, instance, **kwargs):
    start_job_async_or_sync(async_export_annotation_to_gcs_storages, instance)


class GCSImportStorageLink(ImportStorageLink):
    storage = models.ForeignKey(GCSImportStorage, on_delete=models.CASCADE, related_name='links')


class GCSExportStorageLink(ExportStorageLink):
    storage = models.ForeignKey(GCSExportStorage, on_delete=models.CASCADE, related_name='links')
