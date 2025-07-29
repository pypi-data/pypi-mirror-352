from asgiref.sync import sync_to_async
import asyncio
from django.utils import timezone
from core.settings.base import MAIL_SERVER

def update_notify_install(content, user_id, detail, history_id, type="Install Compute", status="info"):
    from users.models import Notification
    try:
        if not history_id:
            Notification.objects.create(
                content=content,
                is_read=False,
                user_id=user_id,
                detail=detail,
                # deleted_at__isnull=True,
                type=type,
                status=status
            )
        else:
            Notification.objects.create(
                    content=content,
                    is_read=False,
                    user_id=user_id,
                    detail=detail,
                    # deleted_at__isnull=True,
                    type=type,
                    status=status,
                    history_id=history_id
                )

    except Exception as e:
        print(e)

def check_status_port_docker(url, port, user_id, user_uuid, history_id):
    import requests
    from users.models import Notification
    from .functions import notify_for_compute

    try:
        response = requests.get(f'http://{url}:{port}/info', verify=False) 
        if response.status_code == 200:
            return True
        else:
            update_notify_install("The default Docker port 4243 is not open.", user_id, f"The default Docker port 4243 is not active. Please open the port to use the service.", history_id, "Install Compute", Notification.Status.Warning)
            notify_for_compute(user_uuid, "Warning", "The default Docker port 4243 is not open")

            return False
    except requests.exceptions.RequestException as e:
        update_notify_install("The default Docker port 4243 is not open.", user_id, f"The default Docker port 4243 is not active. Please open the port to use the service.", history_id, "Install Compute", Notification.Status.Warning)
        notify_for_compute(user_uuid, "Warning", "The default Docker port 4243 is not open")
        print(f"An error occurred: {e}")
        return False

def check_status_port_minio(url, port, user_id, user_uuid, history_id):
    import requests
    from users.models import Notification
    from .functions import notify_for_compute

    try:
        response = requests.get(f'http://{url}:{port}', verify=False) 
        if response.status_code == 200:
            return True
        else:
            update_notify_install(f"The MinIO port {port} is not open. Please open the port to use the service.", user_id, f"MinIO port {port} is not open. Please open the port to use the service.", history_id, "Install Compute", Notification.Status.Warning)
            notify_for_compute(user_uuid, "Warning", "The MinIO port is not open")
            
            return False
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        update_notify_install(f"The MinIO port {port} is not open. Please open the port to use the service.", user_id, f"MinIO port {port} is not open. Please open the port to use the service.", history_id, "Install Compute", Notification.Status.Warning)
        notify_for_compute(user_uuid, "Warning", "The MinIO port is not open")
        return False

def check_status_port_platform(url, port, user_id, user_uuid, history_id):
    import requests
    from users.models import Notification
    from .functions import notify_for_compute

    try:
        response = requests.get(f'https://{url}:{port}', verify=False) 
        if response.status_code == 200:
            return True
        else:
            update_notify_install(f"Port {port} for the platform is not open. Please ensure the port is open to allow access.", user_id, f"Port {port} for the platform is not open. Please ensure the port is open to allow access.", history_id, "Install Compute", Notification.Status.Warning)
            notify_for_compute(user_uuid, "Warning", "The Platform port is not open")
            
            return False
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        update_notify_install(f"Port {port} for the platform is not open. Please ensure the port is open to allow access.", user_id, f"Port {port} for the platform is not open. Please ensure the port is open to allow access.", history_id, "Install Compute", Notification.Status.Warning)
        notify_for_compute(user_uuid, "Warning", "The Platform port is not open")
        return False

def check_status_port_ml(url, port, user_id, user_uuid, history_id):
    import requests
    from users.models import Notification
    from .functions import notify_for_compute

    try:
        response = requests.get(f'https://{url}:{port}', verify=False) 
        if response.status_code == 200:
            return True
        else:
            update_notify_install(f"The ML port {port} is not open.", user_id, f"ML {port} is not active. Please open the port to use the service.", history_id, "Install Compute", Notification.Status.Warning)
            notify_for_compute(user_uuid, "Warning", "The ML port is not open")
            
            return False
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        update_notify_install(f"ML {port} is not active. Please open the port to use the service.", user_id, f"ML {port} is not active. Please open the port to use the service.", history_id, "Install Compute", Notification.Status.Warning)
        notify_for_compute(user_uuid, "Warning", "The ML port is not open")
        return False

def delete_compute_duplicate_ip(ip_address, compute_id_now=None):
    try:
        from compute_marketplace.models import ComputeMarketplace, History_Rent_Computes
        from django.utils import timezone

        # Tìm compute dựa trên ip_address và loại trừ compute hiện tại
        compute = None
        if compute_id_now is not None:
            compute = ComputeMarketplace.objects.filter(
                ip_address=ip_address, deleted_at__isnull=True
            ).exclude(id=compute_id_now).first()
        else: 
            compute = ComputeMarketplace.objects.filter(
                ip_address=ip_address, deleted_at__isnull=True
            ).first()

        if compute:
            # Cập nhật thời gian xóa của tất cả các compute trong QuerySet
            deleted_time = timezone.now()
            compute.deleted_at=deleted_time
            compute.save()

            # Lấy tất cả các bản ghi trong history liên quan đến các compute
            history_records = History_Rent_Computes.objects.filter(
                compute_marketplace_id= compute.id
            )

            # Cập nhật thời gian xóa của các bản ghi trong history và các compute_gpu liên quan
            for record in history_records:
                record.deleted_at = deleted_time
                if record.compute_gpu:
                    record.compute_gpu.deleted_at = deleted_time
                    record.compute_gpu.save()
                record.save()

            return True  

        else:
            print(
                f"No compute found with ip_address={ip_address} excluding id={compute_id_now}"
            )
            return False  # Indicate that no deletion was necessary

    except Exception as e:
        print(f"An error occurred: {e}")
        return False  


