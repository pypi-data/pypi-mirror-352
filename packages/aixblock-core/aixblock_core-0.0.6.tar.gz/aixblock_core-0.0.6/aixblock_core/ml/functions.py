from .models import MLBackend, MLBackendStatus, MLGPU, MLBackendState
from django.db.models import Q
from django.db import models
from django.db.models import F
from django.db.models import Prefetch
from compute_marketplace.models import ComputeGPU, ComputeMarketplace
from model_marketplace.models import ModelMarketplace
import json
import subprocess
from django.utils import timezone
from django.http import JsonResponse
from urllib.parse import urlparse
from compute_marketplace.models import ComputeGPU, ComputeMarketplace
from model_marketplace.models import ModelMarketplace
from core.utils.docker_container_action import dockerContainerStartStop
import threading
from core.utils.common import get_object_with_check_and_log
from ml.models import MLNetwork, MLNetworkHistory
from django.db.models import OuterRef, Subquery, Q
from compute_marketplace.plugin_provider import vast_provider
from compute_marketplace.functions import notify_for_compute

def get_all_ip_node(project_id):
    ml_backends = MLBackend.objects.filter(
            project_id=project_id,
            deleted_at__isnull=True
        )
    try:
        list_ip = []
        for ml_backend in ml_backends:
            ml_gpu = MLGPU.objects.filter(ml_id=ml_backend.id).first()
            compute_ins = ComputeMarketplace.objects.filter(id=ml_gpu.compute_id).first() 
            if compute_ins:
                master_address = compute_ins.ip_address
                if compute_ins.type=="MODEL-PROVIDER-VAST":
                    # from compute_marketplace.vastai_func import vast_service
                    # response_data = vast_service.get_instance_info(compute_ins.infrastructure_id)
                    response_data = vast_provider.info_compute(compute_ins.infrastructure_id)
                    master_port = response_data['instances']["ports"]["23456/tcp"][0]["HostPort"]
                else:
                    master_port = "23456"
                
                ip_node = f'{master_address}:{master_port}'
                list_ip.append(ip_node)

        return list_ip
    except:
        list_ip = []
        return list_ip

