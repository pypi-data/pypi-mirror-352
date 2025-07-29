import json
from .models import CatalogModelMarketplace, ModelMarketplace
import os
from compute_marketplace.vastai_func import (
    vast_service,
)  
from rest_framework.response import Response
from core.utils.docker_container_create import createDocker, createDockerDeploy
from ml.models import MLBackend, MLGPU, MLBackendState, MLBackendStatus
from model_marketplace.models import History_Build_And_Deploy_Model
from .build_model import build_model
from compute_marketplace.plugin_provider import vast_provider, exabit_provider
import threading
from compute_marketplace.functions import notify_for_compute

def import_catalog_model_templates():
    # Assuming the deletion of existing data if necessary
    # CatalogModelMarketplace.objects.all().delete()
    # print("All CatalogModelMarketplace objects have been deleted.")

    # Read catalog.json to get the templates directory
    base_dir = os.path.dirname(__file__) 
    catalog_path = os.path.join(base_dir, 'seeds', 'catalog.json')
    with open(catalog_path, 'r', encoding='utf-8') as file:
        catalog_data = json.load(file)

    for item in catalog_data:
        if not CatalogModelMarketplace.objects.filter(name=item.get('name')).exists():
            CatalogModelMarketplace.objects.create(
                name=item.get('name'),
                catalog_id=item.get('catalog_id', 0),  # Defaulting to 0 if not present
                order=item.get('order'),
                tag=item.get('tag'),
                status=item.get('status'),
                key=item.get('key')
            )
        else:
            CatalogModelMarketplace.objects.filter(name=item.get('name')).update(
                # name=item.get('name'),
                catalog_id=item.get('catalog_id', 0),  # Defaulting to 0 if not present
                order=item.get('order'),
                tag=item.get('tag'),
                status=item.get('status'),
                key=item.get('key')
            )
    print(f"{len(catalog_data)} CatalogModelMarketplace objects have been created.")

    return item

def import_model_templates(user_id):
    # Assuming the deletion of existing data if necessary
    ModelMarketplace.objects.all().delete()
    print("All ModelMarketplace objects have been deleted.")

    # Read model.json to get the templates directory
    base_dir = os.path.dirname(__file__) 
    model_path = os.path.join(base_dir, 'seeds', 'models.json')
    with open(model_path, 'r', encoding='utf-8') as file:
        model_data = json.load(file)

    for item in model_data:
        config = item.get('config')

        # Convert config to JSON string
        config_json = json.dumps(config)
        catalog_model_key=item.get('catalog_model_key')

        catalog = CatalogModelMarketplace.objects.filter(key=catalog_model_key).first()\
        
        if catalog is not None:
            ModelMarketplace.objects.create(
                name=item.get('name'),
                owner_id=user_id,
                author_id=user_id,
                checkpoint_storage_id=item.get('checkpoint_storage_id'),
                ml_id=item.get('ml_id'),
                catalog_id=catalog.id,
                order=item.get('order'),
                config=config_json,  # Save config as JSON string
                dataset_storage_id=item.get('dataset_storage_id'),
                image_dockerhub_id=item.get('image_dockerhub_id'),
                infrastructure_id=item.get('infrastructure_id'),
                model_desc=item.get('model_desc'),
                type=item.get('type'),
                ip_address=item.get('ip_address'),
                port=item.get('port'),
                status=item.get('status'),
                file=item.get('file'),
                price=item.get('price'),
                docker_access_token=item.get('docker_access_token'),
                docker_image=item.get('docker_image')
            )
        else:
            print(f"No catalog found for key '{catalog_model_key}'")
    print(f"{len(model_data)} ModelMarketplace objects have been created.")

    return item


