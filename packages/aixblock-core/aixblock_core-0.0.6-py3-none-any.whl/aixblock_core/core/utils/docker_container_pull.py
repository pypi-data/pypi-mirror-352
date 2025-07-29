import docker
import time
import threading
import requests
from datetime import datetime
from aixblock_core.core.utils.params import get_env
from configs.models import InstallationService
from django.conf import settings
from core.settings.base import AIXBLOCK_IMAGE_VERSION, ENVIRONMENT, AIXBLOCK_IMAGE_NAME,AXB_PUBLIC_SSL_PORT
import os
from users.models import User
import asyncio
import docker
from concurrent.futures import ThreadPoolExecutor

from compute_marketplace.vastai_func import generate_password


def login_docker(ip_address):
    client = docker.DockerClient(base_url=f"tcp://{ip_address}:4243")
    client.login(username="quoiwowai", password="Abc!23456")
    return client


def get_env(key, default):
    return os.getenv(key, default)


def create_network(client, network_name):
    try:
        network = client.networks.get(network_name)
        
    except docker.errors.NotFound:
        network = client.networks.create(network_name)
    return network


def remove_container(client, name):
    containers = client.containers.list(filters={"name": name}, all=True)
    if containers:
        container = containers[0]
        try:
            container.stop()
            container.remove()
        except Exception as e:
            print(e)


def remove_image(client, reference):
    images = client.images.list(filters={"reference": reference}, all=True)
    if images:
        tag = images[0]
        try:
            client.images.remove(image=tag, force=True)
        except Exception as e:
            print(e)


def pull_image(client, image):
    try:
        print(f"Pulling image {image}...")
        response = client.api.pull(image, stream=True, decode=True)
        for line in response:
            print(line)
        print(f"Image {image} pulled successfully.")
    except Exception as e:
        print(f"Error pulling image {image}: {e}")


def pull_images(client):
    images = [
        'wowai/segment_anything_beta:latest',
        'wowai/llama_meta_2:latest',
        'wowai/falcon7b:latest',
        'wowai/seamless_m4t:latest'
    ]
    for image in images:
        client.api.pull(image, stream=True, decode=True)

def run_commands_in_thread(container):
    try:
        container.exec_run('python3 aixblock_core/manage.py default --created_by_id 1 --status create ')
        container.exec_run('python3 aixblock_core/manage.py create_superuser_with_password --email admin@wow-ai.com --username admin --password 123321 --noinput' )
        container.exec_run('python3 aixblock_core/manage.py create_organization The_title_of_the_organization')
        container.exec_run('python3 aixblock_core/manage.py seed_templates')
    except Exception as e:
        print(e)

def get_latest_platform_version(image_name):
    url = f"https://registry.hub.docker.com/v2/repositories/{image_name}/tags/"
    response = requests.get(url)
    latest_version = "latest"

    if response.status_code == 200:
        data = response.json()
        tags = data["results"]
        sorted_tags = sorted(tags, key=lambda x: x["last_updated"], reverse=True)
        latest_version = sorted_tags[0]

    return latest_version

def pull_lastest_images(client, images, latest_images, image_name):
    if convert_to_datetime(latest_images["last_updated"]) > convert_to_datetime(images.attrs['Created']):
        try:
            client.images.remove(image=images.id, force=True)
        except Exception as e:
            print(e)

        client.api.pull(image_name, stream=True, decode=True)

def convert_to_datetime(date_str):
    return datetime.strptime(date_str.split('.')[0], '%Y-%m-%dT%H:%M:%S').date()

def container_watchtower(client):
    images = client.images.list(filters={'reference': f"containrrr/watchtower"}, all=True)
    if len(images) < 1:
        client.api.pull('containrrr/watchtower:latest-dev', stream=True, decode=True)

    containers =client.containers.list(filters={'name': f"watchtower"}, all=True)
    if len(containers) < 1:
        client.containers.run(
            'containrrr/watchtower',  
            ports={'5080/tcp': None},
            detach=True,              
            name='watchtower',        
            volumes={'/var/run/docker.sock': {'bind': '/var/run/docker.sock', 'mode': 'rw'}}
        )


def install_mqtt(client, network):
    images = client.images.list(filters={"reference": "eclipse-mosquitto"}, all=True)
    if len(images) == 0:
        client.api.pull("eclipse-mosquitto:latest", stream=True, decode=True)

    containers = client.containers.list(filters={"name": "mqtt-server"}, all=True)
    if len(containers) == 0:
        container = client.containers.run(
            "eclipse-mosquitto:latest",
            detach=True,
            name=f"mqtt-server-{network}",
            ports={
                "1883/tcp": None,
            },
            environment={
                "NO_AUTHENTICATION":1 
            },
            volumes={
            }
        )
        container.reload()
        ports = container.attrs["NetworkSettings"]["Ports"]
        mqtt_port = ports["1883/tcp"][0]["HostPort"]
        return mqtt_port
    else:
        container = containers[0]
        container.reload()
        ports = container.attrs["NetworkSettings"]["Ports"]
        mqtt_port = ports["1883/tcp"][0]["HostPort"]
        return mqtt_port


def install_jupyter_notebook_live(client):
    images = client.images.list(filters={'reference': f"wowai/jupyter_notebook_live"}, all=True)
    latest_version = get_latest_platform_version("jupyter_notebook_live")
    if latest_version:
        pull_lastest_images(client, images, latest_version, "wowai/jupyter_notebook_live")