async def check_compute_verify(ip_address, infrastructure_id):
    from compute_marketplace.models import ComputeMarketplace

    # Tìm compute theo ip_address
    compute = await sync_to_async(
        ComputeMarketplace.objects.filter(
            ip_address=ip_address, deleted_at__isnull=True
        ).first
    )()

    # Tìm compute theo infrastructure_id
    check_compute_init = await sync_to_async(
        ComputeMarketplace.objects.filter(
            infrastructure_id=infrastructure_id, deleted_at__isnull=True
        ).first
    )()

    # Điều kiện 1: Cả hai không tồn tại
    if compute is None and check_compute_init is None:
        return False, False

    # Điều kiện 2: Compute không tồn tại nhưng có compute với infrastructure_id, compute_type tồn tại
    if (
        compute is None
        and check_compute_init
        and check_compute_init.compute_type is not None
    ):
        return False, True

    # Điều kiện 3: Compute không tồn tại nhưng có compute với infrastructure_id, compute_type không tồn tại
    if (
        compute is None
        and check_compute_init
        and check_compute_init.compute_type is None
    ):
        return False, False

    # Điều kiện 4: Compute tồn tại nhưng compute_type không tồn tại
    if compute and compute.compute_type is None:
        return True, False

    # Điều kiện 5: Compute tồn tại và compute_type tồn tại, nhưng compute với infrastructure_id không tồn tại
    if compute and compute.compute_type is not None and check_compute_init is None:
        return True, True

    # Điều kiện 6: Compute tồn tại và compute_type tồn tại, compute với infrastructure_id tồn tại nhưng compute_type khác nhau
    if (
        compute
        and compute.compute_type is not None
        and check_compute_init
        and check_compute_init.compute_type != compute.compute_type
    ):
        return True, False

    # Điều kiện 7: Compute tồn tại và compute_type tồn tại, compute với infrastructure_id tồn tại và compute_type giống nhau
    if (
        compute
        and compute.compute_type is not None
        and check_compute_init
        and check_compute_init.compute_type == compute.compute_type
    ):
        return True, True

    # Điều kiện mặc định (trong trường hợp có thêm các trường hợp không lường trước)
    return False, False


def _check_compute_verify(ip_address):
    from compute_marketplace.models import ComputeMarketplace

    compute = ComputeMarketplace.objects.filter(
            ip_address=ip_address, deleted_at__isnull=True
        ).first()
    
    if compute is None:
        # existed, compute type existed
        return False, False
    if compute and compute.compute_type is None:
        return True, False
    return True, True


async def update_server_info(infrastructure_id, config):
    from compute_marketplace.models import ComputeMarketplace

    compute = await sync_to_async(
        ComputeMarketplace.objects.filter(
            infrastructure_id=infrastructure_id, deleted_at__isnull=True
        ).first
    )()
    if compute is None:
        return
    compute.ip_address = config.get("ip")
    compute.config = config
    return  await sync_to_async(compute.save)()

def _update_server_info(infrastructure_id, config):
    from compute_marketplace.models import ComputeMarketplace

    compute = ComputeMarketplace.objects.filter(
            infrastructure_id=infrastructure_id, deleted_at__isnull=True
        ).first()
    
    if compute is None:
        return
    
    compute.ip_address = config.get("ip")
    compute.name = config.get("ip")
    compute.config = config
    return compute.save()

@sync_to_async
def update_compute_gpus(infrastructure_id, gpus = []):
    from compute_marketplace.models import ComputeMarketplace, ComputeGPU, History_Rent_Computes

    compute = ComputeMarketplace.objects.filter(
            infrastructure_id=infrastructure_id, deleted_at__isnull=True
        ).first()
    if compute is None:
        return
    if len(gpus) > 0:
        for gpu in gpus:
            # filter compute record
            compute_gpu = ComputeGPU.objects.filter(gpu_id=gpu["uuid"]).first()
            # tạo compute gpu, history cho card gpu mới
            if compute_gpu is None:
                compute_gpu = ComputeGPU.objects.create(
                    compute_marketplace=compute,
                    infrastructure_id=compute,
                    gpu_name=gpu["name"],
                    power_consumption=gpu["power_consumption"],
                    memory=gpu["memory"],
                    serialno=gpu["serialno"],
                    power_usage=gpu["power_usage"],
                    memory_usage=gpu["memory_usage"],
                    gpu_id=gpu.get("uuid", None),
                )

                # check xem có bản ghi history nào chưa, vì ban đầu đã tạo 1 bản ghi trước.
                # nếu nhiều hơn 1 card thì 1 bản ghi update và còn lại là tạo mới
                # mỗi 1 gpu sẽ tương đương 1 record history
                history_rent = History_Rent_Computes.objects.filter(
                    compute_marketplace_id=compute.id,
                    compute_gpu_id__isnull=True,
                    deleted_at__isnull=True,
                ).first()
                if history_rent is None:
                    # Create History_Rent_Computes record
                    History_Rent_Computes.objects.create(
                        compute_marketplace=compute,
                        compute_gpu=compute_gpu,
                        account_id=compute.owner_id,  # Replace with actual account if available
                        rental_hours=0,  # Set the initial rental hours
                        order_id=0,  # Set initial order ID
                        status=History_Rent_Computes.Status.RENTING,
                        type=History_Rent_Computes.Type.RENT_MARKETPLACE,
                        compute_install=History_Rent_Computes.InstallStatus.WAIT_VERIFY,
                        service_type=History_Rent_Computes.SERVICE_TYPE.ALL_SERVICE,
                        quantity_used=0,
                        ip_address=None,  # Replace with actual IP if available
                        port=None,  # Replace with actual port if available
                        schema=None,  # Replace with actual schema if available
                        container_network=None,  # Replace with actual container network if available
                    )
                else:
                    history_rent.compute_marketplace = compute
                    history_rent.status = History_Rent_Computes.Status.RENTING
                    history_rent.type = History_Rent_Computes.Type.RENT_MARKETPLACE
                    history_rent.compute_install = (
                        History_Rent_Computes.InstallStatus.WAIT_VERIFY
                    )
                    history_rent.service_type = (
                        History_Rent_Computes.SERVICE_TYPE.ALL_SERVICE
                    )
                    history_rent.quantity_used = 0
                    history_rent.ip_address = None  # Replace with actual IP if available
                    history_rent.port = None  # Replace with actual port if available
                    history_rent.schema = None  # Replace with actual schema if available
                    history_rent.container_network = (
                        None  # Replace with actual container network if available
                    )
                    history_rent.save()

            # update nếu đã có
            else:
                compute_gpu.gpu_name = gpu["name"]
                compute_gpu.power_consumption = gpu["power_consumption"]
                compute_gpu.memory = gpu["memory"]
                compute_gpu.power_usage = gpu["power_usage"]
                compute_gpu.memory_usage = gpu["memory_usage"]
                compute_gpu.gpu_id = gpu.get("uuid", None)
                compute_gpu.save()

                history_rent = History_Rent_Computes.objects.filter(
                    compute_marketplace_id=compute.id,
                    compute_gpu_id__isnull=True,
                    deleted_at__isnull=True,
                ).first()
                if history_rent is None:
                    # Update existing History_Rent_Computes record
                    history_rent = History_Rent_Computes.objects.filter(compute_gpu=compute_gpu).first()
                if history_rent is None:
                    History_Rent_Computes.objects.create(
                        compute_marketplace=compute,
                        compute_gpu=compute_gpu,
                        account_id=compute.owner_id,  # Replace with actual account if available
                        rental_hours=0,  # Set the initial rental hours
                        order_id=0,  # Set initial order ID
                        status=History_Rent_Computes.Status.RENTING,
                        type=History_Rent_Computes.Type.RENT_MARKETPLACE,
                        compute_install=History_Rent_Computes.InstallStatus.WAIT_VERIFY,
                        service_type=History_Rent_Computes.SERVICE_TYPE.ALL_SERVICE,
                        quantity_used=0,
                        ip_address=None,  # Replace with actual IP if available
                        port=None,  # Replace with actual port if available
                        schema=None,  # Replace with actual schema if available
                        container_network=None,  # Replace with actual container network if available
                    )
                else:
                    history_rent.account_id = compute.owner_id
                    history_rent.compute_gpu_id = compute_gpu.id
                    history_rent.compute_marketplace = compute
                    history_rent.status = History_Rent_Computes.Status.RENTING
                    history_rent.type = History_Rent_Computes.Type.RENT_MARKETPLACE
                    history_rent.compute_install = (
                        History_Rent_Computes.InstallStatus.WAIT_VERIFY
                    )
                    history_rent.service_type = (
                        History_Rent_Computes.SERVICE_TYPE.ALL_SERVICE
                    )
                    history_rent.quantity_used = 0
                    history_rent.ip_address = None  # Replace with actual IP if available
                    history_rent.port = None  # Replace with actual port if available
                    history_rent.schema = None  # Replace with actual schema if available
                    history_rent.container_network = (
                        None  # Replace with actual container network if available
                    )
                    history_rent.save()

    # xử lý với compute không có card
    if len(gpus) == 0:
        # Update the first History_Rent_Computes record if no GPUs are provided
        history_rent = History_Rent_Computes.objects.filter(
                compute_marketplace=compute,
                deleted_at__isnull=True,
                compute_install=History_Rent_Computes.InstallStatus.WAIT_VERIFY,
            ).first()
        if history_rent:
            history_rent.account_id = compute.owner_id
            history_rent.status = History_Rent_Computes.Status.RENTING
            history_rent.type = History_Rent_Computes.Type.RENT_MARKETPLACE
            history_rent.compute_install = (
                History_Rent_Computes.InstallStatus.WAIT_VERIFY
            )
            history_rent.service_type = History_Rent_Computes.SERVICE_TYPE.ALL_SERVICE
            history_rent.quantity_used = 0
            history_rent.ip_address = compute.ip_address
            history_rent.port = None  # Replace with actual port if available
            history_rent.schema = None  # Replace with actual schema if available
            history_rent.container_network = (
                None 
            )
            history_rent.save()
        # update compute if dont used gpu
        compute.is_using_cpu = True
        compute.save()

    return True