def handle_rent_model(
    self,
    compute,
    model,
    project_id,
    gpus_index,
    gpu_id,
    _model,
    ml,
    ml_gpu,
    docker_image=None,
    ml_network_id = None,
    info_run=None,
    user=None
):
    try:
        if docker_image is None:
            docker_image = _model.docker_image

        _model_reload = ModelMarketplace.objects.filter(pk=_model.id).first()
        ml_reload = MLBackend.objects.filter(pk=ml.id).first()

        if _model_reload:
            _model = _model_reload
        if ml_reload:
            ml = ml_reload

        link_deploy = None
        from projects.models import Project
        from compute_marketplace.models import ComputeGPU
        from datetime import datetime
        project = Project.objects.filter(id=project_id).first()

        if project: # and project.flow_type == Project.FlowType.DEPLOY:
            ml.is_deploy = True
            checkpoint_id = _model.checkpoint_storage_id if _model.checkpoint_storage_id else None
            now = datetime.now()
            date_str = now.strftime("%Y%m%d")
            time_str = now.strftime("%H%M%S")
            
            version = f'{date_str}-{time_str}'
            History_Build_And_Deploy_Model.objects.create(
                    version = version,
                    model_id = _model.pk,
                    checkpoint_id = checkpoint_id,
                    project_id = project_id,
                    user_id = user.id,
                    type = History_Build_And_Deploy_Model.TYPE.DEPLOY
                )
            
            try:
                ml.save()
            except:
                MLBackend.objects.filter(pk=ml.id).update(is_deploy=True)

            if "Origin" in self.request.headers and self.request.headers["Origin"]:
                host_name = self.request.headers["Origin"]
            elif "Host" in self.request.headers:
                host_name = self.request.headers["Host"]
            else:
                host_name = "https://app.aixblock.io/"

            link_deploy = f'{host_name}/{project.flow_type}/{project.id}/demo-and-deploy'
        # Initialize schema variable
        schema = "http"
        tensorboard_endpoint = 6060
        ddp_endpoint = 9090

        if compute.type == "MODEL-PROVIDER-VAST":
            compute_gpu = ComputeGPU.objects.filter(compute_marketplace_id=compute.id, deleted_at__isnull=True).order_by("-id").first()
            try:
                disk_size = compute_gpu.disk
            except:
                disk_size = 40

            schema = "https"
            if info_run and "ssl_used" in info_run and info_run["ssl_used"]==False:
                schema = "http"
                
            if info_run and "grpc_used" in info_run and info_run["grpc_used"]==True:
                schema = "grpc"
            # vast_service.delete_instance_info(compute.infrastructure_id)
            vast_provider.delete_compute(compute.infrastructure_id)
            def remove_proxy(compute_marketplace):
                if compute_marketplace:
                    from aixblock_core.core.utils.nginx_server import NginxReverseProxy
                    from django.conf import settings
                    
                    nginx_proxy_manager = NginxReverseProxy(f'{settings.REVERSE_ADDRESS}', f'{compute_marketplace.ip_address}_{compute_marketplace.port}')
                    nginx_proxy_manager.remove_nginx_service()

            thread = threading.Thread(target=remove_proxy, args=(compute,))
            thread.start()
            # status_install, response = vast_service.func_install_compute_vastai(
            #     compute.infrastructure_desc,
            #     docker_image,
            #     "ml",
            # )
            status_install, response, _ = vast_provider.func_install_compute_vastai(
                compute.infrastructure_desc,
                docker_image,
                "ml",
                info_run=info_run,
                disk_size=disk_size
            )
            if not status_install:
                return Response(
                    {"detail": f"Not available, please try again"}, status=400
                )
            # print(response["instances"]["ports"]["9090/tcp"][0]["HostPort"])
            try:
                _port_info = int(info_run["exposed_ports"][0])
                _port = response["instances"]["ports"][f"{_port_info}/tcp"][0]["HostPort"]
            except:
                _port = response["instances"]["ports"]["9090/tcp"][0]["HostPort"]

            compute.infrastructure_id = response["instances"]["id"]
            compute.infrastructure_desc = response["instances"]["old_id"]
            compute.port = _port
            _model.schema = schema

            if info_run:
                _model.info_run = info_run

            compute.save()
            _model.port = _port
            _model.save()

        elif compute.type == "MODEL-PROVIDER-EXABIT":
            schema = "https"
            if info_run and "ssl_used" in info_run and info_run["ssl_used"]==False:
                schema = "http"
                
            if info_run and "grpc_used" in info_run and info_run["grpc_used"]==True:
                schema = "grpc"

            status_install, response, errors = exabit_provider.install_compute(compute.infrastructure_id, docker_image, 'ml', install_check=True)
            if not status_install:
                return Response(
                    {"detail": f"Not available, please try again"}, status=400
                )
            # print(response["instances"]["ports"]["9090/tcp"][0]["HostPort"])
            try:
                _port_info = int(info_run["exposed_ports"][0])
                _port = response["data"]["ports"][f"{_port_info}"]
            except:
                _port = response["data"]["ports"]["9090"]
                
            compute.port = _port
            compute.save()
            _model.schema = schema
            if info_run:
                _model.info_run = info_run
            _model.port = _port
            _model.save()

        else:
            _port = createDocker(
                docker_image,
                project_id,
                f"tcp://{compute.ip_address}:{compute.docker_port}",
                model.port,
                _model.pk,
                str(gpus_index),
                str(gpu_id),
            )
            _model.port = _port
            _model.schema = schema
            if info_run:
                _model.info_run = info_run
            _model.save()

        ml_gpu = MLGPU.objects.filter(id=ml_gpu.id).first()
        ml_gpu.port = _port
        ml_gpu.save()
        ml = MLBackend.objects.filter(id=ml.id).first()
        ml.url = f"{schema}://{compute.ip_address}:{_port}"
        ml.install_status = MLBackend.INSTALL_STATUS.COMPLEATED
        ml.state = MLBackendState.CONNECTED
        ml.save()

        from plugins.plugin_centrifuge import publish_message
        from core.settings.base import MAIL_SERVER
        from aixblock_core.users.service_notify import send_email_thread
        # publish_message(
        #     channel=f'project/{project_id}/deploy-history', data={"refresh": True}, prefix=True
        # )

        def send_mail_rent_compute(email, compute, model_endpoint, tensorboard, ddp_endpoint, schema, link_deploy):
            try:
                html_file_path =  './templates/mail/install_model_success.html'
                with open(html_file_path, 'r', encoding='utf-8') as file:
                    html_content = file.read()

                html_content = html_content.replace('[user]', f'{email}')
                # html_content = html_content.replace('xxx', f'{compute.id}')
                if link_deploy:
                    html_content = html_content.replace('[link]', link_deploy)
                else:
                    html_content = html_content.replace('[link]', f'https://{compute.ip_address}:{model_endpoint}')

                if "grpc" in schema:
                    print("grpc")
                    # html_content = html_content.replace(
                    #     '[link]',
                    #     f'grpc://{compute.ip_address}:{model_endpoint}. Please verify it yourself as we do not perform grpc checks.'
                    # )
                else:   
                    verify_ssl = False  # Đặt True nếu muốn kiểm tra chứng chỉ SSL
                    import time

                    # Khoảng thời gian giữa các lần thử (giây)
                    retry_interval = 120
                    send_mail_wait = False

                    # Vòng lặp gọi API
                    while True:
                        try:
                            response = requests.get(f"https://{compute.ip_address}:{model_endpoint}", verify=verify_ssl)
                            if response.status_code == 200:  # Điều kiện thành công
                                print("API call successful!")
                                print("Response Body:", response.json())
                                break  # Thoát khỏi vòng lặp nếu thành công
                            else:
                                print(f"Received status code: {response.status_code}. Retrying...")
                        except requests.exceptions.RequestException as e:
                            print(f"Error during API call: {e}. Retrying...")
                        
                            # if not send_mail_wait:
                            #     html_file_path =  './templates/mail/wait_install_checkpoint.html'
                            #     data = {
                            #         "subject": "AIxBlock | Checkpoint Loading Notification",
                            #         "from": "noreply@aixblock.io",
                            #         "to": [f'{email}'],
                            #         "html": html_content,
                            #         "text": "Welcome to AIxBlock!",
                            #         "attachments": []
                            #     }

                            #     docket_api = "tcp://69.197.168.145:4243"
                            #     host_name = MAIL_SERVER

                            #     email_thread = threading.Thread(target=send_email_thread, args=(docket_api, host_name, data,))
                            #     email_thread.start()
                            #     send_mail_wait = True
                        # Chờ trước khi thử lại
                        time.sleep(retry_interval)
                        
                data = {
                    "subject": "AIxBlock | Successful Model Installation",
                    "from": "noreply@aixblock.io",
                    "to": [f'{email}'],
                    "html": html_content,
                    "text": "Welcome to AIxBlock!",
                    "attachments": []
                }

                docket_api = "tcp://69.197.168.145:4243"
                host_name = MAIL_SERVER

                email_thread = threading.Thread(target=send_email_thread, args=(docket_api, host_name, data,))
                email_thread.start()
            except:
                pass
        
        if MLBackend.objects.filter(id=ml.id, deleted_at__isnull=False).exists():
            return
        
        if user:
            send_mail_rent_compute(user.email, compute, _model.port, tensorboard_endpoint, ddp_endpoint, _model.schema, link_deploy)

        notify_for_compute(self.request.user.uuid, "Success", "The model has been successfully installed")
        from plugins.plugin_centrifuge import publish_message

        publish_message(
            channel=f'ml_{ml.id}', data={"refresh": True}, prefix=True
        )

        publish_message(
            channel=f'project/{project_id}/deploy-history', data={"refresh": True}, prefix=True
        )
        # from ml.functions import auto_ml_nodes
        # # run auto select master, join master
        # if ml_network_id:
        #     auto_ml_nodes(self, project_id, ml_network_id)
        return

    except Exception as e:
        print(e)
        notify_for_compute(self.request.user.uuid, "Danger", "The model installation has failed.")
        ml.install_status = MLBackend.INSTALL_STATUS.FAILED
        ml.state = MLBackendState.ERROR
        ml.save()


