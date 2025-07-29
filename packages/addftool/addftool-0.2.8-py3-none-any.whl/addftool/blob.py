import argparse
import requests
import os
import json
import yaml
import tempfile
from cryptography.fernet import Fernet

from .util import execute_command


def add_api(parser):
    parser.add_argument("-k", "--key", help="f key", required=True)
    parser.add_argument("-a", "--api", help="api url")
    parser.add_argument("-n", "--name", help="name")
    parser.add_argument("-c", "--container", help="container")


def get_ubuntu_version():  
    with open("/etc/os-release") as f:
        for line in f:
            if line.startswith("VERSION_ID="):
                version = line.split("=")[1].strip().strip('"')
                return version
    return "22.04"


def create_dir_for_current_user(dir_path, sudo=False):
    command = f"mkdir -p {dir_path}"
    if sudo:
        command = "sudo " + command
    execute_command(command)
    username = os.environ.get("USER")
    if username is None or username == "":
        command = f"chown {os.getuid()} {dir_path}"
    else:
        command = f"chown $USER {dir_path}"
    if sudo:
        command = "sudo " + command
    execute_command(command)


def check_package_installed(package):
    command = f"dpkg -l | grep {package}"
    result = execute_command(command)
    if result is not None and package in result:
        return True
    return False


def install_main(args):

    to_install = []
    for package in args.packages.split():
        if check_package_installed(package):
            print(f"{package} is already installed")
            continue
        to_install.append(package)
    
    if len(to_install) == 0:
        print("All packages are already installed")
        return
    else:
        args.packages = " ".join(to_install)

    # generate install script
    # if args.output_script is not None:
    #     script_writer = open(args.output_script, "w")
    # else:
    script_writer = None
    
    # get ubuntu version
    ubuntu_version = get_ubuntu_version()

    # check if has root permission
    # if has root permission, run install script
    # else, print install script

    print("Get ubuntu version: ", ubuntu_version)
    command = f"wget https://packages.microsoft.com/config/ubuntu/{ubuntu_version}/packages-microsoft-prod.deb -O /tmp/packages-microsoft-prod.deb"
    print("Install packages-microsoft-prod.deb")
    execute_command(command, script_writer)
    command = "dpkg -i /tmp/packages-microsoft-prod.deb"
    if args.sudo:
        command = "sudo " + command
    execute_command(command, script_writer)

    command = "apt-get update"
    if args.sudo:
        command = "sudo " + command
    execute_command(command, script_writer)

    print("Install packages: ", args.packages)

    command = f"apt-get install {args.packages} -y"
    if args.sudo:
        command = "sudo " + command
    execute_command(command, script_writer)


def mount_main(args):
    sas_token = get_token(args, info=True)

    cache_gate = 0 if args.no_cache else 1
    template = {
        'logging': {'type': 'silent', 'level': 'log_off'}, 
        'components': ['libfuse', 'file_cache', 'attr_cache', 'azstorage'], 
        'libfuse': {'attribute-expiration-sec': 120 * cache_gate, 'entry-expiration-sec': 120 * cache_gate, 'negative-entry-expiration-sec': 240 * cache_gate}, 
        'file_cache': {'path': '', 'timeout-sec': 120 * cache_gate, 'max-size-mb': 1024 * int(args.file_cache_size)}, 
        'attr_cache': {'timeout-sec': 7200 * cache_gate}, 
        'azstorage': {
            'type': 'block', 
            'endpoint': '', 
            'account-name': '', 
            'mode': 'sas', 
            'sas': '', 
            'container': ''}, 
    }
    
    if args.template is not None:
        with open(args.template, 'r') as stream:
            try:
                template = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
    
    template['file_cache']['path'] = args.buffer

    template['azstorage']['sas'] = sas_token
    template['azstorage']['endpoint'] = "https://%s.blob.core.windows.net" % args.name
    template['azstorage']['account-name'] = args.name
    template['azstorage']['container'] = args.container

    create_dir_for_current_user(args.buffer, sudo=args.sudo)
    create_dir_for_current_user(args.mount, sudo=args.sudo)

    # write config file into tempfile

    temp_config_dir = tempfile.mktemp()
    print("Create temp config dir: ", temp_config_dir)
    os.makedirs(temp_config_dir, exist_ok=True)
    temp_config = os.path.join(temp_config_dir, "blobfuse2.yaml")
    with open(temp_config, 'w') as stream:
        yaml.dump(template, stream)
    
    print("Create config file: ", temp_config)

    command = f"blobfuse2 mount {args.mount} --config-file={temp_config}"
    if args.no_cache:
        command += " -o direct_io"
    if args.allow_other:
        command += " --allow-other"
        # to avoid "Error: fusermount3: option allow_other only allowed if 'user_allow_other' is set in /etc/fuse.conf"
        # check if 'user_allow_other' is set in /etc/fuse.conf
        exist_user_allow_other = False
        with open("/etc/fuse.conf") as f:
            for line in f:
                if line.startswith("user_allow_other"):
                    exist_user_allow_other = True
                    break
        if not exist_user_allow_other:
            print("Add user_allow_other to /etc/fuse.conf")
            pre_command = "echo 'user_allow_other' | "
            if args.sudo:
                pre_command = "sudo " + pre_command
            pre_command += "tee -a /etc/fuse.conf"
            execute_command(pre_command)

    execute_command(command)