def _update_compute_gpus(infrastructure_id, gpus = []):
    from compute_marketplace.models import ComputeMarketplace, ComputeGPU, History_Rent_Computes

    compute = ComputeMarketplace.objects.filter(
            infrastructure_id=infrastructure_id, deleted_at__isnull=True
        ).first()
    if compute is None:
        return
    if len(gpus) > 0:
        for gpu in gpus:
            # filter compute record
            compute_gpu = ComputeGPU.objects.filter(gpu_id=gpu["uuid"]).first()
            # tạo compute gpu, history cho card gpu mới
            if compute_gpu is None:
                compute_gpu = ComputeGPU.objects.create(
                    compute_marketplace=compute,
                    infrastructure_id=compute,
                    gpu_name=gpu["name"],
                    power_consumption=gpu["power_consumption"],
                    memory=gpu["memory"],
                    serialno=gpu["serialno"],
                    power_usage=gpu["power_usage"],
                    memory_usage=gpu["memory_usage"],
                    gpu_id=gpu.get("uuid", None),
                )

                # check xem có bản ghi history nào chưa, vì ban đầu đã tạo 1 bản ghi trước.
                # nếu nhiều hơn 1 card thì 1 bản ghi update và còn lại là tạo mới
                # mỗi 1 gpu sẽ tương đương 1 record history
                history_rent = History_Rent_Computes.objects.filter(
                    compute_marketplace_id=compute.id,
                    compute_gpu_id__isnull=True,
                    deleted_at__isnull=True,
                ).first()
                if history_rent is None:
                    # Create History_Rent_Computes record
                    History_Rent_Computes.objects.create(
                        compute_marketplace=compute,
                        compute_gpu=compute_gpu,
                        account_id=compute.owner_id,  # Replace with actual account if available
                        rental_hours=0,  # Set the initial rental hours
                        order_id=0,  # Set initial order ID
                        status=History_Rent_Computes.Status.RENTING,
                        type=History_Rent_Computes.Type.RENT_MARKETPLACE,
                        compute_install=History_Rent_Computes.InstallStatus.WAIT_VERIFY,
                        service_type=History_Rent_Computes.SERVICE_TYPE.ALL_SERVICE,
                        quantity_used=0,
                        ip_address=None,  # Replace with actual IP if available
                        port=None,  # Replace with actual port if available
                        schema=None,  # Replace with actual schema if available
                        container_network=None,  # Replace with actual container network if available
                    )
                else:
                    history_rent.compute_marketplace = compute
                    history_rent.status = History_Rent_Computes.Status.RENTING
                    history_rent.type = History_Rent_Computes.Type.RENT_MARKETPLACE
                    history_rent.compute_install = (
                        History_Rent_Computes.InstallStatus.WAIT_VERIFY
                    )
                    history_rent.service_type = (
                        History_Rent_Computes.SERVICE_TYPE.ALL_SERVICE
                    )
                    history_rent.quantity_used = 0
                    history_rent.ip_address = None  # Replace with actual IP if available
                    history_rent.port = None  # Replace with actual port if available
                    history_rent.schema = None  # Replace with actual schema if available
                    history_rent.container_network = (
                        None  # Replace with actual container network if available
                    )
                    history_rent.save()

            # update nếu đã có
            else:
                compute_gpu.gpu_name = gpu["name"]
                compute_gpu.power_consumption = gpu["power_consumption"]
                compute_gpu.memory = gpu["memory"]
                compute_gpu.power_usage = gpu["power_usage"]
                compute_gpu.memory_usage = gpu["memory_usage"]
                compute_gpu.gpu_id = gpu.get("uuid", None)
                compute_gpu.save()

                history_rent = History_Rent_Computes.objects.filter(
                    compute_marketplace_id=compute.id,
                    compute_gpu_id__isnull=True,
                    deleted_at__isnull=True,
                ).first()
                if history_rent is None:
                    # Update existing History_Rent_Computes record
                    history_rent = History_Rent_Computes.objects.filter(compute_gpu=compute_gpu).first()
                if history_rent is None:
                    History_Rent_Computes.objects.create(
                        compute_marketplace=compute,
                        compute_gpu=compute_gpu,
                        account_id=compute.owner_id,  # Replace with actual account if available
                        rental_hours=0,  # Set the initial rental hours
                        order_id=0,  # Set initial order ID
                        status=History_Rent_Computes.Status.RENTING,
                        type=History_Rent_Computes.Type.OWN_NOT_LEASING,
                        compute_install=History_Rent_Computes.InstallStatus.WAIT_VERIFY,
                        service_type=History_Rent_Computes.SERVICE_TYPE.ALL_SERVICE,
                        quantity_used=0,
                        ip_address=None,  # Replace with actual IP if available
                        port=None,  # Replace with actual port if available
                        schema=None,  # Replace with actual schema if available
                        container_network=None,  # Replace with actual container network if available
                    )
                else:
                    history_rent.account_id = compute.owner_id
                    history_rent.compute_gpu_id = compute_gpu.id
                    history_rent.compute_marketplace = compute
                    history_rent.status = History_Rent_Computes.Status.RENTING
                    history_rent.type = History_Rent_Computes.Type.OWN_NOT_LEASING
                    # history_rent.compute_install = (
                    #     History_Rent_Computes.InstallStatus.WAIT_VERIFY
                    # )
                    # history_rent.service_type = (
                    #     History_Rent_Computes.SERVICE_TYPE.ALL_SERVICE
                    # )
                    # history_rent.quantity_used = 0
                    # history_rent.ip_address = None  # Replace with actual IP if available
                    # history_rent.port = None  # Replace with actual port if available
                    # history_rent.schema = None  # Replace with actual schema if available
                    # history_rent.container_network = (
                    #     None  # Replace with actual container network if available
                    # )
                    history_rent.save()

    # xử lý với compute không có card
    if len(gpus) == 0:
        # Update the first History_Rent_Computes record if no GPUs are provided
        history_rent = History_Rent_Computes.objects.filter(
                compute_marketplace=compute,
                deleted_at__isnull=True,
                compute_install=History_Rent_Computes.InstallStatus.WAIT_VERIFY,
            ).first()
        if history_rent:
            history_rent.account_id = compute.owner_id
            history_rent.status = History_Rent_Computes.Status.RENTING
            history_rent.type = History_Rent_Computes.Type.RENT_MARKETPLACE
            history_rent.compute_install = (
                History_Rent_Computes.InstallStatus.WAIT_VERIFY
            )
            history_rent.service_type = History_Rent_Computes.SERVICE_TYPE.ALL_SERVICE
            history_rent.quantity_used = 0
            history_rent.ip_address = compute.ip_address
            history_rent.port = None  # Replace with actual port if available
            history_rent.schema = None  # Replace with actual schema if available
            history_rent.container_network = (
                None 
            )
            history_rent.save()
        # update compute if dont used gpu
        compute.is_using_cpu = True
        compute.save()

    return True

