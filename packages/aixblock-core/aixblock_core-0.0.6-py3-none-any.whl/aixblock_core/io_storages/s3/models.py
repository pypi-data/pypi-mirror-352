"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
import math
import os
import io
import re
import logging
import json
import boto3

from core.redis import start_job_async_or_sync
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete
from plugins.plugin_centrifuge import publish_message
from projects.services.project_cloud_storage import dataset_minio

from io_storages.base_models import ImportStorage, ImportStorageLink, ExportStorage, ExportStorageLink
from io_storages.s3.utils import get_client_and_resource, resolve_s3_url
from tasks.validation import ValidationError as TaskValidationError
from tasks.models import Annotation
import datetime
import zipfile
from io import BytesIO
import threading
from pydub import AudioSegment

from botocore.exceptions import NoCredentialsError, ClientError

logger = logging.getLogger(__name__)
logging.getLogger('botocore').setLevel(logging.CRITICAL)
boto3.set_stream_logger(level=logging.INFO)

clients_cache = {}


class S3StorageMixin(models.Model):
    bucket = models.TextField(
        _('bucket'), null=True, blank=True,
        help_text='S3 bucket name')
    prefix = models.TextField(
        _('prefix'), null=True, blank=True,
        help_text='S3 bucket prefix')
    regex_filter = models.TextField(
        _('regex_filter'), null=True, blank=True,
        help_text='Cloud storage regex for filtering objects')
    use_blob_urls = models.BooleanField(
        _('use_blob_urls'), default=False,
        help_text='Interpret objects as BLOBs and generate URLs')
    aws_access_key_id = models.TextField(
        _('aws_access_key_id'), null=True, blank=True,
        help_text='AWS_ACCESS_KEY_ID')
    aws_secret_access_key = models.TextField(
        _('aws_secret_access_key'), null=True, blank=True,
        help_text='AWS_SECRET_ACCESS_KEY')
    aws_session_token = models.TextField(
        _('aws_session_token'), null=True, blank=True,
        help_text='AWS_SESSION_TOKEN')
    region_name = models.TextField(
        _('region_name'), null=True, blank=True,
        help_text='AWS Region')
    s3_endpoint = models.TextField(
        _('s3_endpoint'), null=True, blank=True,
        help_text='S3 Endpoint')

    def get_client_and_resource(self):
        # s3 client initialization ~ 100 ms, for 30 tasks it's a 3 seconds, so we need to cache it
        if self.s3_endpoint and not self.s3_endpoint.startswith("http://") and not self.s3_endpoint.startswith("https://"):
            self.s3_endpoint = "http://" + self.s3_endpoint
            # self.s3_endpoint = "https://storage.aixblock.io"

        #
        # Temporary disable client cache to debug the upload speed
        #
        # cache_key = f'{self.aws_access_key_id}:{self.aws_secret_access_key}:{self.aws_session_token}:{self.region_name}:{self.s3_endpoint}'
        # if cache_key in clients_cache:
        #     return clients_cache[cache_key]

        result = get_client_and_resource(
            self.aws_access_key_id, self.aws_secret_access_key, self.aws_session_token, self.region_name,
            self.s3_endpoint)
        # clients_cache[cache_key] = result
        return result

    def get_client(self):
        client, _ = self.get_client_and_resource()
        return client

    def get_client_and_bucket(self, validate_connection=True):
        client, s3 = self.get_client_and_resource()
        if validate_connection:
            self.validate_connection(client)
        return client, s3.Bucket(self.bucket)

    def validate_connection(self, client=None):
        logger.debug('validate_connection')
        if client is None:
            client = self.get_client()
        if self.prefix:
            logger.debug(f'Test connection to bucket {self.bucket} with prefix {self.prefix}')
            result = client.list_objects_v2(Bucket=self.bucket, Prefix=self.prefix, MaxKeys=1)
            if not result.get('KeyCount'):
                raise KeyError(f'{self.url_scheme}://{self.bucket}/{self.prefix} not found.')
        else:
            logger.debug(f'Test connection to bucket {self.bucket}')
            client.head_bucket(Bucket=self.bucket.rstrip('\n'))

            try:
                import botocore.exceptions
                bucket_region = client.get_bucket_location(Bucket=self.bucket.rstrip('\n'))['LocationConstraint']
                if self.region_name and self.region_name != bucket_region:
                    raise KeyError(f"Bucket region mismatch: Expected {self.region_name}, but found {bucket_region}.")
            except botocore.exceptions.ClientError:
                logger.warning(f"Could not retrieve region for bucket {self.bucket}. Skipping region check.")
                pass

    @property
    def path_full(self):
        prefix = self.prefix or ''
        return f'{self.url_scheme}://{self.bucket}/{prefix}'

    @property
    def type_full(self):
        return 'Amazon AWS S3'

    class Meta:
        abstract = True