def install_jupyterhub_notebook_live(client, network_name):
    container_name = f"aixblock-jupyterhub-notebook-live-{network_name}"
    images = client.images.list(filters={'reference': f"wowai/jupyter_notebook_live"}, all=True)

    # latest_version = get_latest_platform_version("wowai/jupyter_notebook_live")
    # if latest_version:
    pull_image(client,"wowai/jupyter_notebook_live:latest")
    info = client.info()
    list_index = []
    if "GenericResources" in info:
        if len(info['GenericResources'])>0 :
            for i, _ in info['GenericResources']:
                list_index.append(i)

    container = client.containers.run(
        "wowai/jupyter_notebook_live:latest",
        detach=True,
        name=container_name,
        device_requests=[
            docker.types.DeviceRequest(
                device_ids=[",".join(list_index)], capabilities=[["gpu"]]
            )
        ],
        ports={
            "8100/tcp": None,
        },
        environment={
                "OAUTH2_AUTHORIZE_URL":get_env("JP_OAUTH2_AUTHORIZE_URL","https://stag.aixblock.io/o/authorize"),
                "OAUTH2_TOKEN_URL":get_env("JP_OAUTH2_TOKEN_URL","https://stag.aixblock.io/o/token"),
                "OAUTH2_CALLBACK_URL":get_env("JP_OAUTH2_CALLBACK_URL","https://jupyter.aixblock.io/hub/oauth_callback"),
                "OAUTH2_CLIENT_ID":get_env("JP_OAUTH2_CLIENT_ID","rbwA5vN0Y24kbN3qPgDO7QvimI7FKrDcNuVWr6ow"),
                "OAUTH2_CLIENT_SECRET":get_env("JP_OAUTH2_CLIENT_SECRET","JR0stF65QRawRpgHxFjHrFgNzfXII0eBp1E4yQ82BmNzIFZvHaX2Wct8A7nmr4iMM3pgurDzcJRrbnHa5xp4XmiUzWsRoLAvp7qcVJ3AvhSs5fJUojosbJfA0Kdjsu1n")
        },
        volumes={},
        network=network_name,
    )

    public_port = container.attrs['NetworkSettings']['Ports']['8100/tcp'][0]['HostPort']
    return public_port

    # return None

def install_crawling_server(client):
    images = client.images.list(filters={'reference': f"wowai/crawl-server"}, all=True)
    if len(images) == 0:
        client.api.pull('wowai/crawl-server:latest', stream=True, decode=True)

    containers =client.containers.list(filters={'name': f"wowai-crawling_server"}, all=True)
    if len(containers) == 0:
        info= client.info()
        list_index = []
        if "GenericResources" in info:
            if len(info['GenericResources'])>0 :
                for i, _ in info['GenericResources']:
                    list_index.append(i)

        client.containers.run(
            "wowai/crawl-server:latest",
            detach=True,
            name=f"wowai-crawling_server",
            device_requests=[
                docker.types.DeviceRequest(device_ids=[','.join(list_index)], capabilities=[['gpu']])
                ],
            ports={
                '5000/tcp': None,
            },
            environment={
                "CRAWLING_SERVER":get_env("CRAWLING_SERVER","https://crawling.aixblock.io"),
                "HOST_NAME":get_env("HOST_NAME","https://dev.aixblock.io"),
                "REDIS_SERVER":get_env("REDIS_SERVER","172.17.0.1"),
                "REDIS_PORT":get_env("REDIS_PORT","6379")
            },
            volumes={
            }
        )

def install_calculator_server(client):
    images = client.images.list(filters={'reference': f"wowai/cost-calculator-server"}, all=True)
    if len(images) == 0:
        client.api.pull('wowai/cost-calculator-server:latest', stream=True, decode=True)

    containers = client.containers.list(filters={'name': f"wowai-cost-calculator_server"}, all=True)
    if len(containers) == 0:
        info= client.info()
        list_index = []
        if "GenericResources" in info:
            if len(info['GenericResources'])>0 :
                for i, _ in info['GenericResources']:
                    list_index.append(i)

        client.containers.run(
            "wowai/cost-calculator-server:latest",
            detach=True,
            name=f"wowai-cost-calculator_server",
            device_requests=[
                docker.types.DeviceRequest(device_ids=[','.join(list_index)], capabilities=[['gpu']])
                ],
            ports={
                '5000/tcp': None,
            },
            environment={
                "HOST_NAME":get_env("HOST_NAME","https://dev.aixblock.io"),
                "REDIS_SERVER":get_env("REDIS_SERVER","172.17.0.1"),
                "REDIS_PORT":get_env("REDIS_PORT","6379")
            },
            volumes={
            }
        )

def install_notification_server(client):
    images = client.images.list(filters={'reference': f"wowai/notification-server"}, all=True)
    if len(images) == 0:
        client.api.pull('wowai/notification-server:latest', stream=True, decode=True)

    containers =client.containers.list(filters={'name': f"wowai-notification_server"}, all=True)
    if len(containers) == 0:
        info= client.info()
        client.close()
        list_index = []
        if "GenericResources" in info:
            if len(info['GenericResources'])>0 :
                for i, _ in info['GenericResources']:
                    list_index.append(i)

        client.containers.run(
            "wowai/notification-server:latest",
            detach=True,
            name=f"wowai-notification_server",
            device_requests=[
                # docker.types.DeviceRequest(device_ids=[','.join(list_index)], capabilities=[['gpu']])
                ],
            ports={
                '5000/tcp': None,
            },
            environment={
                "email-host":get_env("EMAIL_HOST", "in-v3.mailjet.com"),
                "email-user":get_env("EMAIL_USER","9a58980cd5610c3cfe943b5e5a727884"),
                "email-pass":get_env("EMAIL_PASS","6541d392e063d45378fcd95e6f99f21e"),
                "email-port":get_env("EMAIL_PORT",587),
            },
            volumes={
            }
        )

