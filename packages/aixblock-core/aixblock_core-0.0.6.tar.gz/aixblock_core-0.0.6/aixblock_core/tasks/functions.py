import os
import sys
import logging
import json
import requests
from core.audio import grab_audio_duration_from_ffmpeg_output, convert_audio, redact_audio, get_audio_duration
from core.label_config import replace_task_data_undefined_with_config_field
from django.conf import settings
from core.models import AsyncMigrationStatus
from core.redis import start_job_async_or_sync
from core.utils.common import batch
from data_export.models import DataExport
from django.db import transaction
from django.utils.crypto import get_random_string
from io_storages.functions import get_all_project_storage
from organizations.models import Organization
from plugins.plugin_centrifuge import publish_message
from projects.models import Project
from tasks.models import Annotation, Task
from data_export.mixins import ExportMixin
from ml.models import MLBackend, MLGPU
from model_marketplace.models import ModelMarketplace
from data_export.serializers import ExportDataSerializer


def calculate_stats_all_orgs(from_scratch, redis):
    logger = logging.getLogger(__name__)
    organizations = Organization.objects.order_by('-id')

    for org in organizations:
        logger.debug(f"Start recalculating stats for Organization {org.id}")

        # start async calculation job on redis
        start_job_async_or_sync(
            redis_job_for_calculation, org, from_scratch,
            redis=redis,
            queue_name='critical',
            job_timeout=3600 * 24  # 24 hours for one organization
        )

        logger.debug(f"Organization {org.id} stats were recalculated")

    logger.debug("All organizations were recalculated")


def redis_job_for_calculation(org, from_scratch):
    """
    Recalculate counters for projects list
    :param org: Organization to recalculate
    :param from_scratch: Start calculation from scratch or skip calculated tasks
    """
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    projects = Project.objects.filter(organization=org).order_by('-updated_at')
    for project in projects:
        migration = AsyncMigrationStatus.objects.create(
            project=project,
            name='0018_manual_migrate_counters',
            status=AsyncMigrationStatus.STATUS_STARTED,
        )
        logger.debug(
            f"Start processing stats project <{project.title}> ({project.id}) "
            f"with task count {project.tasks.count()} and updated_at {project.updated_at}"
        )

        task_count = project.update_tasks_counters(project.tasks.all(), from_scratch=from_scratch)

        migration.status = AsyncMigrationStatus.STATUS_FINISHED
        migration.meta = {'tasks_processed': task_count, 'total_project_tasks': project.tasks.count()}
        migration.save()
        logger.debug(
            f"End processing counters for project <{project.title}> ({project.id}), "
            f"processed {str(task_count)} tasks"
        )


def export_project(project_id, export_format, path, serializer_context=None):
    logger = logging.getLogger(__name__)

    project = Project.objects.get(id=project_id)

    export_format = export_format.upper()
    supported_formats = [s['name'] for s in DataExport.get_export_formats(project)]
    assert export_format in supported_formats, f'Export format is not supported, please use {supported_formats}'

    task_ids = (
        Task.objects.filter(project=project)
        .select_related("project")
        .prefetch_related("annotations", "predictions")
    )

    logger.debug(f"Start exporting project <{project.title}> ({project.id}) with task count {task_ids.count()}.")

    # serializer context
    if isinstance(serializer_context, str):
        serializer_context = json.loads(serializer_context)
    serializer_options = ExportMixin._get_export_serializer_option(serializer_context)

    # export cycle
    tasks = []
    for _task_ids in batch(task_ids, 1000):
        tasks += ExportDataSerializer(
            _task_ids,
            many=True,
            **serializer_options
        ).data

    # convert to output format
    export_stream, _, filename = DataExport.generate_export_file(
        project, tasks, export_format, settings.CONVERTER_DOWNLOAD_RESOURCES, {}
    )

    # write to file
    filepath = os.path.join(path, filename) if os.path.isdir(path) else path
    with open(filepath, "wb") as file:
        file.write(export_stream.read())

    logger.debug(f"End exporting project <{project.title}> ({project.id}) in {export_format} format.")

    return filepath


def auto_gen_dataset(self, project, args):
    data_format = 'JSON'
    # model_instance = ModelMarketplace.objects.filter(id=54).first()
    # data_format = json.loads(model_instance.config)["data_format"]
    try:
        data_types = project.data_types 
        if 'image' in data_types:
            data_format = "COCO"
        elif 'text' in data_types:
            data_format = "llm"

    except Exception as e:
        print(e)

    try:
        ml_instance = MLBackend.objects.filter(project_id=project.id, deleted_at__isnull=True).first()
        ml_gpu = MLGPU.objects.filter(ml_id=ml_instance.id, deleted_at__isnull=True).first()
        model_instance = ModelMarketplace.objects.filter(id=ml_gpu.model_id).first()
        data_format = json.loads(model_instance.config)["dataset_format"]
    except Exception as e:
        print(e)

    if data_format:
        export_type = data_format
    else:
        export_type = 'JSON'

    download_resources = True
    # export_type="YOLO"

    all_tasks = Annotation.objects.filter(task__project=project).order_by('-id').values_list("task_id", flat=True)
    total_tasks = all_tasks.count()
    if project.need_to_qa:
        all_tasks = all_tasks.filter(task__reviewed_result='approved')
    if project.need_to_qc:
        all_tasks = all_tasks.filter(task__qualified_result='qualified')

    batch_size = project.batch_size
    if batch_size == 1:
        batch_size == 20
        
    if all_tasks:
        total_records = all_tasks.count()
        if total_records % batch_size == 0 or total_records==all_tasks:
            if total_records!=total_tasks:
                # last_record = total_records / 10
                all_tasks = all_tasks[-batch_size:]
            tasks = []

            for task_id in all_tasks:
                instance = Task.objects.filter(id=task_id, project=project).first()
                if not instance:
                    continue
                # print(ExportDataSerializer(instance).data)
                tasks.append(ExportDataSerializer(instance).data)
            
            if project.export_dataset:
                export_stream, content_type, filename = DataExport.generate_export_file(
                    project, tasks, export_type, download_resources, args, self=self
                )