def get_token(args, info=False):
    return get_sas_token(args.api, args.name, args.container, args.key, info=info)


# create a new function for function calling
def get_sas_token(api_url, name, container, key, info=False):
    f = Fernet(key.encode())

    an = f.encrypt(name.encode()).decode()
    cn = f.encrypt(container.encode()).decode()

    if info:
        print("Get token from: ", api_url)
        print("Name: ", an)
        print("Container: ", cn)

    params = {"an": an, "cn": cn}
    response = requests.get(api_url, params=params)
    if response.status_code == 200:
        data = json.loads(response.text)
        token = f.decrypt(data["sas"].encode()).decode()
        if token.startswith('"'):
            token = token[1:]
        if token.endswith('"'):
            token = token[:-1]
        if token.startswith("?"):
            return token
        else:
            return "?" + token
    else:
        return f"Error: {response.status_code}"


def parse_blob_account_and_container_from_url(blob_url):
    """
    Parse the blob URL to extract account name and container name.
    """
    if not blob_url.startswith("https://"):
        raise ValueError(f"Invalid blob URL: {blob_url}")

    parts = blob_url.split("/")
    account_name = parts[2].split(".")[0]
    container_name = parts[3].strip()

    return account_name, container_name


def get_sas_token_for_blob_url(api_url, blob_url, key, info=False):
    an, cn = parse_blob_account_and_container_from_url(blob_url)
    if info:
        print(f"Parse blob URL: {blob_url}, account name: {an}, container name: {cn}")
    return get_sas_token(api_url, an, cn, key, info=info)


def add_args(parser):
    subparsers = parser.add_subparsers(dest='blob_command', help='Sub-command help')
    install_parser = subparsers.add_parser('install', help='Install help')
    # install_parser.add_argument("-o", "--output_script", help="output script", default=None)
    install_parser.add_argument("--packages", help="packages", default="fuse3 blobfuse2 azcopy")
    install_parser.add_argument("--sudo", help="sudo", action="store_true")

    mount_parser = subparsers.add_parser('mount', help='Mount help')
    add_api(mount_parser)
    mount_parser.add_argument("-b", "--buffer", help="buffer dir", required=True)
    mount_parser.add_argument("-m", "--mount", help="mount dir", required=True)
    mount_parser.add_argument("-t", "--template", help="yaml template file", default=None)
    mount_parser.add_argument("-o", "--allow-other", help="allow other", action="store_true", default=False)
    mount_parser.add_argument("--file-cache-size", help="file cache size (GB)", default=256)
    mount_parser.add_argument("--sudo", help="sudo", action="store_true")
    mount_parser.add_argument("--no_cache", help="no cache", action="store_true")

    token_parser = subparsers.add_parser('token', help='Token help')
    add_api(token_parser)

def add_blob_args(subparsers):
    deploy_parser = subparsers.add_parser('blob', help='Blob help')
    add_args(deploy_parser)


def blob_main(args):
    # check os is linux/unix and current user, set --sudo if current user is not root
    if os.name == 'posix' and os.getuid() != 0:
        args.sudo = True

    if args.blob_command == 'install':
        install_main(args)
    elif args.blob_command == 'mount':
        mount_main(args)
    elif args.blob_command == 'token':
        print(get_token(args, info=False))


def main():
    # exmaple usage: addfblob install
    # exmaple usage: addfblob mount -k <key> -a <api> -b <buffer> -m <mount_dir>
    # exmaple usage: addfblob token -k <key> -a <api>
    parser = argparse.ArgumentParser(description="Addf's tool")
    add_args(parser)
    args = parser.parse_args()
    blob_main(args)


if __name__ == "__main__":
    main()
