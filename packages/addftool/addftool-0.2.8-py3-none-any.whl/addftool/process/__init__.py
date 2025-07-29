import psutil
import time

from .utils import get_processes, get_process_using_rocm, get_process_using_cuda


def add_killer_args(subparsers):
    process_killer_parser = subparsers.add_parser('kill', help='process kill')

    process_killer_parser.add_argument("-c", "--contains", help="contains of command", action='store_true', default=False)
    process_killer_parser.add_argument("--timeout", help="timeout of command", default=5, type=int)
    process_killer_parser.add_argument("--try_count", help="try count of command", default=3, type=int)

    process_killer_parser.add_argument("--contain_arg", help="args of command", default="", type=str)

    process_killer_parser.add_argument("--rocm", help="kill process using rocm", action='store_true', default=False)
    process_killer_parser.add_argument("--cuda", help="kill process using cuda", action='store_true', default=False)

    process_killer_parser.add_argument("-v", "--view", help="view process", action='store_true', default=False)

    process_killer_parser.add_argument("name", nargs='?', help="name of process", type=str, default="")


def kill_process(processes, timeout=5, try_count=3):
    for process in processes:
        try:
            proc = psutil.Process(process['pid'])
            print(f"Killing process {proc.pid} - {proc.cmdline()}")
            proc.terminate()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            print(f"Process {process['pid']} not found or access denied")
            continue
    
    time.sleep(timeout)
    for _ in range(try_count):
        all_terminated = True
        for process in processes:
            try:
                proc = psutil.Process(process['pid'])
                print("Process still running: ", proc.pid)
                proc.kill()
                all_terminated = False
            except (psutil.NoSuchProcess):
                continue
            except (psutil.AccessDenied):
                print(f"Process {process['pid']} access denied")
                continue
            except (psutil.ZombieProcess):
                print(f"Process {process['pid']} is a zombie process")
                continue
            except Exception as e:
                print(f"Error killing process {process['pid']}: {e}")
                continue
        if all_terminated:
            print("All processes terminated")
            break
        time.sleep(timeout)
    
    if not all_terminated:
        print("Some processes are still running. Please check manually.")
        exit(1)


def find_and_kill_process(command="", contains=False, contain_arg="", use_rocm=False, use_cuda=False, timeout=5, try_count=3, only_view=False):
    do_not_do_anything = command is None or len(command) == 0
    if use_rocm:
        processes = get_process_using_rocm()
    elif use_cuda:
        processes = get_process_using_cuda()
    elif do_not_do_anything and not only_view:
        print("Use top or htop to find the process you want to kill")
        return
    else:
        processes = get_processes(command=command, contains=contains, contain_arg=contain_arg)
    
    if only_view:
        print(f"Found {len(processes)} processes")
        for process in processes:
            print(f"PID: {process['pid']}, Command: {' '.join(process['command'])}")
        return

    if len(processes) > 0:
        print(f"Found {len(processes)} processes to kill")
        kill_process(processes, timeout, try_count)


def killer_main(args):
    print(args)
    find_and_kill_process(
        args.name, args.contains, args.contain_arg, use_rocm=args.rocm, use_cuda=args.cuda, 
        timeout=args.timeout, try_count=args.try_count, only_view=args.view,
    )
