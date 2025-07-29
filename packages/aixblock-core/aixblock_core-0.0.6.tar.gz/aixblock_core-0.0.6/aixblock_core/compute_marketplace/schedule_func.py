import time
import threading
from django.utils import timezone
from django_cron import CronJobBase, Schedule
import logging
from .models import History_Rent_Computes, ComputeGPU, ComputeMarketplace
from .system_info import update_system_info
from .vastai_func import vast_service
from .plugin_provider import vast_provider, exabit_provider
logger = logging.getLogger(__name__)
from ml.models import MLGPU
from ml.functions import destroy_ml_instance
import random
import string
from datetime import timedelta
import uuid
from users.models import User
from aixblock_core.users.service_notify import send_email_thread
from aixblock_core.core.utils.nginx_server import NginxReverseProxy
from django.conf import settings
import os
from .self_host import subscription_selfhost_cron
from core.settings.base import MAIL_SERVER

class UpdateDatabaseCronJob(CronJobBase):
    RUN_EVERY_MINS = 3  # Runs every 3 minutes
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = "aixblock_core.compute_marketplace.schedule_func.UpdateDatabaseCronJob"

    def do(self):
        try:
            time_threshold = timezone.now()
            time_threshold_min = time_threshold + timedelta(minutes=40)
            time_threshold_max = time_threshold + timedelta(minutes=45)

            filtered_records = History_Rent_Computes.objects.filter(
                time_end__lte=time_threshold, deleted_at__isnull=True,deleted_by__isnull = True
            )

            filtered_records_time_end = History_Rent_Computes.objects.filter(
                time_end__gte=time_threshold_min,
                time_end__lte=time_threshold_max,
                deleted_at__isnull=True,
                deleted_by__isnull=True
            )
            for record in filtered_records_time_end:
                html_file_path =  './templates/mail/delete_compute.html'
                user = User.objects.filter(id=record.compute_marketplace.author_id).first()

                with open(html_file_path, 'r', encoding='utf-8') as file:
                    html_content = file.read()
                
                # notify_reponse = ServiceSendEmail(DOCKER_API)
                # send_to = user.username if user.username else user.email
                html_content = html_content.replace('xxx', f'{record.compute_marketplace.id}')

                data = {
                    "subject": f"AIxBlock| Action Required: Back Up Your Data Before Compute Rental Expires",
                    "from": "noreply@aixblock.io",
                    "to": [f"{user.email}"],
                    "html": html_content,
                    "text": "Action Required: Back Up Your Data Before Compute Rental Expires!",
                }

                docket_api = "tcp://69.197.168.145:4243"
                host_name = MAIL_SERVER

                if not History_Rent_Computes.objects.filter(pk = record.id, mail_end_send=True).exists():
                    History_Rent_Computes.objects.filter(pk = record.id).update(mail_end_send=True)
                    email_thread = threading.Thread(target=send_email_thread, args=(docket_api, host_name, data,))
                    email_thread.start()
                
            for record in filtered_records:
                # update compute gpu
                compute_gpu = ComputeGPU.objects.filter(
                    id=record.compute_gpu_id
                ).first()
                if record.compute_marketplace.type == "MODEL-PROVIDER-VAST":
                    # vast_service.delete_instance_info(record.compute_marketplace.infrastructure_id)
                    vast_provider.delete_compute(record.compute_marketplace.infrastructure_id)
                    # delete compute if vast
                    compute_marketplace = ComputeMarketplace.objects.filter(id = record.compute_marketplace_id).first()

                    def generate_random_string(length=6):
                        letters = string.ascii_letters + string.digits
                        return ''.join(random.choice(letters) for i in range(length))

                    if compute_marketplace:
                        compute_marketplace.deleted_at = timezone.now()
                        # save new infrastructure_id (infrastructure_id unique but can rerented)
                        infrastructure_id = f"{compute_marketplace.infrastructure_id}-{uuid.uuid4()}"

                        compute_marketplace.infrastructure_id = infrastructure_id 
                        compute_marketplace.save()
                    compute_gpu.deleted_at = timezone.now()
                    compute_gpu.infrastructure_id = compute_marketplace
                    compute_gpu.save()

                elif record.compute_marketplace.type == "MODEL-PROVIDER-EXABIT":
                    # vast_service.delete_instance_info(record.compute_marketplace.infrastructure_id)
                    exabit_provider.delete_compute(record.compute_marketplace.infrastructure_id)
                    # delete compute if vast
                    compute_marketplace = ComputeMarketplace.objects.filter(id = record.compute_marketplace_id).first()

                    def generate_random_string(length=6):
                        letters = string.ascii_letters + string.digits
                        return ''.join(random.choice(letters) for i in range(length))

                    if compute_marketplace:
                        compute_marketplace.deleted_at = timezone.now()
                        # save new infrastructure_id (infrastructure_id unique but can rerented)
                        infrastructure_id = f"{compute_marketplace.infrastructure_id}-{uuid.uuid4()}"

                        compute_marketplace.infrastructure_id = infrastructure_id
                        compute_marketplace.save()
                    compute_gpu.deleted_at = timezone.now()
                    compute_gpu.infrastructure_id = compute_marketplace
                    compute_gpu.save()

                if compute_gpu and compute_gpu.user_rented > 0:
                    compute_gpu.user_rented -= 1
                    compute_gpu.save()

                # record.deleted_at = timezone.now() #when user click delete
                record.deleted_by = History_Rent_Computes.DELETED_BY.AUTO_SERVICE
                record.status = "completed"
                record.save()

                # delete ml
                mlgpu=  MLGPU.objects.filter(gpus_id = record.compute_gpu_id, deleted_at__isnull = True).first()
                if mlgpu is not None:
                    destroy_ml_instance(mlgpu.ml_id)
            
                try:
                    if compute_marketplace:
                        nginx_proxy_manager = NginxReverseProxy(f'{settings.REVERSE_ADDRESS}', f'{compute_marketplace.ip_address}_{compute_marketplace.port}')
                        nginx_proxy_manager.remove_nginx_service()
                    if compute_marketplace.api_port:
                        nginx_proxy_manager = NginxReverseProxy(f'{settings.REVERSE_ADDRESS}', f'{compute_marketplace.ip_address}_{compute_marketplace.api_port}')
                        nginx_proxy_manager.remove_nginx_service()
                        
                except Exception as e:
                    print(e)

            logger.info("UpdateDatabaseCronJob: Database updated successfully.")
        except Exception as e:
            logger.error(f"UpdateDatabaseCronJob: Error updating database - {e}")


