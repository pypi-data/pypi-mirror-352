import argparse

from .ssh_server import add_deploy_ssh_server_args, deploy_ssh_server_main
from .azure import add_deploy_azure_args, deploy_azure_main
from .vscode_server import add_deploy_vscode_server_args, deploy_vscode_server_main


def add_deploy_args(subparsers: argparse._SubParsersAction):
    """
    Add deploy arguments to the parser.
    Args:
        subparsers (argparse._SubParsersAction): The subparsers object to add the arguments to.
    """
    deploy_parsers = subparsers.add_parser('deploy', help='deploy/install software, script, tools, etc.')
    deploy_subparsers = deploy_parsers.add_subparsers(dest='deploy_type', help='Deploy options')

    ssh_server_parser = deploy_subparsers.add_parser('ssh-server', help='SSH options')
    add_deploy_ssh_server_args(ssh_server_parser)

    azure_parser = deploy_subparsers.add_parser('azure', help='Azure options')
    add_deploy_azure_args(azure_parser)

    vscode_server_parser = deploy_subparsers.add_parser('vscode-server', help='VS Code options')
    add_deploy_vscode_server_args(vscode_server_parser)


def deploy_main(args):
    """
    Main function for deploy.
    Args:
        args (argparse.Namespace): The parsed arguments.
    """
    if args.deploy_type == 'ssh-server':
        deploy_ssh_server_main(args)
    elif args.deploy_type == 'azure':
        deploy_azure_main(args)
    elif args.deploy_type == 'vscode-server':
        deploy_vscode_server_main(args)
    else:
        print("Unknown deploy type")
        print("Deploy type: ", args.deploy_type)
