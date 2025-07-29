import json
import time
import math
import string
import random
import requests
from users.models import User
from datetime import datetime, timedelta
from configs.models import InstallationService
from core.settings.base import AIXBLOCK_IMAGE_NAME, ENVIRONMENT, EXABIT_API_KEY
import paramiko
from aixblock_core.core.utils.params import get_env
from django.conf import settings

from .base_provider import ProviderBase

class ExabitsProvider(ProviderBase):
    def __init__(self, api_key=EXABIT_API_KEY):
        super().__init__(api_key)
        self.regions_id = "66d566ba3a9501001256d6e4"
        self.regions_name = "CANADA-1"
        self.os_name = "Ubuntu Server 22.04 LTS R535 CUDA 12.2 with Docker"
        self.os_id = "66fb14345c85bc0011042736"
        # self.login()

    # def login(self):
    #     url = "https://api.gpu.exabits.ai/api/v1/authenticate/login"

    #     payload = json.dumps({
    #         "username": self.username,
    #         "password": self.password
    #     })

    #     print(payload)

    #     headers = {
    #         'Content-Type': 'application/json'
    #     }

    #     response = requests.request("POST", url, headers=headers, data=payload)

    #     try:
    #         response_json = response.json()  # Chuyển response thành dictionary
    #         access_token = response_json.get("data", {}).get("access_token")
            
    #         if access_token:
    #             print("Access Token:", access_token)
    #             self.api_key = access_token
    #             return access_token
    #         else:
    #             print("Access token not found!")
    #             return None
    #     except json.JSONDecodeError:
    #         print("Failed to parse JSON response!")
    #         return None

    def get_regions(self):
        url = "https://api.gpu.exabits.ai/api/v1/regions"

        payload = {}
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        try:
            response_json = response.json()
            print(response_json)
        except json.JSONDecodeError:
            print("Failed to parse JSON response!")
            return None

    def get_images(self):
        url = f"https://api.gpu.exabits.ai/api/v1/images?region_id={self.regions_id}"

        payload = {}
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        try:
            response_json = response.json()
            print(response_json)
        except json.JSONDecodeError:
            print("Failed to parse JSON response!")
            return None
        
    def list_compute(self, data_filter=None):
        url = f"https://api.gpu.exabits.ai/api/v1/flavors?region_id={self.regions_id}"

        payload = {}
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        result = []
        try:
            response_json = response.json()
            print(response_json["data"])
            for offer in response_json["data"][0]["products"]:
                print(offer)
                total_price_vast = offer['price']
                if data_filter.get("price"):
                    if not float(data_filter["price"]["from"]) <= total_price_vast <= float(data_filter["price"]["to"]):
                        continue

                result_dict = { offer["gpu"]:[]}
                start_date = None
                end_date = None
                effect_ram = 1
                # if offer["cpu_cores"] and offer["cpu_cores_effective"]:
                #     effect_ram = offer["cpu_cores"]/offer["cpu_cores_effective"]
                # Thay thế None bằng 0
                start_date = float(start_date) if start_date is not None else 0.0
                end_date = float(end_date) if end_date is not None else 0.0

                # Tính toán max_duration
                max_duration = int((end_date - start_date)/86400)
                result_dict[offer["gpu"]].append(
                        {
                            "id": offer["id"],
                            "provider_name": "Exabit",
                            "compute_marketplace": {
                                "id": offer["id"],
                                "name": offer["gpu"],
                                "deleted_at": None,
                                "infrastructure_id": f'{offer["id"]}',
                                "owner_id": 0,
                                "arthor_id": 0,
                                "catalog_id": 0,
                                "ip_address": "",
                                "port": "",
                                "config": json.dumps(
                                    {
                                        "cpu": offer["gpu"],
                                        "ram": offer["ram"],
                                        "disk": f'{offer["disk"]}',
                                        "diskType": "SSD",
                                        "os": "Linux",
                                    }
                                ),
                                "is_using_cpu": False,
                                "compute_type": "full",
                                "status": "in_marketplace",
                                "type": "MODEL-PROVIDER-EXABIT",
                                "file": "",
                                "cpu_price": None,
                                "compute_time_working": {},
                            },
                            "prices": [
                                {
                                    "id": 0,
                                    "token_symbol": "USD",
                                    "price": math.ceil(total_price_vast * 1000) / 1000,
                                    "unit": "hour",
                                    "type": "gpu",
                                    "compute_gpu_id": 0,
                                    "compute_marketplace_id": 0,
                                    "model_marketplace_id": None,
                                }
                            ],
                            "gpu_name": offer["gpu"],
                            "power_consumption": "360w",
                            "memory_usage": None,
                            "num_gpus": offer["gpu_count"],
                            "power_usage": None,
                            "gpu_index": 0,
                            "gpu_memory": "",
                            "gpu_tflops": "",
                            "branch_name": "",
                            "batch_size": 8,
                            "gpu_id": "gpsu-789a-cbsd-xysz-45s6",
                            "serialno": None,
                            "created_at": "2024-05-06T04:20:17.921978Z",
                            "updated_at": "2024-05-06T04:20:17.921983Z",
                            "deleted_at": None,
                            "quantity_used": 0,
                            "user_rented": 0,
                            "max_user_rental": 1,
                            "status": "in_marketplace",
                            "owner_id": 1,
                            "infrastructure_id": f'{offer["id"]}',
                            "provider_id": offer["region_id"],  # provider id
                            "per_gpu_ram": int(offer["ram"]),  # convert to GB
                            "max_cuda_version": "",
                            "per_gpu_memory_bandwidth": "",  # convert to GB
                            "motherboard": "",
                            "internet_up_speed": "",  # convert to Mbps
                            "internet_down_speed": "",  # convert to Mbps
                            "number_of_pcie_per_gpu": "", #f'{offer["pci_gen"]}.0,16x',
                            "per_gpu_pcie_bandwidth": "",  # convert to GB
                            "eff_out_of_total_nu_of_cpu_virtual_cores": "",
                            "eff_out_of_total_system_ram": "",  # convert to GB,
                            "max_duration": max_duration,  # convert to day
                            "reliability": "",  # %
                            "dl_performance_score": "",  # %
                            "dlp_score": "",  # DLP/$/hr,
                            "location_id": offer["region_name"],
                            "location_alpha2": offer["region_name"],
                            "location_name": offer["region_name"],
                            "datacenter": "datacenter",  # datacenter/ miners/ consumerGpu
                        }
                    )

                result.append(result_dict)
            return result
        except json.JSONDecodeError:
            print("Failed to parse JSON response!")
            return None
    
    def info_compute(self, id):
        url = f"https://api.gpu.exabits.ai/api/v1/virtual-machines/{id}"

        payload = {}

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        response_data = response.json()

        return response_data

    def delete_compute(self, id):
        url = f"https://api.gpu.exabits.ai/api/v1/virtual-machines/{id}"

        payload = {}

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }

        response = requests.request("DELETE", url, headers=headers, data=payload)
        response_data = response.json()

        if "status" in response_data and response_data["status"] == False:
            return False

        return response_data
    
    def start_compute(self, id):
        url = f"https://api.gpu.exabits.ai/api/v1/virtual-machines/{id}/start"

        payload = {}

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        response_data = response.json()

        return response_data

    def reset_compute(self, id):
        url = f"https://api.gpu.exabits.ai/api/v1/virtual-machines/{id}/reboot"

        payload = {}

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        response_data = response.json()

        return response_data

    def stop_compute(self, id):
        url = f"https://api.gpu.exabits.ai/api/v1/virtual-machines/{id}/stop"

        payload = {}

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        response_data = response.json()

        return response_data

    def add_firewall_rules(self, id, port_min, port_max):
        url = f"https://api.gpu.exabits.ai/api/v1/virtual-machines/{id}/firewall-rules"
        
        payload = json.dumps({
            "direction": "inbound",
            "ethertype": "IPv4",
            "protocol": "tcp",
            "port_range_min": int(port_min),
            "port_range_max": int(port_max),
            "remote_ip_prefix": "0.0.0.0/0",
            "description": ""
        })

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        print(response.text)

    def get_port_instance(self, contract_id):
        get_port = False
        import time
        while not get_port:
            try:
                response = self.info_compute(contract_id)

                print(response)
                status = response["data"]["status"]
                public_ip = response["data"]["public_ip"]
                
                print(status) 
                if status == "running" and public_ip != "":
                    # response['instances']['old_id'] = old_id
                    print(response)
                    # time.sleep(10)
                    get_port = True
                
                if status == "error":
                    return False
                
                time.sleep(30)
                
            except Exception as e:
                print(e)
                time.sleep(30)
                get_port = False

        return response
    
    def ssh_connect(self, public_ip, username, password, max_retries=3):
        retries = 0
        while retries < max_retries:
            try:
                # Tạo SSH client
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                
                # Kết nối đến máy chủ từ xa
                ssh.connect(public_ip, port=22, username=username, password=password, timeout=20)
                print(f"Connected to {public_ip}")
                return ssh  # Trả về kết nối SSH nếu thành công
            
            except Exception as e:
                retries += 1
                print(f"Attempt {retries} failed: {e}")
                if retries < max_retries:
                    print(f"Retrying... ({retries}/{max_retries})")
                    time.sleep(5)  # Đợi 5 giây trước khi thử lại
                else:
                    print("Maximum retries reached. Could not connect.")
                    return None

    def docker_swarm_init_via_ssh(self, ssh):
        """
        Hàm khởi tạo Docker Swarm trên một máy từ xa thông qua SSH.

        Parameters:
        - host (str): Địa chỉ IP hoặc hostname của máy từ xa.
        - username (str): Tên đăng nhập SSH.
        - password (str): Mật khẩu đăng nhập SSH.
        """

        try:
            # Dừng tất cả dịch vụ Docker đang chạy
            print("Stopping all Docker services...")
            ssh.exec_command('sudo docker service rm $(sudo docker service ls -q)')

            # Rời khỏi Swarm (nếu có)
            print("Leaving Docker Swarm...")
            ssh.exec_command('sudo docker swarm leave --force')
            
            # Chạy lệnh docker swarm init
            print("Running docker swarm init...")
            stdin, stdout, stderr = ssh.exec_command('sudo docker swarm init')

            # Đọc kết quả
            output = stdout.read().decode().strip()
            error = stderr.read().decode().strip()

            if output:
                print("Output:", output)
            if error:
                print("Error:", error)

        except Exception as e:
            print(f"An error occurred: {e}")
            
    def ssh_docker_pull(self, ssh, image_name):
        try:
            # Tạo SSH client
            # ssh = paramiko.SSHClient()
            # ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # # Kết nối đến máy chủ từ xa
            # ssh.connect(public_ip, port=22, username=username, password=password)
            # print(f"Connected to {public_ip}")
            
            # Lệnh docker pull
            docker_pull_command = f"sudo docker pull {image_name}"
            print(f"Running: {docker_pull_command}")
            stdin, stdout, stderr = ssh.exec_command(docker_pull_command)
            
            # Đọc kết quả
            output = stdout.read().decode()
            error = stderr.read().decode()
            
            if output:
                print(f"Output:\n{output}")
            if error:
                print(f"Error:\n{error}")
            
            # Đóng kết nối
            # ssh.close()
        except Exception as e:
            print(f"Error: {e}")
    
    def generate_password(self):
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return random_suffix
        
        # return escaped_password

    def ssh_install_postgres(self, ssh):
        # Lệnh chạy container PostgreSQL qua SSH
        container_name = self.generate_service_name()
        docker_run_command = f"""
        sudo docker run -d --name {container_name}\
        -e POSTGRES_PASSWORD={get_env("POSTGRES_PASSWORD", "@9^xwWA")} \
        -e POSTGRES_USER=postgres \
        -e POSTGRES_DB="platform_v2" \
        -p 5432 \
        docker.io/library/postgres:latest
        """

        print(f"Running: {docker_run_command}")
        stdin, stdout, stderr = ssh.exec_command(docker_run_command)

        # Kiểm tra kết quả chạy container
        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()
        if error:
            print(f"Error running PostgreSQL container: {error}")
            return False

        container_id = output.strip()
        print(f"PostgreSQL container started: {container_id}")
        time.sleep(10)  # Đợi container khởi động xong

        # Tạo database qua psql
        create_database_command = f"""
        sudo docker exec -i {container_name} \
        psql -U postgres -c "CREATE DATABASE JupyterHub;"
        """
        stdin, stdout, stderr = ssh.exec_command(create_database_command)
        create_db_output = stdout.read().decode().strip()
        create_db_error = stderr.read().decode().strip()

        if create_db_error:
            print(f"Error creating database: {create_db_error}")
            # return False
        else:
            print("Successfully created database: JupyterHub")

        # # Tạo database thứ hai (platform_v2) với retry logic
        # retry_attempts = 5
        # retry_delay = 5
        # for attempt in range(1, retry_attempts + 1):
        #     create_database_command = f"""
        #     sudo docker exec -i {container_name} \
        #     psql -U {get_env("POSTGRES_USER", "postgres")} -c "CREATE DATABASE platform_v2;"
        #     """
        #     stdin, stdout, stderr = ssh.exec_command(create_database_command)
        #     create_db_output = stdout.read().decode().strip()
        #     create_db_error = stderr.read().decode().strip()

        #     if not create_db_error:
        #         print(f"Successfully created database: platform_v2 (attempt {attempt})")
        #         break
        #     else:
        #         print(f"Error creating database platform_v2 (attempt {attempt}/{retry_attempts}): {create_db_error}")
        #         if attempt < retry_attempts:
        #             time.sleep(retry_delay)
        #         else:
        #             print("Failed to create database platform_v2 after multiple attempts")

        # Lấy port public được ánh xạ
        get_port_command = f"sudo docker port {container_id} 5432"
        stdin, stdout, stderr = ssh.exec_command(get_port_command)
        ports_output = stdout.read().decode().strip()
        ports_error = stderr.read().decode().strip()

        if ports_error:
            print(f"Error fetching ports: {ports_error}")
            return False

        public_port = ports_output.split(":")[-1]
        print(f"PostgreSQL public port: {public_port}")
        return public_port
    
    def ssh_install_redis(self, ssh):
        docker_run_command = f"""
        sudo docker run -d \
        -p 6379:6379 \
        redis/redis-stack-server:latest
        """

        print(f"Running: {docker_run_command}")
        stdin, stdout, stderr = ssh.exec_command(docker_run_command)

        # Kiểm tra kết quả chạy container
        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()
        if error:
            print(f"Error running PostgreSQL container: {error}")
            return False
        
        return 6379

    def ssh_install_s3(self, ssh, minio_user_username, minio_password):
        # Lệnh docker run với cổng tự động
        container_name = self.generate_service_name()
        docker_run_command = f"sudo docker run -d --name {container_name} -p 9000 -p 9001 " \
                     f"-e MINIO_ROOT_USER={minio_user_username} " \
                     f"-e MINIO_ROOT_PASSWORD=\"{minio_password}\" " \
                     f"quay.io/minio/minio server /data --console-address :9001"
        
        print(f"Running: {docker_run_command}")
        stdin, stdout, stderr = ssh.exec_command(docker_run_command)
        
        # Đọc kết quả của lệnh run
        output = stdout.read().decode()
        error = stderr.read().decode()

        if output:
            docker_port_command = f"sudo docker port {container_name}"
            stdin, stdout, stderr = ssh.exec_command(docker_port_command)
            print(f"Output:\n{output}")
        if error:
            print(f"Error:\n{error}")
            return False, False
        
        docker_port_command = f"sudo docker port {container_name}"
        stdin, stdout, stderr = ssh.exec_command(docker_port_command)
        # Đọc kết quả và in ra
        port_info = stdout.read().decode().strip()
        if port_info:
            print(f"Port information: \n{port_info}")
            
            # Tách thông tin cổng
            port_mapping = {}
            for line in port_info.splitlines():
                parts = line.split("->")
                if len(parts) == 2:
                    container_port, host_port = parts
                    container_port = container_port.strip()
                    host_port = host_port.strip().split(":")[-1]  # Lấy phần cổng trên máy chủ
                    port_mapping[container_port] = host_port
            
            print(f"Port mappings: {port_mapping}")
            # Ví dụ, lấy cổng 9000 và 9001
            port_9000 = port_mapping.get('9000/tcp', None)
            port_9001 = port_mapping.get('9001/tcp', None)
            
            print(f"Mapped Port 9000: {port_9000}")
            print(f"Mapped Port 9001: {port_9001}")
        else:
            print(f"Error getting port info: {stderr.read().decode()}")
        
        return port_9000, port_9001
    
    def extract_ports_ml(self, ports_info):
        import re
        port_pattern = r"tcp (\d+) (\d+)"
        matches = re.findall(port_pattern, ports_info)

        # Tạo danh sách các cổng
        ports_list = [{"target_port": target_port, "published_port": published_port} for target_port, published_port in matches]
        return ports_list
        # Dùng regex để tìm các cổng
        # port_pattern = r"tcp (\d+) (\d+)"
        # matches = re.findall(port_pattern, ports_info)

        # # Gán các giá trị cổng vào các biến
        # ports_dict = {}
        # for target_port, published_port in matches:
        #     ports_dict[target_port] = published_port

        # # Trả về các cổng theo dạng yêu cầu
        # port_9090 = ports_dict.get('9090')
        # port_6006 = ports_dict.get('6006')
        # port_23456 = ports_dict.get('23456')

        # return port_9090, port_6006, port_23456

    def extract_ports_platform(self, ports_info):
        import re
        # Dùng regex để tìm các cổng
        port_pattern = r"tcp (\d+) (\d+)"
        matches = re.findall(port_pattern, ports_info)

        # Gán các giá trị cổng vào các biến
        ports_dict = {}
        for target_port, published_port in matches:
            ports_dict[target_port] = published_port

        # Trả về các cổng theo dạng yêu cầu
        port_8081 = ports_dict.get('8081')
        port_8080 = ports_dict.get('8080')

        return port_8081, port_8080
    
    def generate_service_name(self, prefix="aixblock"):
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"{prefix}-{random_suffix}"
    
    def ssh_install_ml(self, ssh, images, max_containers=1, info_run=None):
        # Lệnh Docker run
        service_name = self.generate_service_name()
        args_str = "gunicorn --bind :9090 --workers 1 --threads 1 --timeout 0 _wsgi:app --certfile=/app/cert.pem --keyfile=/app/privkey.pem"
        docker_service_command = f"sudo docker service create " \
                             f"--name {service_name} " \
                             f"--replicas 1 " \
                             f"-p 9090 " \
                             f"-p 6006 " \
                             f"-p 23456 " \
                             f"{images} " \
                            #  f"{args_str}"
    
        print(f"Running: {docker_service_command}")
        if info_run:
            try:
                if "exposed_ports" in info_run and info_run["exposed_ports"]:
                    for port in info_run["exposed_ports"]:
                        if port not in ["9009", "6006", "23456"]:
                            port_mapping = f"-p {port}:{port}"
                            docker_service_command += f" {port_mapping}"

            except Exception as e:
                print(f"An error occurred: {e}")
        
            try:
                if "run_command" in info_run and info_run["run_command"]:
                    args_str = info_run["run_command"]

            except Exception as e:
                print(f"An error occurred: {e}")

        docker_service_command += f"{args_str}"
        try:
            # Chạy lệnh để tạo service
            stdin, stdout, stderr = ssh.exec_command(docker_service_command)
            
            # Đọc kết quả
            output = stdout.read().decode().strip()
            error = stderr.read().decode().strip()
            
            if output:
                print(f"Output:\n{output}")
            if error:
                print(f"Error:\n{error}")
            
            # Lấy thông tin về service sau khi tạo
            service_inspect_command = f"sudo docker service inspect {service_name} --format '{{{{.Endpoint.Ports}}}}'"
            stdin, stdout, stderr = ssh.exec_command(service_inspect_command)
            
            # Đọc kết quả và lấy cổng
            ports_info = stdout.read().decode().strip()
            if ports_info:
                ports_list = self.extract_ports_ml(ports_info)
                print(f"Service ports: {ports_info}")
            else:
                print("No ports information available.")

            return ports_list
        
        except Exception as e:
            print(f"Error: {e}")
        
        return ports_list
    
    def ssh_install_platform(
        self,
        ssh,
        image,
        ip_address,
        minio_port,
        platform_username,
        platform_password,
        platform_email,
        postgres_port,
        client_id,
        client_secret,
        token,
        max_containers,
    ):

        # Cấu hình môi trường
        env_dict = {
            "MQTT_INTERNAL_SERVER": "172.17.0.1",
            "MQTT_SERVER": "172.17.0.1",
            "AXB_PUBLIC_PORT": 8081,
            "POSTGRES_HOST": "172.17.0.1",
            "POSTGRES_PORT": postgres_port,
            "AXB_PUBLIC_SSL_PORT": 8081,
            "POSTGRES_PASSWORD": get_env("POSTGRES_PASSWORD", "@9^xwWA"),
            "POSTGRES_NAME": "platform_v2",
            "POSTGRES_USER": "postgres",
            "ADMIN_EMAIL": platform_email,
            "ADMIN_USERNAME": platform_username,
            "ADMIN_PASSWORD": platform_password,
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
            "MINIO_USER": platform_username,
            "MINIO_PASSWORD": platform_password,
            "ASSETS_CDN": "",
            "SESSION_REDIS_PORT": 6379,
            "SESSION_REDIS_HOST": "172.17.0.1",
            "HOST_IP": f"{ip_address}",
            "INSTALL_TYPE": "SELF-HOST",
            "REVERSE_ADDRESS": settings.REVERSE_ADDRESS,
        }

        if not postgres_port:
            env_dict["DJANGO_DB"] = "sqlite"

        # Chuyển env_dict thành chuỗi
        env_string = " ".join([f"-e {key}='{value}'" for key, value in env_dict.items()])
        service_name = self.generate_service_name()
        # Lệnh Docker service
        docker_command = f"sudo docker service create " \
                             f"--name {service_name} " \
                             f"--replicas 1 " \
                             f"-p 8081 " \
                             f"-p 8080 " \
                             f"{env_string} " \
                             f"{image} " \
                             f"sh /aixblock/deploy/run-platform.sh"
        
        # docker_command = (
        #     f"docker service create"
        #     f"--replicas 1 "
        #     f"-p 8081 -p 8080 "
        #     # f"--label swarm.autoscale=true "
        #     # f"--label swarm.autoscale.min=1 "
        #     # f"--label swarm.autoscale.max={max_containers} "
        #     # f"--limit-cpu 0.50 --limit-memory 512M "
        #     f"{env_string} "
        #     f"{image} sh /aixblock/deploy/run-platform.sh"
        # )

        # Thực thi lệnh qua SSH
        stdin, stdout, stderr = ssh.exec_command(docker_command)
        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()

        if error:
            print(f"Lỗi khi tạo dịch vụ: {error}")
            return None, platform_username, platform_password

        print(f"Dịch vụ đã tạo: {output}")
       # Lấy thông tin về service sau khi tạo
        service_inspect_command = f"sudo docker service inspect {service_name} --format '{{{{.Endpoint.Ports}}}}'"
        _stdin, _stdout, _stderr = ssh.exec_command(service_inspect_command)

        # Đọc kết quả và lấy cổng
        ports_info = _stdout.read().decode().strip()
        if ports_info:
            port_8081, port_8080 = self.extract_ports_platform(ports_info)
            print(f"Service ports: {ports_info}")
        else:
            print("No ports information available.")

        return port_8081

    def install_s3(self, public_ip, username, password, minio_user_username, minio_password, image="quay.io/minio/minio:latest"):
        ssh = self.ssh_connect(public_ip, username, password)
        if not ssh:
            return False, False
        
        self.ssh_docker_pull(ssh, image)
        port_9000, port_9001 = self.ssh_install_s3(ssh, minio_user_username, minio_password)
        return port_9000, port_9001
    
    def install_ml(self, public_ip, username, password, image="aixblock/template_ml"):
        ssh = self.ssh_connect(public_ip, username, password)
        if not ssh:
            return False
        
        self.ssh_docker_pull(ssh, image)
        self.docker_swarm_init_via_ssh(ssh)
        port_list = self.ssh_install_ml(ssh, image)
        return port_list
    
    def install_platform(self, public_ip, username, password, platform_username, platform_password, platform_email, client_id,  client_secret, image="aixblock/platform:latest"):
        ssh = self.ssh_connect(public_ip, username, password)
        if not ssh:
            return False, False, False, False
        
        self.ssh_docker_pull(ssh, "docker.io/library/postgres:latest")
        port_5432 = self.ssh_install_postgres(ssh)
        self.ssh_docker_pull(ssh, "redis")
        self.ssh_install_redis(ssh)
        self.ssh_docker_pull(ssh, "quay.io/minio/minio:latest")
        self.docker_swarm_init_via_ssh(ssh)
        port_9000, port_9001 = self.ssh_install_s3(ssh, platform_username, platform_password)

        self.ssh_docker_pull(ssh, image)
        port_8081 = self.ssh_install_platform(ssh, image, public_ip, port_9000, platform_username, platform_password, platform_email, port_5432,  client_id, client_secret, 1, 1)
        return port_8081, port_5432, port_9000, port_9001
    
    def install_compute(self, id, image=None, type='full', platform_username=None, platform_password=None, platform_email=None, client_id=None, client_secret=None, install_check=False, info_run=None):
        errors = None

        if not install_check:
            url = "https://api.gpu.exabits.ai/api/v1/virtual-machines/"
            
            payload = json.dumps({
                "name": f"{id}",
                "image_id": self.os_id,
                "flavor_id": f"{id}",
                "ssh_key": {
                    "name": "sshkey",
                    "public_key": "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIB6EQ4uTrwo2w+ZEBBgkAZN9kOX/sWMb5biqCet77m3q ubuntu"
                }
            })

            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}'
            }

            response = requests.request("POST", url, headers=headers, data=payload)
        else:
            url = f"https://api.gpu.exabits.ai/api/v1/virtual-machines/{id}"
            
            payload = json.dumps({
                "name": f"{id}",
                "image_id": self.os_id,
                "flavor_id": f"{id}",
                "ssh_key": {
                    "name": "sshkey",
                    "public_key": "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIB6EQ4uTrwo2w+ZEBBgkAZN9kOX/sWMb5biqCet77m3q ubuntu"
                }
            })

            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}'
            }

            response = requests.request("GET", url, headers=headers, data=payload)

        response_data = response.json()

        if response.status_code == 500:
            return False, id, response_data["message"]
        
        if 'status' in response_data and response_data["status"] == False:
            return False, id, response_data["message"]
        
        contract_id = response_data["data"]["id"]

        response = self.get_port_instance(contract_id)
        if not response:
            return False, id, errors
        
        public_ip = response['data']['public_ip']
        username = response['data']['login']['username']
        password = response['data']['login']['password']
        response['data']["old_id"] = id

        if type == 'full':
            if not platform_password:
                platform_password = self.generate_password()
                
            port_8081, port_5432, port_9000, port_9001 = self.install_platform(
                public_ip, username, password, platform_username, platform_password, platform_email, client_id, client_secret
            )

            if not port_8081:
                return False, id, "No connect ssh"

            self.add_firewall_rules(contract_id, port_8081, port_8081)
            self.add_firewall_rules(contract_id, port_5432, port_5432)
            self.add_firewall_rules(contract_id, port_9000, port_9000)
            self.add_firewall_rules(contract_id, port_9001, port_9001)

            response["data"]["info"] = {
                "user_username": platform_username,
                "user_password": platform_password,
                "user_email": platform_email,
            }

            response['data']["ports"] = {
                "8081": port_8081,
                "5432": port_5432,
                "9000": port_9000,
                "9001": port_9001
            }

        elif type == "ml":
            port_list = self.install_ml(public_ip, username, password, image)
            if not port_list:
                return False, id, "No connect ssh"
            
            response['data']["ports"] = {}

            for port in port_list:
                target_port = port["target_port"]
                published_port = port["published_port"]
                response['data']["ports"][target_port] = published_port
                self.add_firewall_rules(contract_id, published_port, published_port)

                # self.add_firewall_rules(contract_id, port_9090, port_9090)
                # self.add_firewall_rules(contract_id, port_6006, port_6006)
                # self.add_firewall_rules(contract_id, port_23456, port_23456)

                # response['data']["ports"] = {
                #     "9090": port_9090,
                #     "6006": port_6006,
                #     "23456": port_23456
                # }
        
        elif type == "deploy-ml":
            port_list = self.install_ml(public_ip, username, password, image)
            if not port_list:
                return False, id, "No connect ssh"
            
            response['data']["ports"] = {}

            for port in port_list:
                target_port = port["target_port"]
                published_port = port["published_port"]
                response['data']["ports"][target_port] = published_port
                self.add_firewall_rules(contract_id, published_port, published_port)

        elif type == "storage":
            if not platform_password:
                platform_password = self.generate_password()

            port_9000, port_9001 = self.install_s3(public_ip, username, password, platform_email, platform_password)
            if not port_9000:
                return False, id, "No connect ssh"
            
            self.add_firewall_rules(contract_id, port_9000, port_9000)
            self.add_firewall_rules(contract_id, port_9001, port_9001)

            response["data"]["info"] = {
                "user_username": platform_username,
                "user_password": platform_password,
                "user_email": platform_email,
            }

            response["data"]["ports"] = {
                "9000": port_9000,
                "9001": port_9001
            }
            
        if not response:
            self.delete_compute(contract_id)
            return False, id, errors
        
        response["data"]["info_compute"] = None
        if not install_check:
            info_compute = self.calc_core(public_ip, username, password)
            if info_compute:
                response["data"]["info_compute"] = info_compute

        return True, response, errors

    def calc_core(self, public_ip, username, password):
        try:
            ssh = self.ssh_connect(public_ip, username, password)
            sftp = ssh.open_sftp()
            sftp.put("./aixblock_core/plugins/cuda_cores.py", "cuda_cores.py")
            sftp.close()

            stdin, stdout, stderr = ssh.exec_command(f"python3 cuda_cores.py")
            output = stdout.read().decode()
            error = stderr.read().decode()

            if error:
                return False
        
            result_json = json.loads(output)
            return result_json[0]
        
        except Exception as e:
            return False
        
        