def create_postgres_container(client, ip_address, network_name):
    container_name = f"aixblock-postgres-{network_name}"
    remove_container(client, container_name)
    remove_image(client, "docker.io/library/postgres")

    pull_image(client, "docker.io/library/postgres:latest")

    container = client.containers.run(
        "docker.io/library/postgres:latest",
        detach=True,
        name=container_name,
        ports={"5432/tcp": None},
        environment={
            "POSTGRES_PASSWORD": get_env("POSTGRES_PASSWORD", "@9^xwWA"),
            "POSTGRES_USER": get_env("POSTGRES_USER", "postgres"),
            "POSTGRES_NAME":get_env("POSTGRES_NAME", "platform_v2"),
        },
        network=network_name,
    )
    container.reload()
    time.sleep(10)
    create_database_command = "CREATE DATABASE JupyterHub;"
    create_database_response = container.exec_run(
        f'psql -v ON_ERROR_STOP=1 --username={get_env("POSTGRES_USER", "postgres")} -c "{create_database_command}"'
    )
    if create_database_response.exit_code == 0:
        print("Tạo cơ sở dữ liệu JupyterHub thành công.")
    else:
        command = f"psql -U {get_env('POSTGRES_USER', 'postgres')} -c 'CREATE DATABASE JupyterHub;'"
        exit_code, output = container.exec_run(command)

        if exit_code == 0:
            print("Cơ sở dữ liệu JupyterHub đã được tạo thành công.")
        else:
            print(
                f"Có lỗi xảy ra khi tạo cơ sở dữ liệu JupyterHub: {output.decode('utf-8')}"
            )

    # create_database_command = f'CREATE DATABASE {get_env("POSTGRES_NAME", "platform_v2")};'
    create_database_command = f'CREATE DATABASE platform_v2;'
    retry_attempts = 5
    retry_delay = 5  

    for attempt in range(1, retry_attempts + 1):
        create_database_response = container.exec_run(
            f'psql -v ON_ERROR_STOP=1 --username={get_env("POSTGRES_USER", "postgres")} -c "{create_database_command}"'
        )
        if create_database_response.exit_code == 0:
            print(f'Tạo cơ sở dữ liệu {get_env("POSTGRES_NAME", "platform_v2")} thành công.')
            break
        else:
            print(
                f"Lỗi khi tạo cơ sở dữ liệu platform_v2 (thử lần {attempt}/{retry_attempts}):",
                create_database_response.output.decode("utf-8"),
            )
            if attempt < retry_attempts:
                time.sleep(retry_delay)
            else:
                print("create db failed")
                return False
    public_port = container.attrs["NetworkSettings"]["Ports"]["5432/tcp"][0]["HostPort"]
    return public_port

def create_minio_container(client, network_name, user_id=None):
    container_name = f"aixblock-minio-{network_name}"

    remove_container(client, container_name)
    remove_image(client, "minio/minio")

    pull_image(client, "quay.io/minio/minio")
    if user_id is not None:
        user = User.objects.filter(id=user_id).first()
    minio_user_email = user.email if user and user.email else "admin@wow-ai.com"
    minio_user_username = user.username if user and user.username else "admin"
    minio_password = generate_password()

    container = client.containers.run(
        "quay.io/minio/minio",
        detach=True,
        name=container_name,
        ports={"9000/tcp": None, "9001/tcp": None},
        command=["server", "/data", "--console-address", ":9001"],
        environment={
            "MINIO_ROOT_USER": minio_user_username,  # "adminwow",
            "MINIO_ROOT_PASSWORD": minio_password,  # "wBTwZsUZWAj3gm4",
        },
        network=network_name,
    )
    container.exec_run(
        f'mc alias set myminio http://localhost:9000 oeqNGzCNEjw21q66jX6G ZCGAQuLnfEREvGQhGA2N6XbGCUNTNpQNkOvTruD7 --api "s3v4" --path "auto"'
    )

    create_database_response = container.exec_run(
        f'mc admin user add myminio {get_env("MINIO_ROOT_USER", minio_user_username)} {get_env("MINIO_ROOT_PASSWORD",minio_password)}'
    )
    container.reload()
    public_port = container.attrs["NetworkSettings"]["Ports"]["9001/tcp"][0]["HostPort"] #ui port
    api_port = container.attrs["NetworkSettings"]["Ports"]["9000/tcp"][0]["HostPort"] # api port
    return public_port, minio_user_username, minio_password, api_port

def create_ml_default(client, network_name, user_id=None, max_containers=1):
    container_name = f"aixblock-ml-{network_name}"

    remove_container(client, container_name)
    remove_image(client, "aixblock/template_ml")

    pull_image(client, "aixblock/template_ml")
    if user_id is not None:
        user = User.objects.filter(id=user_id).first()

    # container = client.containers.run(
    #     "aixblock/template_ml",
    #     detach=True,
    #     name=container_name,
    #     ports={"9090/tcp": 9090, "6006/tcp": 6006, "23456/tcp": 23456},
    #     command=["gunicorn", "--bind", ":9090", "--workers", "1", "--threads", "1", "--timeout", "0", "_wsgi:app", "--certfile=/app/cert.pem", "--keyfile=/app/privkey.pem"],
    #     environment={
    #         # "MINIO_ROOT_USER": minio_user_username,  # "adminwow",
    #         # "MINIO_ROOT_PASSWORD": minio_password,  # "wBTwZsUZWAj3gm4",
    #     },
    #     network=network_name,
    # )
    # container.exec_run(
    #     f'mc alias set myminio http://localhost:9000 oeqNGzCNEjw21q66jX6G ZCGAQuLnfEREvGQhGA2N6XbGCUNTNpQNkOvTruD7 --api "s3v4" --path "auto"'
    # )

    # create_database_response = container.exec_run(
    #     f'mc admin user add myminio {get_env("MINIO_ROOT_USER", minio_user_username)} {get_env("MINIO_ROOT_PASSWORD",minio_password)}'
    # )
    # container.reload()
    # public_port = container.attrs["NetworkSettings"]["Ports"]["9090/tcp"][0]["HostPort"] #api port
    # port_tensorboard = container.attrs["NetworkSettings"]["Ports"]["6006/tcp"][0]["HostPort"] #api port
    # port_train = container.attrs["NetworkSettings"]["Ports"]["23456/tcp"][0]["HostPort"] #api port
    # public_port = container.attrs["NetworkSettings"]["Ports"]["9001/tcp"][0]["HostPort"] # ui port

    try:
        published_port_9090 = create_random_port_container(client)
        published_port_6006 = create_random_port_container(client)
        published_port_23456 = create_random_port_container(client)
    except Exception as e:
        published_port_9090 = 9090
        published_port_6006 = 6006
        published_port_23456 = 23456

    container = client.services.create(
            image="aixblock/template_ml",  # Tên hoặc ID của image bạn muốn sử dụng
            name=container_name,
            mode={"Replicated": {"Replicas": 1}},  # Số lượng replicas
            endpoint_spec={
                "ports": [
                    {"Protocol": "tcp", "PublishedPort": published_port_9090, "TargetPort": 9090},
                    {"Protocol": "tcp", "PublishedPort": published_port_6006, "TargetPort": 6006},
                    {"Protocol": "tcp", "PublishedPort": published_port_23456, "TargetPort": 23456},
                ]
            },
            command=["gunicorn", "--bind", ":9090", "--workers", "1", "--threads", "1", "--timeout", "0", "_wsgi:app", "--certfile=/app/cert.pem", "--keyfile=/app/privkey.pem"],
            # network=network_name,
            labels={
                "swarm.autoscale": "true",  
                "swarm.autoscale.min": "1", 
                "swarm.autoscale.max": f'{max_containers}'
            },
            resources={
                "limits": {
                    "cpus": "0.50",  
                    "memory": "512M"
                }
            }
        )

    service_info = container.attrs
    ports = service_info['Endpoint'].get('Ports', [])
    
    # Lọc và lấy các PublishedPort
    public_port = next((port['PublishedPort'] for port in ports if 'PublishedPort' in port and port['TargetPort'] == 9090), None)
    port_tensorboard = next((port['PublishedPort'] for port in ports if 'PublishedPort' in port and port['TargetPort'] == 6006), None)
    port_train = next((port['PublishedPort'] for port in ports if 'PublishedPort' in port and port['TargetPort'] == 23456), None)

    return public_port, port_tensorboard, port_train

