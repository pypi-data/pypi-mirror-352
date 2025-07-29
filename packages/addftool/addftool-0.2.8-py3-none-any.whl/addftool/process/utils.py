import psutil
import subprocess


def get_processes(command="", contains=False, pids=None, contain_arg=""):
    """获取进程的PID和命令"""
    
    processes = []
    for proc in psutil.process_iter(['pid', 'cmdline']):
        try:
            pid = proc.info['pid']
            cmdline = proc.info['cmdline']
            if cmdline is None or len(cmdline) == 0:
                continue
            if pids is not None and pid not in pids:
                continue
            if len(command) > 0:
                if contains and command not in cmdline[0]:
                    continue
                if not contains and command != cmdline[0]:
                    continue
            if len(cmdline) > 1 and cmdline[1].endswith('addf'):
                continue
            if len(contain_arg) > 0:
                if len(cmdline) <= 1:
                    continue
                flag = False
                for arg in cmdline[1:]:
                    if contain_arg in arg:
                        flag = True
                        break
                if not flag:
                    continue

            processes.append({'pid': pid, 'command': cmdline})
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
            
    return processes


def get_process_using_rocm():
    result = subprocess.run(['rocm-smi', '--showpidgpus'], capture_output=True, text=True)
    if result.returncode != 0:
        return False

    gpu_pids = []
    output_lines = result.stdout.strip().split('\n')
    for line in output_lines:
        if "PID" in line and ":" in line:
            # Extract PID from lines like "GPU[0-7]: PID: 12345"
            try:
                pid_part = line.split("PID:")[1].strip()
                pid = int(pid_part.split()[0])
                gpu_pids.append(pid)
            except (IndexError, ValueError):
                continue
    
    # Remove duplicates
    gpu_pids = list(set(gpu_pids))
    return get_processes(pids=gpu_pids)


def get_process_using_cuda():
    result = subprocess.run(['nvidia-smi', '--query-compute-apps=pid', '--format=csv,noheader'], capture_output=True, text=True)
    if result.returncode != 0:
        return False

    gpu_pids = []
    output_lines = result.stdout.strip().split('\n')
    for line in output_lines:
        try:
            pid = int(line.strip())
            gpu_pids.append(pid)
        except ValueError:
            continue
    
    # Remove duplicates
    gpu_pids = list(set(gpu_pids))

    # get process id and cmdline
    return get_processes(pids=gpu_pids)