# auto start master and join master after rent, add, install model
def auto_ml_nodes(self,project_id, network_id = None):

    if network_id is not None:
        network_history_subquery = MLNetworkHistory.objects.filter(
            ml_network__id=network_id, ml_id=OuterRef("id"), deleted_at__isnull=True
        ).values("ml_id")

        #  filter ml have state connected
        list_ml_backend = (
            MLBackend.objects.filter(
                project_id=project_id,
                deleted_at__isnull=True,
                state=MLBackendState.CONNECTED,
            )
            .exclude(install_status=MLBackend.INSTALL_STATUS.INSTALLING)
            .filter(Q(id__in=network_history_subquery))
            .distinct()
        )

        list_ml_backend_node = (
            MLBackend.objects.filter(project_id=project_id, deleted_at__isnull=True)
            .filter(Q(id__in=network_history_subquery))
            .distinct()
        )

    else:
        list_ml_backend = (
            MLBackend.objects.filter(
                project_id=project_id,
                deleted_at__isnull=True,
                state=MLBackendState.CONNECTED,
            )
            .exclude(install_status=MLBackend.INSTALL_STATUS.INSTALLING)
            .distinct()
        )

        list_ml_backend_node = (
            MLBackend.objects.filter(project_id=project_id, deleted_at__isnull=True)
            .distinct()
        )

    # list_node = []
    list_node = get_all_ip_node(project_id)

    world_size = len(list_ml_backend_node)
    master_address = "127.0.0.1"
    master_port = "23456"
    rank = 0
    worker = [""]
    ps = [""]

    ml_master = {"ml_id": 0,"master_host": "","master_port": 0, "cpu_ram": 0, "count_gpu": 0, "cpu_disk": 0}
    if len(list_ml_backend) > 0:
        for ml_backend in list_ml_backend:
            ml_gpu = MLGPU.objects.filter(ml_id=ml_backend.id, deleted_at__isnull=True).all()

            for gpu in ml_gpu:
                model = ModelMarketplace.objects.filter(id = gpu.model_id).first()
                compute = ComputeMarketplace.objects.filter(id=gpu.compute_id).first()
                if compute is not None and compute.is_using_cpu == False:

                    count_gpu = ComputeGPU.objects.filter(compute_marketplace_id=compute.id).count()
                    if isinstance(compute.config, str):
                        compute_config = json.loads(compute.config)
                    elif isinstance(compute.config, dict):
                        compute_config = compute.config
                    # select master nodes from ml add_manual (in model) - from ml rent model marketplace
                    if model.model_type == ModelMarketplace.ModelType.ADD_MANUAL:
                        update_ml_master(
                            ml_backend, compute_config, ml_master, count_gpu
                        )
                    elif model.model_type == ModelMarketplace.ModelType.RENT_MARKETPLACE:
                        # if not have Ml ADD_MANUAL then select ML from RENT_MARKETPLACE
                        if ml_master["ml_id"] == 0:
                            update_ml_master(
                                ml_backend, compute_config, ml_master, count_gpu
                            )

        # đã chọn được master nodes
        print(ml_master)

        # check xem đã có master chưa
        ml_status_master = (
            MLBackendStatus.objects.filter(
                project_id=project_id,
                status=MLBackendStatus.Status.MASTER,
                deleted_at__isnull=True,
            )
            .filter(
                Q(
                    ml_id__in=MLNetworkHistory.objects.filter(
                        ml_network__id=network_id,
                        ml_id=OuterRef("ml_id"),
                        deleted_at__isnull=True,
                    ).values("ml_id")
                )
            )
            .first()
        )

        # nếu chưa có master set master nodes
        if ml_status_master is None and ml_master["ml_id"] != 0:
            ml_status_master = (
                MLBackendStatus.objects.filter(
                    ml_id=ml_master["ml_id"], project_id=project_id
                ).first()
                # .filter(
                #     Q(
                #         ml_id__in=MLNetworkHistory.objects.filter(
                #             ml_network__id=network_id,
                #             ml_id=OuterRef("ml_id"),
                #             deleted_at__isnull=True,
                #         ).values("ml_id")
                #     )
                # )
                # .first()
            )
            # command set master
            # run_aixblock_master(ml_master["master_host"], len(list_ml_backend), ml_master["master_port"], ml_master["count_gpu"])
            ml_status_master.status = MLBackendStatus.Status.MASTER
            ml_status_master.status_training = MLBackendStatus.Status.TRAINING
            ml_status_master.save()

            ml_gpu = MLGPU.objects.filter(ml_id=ml_status_master.ml_id).first()
            compute_ins = ComputeMarketplace.objects.filter(id=ml_gpu.compute_id).first() 
            if compute_ins:
                master_address_tf = compute_ins.ip_address
                if compute_ins.type=="MODEL-PROVIDER-VAST":
                    # from compute_marketplace.vastai_func import vast_service
                    # response_data = vast_service.get_instance_info(compute_ins.infrastructure_id)
                    response_data = vast_provider.info_compute(compute_ins.infrastructure_id)
                    master_port_tf = response_data['instances']["ports"]["23456/tcp"][0]["HostPort"]
                else:
                    master_port_tf = "23456"

            ps = [f'{master_address_tf}:{master_port_tf}']
            worker = list(set(list_node) - set(ps))
            # ml_be = MLBackend.objects.filter(id=ml_gpu.ml_id).first()
            configs = ml_backend.config

            # tao Thread call train ml for master nodes nếu chưa có master
            train_ml(
                self,
                ml_master.get("ml_id"),
                master_address,
                master_port,
                rank,
                world_size,
                list_node,
                None,
                configs,
            )

        # neeus đã có master thì update ml_master
        elif ml_status_master is not None:
            ml_gpu = MLGPU.objects.filter(ml_id=ml_status_master.ml_id).first()
            compute_ins = ComputeMarketplace.objects.filter(id=ml_gpu.compute_id).first() 
            if compute_ins:
                master_address = compute_ins.ip_address
                if compute_ins.type=="MODEL-PROVIDER-VAST":
                    # from compute_marketplace.vastai_func import vast_service
                    # response_data = vast_service.get_instance_info(compute_ins.infrastructure_id)
                    response_data = vast_provider.info_compute(compute_ins.infrastructure_id)
                    master_port = response_data['instances']["ports"]["23456/tcp"][0]["HostPort"]
                else:
                    master_port = "23456"

            ps = [f'{master_address}:{master_port}']
            worker = list(set(list_node) - set(ps))

            check_node_not_running = MLBackendStatus.objects.filter(project_id = project_id, deleted_at__isnull=True, status_training="join_master").count()
            rank = len(list_ml_backend)-check_node_not_running

            ml_backend = MLBackend.objects.filter(id=ml_status_master.ml_id).first()
            if ml_backend is not None:
                ml_gpu = MLGPU.objects.filter(
                    ml_id=ml_backend.id, deleted_at__isnull=True
                ).first()

                if ml_gpu is not None:
                    count_gpu = ComputeGPU.objects.filter(compute_marketplace_id=ml_gpu.compute_id).count()
                    ml_master.update(
                        {
                            "ml_id": ml_backend.id,
                            "master_host": ml_backend.url.split("//")[1].split(":")[0],
                            "master_port": ml_backend.url.split(":")[-1],
                            "count_gpu": count_gpu,
                        }
                    )

            # xử lý join master
            host_list = ",".join([ml_backend.url.split("//")[1].split(":")[0] for ml_backend in list_ml_backend])

            # Gọi run_aixblock_join_master một lần sau khi đã xử lý tất cả ml_backend
            # run_aixblock_join_master(
            #     host_list,
            #     len(list_ml_backend),
            #     ml_master["master_host"],
            #     ml_master["master_port"],
            #     ml_master["count_gpu"],
            # )
            # join all worker auto join master
            ml_status_worker = MLBackendStatus.objects.filter(
                # ml_id=ml_backend.id,
                project_id=project_id,
                status=MLBackendStatus.Status.WORKER,
                status_training=MLBackendStatus.Status.JOIN_MASTER,
                deleted_at__isnull=True,
                type_training=MLBackendStatus.TypeTraining.AUTO
            ).filter(
                Q(
                    ml_id__in=MLNetworkHistory.objects.filter(
                        ml_network__id=network_id,
                        ml_id=OuterRef("ml_id"),
                        deleted_at__isnull=True,
                    ).values("ml_id")
                )
            ).all()
            for status in ml_status_worker:
                if status is not None:
                    # Gán trạng thái REJECT_MASTER cho ml_status - ml này đã join vào master
                    status.status_training = MLBackendStatus.Status.REJECT_MASTER
                    status.save()
                    configs = ml_backend.config
                    train_ml(
                        self,
                        status.ml_id,
                        master_address,
                        master_port,
                        rank,
                        world_size,
                        list_node,
                        None,
                        configs=configs,
                    )
                # call train ml for worker nodes joined master

        # Trả về danh sách ml_backend sau khi đã cập nhật
        return list_ml_backend
    return 