def create_platform_container(
    client, ip_address, client_id, client_secret, token, network_name, postgres_port , minio_user, minio_password,minio_port, user_id = None, max_containers=1
):
    # mqtt_port = install_mqtt(client, network_name)
    import uuid
    short_uuid = str(uuid.uuid4())[:4]
    container_name = f"aixblock-platform-{network_name}-{short_uuid}"
    remove_container(client, container_name)

    # get from db
    service_install = InstallationService.objects.filter(
        image=get_env("AIXBLOCK_IMAGE_NAME", "aixblock/platform"),
        environment = ENVIRONMENT,
        deleted_at__isnull =True
    ).first()
    image = f"aixblock/platform:latest"

    if service_install:
        image = f"{service_install.image}:{service_install.version}"
    # image = f"{get_env('AIXBLOCK_IMAGE_NAME')}:{get_env('AIXBLOCK_IMAGE_VERSION')}"
    image = f"aixblock/platform:latest"
    pull_image(client, image)
    if user_id is not None:
        user = User.objects.filter(id=user_id).first()
    user_email = user.email if user and user.email else "admin@wow-ai.com"
    user_username = user.username if user and user.username else "admin"
    password = generate_password()
    env_dict = {
            "MQTT_INTERNAL_SERVER": "172.17.0.1",
            # "MQTT_PORT_TCP": mqtt_port,
            "MQTT_SERVER": "172.17.0.1",
            "AXB_PUBLIC_PORT": 8081,
            "POSTGRES_HOST": "172.17.0.1",
            "POSTGRES_PORT": postgres_port,
            "AXB_PUBLIC_SSL_PORT": 8081,
            "POSTGRES_PASSWORD": get_env("POSTGRES_PASSWORD", "@9^xwWA"),
            "POSTGRES_NAME": "platform_v2", #get_env("POSTGRES_NAME", "platform_v2"),
            "POSTGRES_USER": get_env("POSTGRES_USER", "postgres"),
            "ADMIN_EMAIL": user_email,
            "ADMIN_USERNAME": user_username,
            "ADMIN_PASSWORD": password,
            "OAUTH_CLIENT_ID": client_id,
            "OAUTH_CLIENT_SECRET": client_secret,
            "OAUTH_TOKEN_URL": "https://app.aixblock.io",
            "OAUTH_AUTHORIZE_URL": "https://app.aixblock.io/o/authorize",
            "OAUTH_API_BASE_URL": "https://app.aixblock.io",
            "OAUTH_REDIRECT_URL": f"http://{ip_address}:8081/oauth/login/callback",
            "MASTER_NODE": "https://app.aixblock.io",
            "MASTER_TOKEN": token,
            "NOTEBOOK_URL": f"http://{ip_address}:8100/",
            "NOTEBOOK_TOKEN": "639922e8a39e41e7add2d6ac4f45c314",
            "MINIO_API_URL": f"172.17.0.1:{minio_port}",
            "MINIO_USER": minio_user,
            "MINIO_PASSWORD": minio_password,
            "ASSETS_CDN": "",
            "SESSION_REDIS_PORT": 6379,
            "SESSION_REDIS_HOST": "172.17.0.1",
            "HOST_IP": f"{ip_address}",
            "INSTALL_TYPE": "SELF-HOST",
            "REVERSE_ADDRESS": settings.REVERSE_ADDRESS
        }
    
    if not postgres_port:
        env_dict["DJANGO_DB"] = "sqlite"

    # container = client.containers.run(
    #     image,
    #     detach=True,
    #     name=container_name,
    #     ports={"8081/tcp": None, "8080/tcp": None},  # e, "8443/tcp": None
    #     command="sh /aixblock/deploy/run-platform.sh",
    #     environment=env_dict,
    #     network=network_name,
    # )

    try:
        published_port_8081 = create_random_port_container(client)
        published_port_8080 = create_random_port_container(client)
    except Exception as e:
        published_port_8081 = 8081
        published_port_8080 = 8080

    container = client.services.create(
            image=image,  # Tên hoặc ID của image bạn muốn sử dụng
            name=container_name,
            mode={"Replicated": {"Replicas": 1}},  # Số lượng replicas
            endpoint_spec={
                "ports": [
                    {"Protocol": "tcp", "PublishedPort": published_port_8081, "TargetPort": 8081},
                    {"Protocol": "tcp", "PublishedPort": published_port_8080, "TargetPort": 8080},
                ]
            },
            env=env_dict,
            command="sh /aixblock/deploy/run-platform.sh",
            # network=network_name,
            labels={
                "swarm.autoscale": "true",  
                "swarm.autoscale.min": "1", 
                "swarm.autoscale.max": f'{max_containers}'
            },
            resources={
                "limits": {
                    "cpus": "0.50",  
                    "memory": "512M"
                }
            }
        )

    time.sleep(120) # wait 2 minus run platform
    # container.reload()
    # public_port = container.attrs["NetworkSettings"]["Ports"]["8081/tcp"][0]["HostPort"]
    service_info = container.attrs
    ports = service_info['Endpoint'].get('Ports', [])
    
    # Lọc và lấy các PublishedPort
    public_port = next((port['PublishedPort'] for port in ports if 'PublishedPort' in port and port['TargetPort'] == 8081), None)
    return public_port, user_email, password

def createModelTraining(
            client, ip_address, client_id, client_secret, token, network_name, postgres_port
):
    pass