def handle_add_model(
    self,
    compute,
    model,
    project_id,
    gpus_index,
    gpu_id,
    _model,
    ml,
    ml_gpu,
    model_source,
    model_id_url,
    model_token,
    model_name,
    ml_network_id=None,
    file=None,
    file_content=None,
    info_run=None,
    user=None
):
    docker_image = _model.docker_image
    if model_source == "LOCAL" or model_source == "CHECKPOINT":
        docker_image = build_jenkin_from_zipfle(file, model_name, file_content)
        if docker_image:
            _model.docker_image = docker_image
            _model.save()

    if model_source == ModelMarketplace.ModelSource.DOCKER_HUB:
        # if model_id_url:
        #     docker_image = model_id_url
        _model.docker_image = docker_image
        _model.save()

    if model_source == ModelMarketplace.ModelSource.GIT:
        docker_image = build_model(
            model_source, model_id_url, model_token, model_name
        )
        if docker_image:
            _model.docker_image = docker_image
            _model.save()
    if model_source == ModelMarketplace.ModelSource.HUGGING_FACE:
        docker_image = build_model(
            model_source, model_id_url, model_token, model_name
        )

        if docker_image:
            _model.docker_image = docker_image
            _model.save()

    return handle_rent_model(
        self,
        compute,
        _model,
        project_id,
        gpus_index,
        gpu_id,
        _model,
        ml,
        ml_gpu,
        docker_image,
        ml_network_id,
        info_run=info_run,
        user=user
    )


