import json
import time
import math
import string
import random
import requests
from users.models import User
from datetime import datetime, timedelta
from configs.models import InstallationService
from core.settings.base import AIXBLOCK_IMAGE_NAME, ENVIRONMENT, VAST_AI_API_KEY
import logging

from .base_provider import ProviderBase

class VastProvider(ProviderBase):
    def __init__(self, api_key=VAST_AI_API_KEY):
        super().__init__(api_key)

    def list_compute(self, data_filter):
        url = "https://cloud.vast.ai/api/v0/bundles/"
        # type=ask
        payload_data = {
            "disk_space": {"gte": 40},
            "duration": {"gte": 262144},
            "verified": {"eq": True},
            "rentable": {"eq": True},
            "sort_option": {"0": ["dph_total", "asc"], "1": ["total_flops", "asc"]},
            "order": [
                ["inet_down", "desc"],
                ["total_flops", "desc"],
                ["dph_total", "asc"],
            ],
            # "num_gpus": {"gte": 0, "lte": 18},
            "allocated_storage": 40,
            "limit": 20,
            "extra_ids": [],
            "type": "ask" 
        }

        if data_filter.get("gpu_total_ram"):
            payload_data["gpu_totalram"] = {
                "gte": float(data_filter.get("gpu_total_ram", {}).get("from")),
                "lte": float(data_filter.get("gpu_total_ram", {}).get("to")),
            }
        # if data_filter.get("search"):
        #     payload_data["gpu_name"] = {"in": [data_filter.get("search").upper()]}
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
        if data_filter.get('disk_type') == "nvme":
            payload_data["disk_name"] = {"eq": data_filter.get("disk_type")}
        if data_filter.get("disk_type") == "ssd":
            payload_data["disk_name"] = {"neq": "nvme"}
        if data_filter.get("gpus_machine") and data_filter.get("gpus_machine") != 'any':
            num_gpus = data_filter.get("gpus_machine").replace("x", "")
            payload_data["num_gpus"] = {"eq": num_gpus}
        if data_filter.get("provider"):
            provider = data_filter.get("provider")
            payload_data["gpu_arch"] = {"eq": provider}
        if data_filter.get("disk_size"):
            disk_size = data_filter.get("disk_size")
            payload_data["disk_space"] = {"gte": disk_size}
            payload_data["allocated_storage"] = disk_size

        def remove_empty_values(d):
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
            'Authorization': f'Bearer {self.api_key}',
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        data = json.loads(response.text)
        result = []

        if 'offers' in data:
            for offer in data['offers']:
                total_price_vast = offer['search']['totalHour']
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
                                    "price": math.ceil(total_price_vast * 1000) / 1000,
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
                            "num_gpus": offer["num_gpus"],
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

                result.append(result_dict)

        return result

    def info_compute(self, id):
        url = f"https://console.vast.ai/api/v0/instances/{id}"

        payload = {}

        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.api_key}',
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        response_data = response.json()

        return response_data

    def delete_compute(self, id):
        url = f"https://console.vast.ai/api/v0/instances/{id}/"

        payload = {}

        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }

        response = requests.request("DELETE", url, headers=headers, data=payload)
        response_data = response.json()

        return response_data

    def start_compute(self, id):
        url = f"https://cloud.vast.ai/api/v0/instances/{id}/"

        headers = {
            "Accept": "application/json, text/plain, */*",
            "Authorization": f"Bearer {self.api_key}",
            "Referer": "https://cloud.vast.ai/instances/",
            "Content-Type": "application/json",
        }

        response = requests.put(
            url, headers=headers, json={"state": "running"}
        )
        time.sleep(10)
        if response.status_code == 200:
            print(f"Instance start successfully.")
        else:
            print(f"Failed to start instance. Status code: {response.status_code}")
            raise Exception(f"Failed to start instance. Status code: {response.status_code}")
        response_data = response.json()
        return response_data

    def reset_compute(self, id):
        url = f"https://cloud.vast.ai/api/v0/instances/reboot/{id}/"

        headers = {
            "Accept": "application/json, text/plain, */*",
            "Authorization": f"Bearer {self.api_key}",
            "Referer": "https://cloud.vast.ai/instances/",
            "Content-Type": "application/json",
        }

        response = requests.put(
            url, headers=headers,# json={"state": "running"}
        )
        time.sleep(10)
        if response.status_code == 200:
            print(f"Instance start successfully.")
        else:
            print(f"Failed to start instance. Status code: {response.status_code}")
            raise Exception(f"Failed to start instance. Status code: {response.status_code}")
        response_data = response.json()
        return response_data

    def stop_compute(self, id):
        url = f"https://cloud.vast.ai/api/v0/instances/{id}/"

        headers = {
            "Accept": "application/json, text/plain, */*",
            "Authorization": f"Bearer {self.api_key}",
            "Referer": "https://cloud.vast.ai/instances/",
            "Content-Type": "application/json",
        }

        response = requests.put(
            url, headers=headers, json={"state": "stopped"}
        )
        time.sleep(10)
        if response.status_code == 200:
            print(f"Instance stop successfully.")
        else:
            print(f"Failed to stop instance. Status code: {response.status_code}")
            raise Exception(f"Failed to stop instance. Status code: {response.status_code}")
        response_data = response.json()
        return response_data

    def vast_api_install_platform(self, contract_id, image=None, user_id= None, compute = None, disk_size=None):
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
                    "ADMIN_EMAIL": str(user_email),
                    "ADMIN_USERNAME": str(user_username),
                    "ADMIN_PASSWORD": str(password),
                    "MINIO_API_URL": minio_url,
                    "MINIO_USER": minio_user,
                    "MINIO_PASSWORD": minio_password,
                },
                "args_str": "sh /aixblock/deploy/run-platform.sh",
                "onstart": None,
                "runtype": "args",
                "image_login": None,
                "use_jupyter_lab": False,
                "jupyter_dir": None,
                "python_utf8": False,
                "lang_utf8": False,
                "disk": disk_size,
            }
        )

        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        response = requests.request("PUT", url, headers=headers, data=payload)
        error = None
        try:
            response_data = response.json()
        except ValueError:
            logging.error("Invalid JSON response")
            return None

        if 'error' in response_data:
            logging.error(f"Error in response: {response_data['error']}")
            error = response_data
            return None, error

        if 'success' in response_data:
            if response_data['success']:
                return response_data['new_contract'], None
            else:
                logging.error("Installation was not successful")
                return None
        else:
            logging.error("Key 'success' not found in response data")
            return None

    def vast_ai_install_ml(self, contract_id, ml_image, info_run=None, disk_size=None):
        url = f"https://cloud.vast.ai/api/v0/asks/{contract_id}/"

        env = {
                "-p 9090:9090": "1",
                "-p 6006:6006": "1",
                "-p 23456:23456": "1"
            }
        
        args_str = "gunicorn --bind :9090 --workers 1 --threads 1 --timeout 0 _wsgi:app --certfile=/app/cert.pem --keyfile=/app/privkey.pem"
        port_main = 9090

        if info_run:
            try:
                if "exposed_ports" in info_run and info_run["exposed_ports"]:
                    port_main = info_run["exposed_ports"][0]
                    
                    for port in info_run["exposed_ports"]:
                        if port not in ["9009", "6006", "23456"]:
                            port_mapping = f"-p {port}:{port}"
                            env[port_mapping] = "1"
            except Exception as e:
                print(f"An error occurred: {e}")
        
            try:
                if "run_command" in info_run and info_run["run_command"]:
                    args_str = info_run["run_command"]
                    if "$PORT" in args_str:
                        args_str = info_run["run_command"].replace("$PORT", int(port_main))

            except Exception as e:
                print(f"An error occurred: {e}")

        payload = json.dumps({
            "client_id": "me",
            # "image": "aixblock/template_ml-mnist:latest",
            "image": ml_image,
            "env": env,
            "args_str": args_str, 
            "onstart": None,
            "runtype": "args",
            "image_login": None,
            "use_jupyter_lab": False,
            "jupyter_dir": None,
            "python_utf8": False,
            "lang_utf8": False,
            "disk": disk_size
        })
    
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.api_key}',
            'Content-type': 'application/json'
        }
        print(headers)

        response = requests.request("PUT", url, headers=headers, data=payload)
        error = None
        try:
            response_data = response.json()
        except ValueError:
            logging.error("Invalid JSON response")
            return None

        if 'error' in response_data:
            logging.error(f"Error in response: {response_data['error']}")
            error = response_data
            return None, error

        if 'success' in response_data:
            if response_data['success']:
                return response_data['new_contract'], None
            else:
                logging.error("Installation was not successful")
                return None
        else:
            logging.error("Key 'success' not found in response data")
            return None

    def vast_ai_install_deploy_ml(self, contract_id, ml_image, checkpoint_url, info_run=None, disk_size=None):
        url = f"https://cloud.vast.ai/api/v0/asks/{contract_id}/"

        env = {
                "-p 9090:9090": "1",
                "-p 6006:6006": "1",
                "-p 23456:23456": "1"
            }
        
        args_str = "gunicorn --bind :9090 --workers 1 --threads 1 --timeout 0 _wsgi:app --certfile=/app/cert.pem --keyfile=/app/privkey.pem"

        if info_run:
            try:
                if "exposed_ports" in info_run and info_run["exposed_ports"]:
                    for port in info_run["exposed_ports"]:
                        if port not in ["9009", "6006", "23456"]:
                            port_mapping = f"-p {port}:{port}"
                            env[port_mapping] = "1"
            except Exception as e:
                print(f"An error occurred: {e}")
        
            try:
                if "run_command" in info_run and info_run["run_command"]:
                    args_str = info_run["run_command"]

            except Exception as e:
                print(f"An error occurred: {e}")

        payload = json.dumps({
            "client_id": "me",
            # "image": "aixblock/template_ml-mnist:latest",
            "image": ml_image,
            "env": env,
            "args_str": args_str, 
            "onstart": None,
            "runtype": "args",
            "image_login": None,
            "use_jupyter_lab": False,
            "jupyter_dir": None,
            "python_utf8": False,
            "lang_utf8": False,
            "disk": disk_size
        })
    
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.api_key}',
            'Content-type': 'application/json'
        }
        print(headers)

        response = requests.request("PUT", url, headers=headers, data=payload)
        error = None
        try:
            response_data = response.json()
        except ValueError:
            logging.error("Invalid JSON response")
            return None

        if 'error' in response_data:
            logging.error(f"Error in response: {response_data['error']}")
            error = response_data
            return None, error

        if 'success' in response_data:
            if response_data['success']:
                return response_data['new_contract'], None
            else:
                logging.error("Installation was not successful")
                return None
        else:
            logging.error("Key 'success' not found in response data")
            return None
        
    def vast_ai_install_s3(self, contract_id, s3_image="quay.io/minio/minio:latest", user_id= None, disk_size=None):
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
            "disk": disk_size
        })

        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.api_key}',
            'Content-type': 'application/json'
        }
        print(headers)

        response = requests.request("PUT", url, headers=headers, data=payload)
        error = None
        try:
            response_data = response.json()
        except ValueError:
            logging.error("Invalid JSON response")
            return None

        if "error" in response_data:
            logging.error(f"Error in response: {response_data['error']}")
            error = response_data
            return None, error

        if "success" in response_data:
            if response_data["success"]:
                return response_data["new_contract"], None
            else:
                logging.error("Installation was not successful")
                return None
        else:
            logging.error("Key 'success' not found in response data")
            return None

    def get_port_instance(self, contract_id, port_ip, old_id=0):
        get_port = False
        import time
        while not get_port:
            try:
                response = self.info_compute(contract_id)
                if not response['instances']:
                    return False

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

    def func_install_compute_vastai(self, id, image, type='full', user_id=0, compute = None, checkpoint_url=None, info_run=None, disk_size=None):
        errors = None
        if not disk_size:
            disk_size = 40
        if type == 'full':
            contract_id, error = self.vast_api_install_platform(
                id, image, user_id=user_id, compute=compute, disk_size=disk_size
            )
            if error:
                errors = error
            if not contract_id:
                return False, id, errors
            response = self.get_port_instance(contract_id, 8081, id)
            # port = response['instances']["ports"][f"8081/tcp"][0]["HostPort"]

        elif type == "ml":
            contract_id, error = self.vast_ai_install_ml(id, image, info_run=info_run, disk_size=disk_size)
            if error:
                errors = error
            if not contract_id:
                return False, id, errors
            response = self.get_port_instance(contract_id, 9090, id)
        
        elif type == "deploy-ml":
            contract_id, error = self.vast_ai_install_deploy_ml(id, image, checkpoint_url, info_run, disk_size=disk_size)
            if error:
                errors = error
            if not contract_id:
                return False, id, errors
            response = self.get_port_instance(contract_id, 9090, id)
            # port = response['instances']["ports"][f"9090/tcp"][0]["HostPort"]

        elif type == "storage":
            contract_id, error = self.vast_ai_install_s3(id, image, user_id, disk_size=disk_size)
            if error:
                errors = error
            if not contract_id:
                return False, id, errors
            response = self.get_port_instance(contract_id, 9001, id)

        if not response:
            self.delete_compute(contract_id)
            return False, id, errors

        return True, response, errors

def generate_password(length=12):
    # Các ký tự có thể sử dụng trong mật khẩu: chữ hoa, chữ thường và số
    characters = string.ascii_letters + string.digits
    # Tạo mật khẩu ngẫu nhiên
    password = "".join(random.choice(characters) for _ in range(length))
    return password
