import json
from .models import CatalogComputeMarketplace, ComputeMarketplace, ComputeGPU, ComputeGpuPrice, ComputeTimeWorking
from rest_framework.authtoken.models import Token
from core.utils.docker_container_pull import dockerContainerPull, docker_container_check_status
import os
from django.conf import settings
import threading

from plugins.plugin_centrifuge import (
    generate_centrifuge_jwt,
    connect_to_server,
    subscribe_to_channel,
    publish_message,
    run_centrifuge,
)
import asyncio
from threading import Thread
from .models import ComputeMarketplace, History_Rent_Computes


def import_catalog_compute_templates():
    # Assuming the deletion of existing data if necessary
    CatalogComputeMarketplace.objects.all().delete()
    print("All CatalogComputeMarketplace objects have been deleted.")

    # Read catalog.json to get the templates directory
    base_dir = os.path.dirname(__file__)
    catalog_path = os.path.join(base_dir, 'seeds', 'catalog.json') 
    with open(catalog_path, 'r', encoding='utf-8') as file:
      catalog_data = json.load(file)

    for item in catalog_data:
        CatalogComputeMarketplace.objects.create(
            name=item.get('name'),
            catalog_id=item.get('catalog_id', 0),  # Defaulting to 0 if not present
            order=item.get('order'),
            tag=item.get('tag'),
            status=item.get('status'),
        )
    print(f"{len(catalog_data)} CatalogComputeMarketplace objects have been created.")

    return item

def import_compute_templates(user_id):
    # Assuming the deletion of existing data if necessary
    ComputeMarketplace.objects.all().delete()
    print("All ComputeMarketplace objects have been deleted.")

    # Read computes.json to get the templates directory
    base_dir = os.path.dirname(__file__)
    compute_path = os.path.join(base_dir, 'seeds', 'computes.json') 
    with open(compute_path, 'r', encoding='utf-8') as file:
      compute_data = json.load(file)

    for item in compute_data:
        ComputeMarketplace.objects.create(
            # pk=item.get('id'),
            name=item.get('name'),
            catalog_id=item.get('catalog_id'),
            order=item.get('order'),
            status=item.get('status'),
            infrastructure_id=item.get('infrastructure_id'),
            owner_id=user_id,
            author_id=user_id,
            organization_id=item.get('organization_id'),
            config=item.get('config'),
            ip_address=item.get('ip_address'),
            port=item.get('port'),
            docker_port=item.get('docker_port'),
            kubernetes_port=item.get('kubernetes_port'),
            file=item.get('file'),
            type=item.get('type'),
            infrastructure_desc=item.get('infrastructure_desc'),
            callback_url=item.get('callback_url'),
            client_id=item.get('client_id'),
            client_secret=item.get('client_secret'),
            ssh_key=item.get('ssh_key'),
            card=item.get('card'),
            price=item.get('price'),
            compute_type=item.get('compute_type'),
            is_using_cpu=item.get('is_using_cpu')
        )
        # try:
        #    token = Token.objects.get(user_id=1)
        # except:
        #    token = ''

        # dockerContainerPull(
        #     compute.compute_type,
        #     compute.ip_address,
        #     compute.client_id,
        #     compute.client_secret,
        #     token
        # )

    print(f"{len(compute_data)} ComputeMarketplace objects have been created.")

    return item

def import_computegpu_templates(user_id):
    # Assuming the deletion of existing data if necessary
    ComputeGPU.objects.all().delete()
    print("All Compute Gpu objects have been deleted.")

    # Read computes.json to get the templates directory
    base_dir = os.path.dirname(__file__)
    compute_path = os.path.join(base_dir, 'seeds', 'compute_gpu.json') 
    with open(compute_path, 'r', encoding='utf-8') as file:
      compute_data = json.load(file)

    for item in compute_data:
        
        compute = ComputeMarketplace.objects.filter(infrastructure_id=item.get('infrastructure_id')).first()
        if compute is not None:
            ComputeGPU.objects.create(
                # pk=item.get('id'),
                infrastructure_id=compute,
                gpu_name =item.get('gpu_name'),
                power_consumption=item.get('power_consumption'),
                gpu_index=item.get('gpu_index'),
                gpu_memory=item.get('gpu_memory'),
                branch_name=item.get('branch_name'),
                gpu_id= item.get('gpu_id'),
                # "created_at": "2024-03-26 03:58:45.756541+00",
                # "update_at": "2024-03-26 03:58:45.756541+00",
                status= item.get("status"),
                compute_marketplace_id=compute.id,
                quantity_used=item.get('quantity_used'),
                deleted_at=item.get('deleted_at'),
                # seriaino=item.get('seriaino'),
                # memory_usage=item.get('memory_usage'),
                # power_usage=item.get('power_usage'),
                # batch_size=item.get('batch_size')
            )

    print(f"{len(compute_data)} Compute gpu objects have been created.")

    return item