class S3ImportStorage(S3StorageMixin, ImportStorage):

    url_scheme = 's3'

    presign = models.BooleanField(
        _('presign'), default=True,
        help_text='Generate presigned URLs')
    presign_ttl = models.PositiveSmallIntegerField(
        _('presign_ttl'), default=60,
        help_text='Presigned URLs TTL (in minutes)')
    recursive_scan = models.BooleanField(
        _('recursive scan'), default=False,
        help_text=_('Perform recursive scan over the bucket content'))
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
        client, bucket = self.get_client_and_bucket()
        if self.prefix:
            list_kwargs = {'Prefix': self.prefix.rstrip('/') + '/'}
            if not self.recursive_scan:
                list_kwargs['Delimiter'] = '/'
            bucket_iter = bucket.objects.filter(**list_kwargs).all()
        else:
            bucket_iter = bucket.objects.all()
        regex = re.compile(str(self.regex_filter)) if self.regex_filter else None
        for obj in bucket_iter:
            key = obj.key
            if key.endswith('/'):
                logger.debug(key + ' is skipped because it is a folder')
                continue
            if regex and not regex.match(key):
                logger.debug(key + ' is skipped by regex filter')
                continue
            yield key

    def scan_and_create_links(self, key=None, duration=None, user=None, original_file=None, extras_data=None):
        return self._scan_and_create_links(S3ImportStorageLink, key, duration, user=user, original_file=original_file, extras_data=extras_data)

    def _get_validated_task(self, parsed_data, key):
        """ Validate parsed data with labeling config and task structure
        """
        if not isinstance(parsed_data, dict):
            raise TaskValidationError('Error at ' + str(key) + ':\n'
                                      'Cloud storage supports one task (one dict object) per JSON file only. ')
        return parsed_data

    def get_data(self, key, raw_key=None):
        uri = f'{self.url_scheme}://{self.bucket}/{key}'

        if 'json' not in key:
            if 'audio' in self.project.data_types or 'image' in self.project.data_types or 'video' in self.project.data_types:
                # if self.use_blob_urls:
                data_key = settings.DATA_UNDEFINED_NAME

                # try:
                #     self.create_convert_file(key)
                # except:
                #     pass

                if raw_key:
                    try:
                        # Download file từ S3 tạm thời
                        _, s3 = self.get_client_and_resource()
                        audio_obj = s3.Object(self.bucket, key)
                        audio_data = audio_obj.get()['Body'].read()

                        # Load file âm thanh với pydub
                        audio = AudioSegment.from_file(io.BytesIO(audio_data))
                        duration = len(audio) / 1000.0  # Tính thời lượng (giây)
                        return {data_key: uri, 'duration': duration}
                    except Exception as e:
                        print(f"Error calculating duration for audio file {key}: {e}")
                
                return {data_key: uri}

        # read task json from bucket and validate it
        _, s3 = self.get_client_and_resource()
        bucket = s3.Bucket(self.bucket)
        obj_data = s3.Object(bucket.name, key).get()['Body'].read()
        try:
            value = json.loads(obj_data.decode('utf-8'))
            # if not isinstance(value, dict):
            #     raise ValueError(f"Error on key {key}: For S3 your JSON file must be a dictionary with one task")
            if isinstance(value, dict):
                value = self._get_validated_task(value, key)
        except (UnicodeDecodeError, json.JSONDecodeError):
            value = {'text': obj_data.decode('utf-8', 'ignore')}
        # obj = s3.Object(bucket.name, key).get()['Body'].read().decode('utf-8')
        # value = json.loads(obj)
        return value

    def upload_obj(self, client, file, bucket_name, key, extra, publish_channel=None, upload_file_id=None):
        from botocore.exceptions import ReadTimeoutError
        import time

        last_notify_time = 0
        retries = 3
        uploaded = 0
        file.seek(0, os.SEEK_END)
        file_length = file.tell()
        file.seek(0)

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

        def progress(chunk):
            nonlocal uploaded, last_notify_time
            uploaded += chunk

            if time.time() - last_notify_time > 2:
                send_message("Saving to cloud storage...", percent=math.ceil((uploaded / file_length) * 100))
                last_notify_time = time.time()

        for attempt in range(retries):
            try:
                client.upload_fileobj(
                    Fileobj=file,
                    Bucket=bucket_name,
                    Key=key,
                    ExtraArgs={'ContentType': extra},
                    Callback=progress,
                )
                send_message("Saved to cloud storage")
                break
            except ReadTimeoutError as e:
                if attempt < retries - 1:
                    time.sleep(5)
                    send_message(f"Error: {e}. Try again in 5 seconds.")
                else:
                    send_message(f"Failed after 3 attempts. Error: {e}.")
            except Exception as e:
                print(e)
       
    
    def create_folder(self, folder_name="raw_files/"):
        """
        Create an empty folder in the S3 bucket.
        :param folder_name: The name of the folder to create (should end with '/').
        """
        if not folder_name.endswith('/'):
            folder_name += '/'

        _, bucket = self.get_client_and_bucket()
        bucket.put_object(Key=folder_name, Body='')  # Upload an empty object with the folder name as key
        logger.info(f'Created empty folder: {folder_name}')

    def get_iterkeys(self, object_path=None):
        client, bucket = self.get_client_and_bucket()
        lst_object = []

        # Nếu có đường dẫn cụ thể (object_path) được truyền vào, sử dụng nó làm Prefix
        if object_path:
            list_kwargs = {'Prefix': object_path.rstrip('/') + '/'}
        elif self.prefix:  # Nếu không có object_path, sử dụng self.prefix như trước đây
            list_kwargs = {'Prefix': self.prefix.rstrip('/') + '/'}
        else:
            list_kwargs = {}

        if not self.recursive_scan:
            list_kwargs['Delimiter'] = '/'

        # Lọc các đối tượng trong bucket với Prefix đã chỉ định
        if list_kwargs:
            bucket_iter = bucket.objects.filter(**list_kwargs).all()
        else:
            bucket_iter = bucket.objects.all()

        for obj in bucket_iter:
            lst_object.append(obj)

        return lst_object

    def check_obj_iterkeys(self, object_key, object_path="checkpoint"):
        client, bucket = self.get_client_and_bucket()
        list_kwargs = {'Prefix': object_path.rstrip('/') + '/'}
        bucket_iter = bucket.objects.filter(**list_kwargs).all()

        if object_key in bucket_iter:
            return True
        return False
        
    def extract_zip(self, object_key):
        # Lấy client và bucket từ hàm hiện tại của bạn
        client, bucket = self.get_client_and_bucket()

        # Tải tệp ZIP từ S3 về bộ nhớ
        s3_object = client.get_object(Bucket=bucket.name, Key=object_key)
        zip_data = s3_object['Body'].read()  # Đọc nội dung của tệp ZIP
        
        # Sử dụng BytesIO để lưu trữ nội dung zip trong bộ nhớ
        zip_buffer = io.BytesIO(zip_data)

        # Giải nén tệp ZIP từ bộ nhớ và lấy danh sách các tệp
        with zipfile.ZipFile(zip_buffer, 'r') as zip_ref:
            file_list = zip_ref.namelist()  # Lấy danh sách các tệp trong ZIP
            
            return file_list
    
    def download_and_save_folder(self, path, save_path, all_path=True):
        client, bucket = self.get_client_and_bucket()

        # Liệt kê tất cả các đối tượng trong folder
        objects = bucket.objects.filter(Prefix=f"{path}/")

        # Duyệt qua từng file trong folder và tải về
        for obj in objects:
            file_key = obj.key
            relative_path = os.path.relpath(file_key, path)  # Tính đường dẫn file

            # Tạo đường dẫn file tương ứng trên local
            if all_path:
                local_path = os.path.join(save_path, path, relative_path)
            else:
                local_path = os.path.join(save_path, relative_path)

            # Tạo thư mục nếu chưa tồn tại
            os.makedirs(os.path.dirname(local_path), exist_ok=True)

            # Tải file từ MinIO về thư mục local
            try:
                bucket.download_file(Key=file_key, Filename=local_path)
            except Exception as e:
                print(e)
            
    def _upload_file(self, object_name, file_path, prefix="raw_files", scan_link=False, remove_link=False, duration=None, user=None, original_file=None, extras_data=None, publish_channel=None, upload_file_id=None):
        import mimetypes
        client, s3 = self.get_client_and_resource()
        bucket = s3.Bucket(self.bucket)
        # key = f'{prefix}/{object_name}'  # Tạo đường dẫn file trên S3
        key = os.path.join(prefix, object_name)  # Tạo đường dẫn file trên S3

        # Đọc nội dung file vào BytesIO
        with open(file_path, 'rb') as f:
            file_data = BytesIO(f.read())

        file_data.seek(0)

        # Xác định content_type dựa trên file
        content_type, encoding = mimetypes.guess_type(file_path)
        if not content_type:
            content_type = 'application/octet-stream'

        self.upload_obj(client, file_data, bucket.name, key, content_type, publish_channel=publish_channel, upload_file_id=upload_file_id)
        if scan_link:
            self.scan_and_create_links(key, duration, user=user, original_file=original_file, extras_data=extras_data)
            
        if remove_link:
            os.remove(file_path)
        # Upload trực tiếp lên S3
        # client.upload_fileobj(
        #     Fileobj=file_data,
        #     Bucket=bucket.name,
        #     Key=key,
        #     ExtraArgs={'ContentType': content_type}
        # )
    def upload_file(self, object_name, file_path, prefix="raw_files", scan_link=False, remove_link=False, duration=None, user=None, original_file=None, extras_data=None, publish_channel=None, upload_file_id=None):
        # if not thread:
        self._upload_file(object_name, file_path, prefix, scan_link, remove_link, duration, user=user, original_file=original_file, extras_data=extras_data, publish_channel=publish_channel, upload_file_id=upload_file_id)
        # else:
        #     t = threading.Thread(target=self._upload_file, args=(object_name, file_path, prefix, scan_link, remove_link, duration), kwargs={"user": user, "original_file": original_file})
        #     manage_task_thread(t)

    def _upload_folder(self, folder_path, prefix="raw_files"):
        if not os.path.isdir(folder_path):
            raise ValueError(f"{folder_path} is not a valid directory.")

        for root, dirs, files in os.walk(folder_path):
            for file_name in files:
                # Đường dẫn đầy đủ của file trên local
                file_path = os.path.join(root, file_name)

                # Đường dẫn tương đối của file so với thư mục gốc
                relative_path = os.path.relpath(file_path, folder_path)

                # Tạo object_name trên MinIO (giữ nguyên cấu trúc thư mục)
                object_name = os.path.join(relative_path).replace("\\", "/")  # Đảm bảo đường dẫn sử dụng "/"

                # Upload file với object_name và prefix
                self._upload_file(object_name, file_path, prefix)

        print(f"Folder '{folder_path}' đã được upload lên MinIO tại prefix '{prefix}'")


    def upload_folder(self, folder_path, prefix="raw_files"):
        t = threading.Thread(target=self._upload_folder, args=(folder_path, prefix))
        t.start()
        
    def upload_directory(self, directory_path, prefix="checkpoint"):
        import os
        for root, dirs, files in os.walk(directory_path):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                object_name = os.path.relpath(file_path, directory_path)
                self._upload_file(object_name, file_path, prefix)
    
    # def _create_convert_file(self, key):
    #     from PIL import Image
    #
    #     client, s3 = self.get_client_and_resource()
    #     bucket = s3.Bucket(self.bucket)
    #     object = client.get_object(Bucket=bucket.name, Key=key)
    #     file_extension = key.split('.')[-1].lower()
    #     project_id = self.project.id
    #
    #     if file_extension in ['jpg', 'jpeg', 'png']:
    #         # Đọc dữ liệu từ S3 object
    #         image_data = object['Body'].read()
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
    #             self.upload_obj(client, thumbnail_io, bucket.name, thumbnail_key, f'image/{image.format.lower()}')
    #
    #             # Upload trực tiếp thumbnail lên S3
    #             # client.upload_fileobj(
    #             #     Fileobj=thumbnail_io,
    #             #     Bucket=bucket.name,
    #             #     Key=thumbnail_key,
    #             #     ExtraArgs={'ContentType': f'image/{image.format.lower()}'}
    #             # )
    #
    #     elif file_extension in ['mp3', 'wav', 'flac', 'ogg', 'm4a']:
    #         # Xử lý audio
    #         audio_data = object['Body'].read()
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
    #         self.upload_obj(client, audio_io, bucket.name, audio_key, 'audio/ogg')
    #
    #         # # Upload trực tiếp lên S3
    #         # client.upload_fileobj(
    #         #     Fileobj=audio_io,
    #         #     Bucket=bucket.name,
    #         #     Key=audio_key,
    #         #     ExtraArgs={'ContentType': 'audio/ogg'}
    #         # )
    #
    # def create_convert_file(self, key):
    #     import threading
    #     t = threading.Thread(target=self._create_convert_file, args=(key,))
    #     manage_task_thread(t)

    def generate_http_url(self, url, exp_in=None):
        expires_in = self.presign_ttl * 60
        if exp_in:
            expires_in = exp_in * 60
        return resolve_s3_url(url, self.get_client(), self.presign, expires_in=expires_in)
    
    def can_resolve_url(self, url):
        return url.startswith('s3://' + self.bucket + '/')

    def scan_export_storage(self):
        # Kiểm tra bản ghi đầu tiên
        export_storage = S3ExportStorage.objects.filter(project_id=self.project_id).first()
        self.export_storage = export_storage.id
    
    def sync_export_storage(self):
        if not self.export_storage:
            self.scan_export_storage()

        export_storage = S3ExportStorage.objects.filter(id=self.export_storage).first()
        export_storage.sync()
    
    def copy_storage(self, s3_prj, target=True):
        if not target:
            _, current_s3 = self.get_client_and_resource()
            _, destination_s3 = s3_prj.get_client_and_resource()
            current_bucket = current_s3.Bucket(self.bucket)
            destination_bucket = destination_s3.Bucket(s3_prj.bucket)
        else:
            _, destination_s3 = self.get_client_and_resource()
            _, current_s3 = s3_prj.get_client_and_resource()
            current_bucket = current_s3.Bucket(s3_prj.bucket)
            destination_bucket = destination_s3.Bucket(self.bucket)

        # Đặt tên thư mục đích trong bucket đích
        destination_folder = current_bucket.name  # Sử dụng tên của bucket hiện tại làm tên thư mục

        # Lặp qua tất cả các đối tượng trong current_bucket
        for obj in current_bucket.objects.all():
            try:
                s3_object = current_s3.Object(current_bucket.name, obj.key)
                obj_data = s3_object.get()['Body'].read()

                # Kiểm tra nếu đối tượng là một tệp JSON hay một tệp nhị phân
                try:
                    # Nếu là tệp JSON
                    data = json.loads(obj_data.decode('utf-8'))
                    # Chuyển đổi dữ liệu thành chuỗi JSON để lưu trữ
                    body = json.dumps(data)

                except (UnicodeDecodeError, json.JSONDecodeError):
                    # Nếu là tệp nhị phân
                    body = obj_data
                # Tạo khóa mới trong bucket đích
                destination_key = f"{current_bucket.name}/{obj.key}"

                # Ghi dữ liệu vào bucket đích
                destination_bucket.put_object(
                    Key=destination_key,
                    Body=body
                )

                print(f"Copied {obj.key} to {destination_key} in {destination_bucket.name}")

            except ClientError as e:
                error_code = e.response.get('Error', {}).get('Code')
                if error_code == '404':
                    print(f"Object not found: {obj.key} in {current_bucket.name}")
                else:
                    print(f"Failed to copy {obj.key}: {e}")

            except NoCredentialsError:
                print("Credentials not available for S3 access")

        print(f"Data copied from {current_bucket.name} to {destination_folder} in {destination_bucket.name}")

    def alias_storage(self, s3_prj):
        try:
            _, current_s3 = self.get_client_and_resource()
            _, destination_s3 = s3_prj.get_client_and_resource()
            current_bucket = current_s3.Bucket(self.bucket)
            destination_bucket = destination_s3.Bucket(s3_prj.bucket)

            # Tạo một set để lưu trữ các prefix (thư mục) duy nhất
            prefixes = set()

            # Lặp qua tất cả các đối tượng trong current_bucket
            for obj in current_bucket.objects.all():
                key = obj.key
                # Lấy prefix từ key (thư mục)
                if '/' in key:
                    prefix = key.rsplit('/', 1)[0] + '/'
                    prefixes.add(prefix)

            for prefix in prefixes:
                full_prefix = f"{current_bucket.name}/{prefix}"
                destination_bucket.put_object(Key=full_prefix)
                print(f"Created folder {prefix} in {destination_bucket.name}")

        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code')
            if error_code == '404':
                print(f"Bucket or object not found: {e}")
            else:
                print(f"Failed to create folder: {e}")

        except NoCredentialsError:
            print("Credentials not available for S3 access")

        print(f"Structure from {current_bucket.name} copied to {destination_bucket.name}")