@sync_to_async
def handle_install_compute(infrastructure_id):
    from compute_marketplace.models import (
        ComputeMarketplace,
        ComputeGPU,
        History_Rent_Computes,
    )
    from core.utils.docker_container_pull import (
        dockerContainerPull,
        asyncDockerContainerPull,
    )
    import threading
    from django.db import OperationalError
    from aixblock_core.users.service_notify import get_data, send_email_thread
    import time
    from rest_framework.authtoken.models import Token
    from users.models import User
    import asyncio
    from concurrent.futures import ThreadPoolExecutor
    from django.db import OperationalError
    from django.core.exceptions import ObjectDoesNotExist
    from .functions import check_compute_run_status
    from plugins.plugin_centrifuge import (
        publish_message,
    )
    def save_compute_objects(
        compute_marketplace_id,
        port,
        minio_port,
        compute_type,
        compute_install,
        network_name,
    ):
        if port is None:
            port = 8080
        try:
            compute = ComputeMarketplace.objects.filter(pk=compute_marketplace_id).first()
            compute.port = port
            compute.api_port = minio_port
            compute.save()

            compute_gpus = ComputeGPU.objects.filter(
                compute_marketplace_id=compute.pk,
                deleted_at__isnull=True
            )
            history = None
            for compute_gpu in compute_gpus:
                gpu = ComputeGPU.objects.filter(id=compute_gpu.id).first()
                if gpu:
                    gpu.status = ComputeGPU.Status.IN_MARKETPLACE
                    gpu.save()

                    history = History_Rent_Computes.objects.filter(
                        compute_marketplace_id=compute.pk,
                        compute_gpu_id=compute_gpu.id,
                        deleted_at__isnull=True
                    ).first()
                    if history is None:
                        history = History_Rent_Computes.objects.filter(
                            compute_marketplace_id=compute.pk,
                            compute_gpu_id__isnull = True,
                            deleted_at__isnull=True,
                        ).first()

                    if history:
                        # history.compute_install = compute_install
                        history.type = History_Rent_Computes.Type.OWN_NOT_LEASING
                        history.service_type = compute_type
                        history.schema = "https" if compute_type != "storage" else "http"
                        history.container_network = network_name
                        history.port = port
                        history.save()

            if compute.is_using_cpu or len(compute_gpus) == 0:
                compute.is_using_cpu = True
                compute.save()
                history = History_Rent_Computes.objects.filter(
                    compute_marketplace_id=compute.pk,
                    compute_gpu_id__isnull=True,
                    deleted_at__isnull=True
                ).first()

                if history:
                    # history.compute_install = compute_install
                    history.type = History_Rent_Computes.Type.OWN_NOT_LEASING
                    history.service_type = compute_type
                    history.schema = "https" if compute_type != "storage" else "http"
                    history.container_network = network_name
                    history.port = port
                    history.save()
            if history:
                return check_compute_run_status(history.id)
        except OperationalError as e:
            update_notify_install("Error installing compute.", compute.owner_id, f"Database operation error: {e}", history.id, "System", "danger")
            print(f"Database operation error: {e}")
        except ObjectDoesNotExist as e:
            print(f"Object does not exist: {e}")
            update_notify_install("Error installing compute.", compute.owner_id, f"Object does not exist: {e}", history.id, "System", "danger")

        except Exception as e:
            print(f"Unexpected error: {e}")
            update_notify_install("Error installing compute.", compute.owner_id, f"Unexpected error: {e}", history.id, "System", "danger")

    def run_in_executor(func, *args, **kwargs):
        loop = asyncio.get_event_loop()
        executor = ThreadPoolExecutor()
        return loop.run_in_executor(executor, lambda: func(*args, **kwargs))

    def pull_docker_container_and_update(compute_type, ip_address, client_id, client_secret, token, user_id, compute_marketplace_id, user, compute, history_id=None):
        max_retries = 2
        retry_delay = 5  # seconds
        retries = 0
        compute_install = "completed"
        minio_port = None

        try:
            print("Starting dockerContainerPull")

            (
                _port,
                minio_port,
                user_email,
                password,
                minio_user_username,
                minio_password,
                network_name,
                minio_api_port
            ) = dockerContainerPull(
                compute_type, ip_address, client_id, client_secret, token, user_id, history_id
            )
            print("dockerContainerPull finished")

        except Exception as e:
            _port = 0
            compute_install = "failed"
            update_notify_install("Error install images from docker", user_id, f"Error install images from docker: {e}", history_id, "Install Compute", "danger")
            print(f"Error in dockerContainerPull: {e}")

        while retries < max_retries:
            try:
                port = _port
                schema = "https" if compute_type != "storage" else "http"
                if port == 0 or port is None and minio_port is not None:
                    port = minio_port
                save_compute_objects(
                    compute_marketplace_id,
                    port,
                    minio_port,
                    compute_type,
                    compute_install,
                    network_name,
                )
                break
            except OperationalError as e:
                retries += 1
                print(f"Database connection error: {e}. Retry {retries}/{max_retries}...")
                update_notify_install("Database connection error", user_id, f"Database connection error: {e}. Retry {retries}/{max_retries}...", history_id, "Install Compute", "danger")
                time.sleep(retry_delay)
            except Exception as e:
                retries = 5
                update_notify_install("Error installing compute.", user_id, f'{e}', history_id, "Install Compute", "danger")
                print(e)
                # Log other exceptions
                raise  # Re-raise the exception for unexpected errors
        else:
            print("Failed to connect to the database after multiple attempts.")

        def send_email(user, compute, compute_type, user_email, password, minio_user_username, minio_password, minio_port):
            try:
                if compute_type != "model-training":
                    if compute_type in ["full", "label-tool"]:
                        send_mail_rent_compute_platform(user, compute, user_email, password)
                        if minio_user_username:
                            send_mail_s3(user, compute, minio_user_username, minio_password)
                    else:
                        send_mail_s3(user, compute, minio_user_username, minio_password)
                else:
                    send_mail_rent_compute(user, compute, minio_port, user_email)
            except Exception as e:
                print(e)

        def send_mail_rent_compute(user, compute, tensorboard, ddp):
            send_to = user.username if user.username else user.email
            html_file_path = "./aixblock_core/templates/mail/rent_compute_success.html"

            with open(html_file_path, "r", encoding="utf-8") as file:
                html_content = file.read()

            html_content = html_content.replace("[user]", f"{send_to}")
            html_content = html_content.replace("rented", "set up")
            html_content = html_content.replace("xxx", f"{compute.id}")
            html_content = html_content.replace("[endpoint]", f"https://{compute.ip_address}:{compute.port}")
            html_content = html_content.replace("[tensorboard]", f"http://{compute.ip_address}:{tensorboard}")
            html_content = html_content.replace("[ddp]", f"{compute.ip_address}{ddp}")

            data = {
                "subject": "AIxBlock | Confirmation of Successful Compute Setup",
                "from": "noreply@aixblock.io",
                "to": [f"{user.email}"],
                "html": html_content,
                "text": "Welcome to AIxBlock!",
                "attachments": [],
            }

            docket_api = "tcp://69.197.168.145:4243"
            host_name = MAIL_SERVER

            email_thread = threading.Thread(target=send_email_thread, args=(docket_api, host_name, data))
            email_thread.start()

        def send_mail_rent_compute_platform(user, compute, email_user, pass_user):
            send_to = user.username if user.username else user.email
            html_file_path = "./aixblock_core/templates/mail/rent_compute_success_platform.html"

            with open(html_file_path, "r", encoding="utf-8") as file:
                html_content = file.read()

            html_content = html_content.replace("[user]", f"{send_to}")
            html_content = html_content.replace("xxx", f"{compute.id}")
            html_content = html_content.replace("[domain]", f"https://{compute.ip_address}:{compute.port}")
            html_content = html_content.replace("[email]", email_user)
            html_content = html_content.replace("[pass]", pass_user)

            data = {
                "subject": "AIxBlock | Your Access Credentials to Your Private Platform",
                "from": "noreply@aixblock.io",
                "to": [f"{user.email}"],
                "html": html_content,
                "text": "Welcome to AIxBlock!",
                "attachments": [],
            }

            docket_api = "tcp://69.197.168.145:4243"
            host_name = MAIL_SERVER

            email_thread = threading.Thread(target=send_email_thread, args=(docket_api, host_name, data))
            email_thread.start()

        def send_mail_s3(user, compute, email_user, pass_user):
            html_file_path = "./aixblock_core/templates/mail/s3_vast.html"
            with open(html_file_path, "r", encoding="utf-8") as file:
                html_content = file.read()

            html_content = html_content.replace("[user]", f"{user.email}")
            html_content = html_content.replace("renting", "setting")
            html_content = html_content.replace("xxx", f"{compute.id}")
            html_content = html_content.replace("[endpoint_minio]", f"{compute.ip_address}:{compute.port}")
            html_content = html_content.replace("[user_minio]", email_user)
            html_content = html_content.replace("[pass_minio]", pass_user)

            data = {
                "subject": f"AIxBlock | Confirmation of Compute Setup and Your Storage Access",
                "from": "noreply@aixblock.io",
                "to": [f"{user.email}"],
                "html": html_content,
                "text": "Remove compute!",
            }

            docket_api = "tcp://69.197.168.145:4243"
            host_name = MAIL_SERVER

            email_thread = threading.Thread(target=send_email_thread, args=(docket_api, host_name, data))
            email_thread.start()

        if compute_install == 'completed':
            send_email(
                user,
                compute,
                compute_type,
                user_email,
                password,
                minio_user_username,
                minio_password,
                minio_port,
            )

    compute = ComputeMarketplace.objects.filter(
            infrastructure_id=infrastructure_id, deleted_at__isnull=True).first()
    compute_type = History_Rent_Computes.SERVICE_TYPE.ALL_SERVICE
    history = History_Rent_Computes.objects.filter(
            compute_marketplace_id=compute.id, 
            compute_install = History_Rent_Computes.InstallStatus.WAIT_VERIFY,
            deleted_at__isnull=True
        ).first()
    if history is None:
        return

    compute_type = history.service_type
    history.compute_install = History_Rent_Computes.InstallStatus.INSTALLING
    history.save()

    # send refresh page
    delete_compute_duplicate_ip(compute.ip_address, compute.id)
    publish_message(channel=compute.infrastructure_id, data={"refresh": True}, prefix=True)
    user = User.objects.filter(id=compute.owner_id).first()
    token = Token.objects.get(user=user)


    pull_docker_container_and_update(
        compute_type,
        compute.ip_address,
        compute.client_id,
        compute.client_secret,
        token,
        user.id,
        compute.id,
        user,
        compute,
        history.id
    )
    return True