def train_ml(self, ml_id, master_addres=None, master_port=None, rank=None, world_size=None,workers=None, ps=None, configs = []):
    mlgpu = MLGPU.objects.filter(ml_id=ml_id, deleted_at__isnull = True).first()
    if mlgpu is None:
        return
    compute = ComputeMarketplace.objects.filter(id= mlgpu.compute_id, deleted_at__isnull = True).first()
    if compute is None:
        return
    if compute.type == ComputeMarketplace.Type.PROVIDERVAST:
        # xử lý call train ml with vastai
        ml_backend = MLBackend.objects.filter(pk=ml_id).first()

        # if ml_backend.state == "DI" or ml_backend.state == "ER":
        #     return

        from rest_framework.authtoken.models import Token
        token = Token.objects.filter(user=self.request.user)
        return ml_backend.train(
            token.first().key,
            master_address=master_addres,
            master_port=master_port,
            rank=rank,
            world_size=world_size,
            workers=workers,
            ps=ps,
            configs=configs,
            ml_backend_id=ml_backend.id
        )

    else:
        # xử lý call train ml with compute vât lý.
        return


def run_aixblock_master(master_host, num_nodes, master_port, nproc_per_node):
    command = f"aixblock run -host {master_host} --num_nodes {num_nodes} --master_port {master_port} --nproc_per_node {nproc_per_node}"
    subprocess.run(command, shell=True)
    print(command)