def redact_annotation(annotation_pk):
    annotation = Annotation.objects.filter(pk=annotation_pk).first()
    project = annotation.task.project
    task = annotation.task
    data = task.data.copy()
    replace_task_data_undefined_with_config_field(data, project)

    ranges = {}

    for result in annotation.result:
        if result['type'] != 'audioredact' or result['to_name'] not in data:
            continue

        if result['to_name'] not in ranges:
            ranges[result['to_name']] = []

        ranges[result['to_name']].append([
            result['value']['audioredact']['start'],
            result['value']['audioredact']['end'],
            result['id'],
        ])

    _d = task.data.copy()
    replace_task_data_undefined_with_config_field(_d, project)
    storage_filename = task.storage_filename.split("/")[-1]

    for dk in ranges.keys():
        if dk in _d and (_d[dk].startswith("s3://") or _d[dk].startswith("gs://") or _d[dk].startswith("azure-blob://")):
            data[dk] = "".join(data[dk].split(f"/convert_files_{project.pk}/")[0:-1]) + f"/raw_files_{project.pk}/" + storage_filename
            continue

        raise Exception(f"[Redact Task #{task.pk}] Only support apply redact audio from cloud storage")

    removed_region_ids = []
    data = task.resolve_uri(data, project)

    for name in ranges:
        ogg_filename = ".".join(storage_filename.split(".")[0:-1]) + ".ogg"
        src_path = os.path.join(settings.BASE_DATA_DIR, get_random_string() + "_" + storage_filename)
        tgt_path = os.path.join(settings.BASE_DATA_DIR, get_random_string() + "_" + storage_filename)
        tgt_ogg_path = os.path.join(settings.BASE_DATA_DIR, get_random_string() + "_" + ogg_filename)
        original_file_url = data[name]

        with requests.get(original_file_url, stream=True) as response:
            response.raise_for_status()

            with open(src_path, 'wb') as src_file:
                for chunk in response.iter_content(chunk_size=8192):
                    src_file.write(chunk)

            print(f"[Redact Task #{task.pk}] Downloaded file: {original_file_url}")

        if not redact_audio(src_path, tgt_path, ranges[name]):
            try:
                os.remove(src_path)
                os.remove(tgt_path)
            except FileNotFoundError:
                pass

            print(f"[Redact Task #{task.pk}] Failed to redact file: {original_file_url}")
            continue


        if not storage_filename.lower().endswith(".ogg"):
            convert_result = convert_audio(tgt_path, tgt_ogg_path, codec="libopus", bitrate="32k")

            if not convert_result:
                try:
                    os.remove(src_path)
                    os.remove(tgt_path)
                    os.remove(tgt_ogg_path)
                except FileNotFoundError:
                    pass

                print(f"[Redact Task #{task.pk}] Failed to convert redacted file: {original_file_url}")
                continue

        try:
            storages = get_all_project_storage(project.pk)

            for storage in storages:
                storage.upload_file(
                    object_name=storage_filename,
                    file_path=tgt_path,
                    prefix=f'raw_files_{project.pk}',
                    scan_link=False,
                    remove_link=False,
                    user=task.created_by,
                    original_file=data["original_file"] if "original_file" in data else storage_filename,
                )

                if not storage_filename.lower().endswith(".ogg"):
                    storage.upload_file(
                        object_name=ogg_filename,
                        file_path=tgt_ogg_path,
                        prefix=f'convert_files_{project.pk}',
                        scan_link=False,
                        remove_link=False,
                        user=task.created_by,
                        original_file=data["original_file"] if "original_file" in data else storage_filename,
                    )

                break

            print(f"[Redact Task #{task.pk}] Redacted file: {original_file_url}")
        except Exception as e:
            print(e)

        try:
            os.remove(src_path)
            os.remove(tgt_path)

            for r in ranges[name]:
                removed_region_ids.append(r[2])

            os.remove(tgt_ogg_path)
        except FileNotFoundError:
            pass

    if len(removed_region_ids) > 0:
        with transaction.atomic():
            annotation = Annotation.objects.select_for_update().filter(pk=annotation_pk).first()
            annotation.result = list(filter(lambda x: x['id'] not in removed_region_ids, annotation.result))
            annotation.save()

        if not task.is_data_optimized:
            task.is_data_optimized = True
            task.save()

        publish_message(
            channel=f"task/{task.id}",
            data={
                "command": "redacted",
                "reload": list(ranges.keys()),
                "region_ids": removed_region_ids
            },
        )