def generate_network_name(user_id, gpu_id, gpu_index):
    parts = ["aixblock_network"]

    if user_id is not None:
        parts.append(f"u{user_id}")

    if gpu_id is not None:
        parts.append(f"g{gpu_id}")

    if gpu_index is not None:
        parts.append(f"i{gpu_index}")
    import random
    import string

    # char_set = string.ascii_uppercase + string.digits
    # parts.append(random.sample(char_set*6, 6))
    return "_".join(parts) #.append(random.sample(char_set*6, 6))

def init_swarm(client):
    remove_all_services(client)
    try:
        client.swarm.init()
        print("Swarm đã được khởi tạo.")
    except docker.errors.APIError as e:
        print(e)

def remove_all_services(client):
    try:
        # Lấy danh sách tất cả các service
        services = client.services.list()

        # Lặp qua và xóa từng service
        for service in services:
            print(f"Removing service: {service.id}")
            service.remove()

        print("All services removed successfully.")
    except Exception as e:
        print(f"Error removing services: {e}")
        
def deploy_stack(yml_file, stack_name, remote_base_url):
    import subprocess
    command = f'DOCKER_HOST={remote_base_url} docker stack deploy -c {yml_file} {stack_name}'
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Stack deployed successfully:", result.stdout.decode())
    except subprocess.CalledProcessError as e:
        print("Error deploying stack:", e.stderr.decode())

def run_scale_service(client, url):
    remove_all_services(client)

    # pull_image(client, "jcwimer/docker-swarm-autoscaler")
    # pull_image(client, "prom/prometheus")
    # pull_image(client, "google/cadvisor")

    # deploy_stack('./aixblock_core/templates/auto_scale_config/swarm-autoscaler-stack.yml', 'autoscaler', url)

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

    return int(random_port)

def create_redis(client, network_name):
    container_name = f"redis-{network_name}"

    pull_image(client, "redis")
    remove_container(client, container_name)

    container = client.containers.run(
        "redis/redis-stack-server:latest",
        detach=True,
        name=container_name,
        ports={"6379/tcp": "6379"},
        environment={},
        network=network_name,
    )
    return 6379


def dockerContainerPull(
    compute_type,
    ip_address,
    client_id,
    client_secret,
    token,
    user_id=None,
    gpu_id=None,
    gpu_index=None,
    history_id=None
):
    try:
        if compute_type is None:
            compute_type = "full"
        minio_port = None
        api_port = None
        # import os
        # os.environ["PATH"] = "/usr/local/bin:" + os.environ["PATH"]
        client = docker.DockerClient(base_url=f"tcp://{ip_address}:4243")
        client.login(username="quoiwowai", password="Abc!23456")
        network_name = generate_network_name(user_id, gpu_id, gpu_index)
        network = create_network(client, network_name)
        max_containers = 1
        
        if compute_type == "gpu":
            pull_thread = threading.Thread(
                target=pull_image, args=(client, "gpu_image")
            )
            pull_thread.start()

        try:
            from compute_marketplace.calc_info_host import DockerStats
            from compute_marketplace.self_host import update_notify_install
            from compute_marketplace.functions import notify_for_compute

            docker_stats = DockerStats(docker_host=f"http://{ip_address}:4243")
            total_memory, avg_memory_usage, total_cpu = docker_stats.calculate_total_usage()
            max_containers = docker_stats.scale_capacity()
            if avg_memory_usage > 0.7 or total_cpu > 0.7:
                update_notify_install("Your system is currently using over 70% of its memory or CPU.", user_id, "Your system is currently using over 70% of its memory or CPU.", history_id, "Install Compute", "warning")
                if user_id is not None:
                    user = User.objects.filter(id=user_id).first()
                    notify_for_compute(user.uuid, "Warning", "Your system is currently using over 70% of its memory or CPU.")
            
        except Exception as e:
            print(e)

        if compute_type in ["full", "label-tool"]:
            init_swarm(client)
            # run_scale_service(client, f"tcp://{ip_address}:4243") 
            if ip_address != "108.181.196.144":
                postgres_port = create_postgres_container(
                    client, ip_address, network_name
                )
                minio_port, minio_user_username, minio_password, api_port = (
                    create_minio_container(client, network_name, user_id)
                )
                try:
                    redis_port = create_redis(client, network_name)
                    print(f"Redis is running on port {redis_port}")
                except Exception as e:
                    print(f"Failed to create Redis container: {e}")

            public_port, user_email, password = create_platform_container(
                client,
                ip_address,
                client_id,
                client_secret,
                token,
                network_name,
                postgres_port,
                minio_user=minio_user_username,
                minio_password=minio_password,
                minio_port=minio_port,
                user_id=user_id,
                max_containers=max_containers
            )

            # container = client.containers.get(f"aixblock-platform-{network_name}")
            # container.exec_run(
            #     "docker login --username 'quoiwowai' --password-stdin 'Abc!23456'"
            # )

        if compute_type == "storage":
            minio_port, minio_user_username, minio_password, _ = create_minio_container(
                client, network_name, user_id
            )
            client.close()
            return (
                minio_port,
                minio_port,
                minio_user_username,
                minio_password,
                minio_user_username,
                minio_password,
                network_name,
                api_port
            )
        
        if compute_type == "model-training":
            init_swarm(client)
            # run_scale_service(client, f"tcp://{ip_address}:4243") 
            minio_port, minio_user_username, minio_password = create_ml_default(
                client, network_name
            )  # install model
            client.close()
            return (
                minio_port,
                minio_user_username,
                minio_password,
                minio_password,
                minio_user_username,
                minio_password,
                network_name,
                api_port
            )

        client.close()
        return (
            public_port,
            minio_port,
            user_email,
            password,
            minio_user_username,
            minio_password,
            network_name,
            api_port
        )
    except Exception as e:
        print(f"Error in dockerContainerPull: {e}")
        raise


def run_docker_operations(func, *args, **kwargs):

    with ThreadPoolExecutor() as executor:
        loop = asyncio.get_event_loop()
        return loop.run_in_executor(executor, func, *args, **kwargs)