def run_aixblock_join_master(host_list, num_nodes,master_host, master_port, nproc_per_node):
    command = f"aixblock run -host {host_list} --master_addr {master_host}  --num_nodes {num_nodes} --master_port {master_port} --nproc_per_node {nproc_per_node}"
    subprocess.run(command, shell=True)


def update_ml_master(ml_backend, compute_config, ml_master, count_gpu):
    if (
        int(compute_config["ram"]) > int(ml_master["cpu_ram"])
        or (
            int(compute_config["ram"]) == int(ml_master["cpu_ram"])
            and int(compute_config["storage"]) > int(ml_master["cpu_disk"])
        )
        or (
            int(compute_config["storage"]) > int(ml_master["cpu_disk"])
            and compute_config["count_gpu"] > ml_master["count_gpu"]
        )
    ):
        ml_master.update(
            {
                "ml_id": ml_backend.id,
                "master_host": ml_backend.url.split("//")[1].split(":")[0],
                "master_port": ml_backend.url.split(":")[-1],
                "cpu_ram": compute_config["ram"],
                "count_gpu": count_gpu,
                # "cpu_disk": compute_config["storage"] if compute_config["storage"] else "",
            }
        )

def check_connect_ml_vast(url):
    import requests
    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    if response.status_code == 200:
        return True
    else:
        return False


def destroy_ml_instance(ml_id, user_uuid=None):
    ml_gpu = MLGPU.objects.filter(ml_id=ml_id).first()
    if ml_gpu is None:
        pass
    if ml_gpu is not None:
        gpu_ids = [int(id.strip()) for id in ml_gpu.gpus_id.split(",")]
        for gpu_id in gpu_ids:
            compute_gpu = ComputeGPU.objects.filter(pk=gpu_id).first()
            if compute_gpu and compute_gpu.quantity_used > 0:
                compute_gpu.quantity_used -= 1
                compute_gpu.save()

        ml_gpu.deleted_at = timezone.now()
        ml_gpu.save()
        model = ModelMarketplace.objects.filter(id=ml_gpu.model_id).first()
        if model is None:
            # return JsonResponse({"detail": "Not found Model"}, status=404)
            pass

        if compute_gpu.compute_marketplace.type != "MODEL-PROVIDER-VAST":
            try:
                dockerContainerStartStop(
                    base_image=model.docker_image,
                    action="delete",
                    ip_address=ip_address,
                    project_id=mlbackend.project.id,
                    model_id=model.pk,
                )
            except Exception as e:
                print(e)

    MLBackendStatus.objects.filter(ml_id=ml_id).update(deleted_at=timezone.now())
    MLGPU.objects.filter(ml_id=ml_id).update(deleted_at=timezone.now())

    # Assuming instance has a `url` attribute, you might need to fetch the instance first
    mlbackend = MLBackend.objects.filter(id=ml_id).first()
    parsed_url = urlparse(mlbackend.url)
    ip_address = parsed_url.hostname

    mlbackend.deleted_at = timezone.now()
    mlbackend.save()

    if user_uuid:
        notify_for_compute(user_uuid, "Success", "The model has been successfully removed.")
    
    from plugins.plugin_centrifuge import publish_message
    publish_message(
        channel=f'project/{mlbackend.project_id}/deploy-history', data={"refresh": True}, prefix=True
    )
    
    return JsonResponse({"detail": "ML instance destroyed successfully"}, status=200)
