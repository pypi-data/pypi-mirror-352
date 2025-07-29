# GPU picking
# http://stackoverflow.com/a/41638727/419116
# Nvidia-smi GPU memory parsing.
# must set
# CUDA_DEVICE_ORDER=PCI_BUS_ID
# see https://github.com/tensorflow/tensorflow/issues/152#issuecomment-273663277

# Tested on nvidia-smi 370.23

import os
import subprocess
import sys
from pydantic import BaseModel

import regex

class GpuUtil():
    def __init__(self):
        pass
    def run_command(cmd):
        """Run command, return output as string."""
        
        output = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).communicate()[0]
        return output.decode("ascii")

    def list_available_gpus(self):
        """Returns list of available GPU ids."""
        
        output = self.run_command("nvidia-smi -L")
        # lines of the form GPU 0: TITAN X
        #GPU 0: NVIDIA RTX A6000 (UUID: GPU-b8b0bee9-1a2f-a1ca-3f22-9eed1d675873)
        gpu_regex = regex.compile(r"GPU (?P<gpu_index>\d+):(?P<gpu_name>\s+) (UUID: (?P<gpu_id>\s+))")
        result = []
        for line in output.strip().split("\n"):
            m = gpu_regex.match(line)
            assert m, "Couldnt parse "+line
            result.append(int(m.group("gpu_id")))
            print(m.group("gpu_index"))
            print(m.group("gpu_name"))
            print(m.group("gpu_id"))

        return result

    def gpu_memory_map(self):
        """Returns map of GPU id to memory allocated on that GPU."""

        output = self.run_command("nvidia-smi")
        gpu_output = output[output.find("GPU Memory"):]
        # lines of the form
        # |    0      8734    C   python                                       11705MiB |
        memory_regex = regex.compile(r"[|]\s+?(?P<gpu_id>\d+)\D+?(?P<pid>\d+).+[ ](?P<gpu_memory>\d+)MiB")
        rows = gpu_output.split("\n")
        result = {gpu_id: 0 for gpu_id in self.list_available_gpus()}
        for row in gpu_output.split("\n"):
            m = memory_regex.search(row)
            if not m:
                continue
            gpu_id = int(m.group("gpu_id"))
            gpu_memory = int(m.group("gpu_memory"))
            result[gpu_id] += gpu_memory
        return result

    def pick_gpu_lowest_memory(self):
        """Returns GPU with the least allocated memory"""

        memory_gpu_map = [(memory, gpu_id) for (gpu_id, memory) in self.gpu_memory_map().items()]
        best_memory, best_gpu = sorted(memory_gpu_map)[0]
        return best_gpu

    def setup_one_gpu():
        assert not 'tensorflow' in sys.modules, "GPU setup must happen before importing TensorFlow"
        gpu_id = self.pick_gpu_lowest_memory()
        print("Picking GPU "+str(gpu_id))
        os.environ["CUDA_VISIBLE_DEVICES"] = str(gpu_id)

    def setup_no_gpu(self):
        if 'tensorflow' in sys.modules:
            print("Warning, GPU setup must happen before importing TensorFlow")
        os.environ["CUDA_VISIBLE_DEVICES"] = ''
from enum import Enum

class GPU(Enum):
    # NVIDIA A6000 Tensor Core GPU: 38.7 TFLOPS
    A6000 = 38.7
    # NVIDIA A100 Tensor Core GPU: 19.5 TFLOPS
    A100 = 19.5e12
    # NVIDIA K80 GPU (from the Tesla series): 2.91 TFLOPS
    K80 = 2.91e12
    # NVIDIA V100 Tensor Core GPU: 14 TFLOPS
    V100 = 14e12
    # NVIDIA TITAN RTX GPU: 16.3 TFLOPS
    TITAN_RTX = 16.3e12
    # NVIDIA RTX 3090 GPU: 35.6 TFLOPS
    RTX_3090 = 35.6e12
    # NVIDIA RTX 3080 GPU: 29.7 TFLOPS
    RTX_3080 = 29.7e12
    # NVIDIA RTX 4060 GPU: 15.1 TFLOPS
    RTX_4060= 15.1e12
    # AMD Radeon Instinct MI100 GPU: 23.1 TFLOPS
    MI100 = 23.1e12
    # AMD Radeon RX 6900 XT GPU: 23.04 TFLOPS
    RX_6900_XT = 23.04e12
    # Hypothetical GPU: 20 TFLOPS
    H100 = 20e12
    # NVIDIA RTX 2080 Ti GPU: 13.45 TFLOPS
    RTX_2080_TI = 13.45e12
    # NVIDIA RTX 2070 Super GPU: 9.06 TFLOPS
    RTX_2070_SUPER = 9.06e12
    # NVIDIA GTX 1080 Ti GPU: 11.34 TFLOPS
    GTX_1080_TI = 11.34e12
    # NVIDIA GTX 1070 GPU: 5.78 TFLOPS
    GTX_1070 = 5.78e12

def map_gpu_to_tflops(gpu_name):
    for gpu in GPU:
        if gpu.name.replace("_", " ") in gpu_name:
            return gpu.value
    return 0
class PowerConsumption(Enum):
    A100 = 400  # in watts
    K80 = 300
    V100 = 250
    TITAN_RTX = 280
    RTX_3090 = 350
    RTX_3080 = 320
    MI100 = 300
    RX_6900_XT = 300
    H100 = 350
    RTX_2080_TI = 260
    RTX_2070_SUPER = 215
    GTX_1080_TI = 250
    GTX_1070 = 150
    RTX_4060= 115 
    
    
def map_gpu_to_power_consumption(gpu_name):
    for gpu in PowerConsumption:
        if gpu.name.replace("_", " ") in gpu_name:
            return gpu.value
    return 0

class GPUCostCalculator:
    def __init__(self, price_per_flop, price_per_kwh):
        self.price_per_flop = price_per_flop
        self.price_per_kwh = price_per_kwh
        self.gpu_counts = {}
        self.efficiency = 1.0

    def add_gpu(self, gpu_type, count):
        if gpu_type not in GPU:
            raise ValueError(f"Unknown GPU: {gpu_type}. Please add its FLOPS to the GPU Enum.")
        self.gpu_counts[gpu_type] = count

    def set_efficiency(self, efficiency):
        if not (0 <= efficiency <= 1):
            raise ValueError("Efficiency should be between 0 and 1.")
        self.efficiency = efficiency

    def calculate_total_cost(self, hours):
        compute_cost = 0
        power_cost = 0
        
        for gpu_type, count in self.gpu_counts.items():
            flops = gpu_type.value
            power = PowerConsumption[gpu_type.name].value
            
            # Calculate compute cost based on efficiency
            cost_per_gpu = flops * self.price_per_flop * hours * self.efficiency
            compute_cost += cost_per_gpu * count
            
            # Calculate power cost
            power_cost_per_gpu = power/1000 * self.price_per_kwh * hours  # Convert watts to kW
            power_cost += power_cost_per_gpu * count
        
        total_cost = compute_cost + power_cost
        return total_cost


calculator = GPUCostCalculator(
    price_per_flop=1e-13, 
    price_per_kwh=0.1
)
calculator.add_gpu(GPU.A100, 64)
calculator.add_gpu(GPU.V100, 0)
calculator.set_efficiency(0.8)

hours = 600
total_cost = calculator.calculate_total_cost(hours)
# print(f"The cost of running the GPUs for {hours} hours is {total_cost:.2f} NOK")