async def asyncDockerContainerPull(
    compute_type,
    ip_address,
    client_id,
    client_secret,
    token,
    user_id=None,
    gpu_id=None,
    gpu_index=None,
):
    try:
        if compute_type is None:
            compute_type = "full"
        minio_port = None

        # Initialize Docker client
        client = docker.DockerClient(base_url=f"tcp://{ip_address}:4243")
        client.login(username="quoiwowai", password="Abc!23456")
        network_name = generate_network_name(user_id, gpu_id, gpu_index)

        # Run Docker operations in an executor
        network = await run_docker_operations(create_network, client, network_name)

        if compute_type == "gpu":
            await run_docker_operations(pull_image, client, "gpu_image")

        if compute_type in ["full", "label-tool"]:
            if ip_address != "108.181.196.144":
                postgres_port = await run_docker_operations(
                    create_postgres_container, client, ip_address, network_name
                )
                minio_port, minio_user_username, minio_password, _ = (
                    await run_docker_operations(
                        create_minio_container, client, network_name, user_id
                    )
                )
                try:
                    redis_port = await run_docker_operations(
                        create_redis, client, network_name
                    )
                    print(f"Redis is running on port {redis_port}")
                except Exception as e:
                    print(f"Failed to create Redis container: {e}")

            public_port, user_email, password = await run_docker_operations(
                create_platform_container,
                client,
                ip_address,
                client_id,
                client_secret,
                token,
                network_name,
                postgres_port,
                minio_user=minio_user_username,
                minio_password=minio_password,
                minio_port=minio_port,
                user_id=user_id,
            )

            container = client.containers.get(f"aixblock-platform-{network_name}")
            await run_docker_operations(
                container.exec_run,
                "docker login --username 'quoiwowai' --password-stdin 'Abc!23456'",
            )

        if compute_type == "storage":
            minio_port, minio_user_username, minio_password, _ = (
                await run_docker_operations(
                    create_minio_container, client, network_name, user_id
                )
            )
            client.close()
            return (
                minio_port,
                minio_port,
                minio_user_username,
                minio_password,
                minio_user_username,
                minio_password,
            )

        if compute_type == "model-training":
            minio_port, minio_user_username, minio_password = (
                await run_docker_operations(create_ml_default, client, network_name)
            )
            client.close()
            return (
                minio_port,
                minio_user_username,
                minio_password,
                minio_password,
                minio_user_username,
                minio_password,
            )

        client.close()
        return (
            container.ports["8081/tcp"][0]["HostPort"],
            minio_port,
            user_email,
            password,
            minio_user_username,
            minio_password,
        )

    except Exception as e:
        print(f"Error in dockerContainerPull: {e}")
        raise


def docker_container_check_status(compute_type, ip_address,docker_port, network_name):
    try:
        if docker_port is None:
            docker_port = '4243'
        client = docker.DockerClient(base_url=f"tcp://{ip_address}:{docker_port}")
        client.login(username="quoiwowai", password="Abc!23456")

        if compute_type in ["full", "label-tool"]:
            containers = client.containers.list(
                filters={"name": f"aixblock-platform-{network_name}"}, all=True
            )
            if len(containers) > 0:
                container=containers[0]
                status = container.status
                return status

        if compute_type == "storage":
            containers = client.containers.list(
                filters={"name": f"aixblock-minio-{network_name}"}, all=True
            )
            if len(containers) > 0:
                container=containers[0]
                status = container.status
                return status
        if compute_type == "model-training":
            containers = client.containers.list(
                filters={"name": f"aixblock-ml-{network_name}"}, all=True
            )
            if len(containers) > 0:
                container=containers[0]
                status = container.status
                return status

    except Exception as e:
        print(f"Error in dockerContainerPull: {e}")
        raise


# def dockerContainerPull(compute_type, ip_address, client_id, client_secret, token):

#     if compute_type is None:
#         compute_type = "full"
#     client = docker.DockerClient(base_url=f"tcp://{ip_address}:4243")
#     client.login(username='quoiwowai', password='Abc!23456')

#    # container_watchtower(client)
#     if compute_type == 'gpu':
#         pull_thread = threading.Thread(target=pull_images, args=(client))
#         pull_thread.start()
#     if compute_type == 'full' or compute_type == 'label-tool':
#         if ip_address != '108.181.196.144':
#             containers =client.containers.list(filters={'name': f"wowai-postgres"}, all=True)
#             if len(containers) > 0:
#                 container=containers[0]
#                 try:
#                     container.stop()
#                     container.remove()
#                 except Exception as e:
#                     print(e)
#             images = client.images.list(filters={'reference': f"docker.io/library/postgres"}, all=True)
#             if len(images) > 0:
#                 tag=images[0]
#                 try:
#                     client.images.remove(image=tag, force=True)
#                 except Exception as e:
#                     print(e)
#             else:
#                 client.api.pull('docker.io/library/postgres:latest', stream=True, decode=True)
#                 container = client.containers.run(
#                     "docker.io/library/postgres:latest",
#                     detach=True,
#                     name=f"wowai-postgres",
#                     device_requests=[

#                     ],
#                     ports={
#                         '5432/tcp': '5432',
#                     },
#                     environment={
#                         "POSTGRES_PASSWORD": "@9^xwWA"
#                     },
#                     volumes={
#                     }
#                 )
#                 container.reload()

#                 # container.exec_run(f"psql postgres -c \"CREATE USER 'jupyterhub' CREATEDB PASSWORD 'jupyterhub'\"")

#                 create_database_command = f'CREATE DATABASE JupyterHub;'
#                 create_database_response = container.exec_run(
#                     f'psql -v ON_ERROR_STOP=1 --username={get_env("POSTGRES_USER","postgres")} -c "{create_database_command}"'
#                 )
#                 if create_database_response.exit_code == 0:
#                     print("Tạo cơ sở dữ liệu thành công.")
#                 else:
#                     print("Lỗi khi tạo cơ sở dữ liệu:")
#                     print(create_database_response.output.decode("utf-8"))

#                 create_database_command = f"CREATE DATABASE platform_v2;"
#                 create_database_response = container.exec_run(
#                     f'psql -v ON_ERROR_STOP=1 --username={get_env("POSTGRES_USER","postgres")} -c "{create_database_command}"'
#                 )
#                 if create_database_response.exit_code == 0:
#                     print("Tạo cơ sở dữ liệu thành công.")
#                 else:
#                     print("Lỗi khi tạo cơ sở dữ liệu:")
#                     print(create_database_response.output.decode("utf-8"))