def _handle_install_compute(infrastructure_id):
    from compute_marketplace.models import (
        ComputeMarketplace,
        ComputeGPU,
        History_Rent_Computes,
    )
    from core.utils.docker_container_pull import (
        dockerContainerPull,
        asyncDockerContainerPull,
    )
    import threading
    from django.db import OperationalError
    from aixblock_core.users.service_notify import get_data, send_email_thread
    import time
    from rest_framework.authtoken.models import Token
    from users.models import User
    import asyncio
    from concurrent.futures import ThreadPoolExecutor
    from django.db import OperationalError
    from django.core.exceptions import ObjectDoesNotExist
    from .functions import check_compute_run_status

    def save_compute_objects(
        compute_marketplace_id,
        port,
        minio_port,
        compute_type,
        compute_install,
        network_name,
    ):
        if port is None:
            port = 8080
        try:
            compute = ComputeMarketplace.objects.filter(pk=compute_marketplace_id).first()
            compute.port = port
            compute.api_port = minio_port
            compute.is_scale=True
            compute.save()

            compute_gpus = ComputeGPU.objects.filter(
                compute_marketplace_id=compute.pk,
                deleted_at__isnull=True
            )
            history = None
            for compute_gpu in compute_gpus:
                gpu = ComputeGPU.objects.filter(id=compute_gpu.id).first()
                if gpu:
                    gpu.status = ComputeGPU.Status.IN_MARKETPLACE
                    gpu.save()

                    history = History_Rent_Computes.objects.filter(
                        compute_marketplace_id=compute.pk,
                        compute_gpu_id=compute_gpu.id,
                        deleted_at__isnull=True
                    ).first()
                    if history is None:
                        history = History_Rent_Computes.objects.filter(
                            compute_marketplace_id=compute.pk,
                            compute_gpu_id__isnull = True,
                            deleted_at__isnull=True,
                        ).first()

                    if history:
                        # history.compute_install = compute_install
                        history.type = History_Rent_Computes.Type.OWN_NOT_LEASING
                        history.service_type = compute_type
                        history.schema = "https" if compute_type != "storage" else "http"
                        history.container_network = network_name
                        history.port = port
                        history.save()

            if compute.is_using_cpu or len(compute_gpus) == 0:
                compute.is_using_cpu = True
                compute.save()
                history = History_Rent_Computes.objects.filter(
                    compute_marketplace_id=compute.pk,
                    compute_gpu_id__isnull=True,
                    deleted_at__isnull=True
                ).first()

                if history:
                    # history.compute_install = compute_install
                    history.type = History_Rent_Computes.Type.OWN_NOT_LEASING
                    history.service_type = compute_type
                    history.schema = "https" if compute_type != "storage" else "http"
                    history.container_network = network_name
                    history.port = port
                    history.save()
            if history:
                update_notify_install("Compute installation successful.", compute.owner_id, f"Compute installation successful.", history.id, "Install Compute", "success")
                return check_compute_run_status(history.id)
            
        except OperationalError as e:
            update_notify_install("Error installing compute.", compute.owner_id, f"Database operation error: {e}", history.id, "System", "danger")
            print(f"Database operation error: {e}")
        except ObjectDoesNotExist as e:
            print(f"Object does not exist: {e}")
            update_notify_install("Error installing compute.", compute.owner_id, f"Object does not exist: {e}", history.id, "System", "danger")

        except Exception as e:
            print(f"Unexpected error: {e}")
            update_notify_install("Error installing compute.", compute.owner_id, f"Unexpected error: {e}", history.id, "System", "danger")

    def run_in_executor(func, *args, **kwargs):
        loop = asyncio.get_event_loop()
        executor = ThreadPoolExecutor()
        return loop.run_in_executor(executor, lambda: func(*args, **kwargs))

    def pull_docker_container_and_update(compute_type, ip_address, client_id, client_secret, token, user_id, compute_marketplace_id, user, compute, history_id=None):
        max_retries = 2
        retry_delay = 5  # seconds
        retries = 0
        compute_install = "completed"
        minio_port = None

        try:
            print("Starting dockerContainerPull")

            (
                _port,
                minio_port,
                user_email,
                password,
                minio_user_username,
                minio_password,
                network_name,
                minio_api_port
            ) = dockerContainerPull(
                compute_type, ip_address, client_id, client_secret, token, user_id
            )
            print("dockerContainerPull finished")

        except Exception as e:
            _port = 0
            compute_install = "failed"
            update_notify_install("Error in dockerContainerPull", user_id, f"Error in dockerContainerPull: {e}", history_id, "Install Compute", "danger")
            print(f"Error in dockerContainerPull: {e}")

        while retries < max_retries:
            try:
                port = _port
                schema = "https" if compute_type != "storage" else "http"
                if port == 0 or port is None and minio_port is not None:
                    port = minio_port
                save_compute_objects(
                    compute_marketplace_id,
                    port,
                    minio_port,
                    compute_type,
                    compute_install,
                    network_name,
                )
                break
            except OperationalError as e:
                retries += 1
                print(f"Database connection error: {e}. Retry {retries}/{max_retries}...")
                update_notify_install("Database connection error", user_id, f"Database connection error: {e}. Retry {retries}/{max_retries}...", history_id, "Install Compute", "danger")
                time.sleep(retry_delay)
            except Exception as e:
                retries = 5
                update_notify_install("Error installing compute.", user_id, f'{e}', history_id, "Install Compute", "danger")
                print(e)
                # Log other exceptions
                raise  # Re-raise the exception for unexpected errors
        else:
            print("Failed to connect to the database after multiple attempts.")

        def send_email(user, compute, compute_type, user_email, password, minio_user_username, minio_password, minio_port):
            try:
                if compute_type != "model-training":
                    if compute_type in ["full", "label-tool"]:
                        send_mail_rent_compute_platform(user, compute, user_email, password)
                        if minio_user_username:
                            send_mail_s3(user, compute, minio_user_username, minio_password)
                    else:
                        send_mail_s3(user, compute, minio_user_username, minio_password)
                else:
                    send_mail_rent_compute(user, compute, minio_port, user_email)
            except Exception as e:
                print(e)

        def send_mail_rent_compute(user, compute, tensorboard, ddp):
            send_to = user.username if user.username else user.email
            html_file_path = "./aixblock_core/templates/mail/rent_compute_success.html"

            with open(html_file_path, "r", encoding="utf-8") as file:
                html_content = file.read()

            html_content = html_content.replace("[user]", f"{send_to}")
            html_content = html_content.replace("rented", "set up")
            html_content = html_content.replace("xxx", f"{compute.id}")
            html_content = html_content.replace("[endpoint]", f"https://{compute.ip_address}:{compute.port}")
            html_content = html_content.replace("[tensorboard]", f"http://{compute.ip_address}:{tensorboard}")
            html_content = html_content.replace("[ddp]", f"{compute.ip_address}{ddp}")

            data = {
                "subject": "AIxBlock | Confirmation of Successful Compute Setup",
                "from": "noreply@aixblock.io",
                "to": [f"{user.email}"],
                "html": html_content,
                "text": "Welcome to AIxBlock!",
                "attachments": [],
            }

            docket_api = "tcp://69.197.168.145:4243"
            host_name = MAIL_SERVER

            email_thread = threading.Thread(target=send_email_thread, args=(docket_api, host_name, data))
            email_thread.start()

        def send_mail_rent_compute_platform(user, compute, email_user, pass_user):
            send_to = user.username if user.username else user.email
            html_file_path = "./aixblock_core/templates/mail/rent_compute_success_platform.html"

            with open(html_file_path, "r", encoding="utf-8") as file:
                html_content = file.read()

            html_content = html_content.replace("[user]", f"{send_to}")
            html_content = html_content.replace("xxx", f"{compute.id}")
            html_content = html_content.replace("[domain]", f"https://{compute.ip_address}:{compute.port}")
            html_content = html_content.replace("[email]", email_user)
            html_content = html_content.replace("[pass]", pass_user)

            data = {
                "subject": "AIxBlock | Your Access Credentials to Your Private Platform",
                "from": "noreply@aixblock.io",
                "to": [f"{user.email}"],
                "html": html_content,
                "text": "Welcome to AIxBlock!",
                "attachments": [],
            }

            docket_api = "tcp://69.197.168.145:4243"
            host_name = MAIL_SERVER

            email_thread = threading.Thread(target=send_email_thread, args=(docket_api, host_name, data))
            email_thread.start()

        def send_mail_s3(user, compute, email_user, pass_user):
            html_file_path = "./aixblock_core/templates/mail/s3_vast.html"
            with open(html_file_path, "r", encoding="utf-8") as file:
                html_content = file.read()

            html_content = html_content.replace("[user]", f"{user.email}")
            html_content = html_content.replace("renting", "setting")
            html_content = html_content.replace("xxx", f"{compute.id}")
            html_content = html_content.replace("[endpoint_minio]", f"{compute.ip_address}:{compute.port}")
            html_content = html_content.replace("[user_minio]", email_user)
            html_content = html_content.replace("[pass_minio]", pass_user)

            data = {
                "subject": f"AIxBlock | Confirmation of Compute Setup and Your Storage Access",
                "from": "noreply@aixblock.io",
                "to": [f"{user.email}"],
                "html": html_content,
                "text": "Remove compute!",
            }

            docket_api = "tcp://69.197.168.145:4243"
            host_name = MAIL_SERVER

            email_thread = threading.Thread(target=send_email_thread, args=(docket_api, host_name, data))
            email_thread.start()

        if compute_install == 'completed':
            send_email(
                user,
                compute,
                compute_type,
                user_email,
                password,
                minio_user_username,
                minio_password,
                minio_port,
            )

    compute = ComputeMarketplace.objects.filter(
            infrastructure_id=infrastructure_id, deleted_at__isnull=True).first()
    compute_type = History_Rent_Computes.SERVICE_TYPE.ALL_SERVICE
    history = History_Rent_Computes.objects.filter(
            compute_marketplace_id=compute.id, 
            compute_install = History_Rent_Computes.InstallStatus.WAIT_VERIFY,
            deleted_at__isnull=True
        ).first()
    if history is None:
        return

    compute_type = history.service_type
    history.compute_install = History_Rent_Computes.InstallStatus.INSTALLING
    history.save()
    user = User.objects.filter(id=compute.owner_id).first()
    token = Token.objects.get(user=user)
    
    from plugins.plugin_centrifuge import publish_message
    publish_message(
        channel=infrastructure_id, data={"refresh": True}, prefix=True
    )

    pull_docker_container_and_update(
        compute_type,
        compute.ip_address,
        compute.client_id,
        compute.client_secret,
        token,
        user.id,
        compute.id,
        user,
        compute,
        history.id
    )

    try:
        compute = ComputeMarketplace.objects.filter(
            infrastructure_id=infrastructure_id, deleted_at__isnull=True).first()
        
        if compute_type in ["full", "label-tool"]:
            check_status_port_docker(compute.ip_address, 4243, user.id, user.uuid, history.id)
            check_status_port_minio(compute.ip_address, compute.api_port, user.id, user.uuid, history.id)
            # check_status_port_minio(compute.ip_address, 9091, user.id, user.uuid, history.id)
            check_status_port_platform(compute.ip_address, compute.port, user.id, user.uuid, history.id)
        elif compute_type == "storage":
            check_status_port_minio(compute.ip_address, compute.api_port, user.id, user.uuid, history.id)
            # check_status_port_minio(compute.ip_address, 9091, user.id, user.uuid, history.id)
            
        elif compute_type == "model-training":
            check_status_port_ml(compute.ip_address, compute.port, user.id, user.uuid, history.id)

    except Exception as e:
        print(e)
    return True

