import requests

class DockerStats:
    def __init__(self, docker_host="http://127.0.0.1:2375"):
        """
        Khởi tạo đối tượng DockerStats với địa chỉ Docker host.
        """
        self.docker_host = docker_host
    
    def get_system_info(self):
        """
        Lấy thông tin hệ thống từ Docker API.
        
        :return: Tổng bộ nhớ hệ thống (bytes) và số lõi CPU.
        """
        url = f"{self.docker_host}/info"
        response = requests.get(url)

        if response.status_code == 200:
            system_info = response.json()
            total_system_memory = system_info.get('MemTotal', 0)  # Tổng RAM (bytes)
            total_system_cpu_cores = system_info.get('NCPU', 1)  # Số lõi CPU

            return total_system_memory, total_system_cpu_cores
        else:
            raise Exception(f"Không thể lấy thông tin hệ thống: {response.status_code} {response.text}")

    def get_container_stats(self, container_id):
        """
        Lấy thông tin thống kê tài nguyên của container.
        
        :param container_id: ID hoặc tên của container.
        :return: Thống kê tài nguyên của container.
        """
        url = f"{self.docker_host}/containers/{container_id}/stats?stream=false"
        response = requests.get(url)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Không thể lấy thông tin thống kê cho container {container_id}: {response.status_code} {response.text}")

    def calculate_memory_usage(self, memory_stats):
        """
        Tính toán tỷ lệ phần trăm sử dụng bộ nhớ.
        
        :param memory_stats: Thông tin thống kê bộ nhớ.
        :return: Tỷ lệ phần trăm sử dụng bộ nhớ và dung lượng đã sử dụng.
        """
        used_memory = memory_stats['usage'] - memory_stats['stats'].get('cache', 0)
        available_memory = memory_stats['limit']
        memory_usage_percentage = (used_memory / available_memory) * 100.0 if available_memory > 0 else 0.0
        return memory_usage_percentage, used_memory

    def calculate_cpu_usage(self, cpu_stats, precpu_stats):
        """
        Tính toán tỷ lệ phần trăm sử dụng CPU.
        
        :param cpu_stats: Thông tin thống kê CPU hiện tại.
        :param precpu_stats: Thông tin thống kê CPU trước đó.
        :return: Tỷ lệ phần trăm sử dụng CPU.
        """
        cpu_delta = cpu_stats['cpu_usage']['total_usage'] - precpu_stats['cpu_usage']['total_usage']
        system_cpu_delta = cpu_stats['system_cpu_usage'] - precpu_stats['system_cpu_usage']

        if 'percpu_usage' in cpu_stats['cpu_usage']:
            number_cpus = len(cpu_stats['cpu_usage']['percpu_usage'])
        elif 'online_cpus' in cpu_stats:
            number_cpus = cpu_stats['online_cpus']
        else:
            number_cpus = 1

        cpu_usage_percentage = (cpu_delta / system_cpu_delta) * number_cpus * 100.0 if system_cpu_delta > 0 else 0.0
        return cpu_usage_percentage

    def get_all_containers_stats(self):
        """
        Lấy thông tin thống kê tài nguyên cho tất cả các container.
        
        :return: Danh sách thống kê tài nguyên của tất cả các container.
        """
        url = f"{self.docker_host}/containers/json"
        response = requests.get(url)

        if response.status_code == 200:
            container_list = response.json()
            return [container['Id'] for container in container_list]
        else:
            raise Exception(f"Không thể lấy thông tin danh sách container: {response.status_code} {response.text}")

    def calculate_total_usage(self):
        """
        Tính tổng dung lượng RAM và CPU mà tất cả các container đang sử dụng.
        """
        total_used_memory = 0
        total_memory_usage_percentage = 0.0
        total_cpu_usage = 0.0
        container_ids = self.get_all_containers_stats()

        for container_id in container_ids:
            try:
                stats = self.get_container_stats(container_id)
                memory_usage, used_memory = self.calculate_memory_usage(stats['memory_stats'])
                cpu_usage = self.calculate_cpu_usage(stats['cpu_stats'], stats['precpu_stats'])

                total_used_memory += used_memory
                total_memory_usage_percentage += memory_usage
                total_cpu_usage += cpu_usage
            except Exception as e:
                print(f"Lỗi khi xử lý container {container_id}: {e}")

        average_memory_usage_percentage = total_memory_usage_percentage / len(container_ids) if container_ids else 0.0

        return total_used_memory, average_memory_usage_percentage, total_cpu_usage

    def calculate_scale_capacity(self, total_system_memory, total_system_cpu_cores, type="ml"):
        """
        Tính toán số lượng container tối đa có thể scale dựa trên tài nguyên hệ thống.
        
        :param total_system_memory: Tổng dung lượng RAM của hệ thống (bytes).
        :param total_system_cpu_cores: Tổng số lõi CPU của hệ thống.
        :return: Số lượng container tối đa có thể scale dựa trên RAM và CPU.
        """
        # Lấy tài nguyên đã sử dụng tổng cộng
        total_used_memory, avg_memory_usage, total_cpu_usage = self.calculate_total_usage()

        if type == "ml":
            # Nếu không có container nào, sử dụng giá trị giả định
            memory_usage_per_container = 128 * 1024 * 1024  # Giả định mỗi container dùng 128MB RAM
            cpu_usage_per_container = 1.0  # Giả định mỗi container dùng 1% CPU

        elif type == "platform":
            memory_usage_per_container = 1024 * 1024 * 1024  # Giả định mỗi container dùng 1GB RAM
            cpu_usage_per_container = 50.0  # Giả định mỗi container dùng 50% CPU

        # Tính số lượng container tối đa có thể scale dựa trên RAM
        remaining_memory = total_system_memory - total_used_memory
        max_containers_ram = remaining_memory / memory_usage_per_container if memory_usage_per_container > 0 else 0

        # Tính số lượng container tối đa có thể scale dựa trên CPU
        remaining_cpu = (total_system_cpu_cores * 100.0) - total_cpu_usage  # 100% cho mỗi CPU
        max_containers_cpu = remaining_cpu / cpu_usage_per_container if cpu_usage_per_container > 0 else 0

        # Trả về số lượng container tối đa có thể scale (lấy giá trị nhỏ nhất giữa RAM và CPU)
        return min(max_containers_ram, max_containers_cpu)
    
    def scale_capacity(self, type="ml"):
        """
        Hiển thị số lượng container tối đa có thể scale.
        """
        try:
            # Lấy thông tin hệ thống từ Docker API
            total_system_memory, total_system_cpu_cores = self.get_system_info()

            # Tính toán số lượng container tối đa có thể scale
            max_containers = self.calculate_scale_capacity(total_system_memory, total_system_cpu_cores, type)
            print(f"Số lượng container tối đa có thể scale ra được: {int(max_containers)}")

            return int(max_containers)
        except Exception as e:
            print(f"Không thể tính toán số lượng container có thể scale: {e}")

    def display_stats(self, container_id):
        """
        Hiển thị thông tin tài nguyên của container cụ thể và tổng tài nguyên của tất cả các container.
        """
        try:
            stats = self.get_container_stats(container_id)
            memory_usage = self.calculate_memory_usage(stats['memory_stats'])[0]
            cpu_usage = self.calculate_cpu_usage(stats['cpu_stats'], stats['precpu_stats'])

            print(f"Tỷ lệ phần trăm sử dụng bộ nhớ của container {container_id}: {memory_usage:.2f}%")
            print(f"Tỷ lệ phần trăm sử dụng CPU của container {container_id}: {cpu_usage:.2f}%")

            total_memory, avg_memory_usage, total_cpu = self.calculate_total_usage()
            print(f"Tổng dung lượng RAM mà tất cả các container đang sử dụng: {total_memory / (1024 ** 2):.2f} MB")
            print(f"Tỷ lệ phần trăm sử dụng RAM trung bình của tất cả các container: {avg_memory_usage:.2f}%")
            print(f"Tổng tỷ lệ phần trăm sử dụng CPU của tất cả các container: {total_cpu:.2f}%")
            
        except Exception as e:
            print(e)
    
    def display_scale_capacity(self):
        """
        Hiển thị số lượng container tối đa có thể scale.
        """
        try:
            # Lấy thông tin hệ thống từ Docker API
            total_system_memory, total_system_cpu_cores = self.get_system_info()
            print(total_system_memory, total_system_cpu_cores)

            # Tính toán số lượng container tối đa có thể scale
            max_containers = self.calculate_scale_capacity(total_system_memory, total_system_cpu_cores)
            print(f"Số lượng container tối đa có thể scale ra được: {int(max_containers)}")
        except Exception as e:
            print(f"Không thể tính toán số lượng container có thể scale: {e}")

if __name__ == "__main__":
    docker_stats = DockerStats()
    # total_memory, avg_memory_usage, total_cpu = docker_stats.calculate_total_usage()
    # print(f"Tổng dung lượng RAM mà tất cả các container đang sử dụng: {total_memory / (1024 ** 2):.2f} MB")
    # print(f"Tỷ lệ phần trăm sử dụng RAM trung bình của tất cả các container: {avg_memory_usage:.2f}%")
    # print(f"Tổng tỷ lệ phần trăm sử dụng CPU của tất cả các container: {total_cpu:.2f}%")

    # Hiển thị số lượng container tối đa có thể scale
    docker_stats.display_scale_capacity()