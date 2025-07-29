import requests
import json
import paramiko
import os
import subprocess
import threading
from core.settings.base import AIXBLOCK_IMAGE_NAME, ENVIRONMENT, VAST_AI_API_KEY
from configs.models import InstallationService
from .models import ComputeMarketplace, ComputeGPU, History_Rent_Computes
from datetime import datetime, timedelta
import platform
from django.utils import timezone
import time
from users.models import User
import string
import random


def generate_password(length=12):
    # Các ký tự có thể sử dụng trong mật khẩu: chữ hoa, chữ thường và số
    characters = string.ascii_letters + string.digits
    # Tạo mật khẩu ngẫu nhiên
    password = "".join(random.choice(characters) for _ in range(length))
    return password


class VastAPIService:
    def __init__(self, api_key=VAST_AI_API_KEY, user=None):
        self.api_key = api_key
        self.user = user

    def vast_api_offer(self, data_filter):
        url = "https://cloud.vast.ai/api/v0/bundles/"

        payload_data = {
            "disk_space": {"gte": 16},
            "duration": {"gte": 262144},
            "verified": {"eq": True},
            "rentable": {"eq": True},
            "sort_option": {"0": ["dph_total", "asc"], "1": ["total_flops", "asc"]},
            "order": [
                ["inet_down", "desc"],
                ["total_flops", "desc"],
                ["dph_total", "asc"],
            ],
            "num_gpus": {"gte": 0, "lte": 18},
            "allocated_storage": 16,
            "limit": 20,
            "extra_ids": [],
            "type": "ask",
        }

        if data_filter.get("gpu_total_ram"):
            payload_data["gpu_totalram"] = {
                "gte": float(data_filter.get("gpu_total_ram", {}).get("from")),
                "lte": float(data_filter.get("gpu_total_ram", {}).get("to")),
            }
        if data_filter.get("search"):
            payload_data["gpu_name"] = {"in": [data_filter.get("search").upper()]}
        if data_filter.get('page_size'):
            payload_data["limit"] = data_filter.get("page_size")
        if data_filter.get("reliability2"):
            payload_data["reliability2"] = {
                "gte": float(data_filter.get("reliability", {}).get("from")) / 100,
                "lte": float(data_filter.get("reliability", {}).get("to")) / 100,
            }
        if data_filter.get("location") and data_filter.get("location").get("alpha2"):
            payload_data["geolocation"] = {
                "in": [data_filter.get("location").get("alpha2").upper()]
            }

        if data_filter.get("free_time") and data_filter.get("free_time").get("from"):
            from_date = datetime.strptime(
                data_filter.get("free_time").get("from"), "%d/%m/%Y"
            )
            to_date = datetime.strptime(
                data_filter.get("free_time").get("to"), "%d/%m/%Y"
            )
            current_date = datetime.now()
            delta_days = (to_date - current_date).days

            payload_data["duration"] = {"gte": float(delta_days)}  # convert float day

        if data_filter.get("price"):
            payload_data["dph_total"] = {
                "gte": float(data_filter["price"]["from"]),
                "lte": float(data_filter["price"]["to"])
            }
        if data_filter.get("gpu_count"):
            payload_data["num_gpus"] = {
                "gte": float(data_filter["gpu_count"]["from"]),
                "lte": float(data_filter["gpu_count"]["to"])
            }
        if data_filter.get("disk_bandwidth"):
            payload_data["disk_bw"] = {
                "gte": float(data_filter["disk_bandwidth"]["from"]),
                "lte": float(data_filter["disk_bandwidth"]["to"])
            }
        if data_filter.get("inet_up"):
            payload_data["inet_up"] = {
                "gte": float(data_filter["inet_up"]["from"]),
                "lte": float(data_filter["inet_up"]["to"]),
            }
        else:
            payload_data["inet_up"] = {
                "gte": 750
            }
        if data_filter.get("inet_down"):
            payload_data["inet_down"] = {
                "gte": float(data_filter["inet_down"]["from"]),
                "lte": float(data_filter["inet_down"]["to"])
            }
        else:
            payload_data["inet_down"] = {
                "gte": 750
                # "lte": float(data_filter["inet_down"]["to"])
            }
        if data_filter.get("open_port"):
            payload_data["direct_port_count"] = {
                "gte": float(data_filter["open_port"]["from"]),
                "lte": float(data_filter["open_port"]["to"])
            }
        if data_filter.get("tflops"):
            payload_data["total_flops"] = {
                "gte":float(data_filter["tflops"]["from"]),
                "lte":float(data_filter["tflops"]["to"])
            }

        def remove_empty_values(d):
            """
            Hàm này loại bỏ các key có giá trị là "" hoặc None ở bất kỳ cấp độ nào trong dict.
            """
            if isinstance(d, dict):
                return {k: remove_empty_values(v) for k, v in d.items() if v not in ["", None] and remove_empty_values(v) != {}}
            elif isinstance(d, list):
                return [remove_empty_values(i) for i in d if i not in ["", None]]
            else:
                return d

        payload_data = remove_empty_values(payload_data)

        print(payload_data)

        payload = json.dumps(payload_data)

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {VAST_AI_API_KEY}',
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        data = json.loads(response.text)
        result = []
        # computes_types = ['full', 'model-training']
        if 'offers' in data:
            for offer in data['offers']:
                result_dict = { offer["gpu_name"]:[]}
                start_date = offer["start_date"]
                end_date = offer["end_date"]
                effect_ram = 1
                if offer["cpu_cores"] and offer["cpu_cores_effective"]:
                    effect_ram = offer["cpu_cores"]/offer["cpu_cores_effective"]
                # Thay thế None bằng 0
                start_date = float(start_date) if start_date is not None else 0.0
                end_date = float(end_date) if end_date is not None else 0.0

                # Tính toán max_duration
                max_duration = int((end_date - start_date)/86400)
                # for i in range(len(offer['gpu_ids'])):
                #     # for computes_type in computes_types:
                result_dict[offer["gpu_name"]].append(
                        {
                            "id": offer["id"],
                            "vast_contract_id": offer["ask_contract_id"],
                            "compute_marketplace": {
                                "id": offer["id"],
                                "name": offer["cpu_name"],
                                "deleted_at": None,
                                "infrastructure_id": f'{offer["id"]}',
                                "owner_id": 0,
                                "arthor_id": 0,
                                "catalog_id": 0,
                                "ip_address": f'{offer["public_ipaddr"]}',
                                "port": f'{offer["host_id"]}',
                                "config": json.dumps(
                                    {
                                        "cpu": offer["cpu_name"],
                                        "ram": offer["cpu_ram"],
                                        "disk": f'{offer["disk_space"]}',
                                        "diskType": "SSD",
                                        "os": "Linux",
                                    }
                                ),
                                "is_using_cpu": False,
                                "compute_type": "full",
                                "status": "in_marketplace",
                                "type": "MODEL-PROVIDER-VAST",
                                "file": offer["logo"],
                                "cpu_price": None,
                                "compute_time_working": {},
                            },
                            "prices": [
                                {
                                    "id": 0,
                                    "token_symbol": "USD",
                                    "price": round(offer["dph_total"], 3),
                                    "unit": "hour",
                                    "type": "gpu",
                                    "compute_gpu_id": 0,
                                    "compute_marketplace_id": 0,
                                    "model_marketplace_id": None,
                                }
                            ],
                            "gpu_name": offer["gpu_name"],
                            "power_consumption": "360w",
                            "memory_usage": None,
                            "power_usage": None,
                            "gpu_index": 0,
                            "gpu_memory": f'{offer["gpu_mem_bw"]}',
                            "gpu_tflops": f'{offer["total_flops"]}',
                            "branch_name": offer["gpu_arch"],
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
                            "provider_id": offer["host_id"],  # provider id
                            "per_gpu_ram": int(offer["gpu_ram"]/1000),  # convert to GB
                            "max_cuda_version": offer["cuda_max_good"],
                            "per_gpu_memory_bandwidth": round(offer["gpu_mem_bw"],2),  # convert to GB
                            "motherboard": offer["mobo_name"],
                            "internet_up_speed": offer["inet_up"],  # convert to Mbps
                            "internet_down_speed": offer["inet_down"],  # convert to Mbps
                            "number_of_pcie_per_gpu": f'{offer["pci_gen"]}.0,16x',
                            "per_gpu_pcie_bandwidth": offer["pcie_bw"],  # convert to GB
                            "eff_out_of_total_nu_of_cpu_virtual_cores": f'{round(offer["cpu_cores_effective"], 1)}/{offer["cpu_cores"]}',
                            "eff_out_of_total_system_ram": f'{int(round(offer["cpu_ram"]/1000, 0))}/{int(round(offer["cpu_ram"]/1000, 0)*effect_ram)}',  # convert to GB,
                            "max_duration": max_duration,  # convert to day
                            "reliability": round((offer["reliability"]*100),2),  # %
                            "dl_performance_score": round(offer["dlperf_per_dphtotal"], 2),  # %
                            "dlp_score": round(offer["dlperf"], 2),  # DLP/$/hr,
                            "location_id": offer["geolocode"],
                            "location_alpha2": offer["geolocation"],
                            "location_name": offer["geolocation"],
                            "datacenter": "datacenter" if offer["hosting_type"] == 1 else None,  # datacenter/ miners/ consumerGpu
                        }
                    )
                # result_dict_copy = result_dict.copy()
                # result.append(result_dict_copy)

                # result_dict[offer["cpu_name"]][0]["compute_marketplace"]["compute_type"] = "model-training"
                result.append(result_dict)

        return result

    def vast_api_offer_old(self):
        url = "https://cloud.vast.ai/api/v0/bundles/?q=%7B%22disk_space%22%3A%7B%22gte%22%3A16%7D%2C%22duration%22%3A%7B%22gte%22%3A262144%7D%2C%22verified%22%3A%7B%22eq%22%3Atrue%7D%2C%22rentable%22%3A%7B%22eq%22%3Atrue%7D%2C%22sort_option%22%3A%7B%220%22%3A%5B%22dph_total%22%2C%22asc%22%5D%2C%221%22%3A%5B%22total_flops%22%2C%22asc%22%5D%7D%2C%22order%22%3A%5B%5B%22dph_total%22%2C%22asc%22%5D%2C%5B%22total_flops%22%2C%22asc%22%5D%5D%2C%22num_gpus%22%3A%7B%22gte%22%3A0%2C%22lte%22%3A18%7D%2C%22allocated_storage%22%3A16%2C%22limit%22%3A256%2C%22extra_ids%22%3A%5B%5D%2C%22type%22%3A%22ask%22%2C%22direct_port_count%22%3A%7B%22gte%22%3A2%7D%7D"
        headers = {
            'Accept': 'application/json'
        }

        response = requests.get(url, headers=headers)

        data = json.loads(response.text)

        result = []

        computes_types = ['full', 'ml']

        for offer in data['offers']:
            for i in range(len(offer['gpu_ids'])):
                result_dict = {
                    "id": offer["ask_contract_id"],
                    "vast_contract_id": offer["ask_contract_id"],
                    "created_by": None,
                    "sortField": None,
                    "compute_gpus": [],
                    "cpu_price": None,
                    # "name": f'{offer["public_ipaddr"]}',
                    "name": offer["gpu_name"],
                    "created_at": "2024-05-06T04:20:17.921978Z",
                    "updated_at": "2024-05-06T04:20:17.921983Z",
                    "deleted_at": None,
                    "infrastructure_id": "",
                    "owner_id": 1,
                    "author_id": 1,
                    "catalog_id": 0,
                    "organization_id": 1,
                    "order": 0,
                    "ip_address": offer["public_ipaddr"],
                    "port": f'{offer["host_id"]}',
                    "docker_port": "4243",
                    "kubernetes_port": "4243",
                    "config": {
                        "cpu": offer["cpu_name"],
                        "ram": offer["cpu_ram"],
                        "disk": f'{offer["disk_space"]}',
                        "diskType": "SSD",
                        "os": "Linux"
                    },
                    "is_using_cpu": False,
                    "status": "in_marketplace",
                    "file": offer["logo"],
                    "type": "MODEL-PROVIDER",
                    "infrastructure_desc": "",
                    "callback_url": "https://app.aixblock.io/oauth/login/callback",
                    "client_id": "Kb6nFOoFmHeAFmDIw2kJirdMISwn2zxv4wWnkhwP",
                    "client_secret": "Kb6nFOoFmHeAFmDIw2kJirdMISwn2zxv4wWnkhwP",
                    "ssh_key": None,
                    "card": None,
                    "prices": 222,
                    "compute_type": "full"
                }

                compute_gpus = {
                    "id": offer["ask_contract_id"],
                    "vast_contract_id": offer["ask_contract_id"],
                    "prices": [{
                        "id": 0,
                        "token_symbol": "eth",
                        "price": round(offer["dph_total"], 3),
                        "unit": "hour",
                        "type": "gpu",
                        "compute_gpu_id": 0,
                        "compute_marketplace_id": 0,
                        "model_marketplace_id": None
                    }],
                    "gpu_name": offer["gpu_name"],
                    "power_consumption": "360w",
                    "memory_usage": None,
                    "power_usage": None,
                    "gpu_index": 0,
                    "gpu_memory": f'{offer["gpu_mem_bw"]}',
                    "gpu_tflops": f'{offer["total_flops"]}',
                    "branch_name": offer["gpu_arch"],
                    "batch_size": 8,
                    "gpu_id": "gpsu-789a-cbsd-xysz-45s6",
                    "serialno": None,
                    "created_at": "2024-05-06T04:20:17.921978Z",
                    "updated_at": "2024-05-06T04:20:17.921983Z",
                    "deleted_at": None,
                    "quantity_used": 0,
                    "status": "in_marketplace",
                    "owner_id": 1,
                    "compute_marketplace": 1,
                    "infrastructure_id": "6hf3rccrtrj9"
                }

                result_dict["compute_gpus"].append(compute_gpus)
                result_dict["config"] = json.dumps(result_dict["config"])

                for computes_type in computes_types:
                    result_dict["compute_type"] = computes_type
                    # result_dict[offer["cpu_name"]]["config"] = json.dumps(result_dict["config"])
                    result.append(result_dict)
                # result.append(result_dict)

        return result

    def vast_api_install_platform(self, contract_id, image=None, user_id= None, compute = None):
        if image is None:
            image_detail = InstallationService.objects.filter(
                environment=ENVIRONMENT, image=AIXBLOCK_IMAGE_NAME, deleted_at__isnull=True
            ).first()
            if image_detail is not None: 
                image = str(image_detail.image) + ":" + str(image_detail.version)
            else:
                image = AIXBLOCK_IMAGE_NAME + ":latest"
        if user_id is not None:
            user = User.objects.filter(id=user_id).first()

        minio_password = None
        minio_user = None
        minio_url = None
        if compute:
            minio_user = compute.username
            minio_password = compute.get_password()
            minio_url = f"{compute.ip_address}:{compute.port}"

        url = f"https://console.vast.ai/api/v0/asks/{contract_id}/"
        user_email = user.email if user and user.email else "admin@wow-ai.com"
        user_username = user.username if user and user.username else "admin"
        password = generate_password()
        payload = json.dumps(
            {
                "client_id": "me",
                "image": image,
                "env": {
                    "-p 5432:5432": "1",
                    "-p 8081:8081": "1",
                    "AXB_PUBLIC_PORT": 8081,
                    "DJANGO_DB": "sqlite",
                    # "POSTGRES_HOST": "173.208.162.74",
                    # "POSTGRES_PASSWORD": "@9^xwWA",
                    # "POSTGRES_NAME": "platform_v2",
                    # "POSTGRES_USER": "postgres",
                    "ADMIN_EMAIL": str(user_email),
                    "ADMIN_USERNAME": str(user_username),
                    "ADMIN_PASSWORD": str(password),
                    "MINIO_API_URL": minio_url,
                    "MINIO_USER": minio_user,
                    "MINIO_PASSWORD": minio_password,
                },
                # "args_str": "./deploy/docker-entrypoint.sh ",
                "args_str": "sh /aixblock/deploy/run-platform.sh",
                "onstart": None,
                # "runtype": "ssh ssh_direc ssh_proxy",
                "runtype": "args",
                "image_login": None,
                "use_jupyter_lab": False,
                "jupyter_dir": None,
                "python_utf8": False,
                "lang_utf8": False,
                "disk": 40,
            }
        )

        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {VAST_AI_API_KEY}',
            'Content-Type': 'application/json'
        }

        response = requests.request("PUT", url, headers=headers, data=payload)
        response_data = response.json()

        if response_data['success']:
            return response_data['new_contract']
        else:
            return response_data['success']

    def vast_ai_install_ml(self, contract_id, ml_image):
        url = f"https://cloud.vast.ai/api/v0/asks/{contract_id}/"

        payload = json.dumps({
            "client_id": "me",
            # "image": "aixblock/template_ml-mnist:latest",
            "image": ml_image,
            "env": {
                "-p 9090:9090": "1",
                "-p 6006:6006": "1",
                "-p 23456:23456": "1"
            },
            "args_str": "gunicorn --bind :9090 --workers 1 --threads 1 --timeout 0 _wsgi:app --certfile=/app/cert.pem --keyfile=/app/privkey.pem", 
            "onstart": None,
            "runtype": "args",
            "image_login": None,
            "use_jupyter_lab": False,
            "jupyter_dir": None,
            "python_utf8": False,
            "lang_utf8": False,
            "disk": 40
        })
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {VAST_AI_API_KEY}',
            'Content-type': 'application/json'
        }
        print(headers)

        response = requests.request("PUT", url, headers=headers, data=payload)

        response_data = response.json()
        print(response_data)
        if response_data['success']:
            return response_data['new_contract']
        else:
            return response_data['success']

    def vast_ai_install_s3(self, contract_id, s3_image="quay.io/minio/minio:latest", user_id= None):
        url = f"https://cloud.vast.ai/api/v0/asks/{contract_id}/"

        if user_id is not None:
            user = User.objects.filter(id=user_id).first()

        user_email = user.email if user and user.email else "admin@wow-ai.com"
        password = generate_password()

        payload = json.dumps({
            "client_id": "me",
            # "image": "wowai/ml_sample:latest",
            "image": s3_image,
            "env": {
                "-p 9000:9000": "1",
                "-p 9001:9001": "1",
                "MINIO_ROOT_USER": user_email,
                "MINIO_ROOT_PASSWORD": password
            },
            "args_str": "minio server /data --console-address :9001",
            "onstart": None,
            "runtype": "args",
            "image_login": None,
            "use_jupyter_lab": False,
            "jupyter_dir": None,
            "python_utf8": False,
            "lang_utf8": False,
            "disk": 40
        })

        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {VAST_AI_API_KEY}',
            'Content-type': 'application/json'
        }
        print(headers)

        response = requests.request("PUT", url, headers=headers, data=payload)

        response_data = response.json()
        print(response_data)
        if response_data['success']:
            return response_data['new_contract']
        else:
            return response_data['success']

    def vast_ai_ssh(self, contract_id, ssh_key):
        url = f"https://cloud.vast.ai/api/v0/instances/{contract_id}/ssh/"

        payload = json.dumps({
            "instance_id": contract_id,
            "ssh_key": ssh_key
        })

        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {VAST_AI_API_KEY}',
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        return response.text

    def get_instance_info(self, contract_id):
        url = f"https://console.vast.ai/api/v0/instances/{contract_id}"

        payload = {}

        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {VAST_AI_API_KEY}',
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        response_data = response.json()

        return response_data

    def stop_start_instance(self, contract_id, action='start'):
        url = f"https://cloud.vast.ai/api/v0/instances/{contract_id}/"
        state = "running" if action == "start" else "stopped"

        headers = {
            "Accept": "application/json, text/plain, */*",
            "Authorization": f"Bearer {VAST_AI_API_KEY}",
            "Referer": "https://cloud.vast.ai/instances/",
            "Content-Type": "application/json",
        }

        response = requests.put(
            url, headers=headers, json={"state": state}
        )
        time.sleep(10)
        if response.status_code == 200:
            print(f"Instance {action} successfully.")
        else:
            print(f"Failed to {action} instance. Status code: {response.status_code}")
            raise Exception(f"Failed to {action} instance. Status code: {response.status_code}")
        response_data = response.json()
        return response_data

    def delete_instance_info(self, contract_id):
        url = f"https://console.vast.ai/api/v0/instances/{contract_id}/"

        payload = {}

        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {VAST_AI_API_KEY}'
        }

        response = requests.request("DELETE", url, headers=headers, data=payload)
        response_data = response.json()

        return response_data

    def get_port_instance(self, contract_id, port_ip, user_id=0, old_id=0):
        get_port = False
        # host = ''
        # port = ''
        import time
        install_compute = 0
        while not get_port:
            try:
                response = self.get_instance_info(contract_id)
                if not response['instances']:
                    return False

                # if install_compute == 0:
                #     create_compute_vast_to_db(response, user_id)
                #     install_compute += 1

                if response['instances']['status_msg']=='Cannot connect to the Docker daemon at unix:///var/run/docker.sock. Is the docker daemon running?\n':
                    return False
                elif 'Error response from daemon' in response['instances']['status_msg']:
                    return False

                host = response['instances']["public_ipaddr"]
                # port = response['instances']["ports"][f"22/tcp"][0]["HostPort"]
                port_platform = response['instances']["ports"][f"{port_ip}/tcp"][0]["HostPort"]
                response['instances']['old_id'] = old_id
                print(response)
                time.sleep(10)
                get_port = True
            except Exception as e:
                print(e)
                time.sleep(10)
                get_port = False

        return response

    def generate_ssh_key_pair(self):
        # Detect the platform
        current_platform = platform.system()

        # Expand the home directory
        home_dir = os.path.expanduser("~")
        private_key_path = os.path.join(home_dir, ".ssh", "id_rsa")
        public_key_path = os.path.join(home_dir, ".ssh", "id_rsa.pub")

        # Create .ssh directory if it does not exist
        os.makedirs(os.path.dirname(private_key_path), exist_ok=True)

        # Generate the RSA key pair
        # subprocess.run(["ssh-keygen", "-t", "rsa", "-f", private_key_path, "-N", ""])

        # Add the private key to the SSH agent
        if current_platform == "Windows":
            subprocess.run(["ssh-keygen", "-t", "rsa", "-f", private_key_path, "-N", "", "-y"], input="y\n", text=True)

            # For Windows, use ssh-add from Git Bash or similar environments
            subprocess.run(["ssh-add", private_key_path], shell=True)
        elif current_platform == "Linux" or  current_platform == "linux" or current_platform == "Ubuntu":
            subprocess.run(["apt-get", "install", "openssh-server"], check=True)  
            subprocess.run(["systemctl", "enable", "ssh"], check=True) 
            subprocess.run("eval $(ssh-agent -s)", shell=True, check=True)       
            subprocess.run(["ssh-keygen", "-t", "rsa", "-f", private_key_path, "-N", "", "-y"], input="y\n", text=True)
            subprocess.run(["ssh-add", private_key_path], shell=True)
        else:
            subprocess.run(["ssh-keygen", "-t", "rsa", "-f", private_key_path, "-N", "", "-y"], input="y\n", text=True)
            # For Linux and macOS
            subprocess.run(["ssh-add", private_key_path], shell=True)
        # Read the public key
        try:
            with open(public_key_path, "r") as f:
                public_key_content = f.read()
                return public_key_path, public_key_content
        except FileNotFoundError:
            print("Public key not found at:", public_key_path)
            return None

    def func_install_compute_vastai(self, id, image, type='full', user_id=0, compute = None):
        if type == 'full':
            contract_id = self.vast_api_install_platform(id, image, user_id=user_id, compute=compute)
            if not contract_id:
                return False, id
            response = self.get_port_instance(contract_id, 8081, user_id, id)
            # port = response['instances']["ports"][f"8081/tcp"][0]["HostPort"]

        elif type == "ml":
            contract_id = self.vast_ai_install_ml(id, image)
            if not contract_id:
                return False, id
            response = self.get_port_instance(contract_id, 9090, user_id, id)
            # port = response['instances']["ports"][f"9090/tcp"][0]["HostPort"]

        elif type == "storage":
            contract_id = self.vast_ai_install_s3(id, image, user_id)
            if not contract_id:
                return False, id
            response = self.get_port_instance(contract_id, 9001, user_id, id)

        if not response:
            self.delete_instance_info(contract_id)
            return False, id

        return True, response

    # import re
    # host = response['instances']["public_ipaddr"]
    # host = re.findall(r'\d+\.\d+\.\d+\.\d+', host)[0]
    # print(host, port)
    # def postgresql_setup(host, port):
    #     check = False
    #     while not check:
    #         try:
    #             client = paramiko.client.SSHClient()
    #             client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #             client.connect(host, username="root", key_filename=public_key_path, port=port, allow_agent=True, timeout=None)
    #             _stdin, stdout, stderr = client.exec_command("curl https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -")
    #             print(stderr.read().decode())

    #             _stdin, stdout, stderr = client.exec_command("DEBIAN_FRONTEND=noninteractive TZ=UTC apt install -y postgresql postgresql-contrib")
    #             print(stderr.read().decode())

    #             # _stdin, stdout, stderr = client.exec_command("apt show postgresql")
    #             # print(stderr.read().decode())
    #             _stdin, stdout, stderr = client.exec_command("/etc/init.d/postgresql start")
    #             print(stderr.read().decode())

    #             _stdin, stdout, stderr = client.exec_command(f"sudo -u postgres psql -c \"ALTER USER postgres WITH PASSWORD '@9^xwWA';\"")
    #             print(stderr.read().decode())
    #             _stdin, stdout, stderr = client.exec_command(f"sudo -u postgres psql -c \"CREATE DATABASE platform_v2;\"")
    #             print(stderr.read().decode())
    #             _stdin, stdout, stderr = client.exec_command(f"sudo -u postgres psql -c \"GRANT ALL PRIVILEGES ON DATABASE platform_v2 TO postgres;\"")
    #             print(stderr.read().decode())

    #             # _stdin, stdout, stderr = client.exec_command("exit")

    #             _stdin, stdout, stderr = client.exec_command("python3 ../aixblock/aixblock_core/manage.py migrate")
    #             print(stdout.read().decode())

    #             # _stdin, stdout, stderr = client.exec_command("python3 ../aixblock/aixblock_core/manage.py createsuperuser --email abc@gmail.com --skip-checks --noinput")
    #             # _stdin, stdout, stderr = client.exec_command("python3 ../aixblock/aixblock_core/manage.py default --created_by_id 1 --status create")
    #             # print(stdout.read().decode())
    #             _stdin, stdout, stderr = client.exec_command("python3 ../aixblock/aixblock_core/manage.py create_superuser_with_password --username admin --password 123321 --noinput --email admin@wow-ai.com")
    #             print(stdout.read().decode())

    #             _stdin, stdout, stderr = client.exec_command("python3 ../aixblock/aixblock_core/manage.py create_organization The_title_of_the_organization")
    #             print(stdout.read().decode())

    #             _stdin, stdout, stderr = client.exec_command("python3 ../aixblock/aixblock_core/manage.py seed_templates")
    #             print(stdout.read().decode())

    #             _stdin, stdout, stderr = client.exec_command("python3 ../aixblock/aixblock_core/manage.py runsslserver 0.0.0.0:8081")
    #             print(stdout.read().decode())
    #             _stdin.close()
    #             check = True
    #         except Exception as e:
    #             # if 'no sessions' in e:
    #             #     delete_instance_info(contract_id)
    #             #     continue
    #             print(e)
    #             check = False

    # if type == 'full':
    #     thread = threading.Thread(target=postgresql_setup, args=(host, port))
    #     thread.start()