@sync_to_async
def handle_service_type(infrastructure_id, type):
    from compute_marketplace.models import ComputeMarketplace, History_Rent_Computes

    # type (1: model-training, 2: storage, 3: labeling-tool, 4: all)
    service_type = History_Rent_Computes.SERVICE_TYPE.ALL_SERVICE
    if type == "1":
        service_type = History_Rent_Computes.SERVICE_TYPE.MODEL_TRAINING
    if type == "2":
        service_type = History_Rent_Computes.SERVICE_TYPE.STORAGE
    if type == "3":
        service_type = History_Rent_Computes.SERVICE_TYPE.LABEL_TOOL
    if type == "4":
        service_type = History_Rent_Computes.SERVICE_TYPE.ALL_SERVICE
    compute =ComputeMarketplace.objects.filter(infrastructure_id=infrastructure_id, deleted_at__isnull = True).first()
    if compute is None:
        return
    history =History_Rent_Computes.objects.filter(compute_marketplace_id = compute.id, compute_gpu_id__isnull = True, deleted_at__isnull = True).first()
    if history is None:
        return
    history.service_type = service_type
    history.save()
    return history

def _handle_service_type(infrastructure_id, type):
    from compute_marketplace.models import ComputeMarketplace, History_Rent_Computes

    # type (1: model-training, 2: storage, 3: labeling-tool, 4: all)
    service_type = History_Rent_Computes.SERVICE_TYPE.ALL_SERVICE
    if type == "1":
        service_type = History_Rent_Computes.SERVICE_TYPE.MODEL_TRAINING
    if type == "2":
        service_type = History_Rent_Computes.SERVICE_TYPE.STORAGE
    if type == "3":
        service_type = History_Rent_Computes.SERVICE_TYPE.LABEL_TOOL
    if type == "4":
        service_type = History_Rent_Computes.SERVICE_TYPE.ALL_SERVICE
    compute =ComputeMarketplace.objects.filter(infrastructure_id=infrastructure_id, deleted_at__isnull = True).first()
    if compute is None:
        return
    history =History_Rent_Computes.objects.filter(compute_marketplace_id = compute.id, compute_gpu_id__isnull = True, deleted_at__isnull = True).first()
    if history is None:
        return
    history.service_type = service_type
    history.save()
    return history

