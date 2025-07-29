"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
import logging
import json
import socket
import google.auth
import re
import io

from core.redis import start_job_async_or_sync
from google.auth import compute_engine
from google.cloud import storage as google_storage
from google.cloud.storage.client import _marker
from googleapiclient.errors import HttpError
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

from types import SimpleNamespace
from googleapiclient.http import MediaIoBaseDownload, MediaInMemoryUpload

from io_storages.base_models import ImportStorage, ImportStorageLink, ExportStorage, ExportStorageLink
from tasks.models import Annotation
from django.core.files.base import ContentFile
from data_import.models import FileUpload

logger = logging.getLogger(__name__)

clients_cache = {}

SCOPES = ['https://www.googleapis.com/auth/drive']

class GDriverStorageMixin(models.Model):
    bucket = models.TextField(
        _('bucket'), null=True, blank=True,
        help_text='GDriver bucket name')
    prefix = models.TextField(
        _('prefix'), null=True, blank=True,
        help_text='GDriver bucket prefix')
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

        try:
            cache_key = f'{self.google_application_credentials}'
            
            if self.google_application_credentials:
                if cache_key in clients_cache:
                    return clients_cache[cache_key]
                
                try:
                    service_account_info = json.loads(self.google_application_credentials)
                    project_id = service_account_info.get('project_id', _marker)
                    credentials = service_account.Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
                except Exception as exc:
                    if raise_on_error:
                        raise
                    logger.error(f"Can't create GDriver credentials", exc_info=True)
                    credentials = None
                    project_id = _marker

            client = google_storage.Client(project=project_id, credentials=credentials)
            client = build('drive', 'v3', credentials=credentials)
            if credentials is not None:
                clients_cache[cache_key] = client
            return client
        except Exception as e:
            print(e)
            return None

    def get_bucket(self, client=None, bucket_name=None, parent_id=None):
        if not client:
            client = self.get_client()

        if bucket_name:
            query = f"mimeType='application/vnd.google-apps.folder' and name='{bucket_name}'"
        else:
            query = f"mimeType='application/vnd.google-apps.folder' and name='{self.bucket}'"

        if parent_id:
            query += f" and '{parent_id}' in parents"

        results = client.files().list(q=query, fields="files(id, name)").execute()
        items = results.get('files', [])

        if len(items) == 0:
            return None
        
        return items[0]
    

    def validate_connection(self):
        logger.debug('Validating GDriver connection')
        client = self.get_client(raise_on_error=True)
        logger.debug('Validating GDriver bucket')
        self.get_bucket(client=client)


