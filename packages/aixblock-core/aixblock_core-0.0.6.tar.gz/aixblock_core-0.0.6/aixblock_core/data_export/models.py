"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
import hashlib
import logging
import os
import shutil
from copy import deepcopy
from datetime import datetime

import ujson as json
from core import version
from core.utils.common import load_func
from core.utils.io import get_all_files_from_dir, get_temp_dir, read_bytes_stream
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
# from aixblock_core_converter import Converter
from aixblock_converter.converter import Converter
from tasks.models import Annotation
from projects.services.project_cloud_storage import dataset_minio
from .gen_dataset_llm import gen_dataset_llm

from projects.services.project_cloud_storage import ProjectCloudStorage
from model_marketplace.models import DatasetModelMarketplace
import threading
from aixblock_core.users.service_notify import send_email_thread
from core.settings.base import MAIL_SERVER

logger = logging.getLogger(__name__)


ExportMixin = load_func(settings.EXPORT_MIXIN)


class Export(ExportMixin, models.Model):
    class Status(models.TextChoices):
        CREATED = 'created', _('Created')
        IN_PROGRESS = 'in_progress', _('In progress')
        FAILED = 'failed', _('Failed')
        COMPLETED = 'completed', _('Completed')

    title = models.CharField(
        _('title'),
        blank=True,
        default='',
        max_length=2048,
    )
    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True,
        help_text='Creation time',
    )
    file = models.FileField(
        upload_to=settings.DELAYED_EXPORT_DIR,
        null=True,
    )
    md5 = models.CharField(
        _('md5 of file'),
        max_length=128,
        default='',
    )
    finished_at = models.DateTimeField(
        _('finished at'),
        help_text='Complete or fail time',
        null=True,
        default=None,
    )

    status = models.CharField(
        _('Export status'),
        max_length=64,
        choices=Status.choices,
        default=Status.CREATED,
    )
    counters = models.JSONField(
        _('Exporting meta data'),
        default=dict,
    )
    project = models.ForeignKey(
        'projects.Project',
        related_name='exports',
        on_delete=models.CASCADE,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='+',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('created by'),
    )


@receiver(post_save, sender=Export)
def set_export_default_name(sender, instance, created, **kwargs):
    if created and not instance.title:
        instance.title = instance.get_default_title()
        instance.save()

