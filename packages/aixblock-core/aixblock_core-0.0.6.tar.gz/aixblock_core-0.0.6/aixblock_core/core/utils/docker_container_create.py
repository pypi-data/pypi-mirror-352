from rest_framework.response import Response
import docker
import random
import os
from rest_framework.exceptions import ValidationError as RestValidationError

HOSTNAME = os.environ.get('HOST', 'https://app.aixblock.io/')
API_KEY = os.environ.get('API_KEY', 'fb5b650c7b92ddb5150b7965b58ba3854c87d94b')
IN_DOCKER = bool(os.environ.get('IN_DOCKER', True))
DOCKER_API = "tcp://108.181.196.144:4243" if IN_DOCKER else "unix://var/run/docker.sock"
NUM_GPUS = int(os.environ.get('NUM_GPUS', 1))
TOTAL_CONTAINERS = int(os.environ.get('TOTAL_CONTAINERS', 50))
IMAGE_TO_SERVICE = {
    'huggingface_image_classification': 'computer_vision/image_classification',
    'huggingface_text_classification': 'nlp/text_classification',
    'huggingface_text2text': 'nlp/text2text',
    'huggingface_text_summarization': 'nlp/text_summarization',
    'huggingface_question_answering': 'nlp/question_answering',
    'huggingface_token_classification': 'nlp/token_classification',
    'huggingface_translation': 'nlp/translation',
}

# docker image, project id, docker url, model port, model id, gpus index, gpus id
def createDocker(base_image, pk, url,port, modelPk, gpus_index_str = None, gpus_id_str = None, checkpoint=None):
    client = docker.DockerClient(base_url=url)
    # team_id = self.request.user.team_id
    # get service string from POST request data

    service = base_image
    print(url)
    # container_name = f"project-{self.kwargs['pk']}_{service.replace('/', '-').replace(':', '-')}"
    if service != None:
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
        random_id = ''.join(random.choice(chars) for _ in range(8))
        container_name = f"project-{pk}_{modelPk}_{service.replace('/', '-').replace(':', '-')}_{random_id}"
    else:
        container_name = f"project-{pk}_{modelPk}"

    # gpu_id = 0
    # list all docker containers contains GPU_ID in name
    # gpus = [i for i in range(NUM_GPUS)]
    # random.shuffle(gpus)
    gpu_index = '0'
    gpus_index_arr = []
    gpus_id = []

    if isinstance(gpus_index_str, list):
        gpus_index_arr = gpus_index_str
    else: 
        gpus_index_arr = gpus_index_str.split(',')
    if isinstance(gpus_id_str, list):
        gpus_id = gpus_id_str
    else:
        gpus_id = gpus_id_str.split(',')
    for i, value in enumerate(gpus_id):
        gpu_containers = client.containers.list(filters={'name': f"*GPU{value}*"})
        if len(gpu_containers) >= TOTAL_CONTAINERS:
            # exceed max container for this GPU
            continue
        # assign GPU_ID to container name
        container_name += f"_GPU{value}"
        gpu_index = gpus_index_arr[i]
        # gpu_id = i
        break
    # check if container name is already exists
    # try:
    # create container from service
    # for training only
    info= client.info()

    device_requests = []
    if 'GenericResources' in info:
        # print(info['GenericResources'])
        if info['GenericResources'] != None:
            device_requests.append(docker.types.DeviceRequest(device_ids=[gpu_index], capabilities=[['gpu']]))

    if service != None:
        containers =client.containers.list(filters={'name': f"project-{pk}_{modelPk}_{service.replace('/', '-').replace(':', '-')}"}, all=True)
    else:
        containers = client.containers.list(
            filters={'name': f"project-{pk}_{modelPk}"}, all=True)
    # print(info)
    # device_requests=[]
    if len(containers) > 0:
        for container in containers:
            try:
                port=None
            except Exception as e:
                print(e)
    images = client.images.list(filters={'reference': service}, all=True)
    if len(images) > 0:
        tag=images[0]
        try:
            client.images.remove(image=tag, force=True)
        except Exception as e:
            print(e)
    client.api.pull(service, stream=True, decode=True)
    print(device_requests)
    print('port', port)
    print(port)
    print(service)
    print(container_name)

    def check_port_in_use(client, port):
        containers = client.containers.list()
        for container in containers:
            container_ports = container.attrs['NetworkSettings']['Ports']
            print(container_ports)
            if container_ports and f'{port}/tcp' or f'{port}' in container_ports:
                return True
        return False

    if check_port_in_use(client, port):
        port = None

    print(port)
    container = client.containers.run(
        service,
        detach=True,
        name=container_name,
        device_requests=device_requests,
        # [
        #     # docker.types.DeviceRequest(device_ids=[','.join(list_index)], capabilities=[['gpu']])
        #     docker.types.DeviceRequest(device_ids=['0'], capabilities=[['gpu']])
        # ],
        ports={
            "9090/tcp": port,
            "6006/tcp": None,
        },
        environment={
            "IN_DOCKER": "True",
            "HOST": f"{HOSTNAME}",
            "API_KEY": f"{API_KEY}",
            "REDIS_HOST": "redis",
            "REDIS_PORT": 6379,
            "CHECKPOINT_URL": checkpoint
        },
        volumes={
            "/data/ml-backend/data/": {
                "bind": "/data",
                "mode": "Z",
            },
            "/data/models": {
                "bind": "/models",
                "mode": "Z",
            },
            "/data/datasets": {
                "bind": "/datasets",
                "mode": "Z",
            },
        },
    )
    container.reload() # need to reload
    container.exec_run("docker login --username 'quoiwowai' --password-stdin 'Abc!23456'")
    print(container.ports['9090/tcp'][0]['HostPort'])
    # Check if GPU have available memory for this container
    # Example: Each GPU has 24GB can host max 10 containers
    # Each team can have 1 dataset and 1 container, members should use the same container
    # Export specific port for each container
    client.close()
    return container.ports['9090/tcp'][0]['HostPort']
    # except Exception as e:
    #     print(e)
    # client.close()
    # return ""# Response(f"Container {container_name} already exists", status=400)