def normalize_name(name):
    return name.lower().replace(" ", "-")

from pathlib import Path
import base64
from jenkinsapi.jenkins import Jenkins
import requests

def build_jenkin_from_zipfle(zip_file, name, zip_file_content = None):
    import time
    from core.settings.base import JENKINS_TOKEN, JENKINS_URL

    if not zip_file:
        return False

    # Normalize the project name
    model_name = normalize_name(name) if name else Path(zip_file.name).stem

    # Jenkins configuration
    jenkins_url = JENKINS_URL
    jenkins = Jenkins(jenkins_url, username="admin", password="admin123@")

    job_name = model_name

    # Path to Jenkins job config XML file
    job_config_path = os.path.join(os.path.dirname(__file__), "jenkins-no-git.xml")
    with open(job_config_path, "r") as file:
        xml = file.read()

    # Create or update the Jenkins job
    if job_name not in jenkins.jobs:
        jenkins.create_job(jobname=job_name, xml=xml)
    else:
        job = jenkins[job_name]
        # job.update_config(xml)

    # Trigger the Jenkins build
    job = jenkins[job_name]
    try:
        if job.is_queued_or_running():
            return Response(
                {"message": "A build is already running for this job."},
                status=409,
            )
        else:
            if zip_file_content:
                encoded_file = base64.b64encode(zip_file_content).decode("utf-8")
            else: 
                encoded_file = base64.b64encode(zip_file.read()).decode("utf-8")

            files = {
                'THEFILE': (zip_file.name, encoded_file, 'application/zip')
            }
            for _ in range(2):
                response = requests.post(
                    f"{jenkins_url}/job/{job_name}/buildWithParameters",
                    auth=("admin", JENKINS_TOKEN),
                    files=files,
                    data={"THEFILE": zip_file.name},
                )
                response.raise_for_status()
                time.sleep(10)

                # build_number = job.get_next_build_number()
                # build = job.get_build(build_number)
                # build.block_until_complete()

                # Check number of builds
                # current_number = job.get_next_build_number()
                # complete_last_build = job.get_last_completed_build()
                # if complete_last_build.buildno == current_number and current_number> 1:
                #     print(f"Deleting job {job_name} after build completion.")
                #     jenkins.delete_job(job_name)
                #     print(f"Job {job_name} deleted.")
            # Lấy số build mới nhất
            # job_info = requests.get(f"{jenkins_url}/job/{job_name}/api/json", auth=("admin", JENKINS_TOKEN)).json()
            next_build_number = 2

            # Theo dõi trạng thái build
            while True:
                build_info = requests.get(f"{jenkins_url}/job/{job_name}/{next_build_number}/api/json", auth=("admin", JENKINS_TOKEN)).json()

                if build_info['building']:
                    print(f"Build {next_build_number} is still running...")
                    time.sleep(10)  # Đợi một khoảng thời gian trước khi kiểm tra lại
                else:
                    print(f"Build {next_build_number} finished with status: {build_info['result']}")
                    break

            jenkins.delete_job(job_name)
            print(f"Job {job_name} deleted.")

            return f'wowai/{job_name}'

    except Exception as e:
        return False

