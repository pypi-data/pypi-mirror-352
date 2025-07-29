import uuid

from django.core.management.base import BaseCommand
from plugins.plugin_centrifuge import publish_message


class Command(BaseCommand):
    help = "Send fake compute information while add compute in Computes Supplier and Computes Self-Hosted."

    def add_arguments(self, parser):
        parser.add_argument('--token', dest="token", type=str)
        parser.add_argument('--ip', dest="ip", type=str)

    def handle(self, *args, **options):
        gpu_ids = [uuid.uuid4().__str__(), uuid.uuid4().__str__(), uuid.uuid4().__str__(), uuid.uuid4().__str__()]

        publish_message(
            channel=options.get("token"),
            data={
                "action": "",
                "type": "IP_ADDRESS",
                "data": options.get("ip"),
            },
            prefix=False,
        ).join()

        publish_message(
            channel=options.get("token"),
            data={
                "action": "",
                "type": "DOCKER",
            },
            prefix=False,
        ).join()

        cuda_data = []

        for gpu_id in gpu_ids:
            cuda_data.append({
                    "uuid": gpu_id,
                    "tflops": 12.22,
                    "mem_clock_mhz": "2134",
                    "gpu_clock_mhz": "2134",
                    "memory_bus_width": "32GT/s",
                    "pcie_link_gen_max": "4.0",
                    "pcie_link_width_max": "234GT/s",
                    "driver_version": "543.21",
                    "cores": "145",
                    "cuda_cores": "3245",
                    "ubuntu_version": "22.04",
                    "used_cores": "2",
                    "cpu_cores": "18",
                    "mem_bandwidth_gb_per_s": 236,
                    "ram_info": {
                        "total_ram_mb": 32768,
                        "used_ram_mb": 4673,
                    },
                    "all_disk_info": [],
                    "total_mem_mb": 4096,
                    "free_mem_mb": 4000,
                })

        publish_message(
            channel=options.get("token"),
            data={
                "action": "",
                "type": "CUDA",
                "data": [],
            },
            prefix=False,
        ).join()

        publish_message(
            channel=options.get("token"),
            data={
                "action": "",
                "type": "SERVER_INFO",
                "data": [
                    {
                        "name": "fake-pc",
                        "cpu": "Intel(R) Core(TM) i5-9300H CPU @ 2.40GHz",
                        "ram": "33486311424",
                        "storage": "155889332224",
                        "diskType": "ext2/ext3",
                        "os": "GNU/Linux",
                        "serial_number": "C1W1MVV69B",
                        "ip": options.get("ip"),
                    },
                ],
            },
            prefix=False,
        ).join()

        publish_message(
            channel=options.get("token"),
            data={
                "action": "",
                "type": "GPU",
                "data": [
                    {"id":0,"name":"NVIDIA RTX A6000","uuid":gpu_ids[0],"fan":"N/A","temperature":"40C","power_usage":"30W","power_consumption":"360w","memory_usage":"1425MiB","memory":"32GiB","serialno":"52U82V5C00"},
                    {"id":1,"name":"NVIDIA RTX A5000","uuid":gpu_ids[1],"fan":"N/A","temperature":"38C","power_usage":"46W","power_consumption":"360w","memory_usage":"964MiB","memory":"24GiB","serialno":"RI0GPZMYOR"},
                    {"id":2,"name":"NVIDIA RTX A4000","uuid":gpu_ids[2],"fan":"N/A","temperature":"58C","power_usage":"24W","power_consumption":"360w","memory_usage":"1148MiB","memory":"16GiB","serialno":"91ZV75L0HL"},
                    {"id":3,"name":"NVIDIA RTX A3000","uuid":gpu_ids[3],"fan":"N/A","temperature":"60C","power_usage":"66W","power_consumption":"360w","memory_usage":"1687MiB","memory":"8GiB","serialno":"IRT3IJPWTD"},
                ],
            },
            prefix=False,
        ).join()

        publish_message(
            channel=options.get("token"),
            data={
                "action": "",
                "type": "CONFIRM_RESET",
                "data": "yes",
            },
            prefix=False,
        ).join()