def createDockerDeploy(base_image, pk, url, port, modelPk, gpus_index_str = None, gpus_id_str = None, checkpoint=None, num_scale=None):
    client = docker.DockerClient(base_url=url)

    import subprocess

    

    service = base_image
   
    # if service != None:
    #     chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
    #     random_id = ''.join(random.choice(chars) for _ in range(8))
    #     container_name = f"project-{pk}_{modelPk}_{random_id}"
    # else:
    service_name = f"project-{pk}_{modelPk}"

    gpu_index = '0'
    gpus_index_arr = []
    gpus_id = []

    scale_rep = 1
    if num_scale:
        scale_rep = num_scale

    if isinstance(gpus_index_str, list):
        gpus_index_arr = gpus_index_str
    else: 
        gpus_index_arr = gpus_index_str.split(',')
    if isinstance(gpus_id_str, list):
        gpus_id = gpus_id_str
    else:
        gpus_id = gpus_id_str.split(',')
    for i, value in enumerate(gpus_id):
        gpu_containers = client.containers.list(filters={'name': f"*GPU{value}*"})
        if len(gpu_containers) >= TOTAL_CONTAINERS:
            # exceed max container for this GPU
            continue
        # assign GPU_ID to container name
        service_name += f"_GPU{value}"
        gpu_index = gpus_index_arr[i]
        # gpu_id = i
        break

    info= client.info()

    device_requests = []
    if 'GenericResources' in info:
        # print(info['GenericResources'])
        if info['GenericResources'] != None:
            device_requests.append(docker.types.DeviceRequest(device_ids=[gpu_index], capabilities=[['gpu']]))

    # if service != None:
    #     containers =client.containers.list(filters={'name': f"project-{pk}_{modelPk}_{service.replace('/', '-').replace(':', '-')}"}, all=True)
    # else:
    services = client.services.list(
        filters={'name': service_name})

    if len(services) > 0:
        for ser in services:
            try:
                port=None
                ser.remove()
            except Exception as e:
                print(e)

    images = client.images.list(filters={'reference': service}, all=True)
    if len(images) > 0:
        tag=images[0]
        try:
            client.images.remove(tag.id, force=True)
        except Exception as e:
            print(e)

    # client.api.pull(service, stream=True, decode=True)
    client.api.pull(service)

    def check_port_in_use(client, port):
        containers = client.containers.list()
        for container in containers:
            container_ports = container.attrs['NetworkSettings']['Ports']
            print(container_ports)
            if container_ports and f'{port}/tcp' or f'{port}' in container_ports:
                return True
        return False

    def docker_pull(client, image):
        try:
            images = client.images.list(filters={'reference': image}, all=True)
            if len(images) > 0:
                tag=images[0]
                try:
                    client.images.remove(tag.id, force=True)
                except Exception as e:
                    print(e)

            client.api.pull(image)
    
        except Exception as e:
            print(e)

    if check_port_in_use(client, port):
        port = None

    print(port)
    
    def init_swarm():
        try:
            client.swarm.init()
            print("Swarm đã được khởi tạo.")
        except docker.errors.APIError as e:
            print(e)

    import socket
    
    def deploy_stack(yml_file, stack_name, remote_base_url):
        # Tạo lệnh docker stack deploy
        command = f'DOCKER_HOST={remote_base_url} docker stack deploy -c {yml_file} {stack_name}'
        try:
            result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("Stack deployed successfully:", result.stdout.decode())
        except subprocess.CalledProcessError as e:
            print("Error deploying stack:", e.stderr.decode())

    docker_pull(client, "jcwimer/docker-swarm-autoscaler")
    docker_pull(client, "prom/prometheus")
    docker_pull(client, "google/cadvisor")

    deploy_stack('./aixblock_core/templates/auto_scale_config/swarm-autoscaler-stack.yml', 'autoscaler', url)

    # def find_free_port():
    #     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    #         sock.bind(('', 0))  # Bind to a free port
    #         return sock.getsockname()[1]  # Get the port number

    def create_random_port_container(client):
        # Tạo một container với cổng ngẫu nhiên (sử dụng image nginx)
        container = client.containers.run("nginx", detach=True, ports={'80/tcp': None})
        container.reload()

        # Lấy thông tin cổng đã gán cho container
        port_info = container.ports
        random_port = None

        # Tìm cổng được gán
        for port in port_info:
            if port_info[port]:
                random_port = port_info[port][0]['HostPort']
                break

        # Xóa container
        container.stop()
        container.remove()

        return random_port
    
    try:
        published_port_9090 = create_random_port_container(client)
        published_port_6006 = create_random_port_container(client)
    except Exception as e:
        published_port_9090 = 11111
        published_port_6006 = 22222
    
    # 2. Tạo dịch vụ trong Docker Swarm
    def create_service(service, container_name):
        service = client.services.create(
            image=service,  # Tên hoặc ID của image bạn muốn sử dụng
            name=container_name,
            mode={"Replicated": {"Replicas": 1}},  # Số lượng replicas
            endpoint_spec={
                "ports": [
                    {"Protocol": "tcp", "PublishedPort": published_port_9090, "TargetPort": 9090},
                    {"Protocol": "tcp", "PublishedPort": published_port_6006, "TargetPort": 6006},
                ]
            },
            env=[
                "IN_DOCKER=True",
                f"HOST={HOSTNAME}",
                f"API_KEY={API_KEY}",
                "REDIS_HOST=redis",
                "REDIS_PORT=6379",
            ],
            labels={
                "swarm.autoscale": "true",  
                "swarm.autoscale.min": "1", 
                "swarm.autoscale.max": str(scale_rep)
            },
            resources={
                "limits": {
                    "cpus": "0.50",  
                    "memory": "512M"
                }
            }
        )

        # Nếu bạn cần xem trạng thái của service
        print(f"Service {service.id} đã được tạo.")
        return service

    init_swarm()
    service = create_service(service, service_name)
    service_info = service.attrs

    ports = service_info['Endpoint'].get('Ports', [])
    
    # Lọc và lấy các PublishedPort
    published_ports = [port['PublishedPort'] for port in ports if 'PublishedPort' in port and port['TargetPort']==9090]

    return published_ports[0]