def handle_deploy_model(
    self,
    compute,
    model,
    project_id,
    gpus_index,
    gpu_id,
    _model,
    ml,
    ml_gpu,
    docker_image=None,
    ml_network_id = None,
    checkpoint = None,
    num_scale = None,
    info_run=None,
    user=None
):
    try:
        if docker_image is None:
            docker_image = _model.docker_image
        link_deploy = None
        from projects.models import Project
        from compute_marketplace.models import ComputeGPU
        from datetime import datetime
        project = Project.objects.filter(id=project_id).first()

        if project: # and project.flow_type == Project.FlowType.DEPLOY:
            ml.is_deploy = True
            checkpoint_id = _model.checkpoint_storage_id if _model.checkpoint_storage_id else None
            now = datetime.now()
            date_str = now.strftime("%Y%m%d")
            time_str = now.strftime("%H%M%S")
            
            version = f'{date_str}-{time_str}'
            History_Build_And_Deploy_Model.objects.create(
                    version = version,
                    model_id = _model.pk,
                    checkpoint_id = checkpoint_id,
                    project_id = project_id,
                    user_id = user.id,
                    type = History_Build_And_Deploy_Model.TYPE.DEPLOY
                )
            ml.save()

            if "Origin" in self.request.headers and self.request.headers["Origin"]:
                host_name = self.request.headers["Origin"]
            elif "Host" in self.request.headers:
                host_name = self.request.headers["Host"]
            else:
                host_name = "https://app.aixblock.io/"

            link_deploy = f'{host_name}/{project.flow_type}/{project.id}/demo-and-deploy'
        # Initialize schema variable
        schema = "http"
        tensorboard_endpoint = 6060
        ddp_endpoint = 9090

        if compute.type == "MODEL-PROVIDER-VAST":
            compute_gpu = ComputeGPU.objects.filter(compute_marketplace_id=compute.id, deleted_at__isnull=True).order_by("-id").first()
            try:
                disk_size = compute_gpu.disk
            except:
                disk_size = 40

            schema = "https"
            if info_run and "ssl_used" in info_run and info_run["ssl_used"]==False:
                schema = "http"

            if info_run and "grpc_used" in info_run and info_run["grpc_used"]==True:
                schema = "grpc"
            # vast_service.delete_instance_info(compute.infrastructure_id)
            vast_provider.delete_compute(compute.infrastructure_id)
            # status_install, response = vast_service.func_install_compute_vastai(
            #     compute.infrastructure_desc,
            #     docker_image,
            #     "ml",
            # )
            status_install, response, _ = vast_provider.func_install_compute_vastai(
                compute.infrastructure_desc,
                docker_image,
                "ml",
                info_run=info_run,
                disk_size=disk_size
            )
            if not status_install:
                return Response(
                    {"detail": f"Not available, please try again"}, status=400
                )
            # print(response["instances"]["ports"]["9090/tcp"][0]["HostPort"])
            try:
                _port_info = int(info_run["exposed_ports"][0])
                _port = response["instances"]["ports"][f"{_port_info}/tcp"][0]["HostPort"]
            except:
                _port = response["instances"]["ports"]["9090/tcp"][0]["HostPort"]

            compute.infrastructure_id = response["instances"]["id"]
            compute.infrastructure_desc = response["instances"]["old_id"]
            compute.port = _port
            _model.schema = schema

            if info_run:
                _model.info_run = info_run

            compute.save()
            _model.port = _port
            _model.save()

        elif compute.type == "MODEL-PROVIDER-EXABIT":
            schema = "https"
            if info_run and "ssl_used" in info_run and info_run["ssl_used"]==False:
                schema = "http"

            if info_run and "grpc_used" in info_run and info_run["grpc_used"]==True:
                schema = "grpc"

            status_install, response, errors = exabit_provider.install_compute(compute.infrastructure_id, docker_image, 'ml', install_check=True)
            if not status_install:
                return Response(
                    {"detail": f"Not available, please try again"}, status=400
                )
            # print(response["instances"]["ports"]["9090/tcp"][0]["HostPort"])
            try:
                _port_info = int(info_run["exposed_ports"][0])
                _port = response["data"]["ports"][f"{_port_info}"]
            except:
                _port = response["data"]["ports"]["9090"]
                
            compute.port = _port
            compute.save()
            _model.schema = schema
            if info_run:
                _model.info_run = info_run
            _model.port = _port
            _model.save()

        else:
            _port = createDocker(
                docker_image,
                project_id,
                f"tcp://{compute.ip_address}:{compute.docker_port}",
                model.port,
                _model.pk,
                str(gpus_index),
                str(gpu_id),
            )
            _model.port = _port
            _model.schema = schema
            if info_run:
                _model.info_run = info_run
            _model.save()

        ml_gpu = MLGPU.objects.filter(id=ml_gpu.id).first()
        ml_gpu.port = _port
        ml_gpu.save()
        ml = MLBackend.objects.filter(id=ml.id).first()
        ml.url = f"{schema}://{compute.ip_address}:{_port}"
        ml.install_status = MLBackend.INSTALL_STATUS.COMPLEATED
        ml.state = MLBackendState.CONNECTED
        ml.save()

        from plugins.plugin_centrifuge import publish_message
        from core.settings.base import MAIL_SERVER
        from aixblock_core.users.service_notify import send_email_thread
        # publish_message(
        #     channel=f'project/{project_id}/deploy-history', data={"refresh": True}, prefix=True
        # )

        def send_mail_rent_compute(email, compute, model_endpoint, tensorboard, ddp_endpoint, schema, link_deploy):
            try:
                html_file_path =  './templates/mail/install_model_success.html'
                with open(html_file_path, 'r', encoding='utf-8') as file:
                    html_content = file.read()

                html_content = html_content.replace('[user]', f'{email}')
                # html_content = html_content.replace('xxx', f'{compute.id}')
                if link_deploy:
                    html_content = html_content.replace('[link]', link_deploy)
                else:
                    html_content = html_content.replace('[link]', f'https://{compute.ip_address}:{model_endpoint}')

                if "grpc" in schema:
                    print("grpc")
                    # html_content = html_content.replace(
                    #     '[link]',
                    #     f'grpc://{compute.ip_address}:{model_endpoint}. Please verify it yourself as we do not perform grpc checks.'
                    # )
                else:   
                    verify_ssl = False  # Đặt True nếu muốn kiểm tra chứng chỉ SSL
                    import time

                    # Khoảng thời gian giữa các lần thử (giây)
                    retry_interval = 120
                    send_mail_wait = False

                    # Vòng lặp gọi API
                    while True:
                        try:
                            response = requests.get(f"https://{compute.ip_address}:{model_endpoint}", verify=verify_ssl)
                            if response.status_code == 200:  # Điều kiện thành công
                                print("API call successful!")
                                print("Response Body:", response.json())
                                break  # Thoát khỏi vòng lặp nếu thành công
                            else:
                                print(f"Received status code: {response.status_code}. Retrying...")
                        except requests.exceptions.RequestException as e:
                            print(f"Error during API call: {e}. Retrying...")
                        
                            # if not send_mail_wait:
                            #     html_file_path =  './templates/mail/wait_install_checkpoint.html'
                            #     data = {
                            #         "subject": "AIxBlock | Checkpoint Loading Notification",
                            #         "from": "noreply@aixblock.io",
                            #         "to": [f'{email}'],
                            #         "html": html_content,
                            #         "text": "Welcome to AIxBlock!",
                            #         "attachments": []
                            #     }

                            #     docket_api = "tcp://69.197.168.145:4243"
                            #     host_name = MAIL_SERVER

                            #     email_thread = threading.Thread(target=send_email_thread, args=(docket_api, host_name, data,))
                            #     email_thread.start()
                            #     send_mail_wait = True
                        # Chờ trước khi thử lại
                        time.sleep(retry_interval)
                        
                data = {
                    "subject": "AIxBlock | Successful Model Installation",
                    "from": "noreply@aixblock.io",
                    "to": [f'{email}'],
                    "html": html_content,
                    "text": "Welcome to AIxBlock!",
                    "attachments": []
                }

                docket_api = "tcp://69.197.168.145:4243"
                host_name = MAIL_SERVER

                email_thread = threading.Thread(target=send_email_thread, args=(docket_api, host_name, data,))
                email_thread.start()
            except:
                pass
        
        if MLBackend.objects.filter(id=ml.id, deleted_at__isnull=False).exists():
            return
        
        if user:
            send_mail_rent_compute(user.email, compute, _model.port, tensorboard_endpoint, ddp_endpoint, _model.schema, link_deploy)

        notify_for_compute(self.request.user.uuid, "Success", "The model has been successfully installed")
        from plugins.plugin_centrifuge import publish_message
        publish_message(
            channel=f'project/{project_id}/deploy-history', data={"refresh": True}, prefix=True
        )
        # from ml.functions import auto_ml_nodes
        # # run auto select master, join master
        # if ml_network_id:
        #     auto_ml_nodes(self, project_id, ml_network_id)
        return

    except Exception as e:
        print(e)
        notify_for_compute(self.request.user.uuid, "Danger", "The model installation has failed.")
        ml.install_status = MLBackend.INSTALL_STATUS.FAILED
        ml.state = MLBackendState.ERROR
        ml.save()