class UpdateSystemInfoCronJob(CronJobBase):
    RUN_EVERY_MINS = 5  # Runs every 1 minute
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = (
        "aixblock_core.compute_marketplace.schedule_func.UpdateSystemInfoCronJob"
    )

    def do(self):
        update_system_info()
        logger.info(
            "UpdateSystemInfoCronJob: System information updated successfully."
        )


class SubcriptionSelfhost(CronJobBase):

    RUN_EVERY_MINS = 1  # Runs every 1 minute
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = "aixblock_core.compute_marketplace.schedule_func.SubcriptionSelfhost"

    def do(self):
        subscription_selfhost_cron()
        logger.info("SubcriptionSelfhost Job: System information updated successfully.")


def start_cron_jobs(job_class):
    while True:
        job = job_class()
        job.do()
        sleep_time_seconds = int(job.RUN_EVERY_MINS) * 60
        time.sleep(sleep_time_seconds)


def start_cron_jobs_self_host(job_class):
    while True:
        job = job_class()
        job.do()
        sleep_time_seconds = int(job.RUN_EVERY_MINS) * 60
        time.sleep(sleep_time_seconds)


def start_threaded_cron_jobs(job_class, thread_name):
    if os.getenv('RUNNING_CRONJOB') != '1':
        os.environ['RUNNING_CRONJOB'] = '1'
        if not hasattr(start_threaded_cron_jobs, thread_name):
            setattr(start_threaded_cron_jobs, thread_name, True)
            thread = threading.Thread(target=start_cron_jobs, args=(job_class,))
            thread.daemon = True
            thread.start()


def start_threaded_cron_jobs_self_host(job_class, thread_name):
    if os.getenv("RUNNING_CRONJOB") != "2":
        os.environ["RUNNING_CRONJOB"] = "2"
        if not hasattr(start_threaded_cron_jobs, thread_name):
            setattr(start_threaded_cron_jobs, thread_name, True)
            thread = threading.Thread(
                target=start_cron_jobs_self_host, args=(job_class,)
            )
            thread.daemon = True
            thread.start()


# Start the cron jobs in separate threads
start_thread_cron = start_threaded_cron_jobs(UpdateDatabaseCronJob, "database_thread")
# start_threaded_cron_jobs(UpdateDatabaseCronJob, "database_thread")
# start_threaded_cron_jobs(UpdateSystemInfoCronJob, "system_info_thread")
# start_thread_cron_self_host = start_threaded_cron_jobs_self_host(
#     SubcriptionSelfhost, "subcription_self_host"
# )