#             containers = client.containers.list(filters={'name': f"wowai-minio"}, all=True)
#             if len(containers) > 0:
#                 container=containers[0]
#                 try:
#                     container.stop()
#                     container.remove()
#                 except Exception as e:
#                     print(e)

#             images = client.images.list(filters={'reference': f"minio/minio"}, all=True)
#             if len(images) > 0:
#                 tag=images[0]
#                 try:
#                     client.images.remove(image=tag, force=True)
#                 except Exception as e:
#                     print(e)
#             if len(containers) == 0:
#                 client.api.pull('quay.io/minio/minio', stream=True, decode=True)
#                 container = client.containers.run(
#                     "quay.io/minio/minio",
#                     detach=True,
#                     name=f"wowai-minio",
#                     device_requests=[

#                     ],
#                     ports={
#                         '9000/tcp': '9000',
#                         '9001/tcp': '9001'
#                     },
#                     command=["server", "/data", "--console-address", ":9001"],
#                     environment={
#                         "MINIO_ROOT_USER": "adminwow",
#                         "MINIO_ROOT_PASSWORD": "wBTwZsUZWAj3gm4"
#                     },
#                     volumes={
#                     }
#                 )
#             create_database_response = container.exec_run(
#                     f'mc admin user add sib {get_env("MINIO_ROOT_USER","adminwow")} {get_env("MINIO_ROOT_PASSWORD","wBTwZsUZWAj3gm4")}'
#                 )

#         containers =client.containers.list(filters={'name': f"wowai-label-tool"}, all=True)
#         if len(containers) > 0:
#             container=containers[0]
#             try:
#                 container.stop()
#                 container.remove()
#             except Exception as e:
#                 print(e)

#         # get image version
#         image = f"{AIXBLOCK_IMAGE_NAME}:{AIXBLOCK_IMAGE_VERSION}"
#         image_dataset_live = InstallationService.objects.filter(
#             image=AIXBLOCK_IMAGE_NAME,
#             deleted_at__isnull=True,
#             environment=ENVIRONMENT,
#             status="active",
#         ).first()
#         if image_dataset_live:
#             image = str(image_dataset_live.image)+":"+str(image_dataset_live.version)
#         images = client.images.list(filters={"reference": f"{AIXBLOCK_IMAGE_NAME}"}, all=True)
#         if len(images) > 0 and image is None:
#             images_curr=images[0]
#             # image_tags = images_curr.tags[0]
#             # image_created = images_curr.attrs['Created']
#             latest_version = get_latest_platform_version(AIXBLOCK_IMAGE_NAME)

#             # print(latest_version["last_updated"], images_curr.attrs['Created'])
#             if latest_version:
#                 pull_lastest_images(client, images_curr, latest_version, AIXBLOCK_IMAGE_NAME)
#         else:
#             client.api.pull(image, stream=True, decode=True)

#         port = None #8080
#         assets_cdn = None
#         if ip_address == '108.181.196.144':
#             token=''
#             port = 8080
#             assets_cdn = "https://aixblock-staging.b-cdn.net"

#         # if len(containers) > 0:
#         #     container=containers[0]
#         # else:
#         container = client.containers.run(
#             image,
#             detach=True,
#             name=f"wowai-label-tool",
#             device_requests=[],
#             ports={
#                 "8080/tcp": port,
#                 "8443/tcp": port,
#             },
#             environment={
#                 "POSTGRES_HOST": ip_address,
#                 "AXB_PUBLIC_SSL_PORT": 8443,
#                 "POSTGRES_PASSWORD": "@9^xwWA",
#                 "POSTGRES_NAME": get_env("POSTGRES_NAME", "platform_v2"),
#                 "POSTGRES_USER": "postgres",
#                 "OAUTH_CLIENT_ID": get_env("OAUTH_CLIENT_ID", f"{client_id}"),
#                 "OAUTH_CLIENT_SECRET": get_env(
#                     "OAUTH_CLIENT_SECRET", f"{client_secret}"
#                 ),
#                 "OAUTH_TOKEN_URL": get_env(
#                     "OAUTH_TOKEN_URL", "https://app.aixblock.io"
#                 ),
#                 "OAUTH_AUTHORIZE_URL": get_env(
#                     "OAUTH_AUTHORIZE_URL", "https://app.aixblock.io/o/authorize"
#                 ),
#                 "OAUTH_API_BASE_URL": get_env(
#                     "OAUTH_API_BASE_URL", "https://app.aixblock.io"
#                 ),
#                 "OAUTH_REDIRECT_URL": get_env(
#                     "OAUTH_REDIRECT_URL",
#                     f"http://{ip_address}:8080/oauth/login/callback",
#                 ),
#                 "MASTER_NODE": get_env("MASTER_NODE", "https://app.aixblock.io"),
#                 "MASTER_TOKEN": token,
#                 "NOTEBOOK_URL": f"http://{ip_address}:8100/",
#                 "NOTEBOOK_TOKEN": "639922e8a39e41e7add2d6ac4f45c314",
#                 "MINIO_API_URL": f"{ip_address}:7878",
#                 "MINIO_USER": "adminwow",
#                 "MINIO_PASSWORD": "wBTwZsUZWAj3gm4",
#                 "ASSETS_CDN": ""
#             },
#             volumes={},
#         )

#         # thread_command = threading.Thread(target=run_commands_in_thread, args=(container,))
#         # thread_command.start()

#         try:
#             container.exec_run('python3 aixblock_core/manage.py default --created_by_id 1 --status create ')
#             container.exec_run('python3 aixblock_core/manage.py create_superuser_with_password --email admin@wow-ai.com --username admin --password 123321 --noinput' )
#             container.exec_run('python3 aixblock_core/manage.py create_organization The_title_of_the_organization')
#             container.exec_run('python3 aixblock_core/manage.py seed_templates')
#             container.exec_run(f'python3 aixblock_core/manage.py runsslserver 0.0.0.0:{AXB_PUBLIC_SSL_PORT}')
#         except Exception as e:
#             print(e)
#         container.reload()
#         pull_thread = threading.Thread(target=pull_images, args=(client,))
#         pull_thread.start()
#         # thread create notebook
#         jupyterhub_notebook_live = threading.Thread(target=install_jupyterhub_notebook_live, args=(client,))
#         jupyterhub_notebook_live.start()