class GDriverImportStorage(GDriverStorageMixin, ImportStorage):
    url_scheme = 'gdr'

    presign = models.BooleanField(
        _('presign'), default=True,
        help_text='Generate presigned URLs')
    presign_ttl = models.PositiveSmallIntegerField(
        _('presign_ttl'), default=1,
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
        client = self.get_client()
        # query = f"'{bucket['id']}' in parents and mimeType != 'application/vnd.google-apps.folder'"
        # results = client.files().list(q=query, fields="files(id, name)").execute()
        # files = results.get('files', [])
        # Hàm đệ quy để lấy tất cả các file trong thư mục

        prefix = str(self.prefix) if self.prefix else ''
        regex = re.compile(str(self.regex_filter)) if self.regex_filter else None

        def list_files_in_folder(folder_id, current_path=""):
            query = f"'{folder_id}' in parents"
            results = client.files().list(q=query, fields="files(id, name, mimeType)").execute()
            items = results.get('files', [])
            
            files = []
            for item in items:
                # Tạo đường dẫn đầy đủ cho file/thư mục hiện tại
                full_path = current_path + '/' + item['name'] if current_path else item['name']

                if item['mimeType'] == 'application/vnd.google-apps.folder':
                    # Đệ quy gọi lại để lấy file trong thư mục con, cập nhật đường dẫn
                    files.extend(list_files_in_folder(item['id'], full_path))
                else:
                    # Áp dụng bộ lọc regex với đường dẫn đầy đủ
                    if regex and not regex.match(full_path):
                        logger.debug(full_path + ' is skipped by regex filter')
                        continue
                    # Thêm file vào danh sách với đường dẫn đầy đủ
                    files.append(SimpleNamespace(id=item['id'], name=item['name'], path=full_path))
            return files

        files = list_files_in_folder(bucket['id'])
        # files = [SimpleNamespace(**file) for file in files]
        for file in files:
            # if file.name == (prefix.rstrip('/') + '/'):
            #     continue
            # check regex pattern filter
            # if regex and not regex.match(file.name):
            #     logger.debug(file.name + ' is skipped by regex filter')
            #     continue
            yield f'{file.path}_{file.id}'

    def create_connect_to_import_storage(self, import_id):
        GDriverImportStorage.objects.filter(id=import_id).update(export_storage=self.id)
        
    def _upload_file(self, object_name, file_path, prefix="raw_files", scan_link=False, remove_link=False, duration=None, user=None, original_file=None, extras_data=None):
        try:
            import mimetypes
            from googleapiclient.http import MediaFileUpload

            bucket = self.get_bucket()
            client = self.get_client()

            bucket_snapshot = self.get_bucket(bucket_name=prefix, parent_id=bucket['id'])
            if not bucket_snapshot:
                folder_metadata = {
                    'name': f'{prefix}',
                    'mimeType': 'application/vnd.google-apps.folder',
                    'parents': [bucket['id']]
                }
                try:
                    file = client.files().create(body=folder_metadata, fields='id').execute()
                    folder_id = file.get('id')

                except HttpError as error:
                    print(f'An error occurred: {error}')
                    return None
            else:
                folder_id = bucket_snapshot['id']

            mime_type, _ = mimetypes.guess_type(file_path)
            file_metadata = {
                'name': f'{object_name}',
                'parents': [folder_id]
            }

            with open(file_path, 'rb') as file:
                file_bytes = file.read()

            media = MediaInMemoryUpload(file_bytes, mimetype=mime_type)

            try:
                query = f"'{folder_id}' in parents and name='{file_metadata['name']}' and trashed=false"
                results = client.files().list(q=query, fields="files(id, name)").execute()
                items = results.get('files', [])
                if len(items) > 0:
                    file_id = items[0]['id']
                    file = client.files().update(fileId=file_id, media_body=media).execute()
                else:
                    file = client.files().create(body=file_metadata, media_body=media, fields='id').execute()

                permission = {
                    'type': 'anyone',
                    'role': 'writer'
                }

                client.permissions().create(
                    fileId=bucket['id'],
                    body=permission,
                    fields='id',
                ).execute()

                # create link if everything ok
                # GDriverExportStorageLink.create(annotation, self)

            except HttpError as error:
                print(f'An error occurred: {error}')
                return None
            
        except Exception as error:
            print(f'An error occurred: {error}')
            return None
        
    def upload_file(self, object_name, file_path, prefix="raw_files", scan_link=False, remove_link=False, duration=None, user=None, original_file=None, extras_data=None):
        # import threading
        # if not thread:
        self._upload_file(object_name, file_path, prefix, scan_link, remove_link, duration, user=user, original_file=original_file, extras_data=extras_data)
        # else:
        #     t = threading.Thread(target=self._upload_file, args=(object_name, file_path, prefix, scan_link, remove_link, duration), kwargs={"user": user, "original_file": original_file})
        #     manage_task_thread(t)

    def get_iterkeys(self, object_path=None):
        pass

    def extract_zip(self, object_key):
        pass
    
    def create_folder(self, folder_name="raw_files"):
        pass

    def _upload_folder(self, folder_path, prefix="raw_files"):
        pass

    def upload_folder(self, folder_path, prefix="raw_files"):
        pass

    def download_and_save_folder(self, path, save_path, all_path=True):
        pass
    
    def get_data(self, key, raw_key=None):
        # if self.use_blob_urls:
        #     return {settings.DATA_UNDEFINED_NAME: f'{self.url_scheme}://{self.bucket}/{key}'}
        
        # bucket = self.get_bucket()
        client = self.get_client()
        
        file = client.files().get(fileId=key, fields='name, mimeType').execute()
        mime_type = file['mimeType']
        file_name = file['name']

        request = client.files().get_media(fileId=key)
        file_data = io.BytesIO()
        downloader = MediaIoBaseDownload(file_data, request)
        done = False

        while not done:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}%.")

        file_data.seek(0)
        file_content = file_data.read()

        django_file = ContentFile(file_content, name=file_name)
    
        # Create and save the FileUpload instance
        instance = FileUpload(user_id=1, project=self.project, file=django_file)
        instance.save()

        if "text" in mime_type:
            value = {
                "text": f"{file_content.decode('utf-8')}"
            }

        elif "audio" in mime_type:
            import mutagen
            file_path = instance.filepath
            media_path = settings.MEDIA_ROOT.rstrip('/')
            file_meta = mutagen.File(media_path + '/' + file_path)
            value = {
                "audio": instance.url,
                "duration": file_meta.info.length
            }

        elif "image" in mime_type:
            value = {
                "image": instance.url
            }

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

    def generate_http_url(self, url):
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

        logger.debug('Generated GDriver signed url: ' + url)
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

    def scan_and_create_links(self):
        return self._scan_and_create_links(GDriverImportStorageLink)

    def scan_export_storage(self):
        # Kiểm tra bản ghi đầu tiên
        export_storage = GDriverExportStorage.objects.filter(project_id=self.project_id).first()
        self.export_storage = export_storage.id

    def sync_export_storage(self):
        if not self.export_storage:
            self.scan_export_storage()

        export_storage = GDriverExportStorage.objects.filter(id=self.export_storage).first()
        export_storage.sync()
    
    def copy_storage(self, s3_prj, target=True):
        pass

    def alias_storage(self, s3_prj):
        pass