vast_service = VastAPIService()

# response = func_install_compute_vastai(10755813, "wowai/dataset_live:latest", 'full')
# print(response)

def create_compute_vast_to_db(response, user_id):
    compute = ComputeMarketplace.objects.filter(
        infrastructure_id=response["instances"]["id"]
    ).update(
        name=response["instances"]["public_ipaddr"],
        status="rented_bought",
        infrastructure_id=response["instances"]["id"],
        owner_id=0,
        author_id=user_id,
        organization_id=1,
        config=json.dumps(
            {
                "cpu": response["instances"]["cpu_name"],
                "ram": response["instances"]["cpu_ram"],
                "disk": response["instances"]["disk_space"],
                "diskType": "SSD",
                "os": "Linux",
            }
        ),
        ip_address=response["instances"]["public_ipaddr"],
        port=8080,
        type="MODEL-PROVIDER-VAST",
        client_id="",
        client_secret="",
        ssh_key="",
        price=0,
        compute_type="full",
        is_using_cpu=False,
    )

    compute_gpu = ComputeGPU.objects.filter(infrastructure_id=compute).update(
        compute_marketplace=compute,
        infrastructure_id=compute,
        gpu_id="0",
        gpu_name=response["instances"]["gpu_name"],
        memory_usage=response["instances"]["mem_usage"],
        gpu_memory=response["instances"]["gpu_totalram"],
        gpu_tflops=response["instances"]["total_flops"],
        status="renting",
    )

    time_start = timezone.now()
    time_end = time_start + timedelta(hours=1)

    History_Rent_Computes.objects.create(
        account_id=user_id,
        compute_marketplace=compute,
        compute_gpu=compute_gpu,
        status="renting",
        # order_id=payment["order_id"],
        rental_hours=1,
        time_end=time_end,
        compute_install="installing",
    )