class S3ExportStorage(S3StorageMixin, ExportStorage):

    def save_annotation(self, annotations, project = None, file_path = None, is_folder=False):
        client, s3 = self.get_client_and_resource()
        logger.debug(f'Creating new object on {self.__class__.__name__} Storage {self} for annotation {annotations}')
        
        if annotations:
            try:
                from django.db.models.query import QuerySet
                version = datetime.datetime.now().strftime("%Y%m%d%H")
                if not isinstance(annotations, QuerySet):
                    annotations = [annotations]
                for annotation in annotations:
                    ser_annotation = self._get_serialized_data(annotation)
                    try:
                        if 'audio' in self.project.data_types:
                            data_name = ser_annotation['task']['data']['audio']
                        elif 'image' in self.project.data_types:
                            data_name = ser_annotation['task']['data']['image']
                        else:
                            data_name = ser_annotation['task']['data']['text']

                        data_name = data_name.split('/')[-1]
                        key = S3ExportStorageLink.get_key(annotation)
                    except:
                    # get key that identifies this object in storage
                        key = S3ExportStorageLink.get_key(annotation)
                    # key = str(self.prefix) + '/' + key if self.prefix else key
                    key = f"snapshot_{self.project_id}/{version}/{key}_{data_name}.json"

                    # put object into storage
                    s3.Object(self.bucket, key).put(Body=json.dumps(ser_annotation))

                    # create link if everything ok
                    S3ExportStorageLink.create(annotation, self)
            except Exception as e:
                logger.error(e)

        # save to s3
        if project:
            if not is_folder:
                dataset_minio.upload_file(
                    project=project,
                    bucket_name=str(project.id),
                    object_name=str(os.path.basename(file_path)),
                    file_path=file_path
                )
            else:
                dataset_minio.upload_directory(
                    project=project,
                    bucket_name=str(project.id),
                    directory_path=file_path,
                    new_thread=True
                )

    def delete_annotation(self, annotation):
        client, s3 = self.get_client_and_resource()
        logger.debug(f'Deleting object on {self.__class__.__name__} Storage {self} for annotation {annotation}')

        # get key that identifies this object in storage
        key = S3ExportStorageLink.get_key(annotation)
        key = str(self.prefix) + '/' + key if self.prefix else key

        # delete object from storage
        s3.Object(self.bucket, key).delete()

        # delete link if everything ok
        S3ExportStorageLink.objects.filter(storage=self, annotation=annotation).delete()

    def create_connect_to_import_storage(self, import_id):
        S3ImportStorage.objects.filter(id=import_id).update(export_storage=self.id)

