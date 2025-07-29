from model_marketplace.calc_transformer_flops import config_parser, calc_params
import torch
# from projects.flops_engine import TorchFLOPsByFX
from calflops import calculate_flops
from aixblock_core.projects.flops_tensor import model_profiler
import tensorflow as tf
from aixblock_core.model_marketplace.calc_transformer_flops import convert_flops
# from thop import profile

def calc_only_time_need(flops, num_gpu, model_size,  assumed_mfu=0.37, tokens_num=300e9):
    flops_throughput = flops * num_gpu * assumed_mfu
    if tokens_num:
        flops_needed = 6 * model_size * tokens_num
    else:
        flops_needed = 6 * model_size

    time_needed_s = flops_needed / flops_throughput # in seconds
    hours = time_needed_s/3600

    return hours

def calc_time_neeed_nlp(args, num_gpu, model_size, assumed_mfu=0.37, tokens_num=300e9):
    total_flops = calc_params(args)

    flops_throughput = total_flops * num_gpu * assumed_mfu
    flops_needed = 6 * model_size * tokens_num 
    time_needed_s = flops_needed / flops_throughput # in seconds
    hours = time_needed_s/3600

    return total_flops, hours

def calc_mem_pytorch_images(model, matrix, input_shape):
    gpu_mem = 0
    # try:
    #     x = torch.randn(input_shape).to(device='cuda:0')

    #     with torch.no_grad():
    #         flops_counter = TorchFLOPsByFX(model)
    #         flops_counter.propagate(matrix)

    #     result_table = flops_counter.print_result_table()
    #     total_flops = flops_counter.print_total_flops(show=True)
    #     total_time = flops_counter.print_total_time() 
    #     max_memory = flops_counter.print_max_memory()
    #     gpu_mem = flops_counter.print_max_memory()
    # except Exception as e:
    #     print(e)

    return gpu_mem

def calc_flops_neeed_pytorch_images(model, input_shape):
    total_flops_str, macs, params = calculate_flops(model=model, 
                                    input_shape=input_shape,
                                    output_as_string=True,
                                    output_precision=4)
    
    return total_flops_str, macs, params

def calc_time_neeed_pytorch_images(model, input_shape, num_gpu, assumed_mfu=0.37):
    total_flops_str, macs, params = calculate_flops(model=model, 
                                    input_shape=input_shape,
                                    output_as_string=True,
                                    output_precision=4)
    
    flops_value, _ = total_flops_str.split()
    param_value, _ = params.split()

    total_flops = float(flops_value) * 10**6
    param_value = float(param_value) * 10**6

    flops_throughput = total_flops * num_gpu * assumed_mfu
    flops_needed = 6 * param_value

    time_needed_s = flops_needed / flops_throughput # in seconds
    hours = time_needed_s/3600

    return hours, total_flops, param_value

def calc_param_from_tflop(flops_value, acc=0.7, epochs = 50):
    flops_needed = float(flops_value) * 10**12 * acc

    param_value = flops_needed / (6*10**6)

    flops_throughput = float(flops_value) * 10**12

    time_needed_s = flops_needed * epochs / flops_throughput
    
    hours = time_needed_s/3600

    return hours, flops_needed, param_value

def calc_tflop_from_param(tflops_value, param_value, acc=0.7, epochs = 50):
    param_value = float(param_value)* 10**6

    flops_needed = param_value * 6

    flops_throughput = tflops_value *10**12

    time_needed_s = flops_needed * epochs / flops_throughput

    hours = time_needed_s/3600

    return hours, flops_needed, param_value

def calc_mem_tf(model, batch_size, num_gpu, assumed_mfu=0.37):
    from tensorflow.python.profiler import model_analyzer, option_builder

    input_signature = [
        tf.TensorSpec(
            shape=(1, *params.shape[1:]), 
            dtype=params.dtype, 
            name=params.name
        ) for params in model.inputs
    ]
    forward_graph = tf.function(model, input_signature).get_concrete_function().graph
    options = option_builder.ProfileOptionBuilder.float_operation()
    graph_info = model_analyzer.profile(forward_graph, options=options)
    flops = graph_info.total_float_ops // 2

    flops_throughput = flops * num_gpu * assumed_mfu
    flops_needed = 6 * model.count_params()

    time_needed_s = flops_needed / flops_throughput # in seconds
    hours = time_needed_s/3600

    return flops, hours

    # return flops

def calc_mem_gpu_tf(model, batch_size):
    default_dtype = tf.keras.backend.floatx()
    shapes_mem_count = 0
    internal_model_mem_count = 0
    # for layer in model.layers:
    #     if isinstance(layer, tf.keras.Model):
    #         internal_model_mem_count += keras_model_memory_usage_in_bytes(
    #             layer, batch_size=batch_size
    #         )
    #     single_layer_mem = tf.as_dtype(layer.dtype or default_dtype).size
        
    #     # print(layer.input)
    #     # print(layer.output)
    #     out_shape = layer.output.shape
    #     if isinstance(out_shape, list):
    #         out_shape = out_shape[0]
            
    trainable_count = sum(
        [tf.keras.backend.count_params(p) for p in model.trainable_weights]
    )
    non_trainable_count = sum(
        [tf.keras.backend.count_params(p) for p in model.non_trainable_weights]
    )

    total_memory = (
        batch_size 
        + internal_model_mem_count
        + trainable_count
        + non_trainable_count
    )

    return total_memory


    




