import os
import subprocess


def execute_command(command, to_file=None, only_stdout=True, hide=False):
    if to_file is not None:
        to_file.write(command + "\n")
        return None
    else:
        if not hide:
            print("Execute command: ", command)
        result = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        result.wait()
        print(f"Return code: {result.returncode}")
        if result.stdout is not None:
            stdout = result.stdout.read().decode()
            print(f"Stdout: {stdout}")
        else:
            stdout = None
        if only_stdout:
            if not hide and stdout is not None:
                print(stdout)
            return stdout
        if result.stderr is not None:
            stderr = result.stderr.read().decode()
            print(f"Stderr: {stderr}")
        else:
            stderr = None

        return {'stdout': stdout, 'stderr': stderr, 'returncode': result.returncode}


def need_sudo():
    return os.name == 'posix' and os.getuid() != 0


def is_running_in_docker():
    return os.path.exists('/.dockerenv') or \
           any('docker' in line for line in open('/proc/self/cgroup', 'r')) if os.path.exists('/proc/self/cgroup') else False or \
           os.environ.get('container') == 'docker' or \
           os.environ.get('DOCKER') == 'true' or \
           os.environ.get('DOCKER_CONTAINER') == 'yes'


def get_ubuntu_version():  
    with open("/etc/os-release") as f:
        for line in f:
            if line.startswith("VERSION_ID="):
                version = line.split("=")[1].strip().strip('"')
                return version
    return "22.04"


def check_package_installed(package):
    command = f"dpkg -l | grep {package}"
    result = execute_command(command)
    if result is not None and package in result:
        return True
    return False


def install_packages(package_list):
    to_install = []
    for package in package_list:
        if check_package_installed(package):
            print(f"{package} is already installed")
            continue
        to_install.append(package)
    
    if len(to_install) > 0:
        packages = " ".join(to_install)
        command = f"apt-get install -y {packages}"
        if need_sudo():
            command = "sudo " + command
        execute_command(command)
