from addftool.util import need_sudo, execute_command, install_packages


def deploy_vscode_server(install_tunnel=True):
    """
    Deploy Visual Studio Code and optionally start VS Code Tunnel.
    
    Args:
        install_tunnel (bool): Whether to start VS Code Tunnel after installation
    """
    command_prefix = "sudo " if need_sudo() else ""
    
    # Install prerequisites
    print("Installing prerequisites...")
    execute_command(command_prefix + "apt-get install -y wget gpg")
    
    # Add Microsoft's GPG key
    print("Adding Microsoft's GPG key...")
    execute_command("wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg")
    execute_command(command_prefix + "install -D -o root -g root -m 644 packages.microsoft.gpg /etc/apt/keyrings/packages.microsoft.gpg")
    
    # Add VS Code repository
    print("Adding VS Code repository...")
    execute_command(command_prefix + "sh -c 'echo \"deb [arch=amd64,arm64,armhf signed-by=/etc/apt/keyrings/packages.microsoft.gpg] "
                   "https://packages.microsoft.com/repos/code stable main\" > /etc/apt/sources.list.d/vscode.list'")
    
    # Clean up
    execute_command("rm -f packages.microsoft.gpg")
    
    # Install VS Code
    print("Installing VS Code...")
    execute_command(command_prefix + "apt install -y apt-transport-https")
    execute_command(command_prefix + "apt update")
    execute_command(command_prefix + "apt install -y code")
    
    # Start VS Code Tunnel if requested
    if install_tunnel:
        print("Starting VS Code Tunnel...")
    
    print("VS Code installation completed successfully!")
    print("You can start VS Code by running 'code' in the terminal., such as: \"code tunnel --accept-server-license-terms\"")


def add_deploy_vscode_server_args(parser):
    """
    Add VS Code deployment arguments to the parser.
    
    Args:
        parser (argparse.ArgumentParser): The argument parser to add the arguments to.
    """
    parser.add_argument("--no-tunnel", dest="install_tunnel", action="store_false", 
                        help="Skip starting VS Code Tunnel after installation")
    parser.set_defaults(install_tunnel=True)


def deploy_vscode_server_main(args):
    """
    Main function for VS Code deployment.
    
    Args:
        args: Parsed command-line arguments
    """
    deploy_vscode_server(install_tunnel=args.install_tunnel)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="VS Code deployment arguments")
    add_deploy_vscode_server_args(parser)

    args = parser.parse_args()

    deploy_vscode_server_main(args)