def gen_ml_hf_source(url, name):
    from aixblock_ml.server import create_dir
    import io
    import zipfile
    import uuid
    import shutil
    
    # Bước 1: Tạo thư mục tạm thời 'template'
    template_dir = os.path.join(os.getcwd(), f'template_{uuid.uuid4()}')
    
    if not os.path.exists(template_dir):
        os.makedirs(template_dir)
    
    # Bước 2: Tạo đường dẫn dự án bên trong thư mục 'template'
    project_dir = os.path.join(template_dir, name)
    
    # Tạo đối tượng `args` để truyền vào hàm `create_dir`
    class Args:
        def __init__(self, root_dir, project_name, script=None, force=False):
            self.root_dir = root_dir
            self.project_name = project_name
            self.script = script
            self.force = force
    
    args = Args(root_dir=template_dir, project_name=name, force=True)
    
    # Bước 3: Gọi hàm `create_dir` từ `aixblock_ml.server` để tạo dự án
    try:
        create_dir(args)
    except SystemExit as e:
        # Bắt nếu `create_dir` gọi sys.exit() hoặc exit()
        print(f"SystemExit caught: {e}")
    # Bước 4: Nén thư mục dự án thành một tệp .zip
    zip_buffer = io.BytesIO()  # Sử dụng BytesIO để lưu trữ nội dung zip trong bộ nhớ
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(project_dir):
            for file in files:
                filepath = os.path.join(root, file)
                # Thêm file vào zip với đường dẫn tương đối
                zipf.write(filepath, os.path.relpath(filepath, project_dir))
    
    # Di chuyển con trỏ của zip_buffer về đầu
    zip_buffer.seek(0)
    shutil.rmtree(template_dir)
    
    # Bước 5: Giả lập quá trình xử lý như thể file được tải lên trong request.FILES
    file_like_object = io.BytesIO(zip_buffer.read())  # Đây là file bạn có thể sử dụng giống như request.FILES
    file_like_object.name = f"{name}.zip"  # Thiết lập tên cho file
    
    return file_like_object

