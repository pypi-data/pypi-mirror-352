# tasks.py
from django.http import HttpResponse
from django.core.files import File
from tasks.models import Task
from projects.models import Project
from .serializers import ExportDataSerializer, ExportSerializer, ExportCreateSerializer, \
    ExportParamSerializer, ExportDatasetRequestSerializer
from core.utils.common import get_object_with_check_and_log, batch
from .models import DataExport, Export
import logging

logger = logging.getLogger(__name__)


def process_export(
    project_id,
    export_type,
    only_finished,
    download_resources,
    interpolate_key_frames,
    tasks_ids,
    user,
    request_get,
    custom_format = None,
):
    project = Project.objects.get(id=project_id)
    print("Work", project_id)

    logger.debug('Get tasks')
    query = Task.objects.filter(project=project)

    # if project.need_to_qa:
    #     if project.need_to_qc:
    #         query = query.filter(qualified_result="qualified")
    #     else:
    #         query = query.filter(reviewed_result="approved")

    if tasks_ids and len(tasks_ids) > 0:
        logger.debug(f'Select only subset of {len(tasks_ids)} tasks')
        query = query.filter(id__in=tasks_ids)
    # if only_finished:
    #     query = query.filter(annotations__isnull=False).distinct()

    task_ids = query.values_list('id', flat=True)

    logger.debug('Serialize tasks for export')
    tasks = []
    for _task_ids in batch(task_ids, 1000):
        tasks += ExportDataSerializer(
            Task.objects.filter(id__in=_task_ids), many=True, expand=['drafts'],
            context={'interpolate_key_frames': interpolate_key_frames}
        ).data
    logger.debug('Prepare export files')
    # def do_export(project, tasks, export_type, download_resources, request_get, user_id):
    export_stream, content_type, filename = DataExport.generate_export_file(
        project, tasks, export_type, download_resources, request_get, user, custom_format=custom_format
    )

    # response = HttpResponse(File(export_stream), content_type=content_type)
    # response['Content-Disposition'] = 'attachment; filename="%s"' % filename
    # response['filename'] = filename

    print("Done")


import django_rq
import time
from django_rq import job
from django_cron import CronJobBase, Schedule
import threading
from rq.job import JobStatus

class ProcessQueueCronJob(CronJobBase):
    RUN_EVERY_MINS = 1  # Chạy mỗi 1 phút
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = "aixblock_core.data_export.func_rq.ProcessQueueCronJob"
    
    def do(self):
        queue = django_rq.get_queue('critical')
            
        # Lặp qua tất cả các job trong hàng đợi 'critical'
        for job_id in queue.job_ids:
            job = queue.fetch_job(job_id)
            
            if job:
                # Thực hiện job nếu job chưa hoàn thành
                job.perform()
                # Sau khi thực hiện xong, xoá job từ hàng đợi
                job.delete()
                print(f"Đã xoá job có ID {job.id} sau khi thực hiện xong.")
    
            # time.sleep(60)   # Thực hiện job

        # time.sleep(60)  # Đợi 60 giây trước khi kiểm tra lại

def start_cron_jobs(job_class):
    while True:
        job = job_class()
        job.do()
        sleep_time_seconds = int(job.RUN_EVERY_MINS) * 60
        time.sleep(sleep_time_seconds)

def start_threaded_cron_jobs(job_class, thread_name):
    if not hasattr(start_threaded_cron_jobs, thread_name):
        setattr(start_threaded_cron_jobs, thread_name, True)
        thread = threading.Thread(target=start_cron_jobs, args=(job_class,))
        thread.daemon = True
        thread.start()

# Khởi chạy cron job trong thread riêng
# start_threaded_cron_jobs(ProcessQueueCronJob, "queue_processor_thread")