from .converters import CustomConverter as Converter
from io_storages.s3.models import S3ExportStorage
from core.version import info
class DataExport(object):
    # TODO: deprecated
    @staticmethod
    def save_export_files(project, now, get_args, data, md5, name ):
        """Generate two files: meta info and result file and store them locally for logging"""
        filename_results = os.path.join(settings.EXPORT_DIR, name + '.json')
        filename_info = os.path.join(settings.EXPORT_DIR, name + '-info.json')
        annotation =  Annotation.objects.filter(task__project=project).all()
        annotation_number = annotation.count()
        # annotation_number = Annotation.objects.filter(task__project=project).count()
        # try:
        #     platform_version = version.get_git_version()
        # except:
        #     platform_version = 'none'
        #     logger.error('Version is not detected in save_export_files()')
        platform_version = "2.1.2"
        info = {
            'project': {
                'title': project.title,
                'id': project.id,
                'created_at': project.created_at.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'created_by': project.created_by.email,
                'task_number': project.tasks.count(),
                'annotation_number': annotation_number,
            },
            'platform': {'version': platform_version},
            'download': {
                'GET': dict(get_args),
                'time': now.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'result_filename': filename_results,
                'md5': md5,
            },
        }

        with open(filename_results, 'w', encoding='utf-8') as f:
            f.write(data)
        with open(filename_info, 'w', encoding='utf-8') as f:
            json.dump(info, f, ensure_ascii=False)

        # try:
        #     s3_export_storage_objects = S3ExportStorage.objects.filter(project_id = project.id).all()
        #     for s3_export_storage in s3_export_storage_objects:
        #         s3_export_storage.save_annotation(annotation, None, filename_results)
        # except Exception as e:
        #     print(e)

        return filename_results

    @staticmethod
    def get_export_formats(project):
        converter = Converter(config=project.get_parsed_config(), project_dir=None)
        formats = []
        supported_formats = set(converter.supported_formats)
        for format, format_info in converter.all_formats().items():
            format_info = deepcopy(format_info)
            format_info['name'] = format.name
            if format.name not in supported_formats:
                format_info['disabled'] = True
            formats.append(format_info)
        return sorted(formats, key=lambda f: f.get('disabled', False))

    @staticmethod
    def generate_export_file(project, tasks, output_format, download_resources, get_args, user=None, self=None , custom_format= None):
        # prepare for saving
        from typing import List, Dict, Any
        now = datetime.now()
        data = json.dumps(tasks, ensure_ascii=False)
        def format_custom_format(custom_format):
            def update_format_value(format_value, parent_key=""):
                if isinstance(format_value, str):
                    if format_value.startswith("{{$") and format_value.endswith("}}"):
                        field_name = format_value[3:-2].strip()
                        # Check if this is a nested field (i.e., contains '.')
                        if '.' in field_name:
                            return f'{{$' + field_name + '}}'
                        # If no dots, return as is
                        return format_value
                    return format_value
                elif isinstance(format_value, list):
                    return [update_format_value(item, parent_key) for item in format_value]
                elif isinstance(format_value, dict):
                    new_dict = {}
                    for key, val in format_value.items():
                        # Prepare the new key path for nested values
                        new_parent_key = f"{parent_key}.{key}" if parent_key else key
                        new_dict[key] = update_format_value(val, new_parent_key)

                        # Only update format for nested fields (level 2, 3, etc.)
                        if isinstance(new_dict[key], str) and new_dict[key].startswith("{{$") and new_dict[key].endswith("}}"):
                            field_name = new_dict[key][3:-2].strip()
                            if '.' not in field_name and parent_key:
                                new_dict[key] = f"{{{{${parent_key}.{field_name}}}}}"
                    return new_dict
                else:
                    return format_value

            return update_format_value(custom_format)

        def handle_data_custom(data, custom_format):
            def replace_placeholders(format_value, data_entry):
                if isinstance(format_value, str):
                    if format_value.startswith("{{$") and format_value.endswith("}}"):
                        field_name = format_value[3:-2].strip()  # Remove the placeholders syntax
                        field_parts = field_name.split('.')  # Split the field name by dots for nested fields

                        # Navigate through the data_entry to get the desired value
                        value = data_entry
                        for part in field_parts:
                            if isinstance(value, dict):
                                value = value.get(part)
                            else:
                                return None
                        return value
                    else:
                        return format_value
                elif isinstance(format_value, list):
                    return [replace_placeholders(item, data_entry) for item in format_value]
                elif isinstance(format_value, dict):
                    return {key: replace_placeholders(val, data_entry) for key, val in format_value.items()}
                else:
                    return format_value

            # Load the JSON data
            data_list = json.loads(data)

            # Handle custom format
            if isinstance(data_list, list):
                return [replace_placeholders(custom_format, entry) for entry in data_list]
            else:
                return replace_placeholders(custom_format, data_list)

        if custom_format:
            # handle custom format json
            formatted_custom_format = format_custom_format(custom_format)
            data_custom = handle_data_custom(data, formatted_custom_format)
            data = json.dumps(data_custom, ensure_ascii=False)
            pass
        md5 = hashlib.md5(json.dumps(data).encode('utf-8')).hexdigest()   # nosec
        name = 'project-' + str(project.id) + '-at-' + now.strftime('%Y-%m-%d-%H-%M') + f'-{md5[0:8]}'

        input_json = DataExport.save_export_files(project, now, get_args, data, md5, name)

        converter = Converter(
            config=project.get_parsed_config(),
            project_dir=None,
            upload_dir=os.path.join(settings.MEDIA_ROOT, settings.UPLOAD_DIR),
            download_resources=download_resources,
        )

        date_str = now.strftime("%Y%m%d")
        time_str = now.strftime("%H%M%S")

        version = f'{date_str}-{time_str}'
        # dir_path = f"dataset/{version}/"
        # dataset_upload = ProjectCloudStorage(bucket_prefix="project-", object_prefix=dir_path)
        from io_storages.functions import get_all_project_storage_with_name
        storages = get_all_project_storage_with_name(project.id)

        with get_temp_dir() as tmp_dir:
            # output_format = 'LLM'
            if output_format.lower() == 'llm':
                gen_dataset_llm(json.loads(data), tmp_dir)
            else:
                converter.convert(input_json, tmp_dir, output_format, is_dir=False)
                files = get_all_files_from_dir(tmp_dir)

            from ml.models import MLBackend, MLGPU
            from model_marketplace.models import ModelMarketplace
            try:
                if not user:
                    user_id = 1
                else:
                    user_id = user.id

                # upload to s3
                # dataset_upload.upload_directory(
                #         project=project,
                #         bucket_name=str(project.id),
                #         directory_path=f'{tmp_dir}',
                #         new_thread=True
                #     )
                
                for storage in storages:
                    try:
                        storage.upload_directory(f'{tmp_dir}', f'dataset_{project.id}/{version}')
                        
                        dataset_instance = DatasetModelMarketplace.objects.create(
                            name=version,
                            owner_id=user_id,
                            author_id=user_id,
                            project_id=project.id,
                            catalog_id=0,
                            model_id=0,
                            order=0,
                            config=0,
                            dataset_storage_id=storage.id,
                            dataset_storage_name=storage.storage_name,
                            version=version
                        )
                    except:
                        pass
                    # break

                
                try:
                    html_file_path =  './templates/mail/export_dataset_done.html'
                    if not user:
                        user = self.user

                    with open(html_file_path, 'r', encoding='utf-8') as file:
                        html_content = file.read()

                    # notify_reponse = ServiceSendEmail(DOCKER_API)
                    html_content = html_content.replace('[user]', f'{user.email}')
                    html_content = html_content.replace('xxx', f'{version}')

                    data = {
                        "subject": f"AIxBlock | Your dataset is generated",
                        "from": "noreply@aixblock.io",
                        "to": [f"{user.email}"],
                        "html": html_content,
                        "text": "Remove compute!",
                    }

                    docket_api = "tcp://69.197.168.145:4243"
                    host_name = MAIL_SERVER

                    email_thread = threading.Thread(target=send_email_thread, args=(docket_api, host_name, data,))
                    email_thread.start()
                except:
                    pass

                ml_backend = MLBackend.objects.filter(
                            project_id=project.id,
                            deleted_at__isnull=True
                        ).first()

                if ml_backend:
                    ml_gpu = MLGPU.objects.filter(
                        ml_id=ml_backend.id, deleted_at__isnull=True
                    ).first()

                    if ml_gpu:
                        ModelMarketplace.objects.filter(id=ml_gpu.model_id).update(dataset_storage_id=dataset_instance.id)

                if project.min_annotations_to_start_training == 0:
                    from ml.functions import auto_ml_nodes
                    ml_backends = MLBackend.objects.filter(
                            project_id=project.id,
                            deleted_at__isnull=True
                        )
                    for ml_backend in ml_backends:
                        auto_ml_nodes(self, project_id=project.id)

            except Exception as e:
                print(e)
                # api.train(project)
            # if only one file is exported - no need to create archive
            if len(os.listdir(tmp_dir)) == 1:
                output_file = files[0]
                ext = os.path.splitext(output_file)[-1]
                content_type = f'application/{ext}'
                out = read_bytes_stream(output_file)
                filename = name + os.path.splitext(output_file)[-1]

                return out, content_type, filename

            # otherwise pack output directory into archive
            shutil.make_archive(tmp_dir, 'zip', tmp_dir)
            out = read_bytes_stream(os.path.abspath(tmp_dir + '.zip'))
            content_type = 'application/zip'
            filename = name + '.zip'

            return out, content_type, filename
