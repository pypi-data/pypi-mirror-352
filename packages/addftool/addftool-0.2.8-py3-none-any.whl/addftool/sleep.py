import time
import subprocess
import sys
import multiprocessing as mp

try:
    import torch
except ImportError:
    print("PyTorch is not installed. Please install it to run this script.")
    sys.exit(1)


def get_gpu_stats(device_id):
    """获取指定GPU的利用率和显存使用情况"""
    try:
        cmd = f"nvidia-smi --id={device_id} --query-gpu=utilization.gpu,memory.used --format=csv,noheader,nounits"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error running nvidia-smi for GPU {device_id}")
            return None, None
        
        # 解析输出
        output = result.stdout.strip()
        if output:
            parts = output.split(',')
            if len(parts) == 2:
                gpu_util = int(parts[0])  # GPU利用率百分比
                memory_used = int(parts[1])  # 显存使用量(MB)
                return gpu_util, memory_used
        
        return None, None
    except Exception as e:
        print(f"Error getting GPU stats for device {device_id}: {e}")
        return None, None

def check_gpu_occupied(device_id, util_threshold=20, memory_threshold=2048):
    """检查GPU是否被其他进程占用
    
    Args:
        device_id: GPU设备ID
        util_threshold: GPU利用率阈值(默认20%)
        memory_threshold: 显存使用阈值(默认2048MB = 2GB)
    
    Returns:
        bool: True表示GPU被占用，False表示GPU空闲
    """
    gpu_util, memory_used = get_gpu_stats(device_id)
    
    if gpu_util is None or memory_used is None:
        # 获取失败时保守处理
        return True
    
    # 判断是否被占用
    is_occupied = gpu_util > util_threshold or (memory_threshold > 0 and memory_used > memory_threshold)
    
    if is_occupied:
        print(f"GPU {device_id}: Util={gpu_util}%, Memory={memory_used}MB - Occupied")
    
    return is_occupied

def check_all_gpus(num_gpus, util_threshold=20, memory_threshold=-1):
    """检查所有GPU是否被占用"""
    for device_id in range(num_gpus):
        if check_gpu_occupied(device_id, util_threshold, memory_threshold):
            return True, device_id
    return False, -1

def get_all_gpu_status(num_gpus):
    """获取所有GPU的状态信息"""
    print("\nGPU Status:")
    print("-" * 50)
    for device_id in range(num_gpus):
        gpu_util, memory_used = get_gpu_stats(device_id)
        if gpu_util is not None and memory_used is not None:
            status = "Available" if (gpu_util <= 20 and memory_used <= 2048) else "Occupied"
            print(f"GPU {device_id}: Util={gpu_util:3d}%, Memory={memory_used:5d}MB - {status}")
        else:
            print(f"GPU {device_id}: Unable to get stats")
    print("-" * 50)

def matrix_multiply_worker(matrix_size=8192, time_duration=4.0, sleep_duration=1.0, util_threshold=20, memory_threshold=-1):
    # 获取GPU数量
    num_gpus = torch.cuda.device_count()
    if num_gpus == 0:
        print("No GPUs available!")
        return

    matrices = {}
    # print(f"Creating {matrix_size}x{matrix_size} matrices on all GPUs...")
    for device_id in range(num_gpus):
        device = torch.device(f'cuda:{device_id}')
        matrices[device_id] = {
            'a': torch.randn(matrix_size, matrix_size, device=device, dtype=torch.float32),
            'b': torch.randn(matrix_size, matrix_size, device=device, dtype=torch.float32)
        }

    # 主循环
    while True:
        try:
            # 检查所有GPU是否被占用
            has_occupied_gpu, occupied_gpu = check_all_gpus(num_gpus, util_threshold, memory_threshold)
            if has_occupied_gpu:
                break

            start_time = time.time()
            perform_count = 0
            while True:
                # 在所有GPU上同时执行矩阵乘法
                results = {}
                for device_id in range(num_gpus):
                    results[device_id] = torch.matmul(matrices[device_id]['a'], matrices[device_id]['b'])
                
                perform_count += 1

                if perform_count % 10 == 0:
                    for device_id in range(num_gpus):
                        torch.cuda.synchronize(device_id)
                
                torch.cuda.synchronize()  # 确保所有GPU操作完成
                elapsed_time = time.time() - start_time
                if elapsed_time > time_duration:
                    break

            # 清理内存
            
            time.sleep(sleep_duration)
            
        except KeyboardInterrupt:
            print("\nKeyboardInterrupt received, stopping...")
            stop_flag = True
            exit(0)
        except Exception as e:
            print(f"\nError occurred: {e}")
            # 尝试清理内存
            try:
                for device_id in range(num_gpus):
                    torch.cuda.set_device(device_id)
                    torch.cuda.empty_cache()
            except:
                pass
            time.sleep(5)
    
def sleep_main(args):
    # 设置多进程启动方法
    mp.set_start_method('spawn', force=True)

    num_gpus = torch.cuda.device_count()
    if num_gpus == 0:
        print("No GPUs available!")
        exit(1)
        
    # 显示初始GPU状态
    get_all_gpu_status(num_gpus)

    current_process = None
    
    # 主循环
    while True:
        try:
            # 检查所有GPU是否被占用
            has_occupied_gpu, occupied_gpu = check_all_gpus(num_gpus, util_threshold=args.util_threshold, memory_threshold=args.memory_threshold)
            
            if has_occupied_gpu:
                # 休眠60秒
                print("Holding for 60 seconds...")
                time.sleep(60)
                
            else:
                # GPU空闲，启动矩阵乘法进程
                current_process = mp.Process(
                    target=matrix_multiply_worker,
                    args=(args.matrix_size, args.time_duration, args.sleep_duration, args.util_threshold, args.memory_threshold), 
                )
                current_process.start()
                current_process.join()
            
        except KeyboardInterrupt:
            print("\nKeyboardInterrupt received, stopping...")
            stop_flag = True
            break
        except Exception as e:
            print(f"\nError occurred: {e}")
            time.sleep(5)

    print("\nProgram stopped")


def add_sleep_args(subparsers):
    sleep_parser = subparsers.add_parser('sleep', help='Sleep for a while and check GPU status')
    add_args(sleep_parser)


def add_args(parser):
    parser.add_argument('--matrix_size', type=int, default=8192, help='Size of the matrices to multiply')
    parser.add_argument('--time_duration', type=float, default=4.0, help='Duration to perform matrix multiplication')
    parser.add_argument('--sleep_duration', type=float, default=1.0, help='Duration to sleep between checks')

    parser.add_argument('--util_threshold', type=int, default=20, help='GPU utilization threshold to consider it occupied')
    parser.add_argument('--memory_threshold', type=int, default=-1, help='Memory usage threshold (in GB) to consider it occupied, set to -1 to disable')


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Sleep and check GPU status')
    add_args(parser)
    args = parser.parse_args()
    while True:
        try:
            sleep_main(args)
        except KeyboardInterrupt:
            print("\nKeyboardInterrupt received, exiting...")
            sys.exit(0)
        except Exception as e:
            print(f"\nUnexpected error: {e}")
            print("Restarting the program in 5 seconds...")
            time.sleep(5)
            continue