def async_export_annotation_to_s3_storages(annotation):
    project = annotation.task.project
    if hasattr(project, 'io_storages_s3exportstorages'):
        for storage in project.io_storages_s3exportstorages.all():
            logger.debug(f'Export {annotation} to S3 storage {storage}')
            storage.save_annotation(annotation)


@receiver(post_save, sender=Annotation)
def export_annotation_to_s3_storages(sender, instance, **kwargs):
    start_job_async_or_sync(async_export_annotation_to_s3_storages, instance)


@receiver(pre_delete, sender=Annotation)
def delete_annotation_from_s3_storages(sender, instance, **kwargs):
    links = S3ExportStorageLink.objects.filter(annotation=instance)
    for link in links:
        storage = link.storage
        if storage.can_delete_objects:
            logger.debug(f'Delete {instance} from S3 storage {storage}')
            storage.delete_annotation(instance)


class S3ImportStorageLink(ImportStorageLink):
    storage = models.ForeignKey(S3ImportStorage, on_delete=models.CASCADE, related_name='links')

    @classmethod
    def exists(cls, key, storage):
        storage_link_exists = super(S3ImportStorageLink, cls).exists(key, storage)
        # TODO: this is a workaround to be compatible with old keys version - remove it later
        prefix = str(storage.prefix) or ''
        return storage_link_exists or \
            cls.objects.filter(key=prefix + key, storage=storage.id).exists() or \
            cls.objects.filter(key=prefix + '/' + key, storage=storage.id).exists()


class S3ExportStorageLink(ExportStorageLink):
    storage = models.ForeignKey(S3ExportStorage, on_delete=models.CASCADE, related_name='links')

# class S3Global(models.Model): #, null=True, blank=True
#     storage_id = models.IntegerField(
#         _('storage_id'))
#     user_id = models.IntegerField(
#         _('user_id'))
#     org_id = models.IntegerField(
#         _('org_id'))
#     project_id = models.IntegerField(
#         _('project_id'))
   