from urllib.parse import urlparse

import torch
from accelerate.commands.estimate import check_has_model, create_empty_model, estimate_training_usage
from accelerate.utils import calculate_maximum_sizes, convert_bytes
from huggingface_hub.utils import GatedRepoError, RepositoryNotFoundError


DTYPE_MODIFIER = {"float32": 1, "float16/bfloat16": 2, "int8": 4, "int4": 8}


def extract_from_url(name: str):
    "Checks if `name` is a URL, and if so converts it to a model name"
    is_url = False
    try:
        result = urlparse(name)
        is_url = all([result.scheme, result.netloc])
    except Exception:
        is_url = False
    # Pass through if not a URL
    if not is_url:
        return name
    else:
        path = result.path
        return path[1:]


def translate_llama(text):
    "Translates Llama-2 and CodeLlama to its hf counterpart"
    if not text.endswith("-hf"):
        return text + "-hf"
    return text


def get_model(model_name: str, library: str, access_token: str):
    "Finds and grabs model from the Hub, and initializes on `meta`"
    if "meta-llama/Llama-2-" in model_name or "meta-llama/CodeLlama-" in model_name:
        model_name = translate_llama(model_name)
    if library == "auto":
        library = None
    model_name = extract_from_url(model_name)
    try:
        model = create_empty_model(model_name, library_name=library, trust_remote_code=True, access_token=access_token)
    except GatedRepoError:
        error = f"Model `{model_name}` is a gated model, please ensure to pass in your access token and try again if you have access. You can find your access token here : https://huggingface.co/settings/tokens. "
        return error
    
    except RepositoryNotFoundError:
        error = f"Model `{model_name}` was not found on the Hub, please try another model name."
    except ValueError:
        error = f"Model `{model_name}` does not have any library metadata on the Hub, please manually select a library_name to use (such as `transformers`)"

    except (RuntimeError, OSError) as e:
        library = check_has_model(e)
        if library != "unknown":
            error = f"Tried to load `{model_name}` with `{library}` but a possible model to load was not found inside the repo."
            return error

        error = f"Model `{model_name}` had an error, please open a discussion on the model's page with the error message and name: `{e}`"

        return error
    except ImportError:
        # hacky way to check if it works with `trust_remote_code=False`
        model = create_empty_model(
            model_name, library_name=library, trust_remote_code=True, access_token=access_token
        )
    except Exception as e:
        error = f"Model `{model_name}` had an error, please open a discussion on the model's page with the error message and name: `{e}`"
        return error
    
    return model