@sync_to_async
def handle_cuda(infrastructure_id, data):
    print(data)
    from compute_marketplace.models import ComputeGPU, ComputeMarketplace
    from core.utils.convert_memory_to_byte import (
        convert_mb_to_byte,
        convert_mb_to_gb,
        convert_gb_to_byte,
        convert_byte_to_gb,
        convert_byte_to_mb,
    )
    for cuda in data:
        compute_gpu = ComputeGPU.objects.filter(gpu_id=cuda.get("uuid"), deleted_at__isnull = True).first()
        if compute_gpu is None:
            compute = ComputeMarketplace.objects.filter(infrastructure_id = infrastructure_id, deleted_at__isnull = True).first()
            if compute is None:
                return
            gpu = ComputeGPU.objects.create(
                compute_marketplace_id=compute.id,
                infrastructure_id=infrastructure_id,
                gpu_tflops=cuda.get("tflops"),
                cuda_cores=cuda.get("cpu_cores"),
                gpu_memory=convert_mb_to_byte(cuda.get("total_mem_mb")),
                gpu_memory_bandwidth=convert_gb_to_byte(
                    cuda.get("mem_bandwidth_gb_per_s")
                ),
                memory=convert_gb_to_byte(cuda.get("total_mem_mb")),
                ubuntu_version=cuda.get("ubuntu_version"),
                max_cuda_version=cuda.get("cuda_version"),
                driver_version=cuda.get("driver_version"),
            )
            return gpu
        else:
            compute_gpu.gpu_tflops = cuda.get('tflops')
            compute_gpu.cuda_cores = cuda.get("cpu_cores")
            compute_gpu.gpu_memory = convert_mb_to_byte(cuda.get("total_mem_mb"))
            compute_gpu.gpu_memory_bandwidth = convert_gb_to_byte(cuda.get(
                "mem_bandwidth_gb_per_s"
            ))
            compute_gpu.memory = convert_gb_to_byte(cuda.get("total_mem_mb"))
            compute_gpu.eff_out_of_total_nu_of_cpu_virtual_cores = (
                f"{cuda.get('used_cores')}/{cuda.get('cpu_cores')}"
            )
            compute_gpu.ubuntu_version = cuda.get("ubuntu_version")
            compute_gpu.max_cuda_version = cuda.get("cuda_version")
            compute_gpu.driver_version = cuda.get("driver_version")
            compute_gpu.save()
            return compute_gpu

