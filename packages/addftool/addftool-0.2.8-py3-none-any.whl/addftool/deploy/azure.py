from addftool.util import need_sudo, execute_command, get_ubuntu_version, install_packages


def deploy_azure(packages):
    ubuntu_version = get_ubuntu_version()
    print("Get ubuntu version: ", ubuntu_version)

    command = f"wget https://packages.microsoft.com/config/ubuntu/{ubuntu_version}/packages-microsoft-prod.deb -O /tmp/packages-microsoft-prod.deb"
    print("Install packages-microsoft-prod.deb")
    execute_command(command)
    command_prefix = "sudo " if need_sudo() else ""
    command = "dpkg -i /tmp/packages-microsoft-prod.deb"
    execute_command(command_prefix + command)
    execute_command(command_prefix + "apt-get update")

    install_packages(packages)


def add_deploy_azure_args(parser):
    """
    Add Azure deployment arguments to the parser.
    Args:
        parser (argparse.ArgumentParser): The argument parser to add the arguments to.
    """
    parser.add_argument("packages", help="packages", default=['fuse3', 'blobfuse2', 'azcopy'], nargs="*")

def deploy_azure_main(args):
    # print(args.packages)
    deploy_azure(args.packages)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Azure deployment arguments")
    add_deploy_azure_args(parser)

    args = parser.parse_args()

    deploy_azure_main(args)