def calculate_memory(model: torch.nn.Module, options: list):
    "Calculates the memory usage for a model init on `meta` device, output in GB"
    total_size, largest_layer = calculate_maximum_sizes(model)

    data = []
    for dtype in options:
        dtype_total_size = total_size
        dtype_largest_layer = largest_layer[0]
        
        try:
            modifier = DTYPE_MODIFIER[dtype]
        except KeyError:
            modifier = 2

        dtype_training_size = estimate_training_usage(
            dtype_total_size, dtype if dtype != "float16/bfloat16" else "float16"
        )
        dtype_total_size /= modifier
        dtype_largest_layer /= modifier

        # Chuyển đổi sang GB
        dtype_total_size_gb = dtype_total_size / 1_073_741_824  # 1 GB = 1_073_741_824 bytes
        dtype_largest_layer_gb = dtype_largest_layer / 1_073_741_824
        # Trích xuất dữ liệu bên trong key "Training using Adam (Peak vRAM)"

        # Chuyển đổi từng giá trị sang GB
        dtype_training_size_gb = {
            key: value / 1_073_741_824 for key, value in dtype_training_size.items()
        }

        data.append(
            {
                "dtype": dtype,
                "Largest Layer or Residual Group (GB)": dtype_largest_layer_gb,
                "Infer": dtype_total_size_gb, #Total size
                "Training": dtype_training_size_gb, #Training using Adam (Peak vRAM in GB)
            }
        )

    # return data
    return data