class GDriverExportStorage(GDriverStorageMixin, ExportStorage):

    def save_annotation(self, annotation):
        try:
            bucket = self.get_bucket()
            client = self.get_client()
            logger.debug(f'Creating new object on {self.__class__.__name__} Storage {self} for annotation {annotation}')
            ser_annotation = self._get_serialized_data(annotation)

            # get key that identifies this object in storage
            key = GDriverExportStorageLink.get_key(annotation)

            bucket_snapshot = self.get_bucket(bucket_name="snapshot", parent_id=bucket['id'])
            if not bucket_snapshot:
                folder_metadata = {
                    'name': 'snapshot',
                    'mimeType': 'application/vnd.google-apps.folder',
                    'parents': [bucket['id']]
                }
                try:
                    file = client.files().create(body=folder_metadata, fields='id').execute()
                    folder_id = file.get('id')

                except HttpError as error:
                    print(f'An error occurred: {error}')
                    return None
            else:
                folder_id = bucket_snapshot['id']

            file_metadata = {
                'name': f'{key}.json',
                'parents': [folder_id]
            }

            media = MediaInMemoryUpload(f'{ser_annotation}'.encode('utf-8'), mimetype='text/plain')

            try:
                query = f"'{folder_id}' in parents and name='{file_metadata['name']}' and trashed=false"
                results = client.files().list(q=query, fields="files(id, name)").execute()
                items = results.get('files', [])
                if len(items) > 0:
                    file_id = items[0]['id']
                    file = client.files().update(fileId=file_id, media_body=media).execute()
                else:
                    file = client.files().create(body=file_metadata, media_body=media, fields='id').execute()

                permission = {
                    'type': 'anyone',
                    'role': 'writer'
                }

                client.permissions().create(
                    fileId=bucket['id'],
                    body=permission,
                    fields='id'
                ).execute()

                # create link if everything ok
                GDriverExportStorageLink.create(annotation, self)

            except HttpError as error:
                print(f'An error occurred: {error}')
                return None
            
        except Exception as error:
            print(f'An error occurred: {error}')
            return None

def async_export_annotation_to_gdr_storages(annotation):
    project = annotation.task.project
    if hasattr(project, 'io_storages_gdriverexportstorages'):
        for storage in project.io_storages_gdriverexportstorages.all():
            logger.debug(f'Export {annotation} to GDriver storage {storage}')
            storage.save_annotation(annotation)


@receiver(post_save, sender=Annotation)
def export_annotation_to_s3_storages(sender, instance, **kwargs):
    start_job_async_or_sync(async_export_annotation_to_gdr_storages, instance)


class GDriverImportStorageLink(ImportStorageLink):
    storage = models.ForeignKey(GDriverImportStorage, on_delete=models.CASCADE, related_name='links')


class GDriverExportStorageLink(ExportStorageLink):
    storage = models.ForeignKey(GDriverExportStorage, on_delete=models.CASCADE, related_name='links')