def import_computegpu_price_templates(user_id):
    # Assuming the deletion of existing data if necessary
    ComputeGpuPrice.objects.all().delete()
    print("All Compute Gpu objects have been deleted.")

    # Read computes.json to get the templates directory
    base_dir = os.path.dirname(__file__)
    compute_path = os.path.join(base_dir, 'seeds', 'compute_gpu_price.json') 
    with open(compute_path, 'r', encoding='utf-8') as file:
        compute_data = json.load(file)
    
    price_data = 0

    for item in compute_data:
        compute_gpus = ComputeGPU.objects.filter(infrastructure_id=item.get('infrastructure_id'))
        for compute_gpu in compute_gpus:
            ComputeGpuPrice.objects.create(
                compute_gpu_id=compute_gpu,
                compute_marketplace_id=compute_gpu.compute_marketplace,
                token_symbol=item.get('token_symbol'),
                price=item.get("price"),
                model_marketplace_id=item.get("model_marketplace_id"),
                unit=item.get("unit"),
                type=item.get("type")
            )
            price_data += 1

    print("Compute gpu price objects have been created.")
    
    return f'{price_data}'

def import_computegpu_timeworking_templates(user_id):
    # Assuming the deletion of existing data if necessary
    ComputeTimeWorking.objects.all().delete()
    print("All Compute Gpu objects have been deleted.")

    # Read computes.json to get the templates directory
    base_dir = os.path.dirname(__file__)
    compute_path = os.path.join(base_dir, 'seeds', 'compute_gpu_timeworking.json') 
    with open(compute_path, 'r', encoding='utf-8') as file:
      compute_data = json.load(file)

    time_data = 0

    for item in compute_data:
        compute = ComputeMarketplace.objects.filter(infrastructure_id=item.get('infrastructure_id')).first()
        ComputeTimeWorking.objects.create(
            # pk=item.get('id'),
            infrastructure_id= item.get("infrastructure_id"),
            time_start=item.get("time_start"),
            time_end=item.get("time_end"),
            # compute_gpu_id=item.get("compute_gpu_id"),
            status=item.get("status"),
            compute_id=compute.id,
            day_range=item.get("day_range")
        )

        time_data += 1

    print(f"{len(compute_data)} Compute gpu time working objects have been created.")

    return f'{time_data}'


async def handle_centrifuge_verify_compute(user_id, channel):
    # Subscribe to the desired channel
    # publish_message(channel="string", data="Training started")

    await asyncio.Future()


def run_event_loop_in_thread(user_id, infrastructure_id, host_name=None, token=None):
    try:
        import requests

        url = settings.API_VERIFY_JOB

        payload = json.dumps({
            "user_id": user_id,
            "infrastructure_id": infrastructure_id,
            "host_name": host_name,
            "token": token
        })

        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        if response.status_code != 200:
            run_centrifuge(user_id,infrastructure_id)

    except requests.exceptions.RequestException as e:
        import logging
        logging.error(f"Request failed: {e}")
        run_centrifuge(user_id,infrastructure_id)


def check_compute_verify(infrastructure_id, ip_address):
    compute = ComputeMarketplace.objects.filter(
        ip_address=ip_address,
        deleted_at__isnull = True
    ).first()
    return True


def check_compute_run_status(history_compute_id):
    from plugins.plugin_centrifuge import publish_message
    history = History_Rent_Computes.objects.filter(id = history_compute_id, deleted_at__isnull = True).first()
    compute = ComputeMarketplace.objects.filter(id= history.compute_marketplace_id, deleted_at__isnull = True).first()
    try:
        docker_status = docker_container_check_status(
        history.service_type, compute.ip_address, compute.docker_port, history.container_network
        )
    except ValueError as e:
        print(f"Error: {e}")
        history.install_logs = str(e)
        history.compute_install = "failed"
        history.save()
        publish_message(
            channel=compute.infrastructure_id, data={"refresh": True}, prefix=True
        )
        return

    if docker_status == 'running':
        #  handle update if running
        history.compute_install = "completed"
        history.install_logs = ""
        history.save()
        publish_message(channel=compute.infrastructure_id, data={"refresh": True}, prefix=True)
        return docker_status
    elif docker_status == 'exited':
        history.compute_install = "failed"
        # add logs if install error
        history.install_logs = ""
        history.save()
        publish_message(
            channel=compute.infrastructure_id, data={"refresh": True}, prefix=True
        )
        return docker_status
    elif docker_status == 'created':
        pass
    else:
        return docker_status


#   Default = "Default",
#   Info = "Info",
#   Danger = "Danger",
#   Success = "Success",
#   Warning = "Warning",

def notify_for_compute(user_id, type, message):
    try:
        publish_message(
            channel=f"user-notification/{user_id}",
            data={
                "type": type,
                "message": message
            },
        )
    except Exception as e:
        print(e)


class ThreadManager:
    def __init__(self):
        self.lock = threading.Lock()
        self.threads = {}

    def start_thread(self, target, thread_name):
        with self.lock:
            if thread_name in self.threads and self.threads[thread_name].is_alive():
                print(f"Thread {thread_name} is already running. Skipping.")
                return

            # Tạo và khởi động thread mới
            thread = threading.Thread(target=target, name=thread_name)
            self.threads[thread_name] = thread
            thread.start()

    def join_threads(self):
        with self.lock:
            for thread in self.threads.values():
                if thread.is_alive():
                    thread.join()