#         # thread create install_crawling_server
#         # crawling_server = threading.Thread(target=install_crawling_server, args=(client,))
#         # crawling_server.start()

#         # thread install_calculator_server
#         # calculator_server = threading.Thread(target=install_calculator_server, args=(client,))
#         # calculator_server.start()

#         # thread install_notification_server
#         # notification_server = threading.Thread(target=install_notification_server, args=(client,))
#         # notification_server.start()

#         container.exec_run("docker login --username 'quoiwowai' --password-stdin 'Abc!23456'")
#         print(container.ports['8080/tcp'][0]['HostPort'])
#         client.close()
#         return container.ports['8080/tcp'][0]['HostPort']

#         # install jupyter notebook
#         # images = client.images.list(filters={'reference': f"wowai/jupyter_notebook_live"}, all=True)
#         # if len(images) > 0:
#         #     tag=images[0]
#         #     try:
#         #         client.images.remove(image=tag, force=True)
#         #     except Exception as e:
#         #         print(e)
#         # images = client.images.list(filters={'reference': f"wowai/jupyter_notebook_live"}, all=True)
#         # if len(images) > 0:
#         #     tag=images[0]
#         #     try:
#         #         client.images.remove(image=tag, force=True)
#         #     except Exception as e:
#         #         print(e)
#         # client.api.pull('wowai/jupyter_notebook:latest', stream=True, decode=True)
#         # containers =client.containers.list(filters={'name': f"wowai-jupyterhub-notebook-live"}, all=True)
#         # if len(containers) > 0:
#         #     container=containers[0]
#         #     try:
#         #         container.stop()
#         #         container.remove()
#         #     except Exception as e:
#         #         print(e)

#         # container = client.containers.run(
#         #     "wowai/jupyter_notebook:latest",
#         #     detach=True,
#         #     name=f"wowai-jupyterhub-notebook-live",
#         #     device_requests=[
#         #     #    docker.types.DeviceRequest(device_ids=[str("0")], capabilities=[['gpu']])
#         #     ],
#         #     ports={
#         #         '8100/tcp': '8100',
#         #     },
#         #     environment={

#         #     },
#         #     volumes={
#         #         # "createusers.txt":"/root/createusers.txt"
#         #     }
#         # )

#         # install crawling server
#         # containers =client.containers.list(filters={'name': f"wowai-crawling_server"}, all=True)
#         # if len(containers) > 0:
#         #     container=containers[0]
#         #     try:
#         #         container.stop()
#         #         container.remove()
#         #     except Exception as e:
#         #         print(e)
#         # images = client.images.list(filters={'reference': f"wowai/crawl-server"}, all=True)
#         # if len(images) > 0:
#         #     tag=images[0]
#         #     try:
#         #         client.images.remove(image=tag, force=True)
#         #     except Exception as e:
#         #         print(e)
#         # client.api.pull('wowai/crawl-server:latest', stream=True, decode=True)

#         # info= client.info()
#         # client.close()
#         # list_index = []
#         # if "GenericResources" in info:
#         #     if len(info['GenericResources'])>0 :
#         #         for i, _ in info['GenericResources']:
#         #             list_index.append(i)

#         # container = client.containers.run(
#         #     "wowai/crawl-server:latest",
#         #     detach=True,
#         #     name=f"wowai-crawling_server",
#         #     device_requests=[
#         #         # docker.types.DeviceRequest(device_ids=[','.join(list_index)], capabilities=[['gpu']])
#         #         ],
#         #     ports={
#         #         '5000/tcp': None,
#         #     },
#         #     environment={

#         #     },
#         #     volumes={
#         #     }
#         # )
#         # install cost calculator server
#         # containers =client.containers.list(filters={'name': f"wowai-cost-calculator_server"}, all=True)
#         # if len(containers) > 0:
#         #     container=containers[0]
#         #     try:
#         #         container.stop()
#         #         container.remove()
#         #     except Exception as e:
#         #         print(e)
#         # images = client.images.list(filters={'reference': f"wowai/cost-calculator-server"}, all=True)
#         # if len(images) > 0:
#         #     tag=images[0]
#         #     try:
#         #         client.images.remove(image=tag, force=True)
#         #     except Exception as e:
#         #         print(e)
#         # client.api.pull('wowai/cost-calculator-server:latest', stream=True, decode=True)

#         # info= client.info()
#         # client.close()
#         # list_index = []
#         # if "GenericResources" in info:
#         #     if len(info['GenericResources'])>0 :
#         #         for i, _ in info['GenericResources']:
#         #             list_index.append(i)

#         # container = client.containers.run(
#         #     "wowai/cost-calculator-server:latest",
#         #     detach=True,
#         #     name=f"wowai-cost-calculator_server",
#         #     device_requests=[
#         #         # docker.types.DeviceRequest(device_ids=[','.join(list_index)], capabilities=[['gpu']])
#         #         ],
#         #     ports={
#         #         '5000/tcp': None,
#         #     },
#         #     environment={

#         #     },
#         #     volumes={
#         #     }
#         # )
#         # install notification server
#         # containers =client.containers.list(filters={'name': f"wowai-notification_server"}, all=True)
#         # if len(containers) > 0:
#         #     container=containers[0]
#         #     try:
#         #         container.stop()
#         #         container.remove()
#         #     except Exception as e:
#         #         print(e)
#         # images = client.images.list(filters={'reference': f"wowai/notification-server"}, all=True)
#         # if len(images) > 0:
#         #     tag=images[0]
#         #     try:
#         #         client.images.remove(image=tag, force=True)
#         #     except Exception as e:
#         #         print(e)
#         # client.api.pull('wowai/notification-server:latest', stream=True, decode=True)

#         # info= client.info()
#         # client.close()
#         # list_index = []
#         # if "GenericResources" in info:
#         #     if len(info['GenericResources'])>0 :
#         #         for i, _ in info['GenericResources']:
#         #             list_index.append(i)

#         # container = client.containers.run(
#         #     "wowai/cost-notification:latest",
#         #     detach=True,
#         #     name=f"wowai-notification_server",
#         #     device_requests=[
#         #         # docker.types.DeviceRequest(device_ids=[','.join(list_index)], capabilities=[['gpu']])
#         #         ],
#         #     ports={
#         #         '5000/tcp': None,
#         #     },
#         #     environment={

#         #     },
#         #     volumes={
#         #     }
#         # )
