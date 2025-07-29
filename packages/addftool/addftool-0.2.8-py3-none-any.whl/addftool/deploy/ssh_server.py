import subprocess
import argparse
import os
from addftool.util import need_sudo, execute_command, is_running_in_docker


def convert_ssh2_to_openssh(ssh2_public_key_content):
    lines = ssh2_public_key_content.strip().split('\n')
    encoded_key = ""
    start_found = False
    for line in lines:
        line = line.strip()
        if line == "---- BEGIN SSH2 PUBLIC KEY ----":
            start_found = True
            continue
        elif line == "---- END SSH2 PUBLIC KEY ----":
            break
        elif start_found and line.startswith("Comment:"):
            comment = line.split(":", 1)[1].strip().strip('"')
        elif start_found:
            encoded_key += line

    if encoded_key:
        # Assuming it's an RSA key based on the comment
        openssh_key = f"ssh-rsa {encoded_key} \"{comment}\""
        return openssh_key
    else:
        return None


def parse_key_from_file(file_path):
    """
    解析 SSH 公钥文件，支持 SSH2 和 OpenSSH 格式
    :param file_path: 公钥文件路径
    :return: 公钥内容
    """
    with open(file_path, "r") as f:
        content = f.read()
        if "---- BEGIN SSH2 PUBLIC KEY ----" in content:
            return convert_ssh2_to_openssh(content)
        else:
            return content.strip()


def configure_ssh_on_ubuntu(port, username, ssh_public_key="", password=""):
    if not is_running_in_docker():
        print("This script is not running in a Docker container. Exiting...")
        return
    print(f"deploy ssh server on port: {port}, username: {username}, ssh_public_key: {ssh_public_key}, password: {password is not None}")
    if not(len(ssh_public_key) > 0 or len(password) > 0):
        print("ssh_public_key or password must be provided.")
        return 
    command_prefix = "sudo " if need_sudo() else ""
    try:
        need_install_ssh = True
        try:
            # execute_command(["which", "sshd"])
            response = execute_command("which sshd", only_stdout=False)
            if response["returncode"] == 0:
                print("SSH server is already installed.")
                need_install_ssh = False
        except subprocess.CalledProcessError:
            pass
        if need_install_ssh:
            print("SSH server is not installed. Installing...")
            execute_command(command_prefix + "apt-get update")
            execute_command(command_prefix + "apt-get install -y openssh-server")

        print("Modifying SSH configuration...")
        # if "#Port 22" in sshd_config
        execute_command(command_prefix + f'sed -i "s/#Port 22/Port {port}/" /etc/ssh/sshd_config')
        # if Port xxx in sshd_config
        execute_command(command_prefix + f'sed -i "s/Port [0-9]*/Port {port}/" /etc/ssh/sshd_config')
        execute_command(command_prefix + 'sed -i "s/#PermitRootLogin prohibit-password/PermitRootLogin yes/" /etc/ssh/sshd_config')

        if not os.path.exists("/etc/ssh/ssh_host_rsa_key"):
            print("SSH host keys not found. Generating new keys...")
            execute_command(command_prefix + 'ssh-keygen -t rsa -f /etc/ssh/ssh_host_rsa_key -N ""')

        print(f'Creating user {username} and configuring SSH key...')
        try:
            # run_command(["id", "-u", username])
            execute_command(command_prefix + f"id -u {username}")
        except subprocess.CalledProcessError:
            print(f"User {username} does not exist. Creating user...")
            execute_command(command_prefix + f"useradd -m -s /bin/bash {username}")

        ssh_dir = f"/home/{username}/.ssh" if username != "root" else "/root/.ssh"
        authorized_keys_file = f"{ssh_dir}/authorized_keys"


        execute_command(command_prefix + f"mkdir -p {ssh_dir}")
        execute_command(command_prefix + f"chmod 700 {ssh_dir}")

        if ssh_public_key:
            key_content = parse_key_from_file(ssh_public_key)
            execute_command(command_prefix + f"bash -c 'echo \"{key_content}\" >> {authorized_keys_file}'", hide=True)
        execute_command(command_prefix + f"chmod 600 {authorized_keys_file}")
        execute_command(command_prefix + f"chown -R {username}:{username} {ssh_dir}")

        if password:
            execute_command(command_prefix + f"echo '{username}:{password}' | chpasswd", hide=True)

        print("Restarting SSH service...")
        # run_command(["sudo", "systemctl", "restart", "ssh"])
        execute_command("/etc/init.d/ssh restart")

        print(f"ssh is configured! You can connect using the following command: ssh -p {port} {username}@<host_ip>")

    except subprocess.CalledProcessError as e:
        print(f"Command called process error: {e}")
    except FileNotFoundError as e:
        print(f"File not found error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

def add_deploy_ssh_server_args(parser):
    """添加 SSH 配置参数"""
    parser.add_argument("--port", type=int, required=True, help="SSH server port")
    parser.add_argument("--username", required=True, help="SSH username")
    parser.add_argument("--password", help="SSH password", type=str, default="")
    parser.add_argument("--ssh-public-key", help="SSH public key", type=str, default="")
    


def deploy_ssh_server_main(args):
    """
    部署 SSH 服务器
    :param args: 命令行参数
    """
    configure_ssh_on_ubuntu(args.port, args.username, args.ssh_public_key, args.password)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="在 Ubuntu 系统中配置 SSH")
    add_deploy_ssh_server_args(parser)

    args = parser.parse_args()

    deploy_ssh_server_main(args)
