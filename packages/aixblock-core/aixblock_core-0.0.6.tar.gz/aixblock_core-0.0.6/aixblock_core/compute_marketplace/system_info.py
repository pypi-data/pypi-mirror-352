from core.utils.docker_container_action import dockerContainerReadConfig
from compute_marketplace.models import ComputeMarketplace, ComputeGPU
import json

from core.utils.convert_memory_to_byte import convert_mb_to_byte, convert_byte_to_gb


def update_system_info():
    print("start update_system_info")
    compute_marketplace = ComputeMarketplace.objects.filter(
        deleted_at__isnull=True, type__in=["MODEL-SYSTEM", "MODEL-CUSTOMER"]
    ).all()
    for compute in compute_marketplace:
        try:
            compute_configs = dockerContainerReadConfig(compute.ip_address)
            print(compute_configs)
            virtual_memory = compute_configs["virtual_memory"]
            # cuda_driver_info = json.loads(compute_configs["cuda_driver_info"])
            compute_gpu = ComputeGPU.objects.filter(
                deleted_at__isnull=True, compute_marketplace_id=compute.id, 
            ).all()
            # pci_devices = compute_configs["pci_devices"]
            # gpu_info = compute_configs["gpu_info"]
            for gpu in compute_gpu:
                try:
                    # for gpu_memory in gpu_info:
                    #     if gpu_memory["index"] == gpu.gpu_index:
                    #         gpu.memory = convert_mb_to_byte(gpu_memory["memory_total"])
                    if compute_configs["download_speed"] is not None:
                        gpu.internet_down_speed = compute_configs["download_speed"]
                    if compute_configs["upload_speed"] is not None:
                        gpu.internet_up_speed = compute_configs["upload_speed"]
                    gpu.motherboard = compute_configs["baseboard_product_name"]
                    # gpu.gpu_memory = virtual_memory["total"]  # convert to byte
                    # gpu.gpu_memory_used = virtual_memory["used"]  # convert to byte
                    gpu.branch_name = "nvidia"
                    # gpu.max_cuda_version = cuda_driver_info["cuda_version"]
                    # gpu.driver_version = cuda_driver_info["driver_version"]
                    # gpu.per_gpu_pcie_bandwidth = compute_configs["lnksta_info"]
                    # gpu.number_of_pcie_per_gpu = f"{pci_devices['pcie_link_gen_max']}/{pci_devices['pcie_link_width_max']}"
                    # gpu.eff_out_of_total_nu_of_cpu_virtual_cores = f"{compute_configs['nu_of_cpu']}/{compute_configs['used_cores']}"
                    gpu.eff_out_of_total_system_ram = f"{convert_byte_to_gb(virtual_memory['used'])}/{convert_byte_to_gb(virtual_memory['total'])}"
                    gpu.save()
                    # gpu memory bandwidth and tflop read from verify app
                except Exception as e:
                    print(f"Error updating GPU info for compute {compute.id}: {e}")
                    continue  
        except Exception as e:
            print(f"Error updating compute {compute.id}: {e}")
            continue  
def update_compute_marketplace(compute_marketplace_id):
    try:
        compute = ComputeMarketplace.objects.get(
            id=compute_marketplace_id,
            deleted_at__isnull=True,
        )
        compute_configs = dockerContainerReadConfig(compute.ip_address)
        print(compute_configs)
        virtual_memory = compute_configs["virtual_memory"]

        compute_gpu = ComputeGPU.objects.filter(
            deleted_at__isnull=True, compute_marketplace_id=compute.id
        ).all()

        for gpu in compute_gpu:
            try:
                if compute_configs["download_speed"] is not None:
                    gpu.internet_down_speed = compute_configs["download_speed"]

                if compute_configs["upload_speed"] is not None:
                    gpu.internet_up_speed = compute_configs["upload_speed"]
                gpu.motherboard = compute_configs["baseboard_product_name"]
                gpu.branch_name = "nvidia"
                gpu.eff_out_of_total_system_ram = f"{convert_byte_to_gb(virtual_memory['used'])}/{convert_byte_to_gb(virtual_memory['total'])}"
                gpu.save()
            except Exception as e:
                print(f"Error updating GPU info for compute {compute.id}: {e}")
                continue
    except ComputeMarketplace.DoesNotExist:
        print(f"Compute Marketplace with id {compute_marketplace_id} does not exist.")
    except Exception as e:
        print(f"Error updating compute {compute_marketplace_id}: {e}")