def _handle_cuda(infrastructure_id, data):
    print(data)
    from compute_marketplace.models import ComputeGPU, ComputeMarketplace
    from core.utils.convert_memory_to_byte import (
        convert_mb_to_byte,
        convert_mb_to_gb,
        convert_gb_to_byte,
        convert_byte_to_gb,
        convert_byte_to_mb,
    )
    for cuda in data:
        compute_gpu = ComputeGPU.objects.filter(gpu_id=cuda.get("uuid"), deleted_at__isnull = True).first()
        if compute_gpu is None:
            compute = ComputeMarketplace.objects.filter(infrastructure_id = infrastructure_id, deleted_at__isnull = True).first()
            if compute is None:
                return
            gpu = ComputeGPU.objects.create(
                compute_marketplace_id=compute.id,
                infrastructure_id=infrastructure_id,
                gpu_tflops=cuda.get("tflops"),
                cuda_cores=cuda.get("cpu_cores"),
                gpu_memory=convert_mb_to_byte(cuda.get("total_mem_mb")),
                gpu_memory_bandwidth=convert_gb_to_byte(
                    cuda.get("mem_bandwidth_gb_per_s")
                ),
                memory=convert_gb_to_byte(cuda.get("total_mem_mb")),
                ubuntu_version=cuda.get("ubuntu_version"),
                max_cuda_version=cuda.get("cuda_version"),
                driver_version=cuda.get("driver_version"),
            )
            return gpu
        else:
            compute_gpu.gpu_tflops = cuda.get('tflops')
            compute_gpu.cuda_cores = cuda.get("cpu_cores")
            compute_gpu.gpu_memory = convert_mb_to_byte(cuda.get("total_mem_mb"))
            compute_gpu.gpu_memory_bandwidth = convert_gb_to_byte(cuda.get(
                "mem_bandwidth_gb_per_s"
            ))
            compute_gpu.memory = convert_gb_to_byte(cuda.get("total_mem_mb"))
            compute_gpu.eff_out_of_total_nu_of_cpu_virtual_cores = (
                f"{cuda.get('used_cores')}/{cuda.get('cpu_cores')}"
            )
            compute_gpu.ubuntu_version = cuda.get("ubuntu_version")
            compute_gpu.max_cuda_version = cuda.get("cuda_version")
            compute_gpu.driver_version = cuda.get("driver_version")
            compute_gpu.save()
            return compute_gpu

def subscription_selfhost_cron():
    from compute_marketplace.models import ComputeMarketplace, History_Rent_Computes
    from plugins.plugin_centrifuge import (
        run_centrifuge,
    )   

    list_history = History_Rent_Computes.objects.filter(deleted_at__isnull=True, compute_install=History_Rent_Computes.InstallStatus.WAIT_VERIFY).all()
    for history in list_history:
        import json
        compute = ComputeMarketplace.objects.filter(id = history.compute_marketplace_id).first()
        run_centrifuge(history.account_id, compute.infrastructure_id)
        # try:
        #     import requests
        #     from django.conf import settings

        #     url = settings.API_VERIFY_JOB

        #     payload = json.dumps({
        #         "user_id": history.account_id,
        #         "infrastructure_id": compute.infrastructure_id
        #     })
            
        #     headers = {
        #         'Content-Type': 'application/json'
        #     }

        #     response = requests.request("POST", url, headers=headers, data=payload)

        #     if response.status_code != 200:
        #         run_centrifuge(history.account_id, compute.infrastructure_id)

        # except:
        #     run_centrifuge(history.account_id, compute.infrastructure_id)
