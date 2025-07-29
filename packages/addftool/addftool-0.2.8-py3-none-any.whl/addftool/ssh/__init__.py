import re
import os
from pssh.clients import ParallelSSHClient
from pssh.config import HostConfig
import gevent


def get_host_config(hostname, configs):
    """Get configuration for a specific host from all configs."""
    host_config = {}
    
    # Check for exact hostname match
    if hostname in configs:
        host_config.update(configs[hostname])
    
    # Check for wildcard matches
    for pattern, config in configs.items():
        if '*' in pattern or '?' in pattern:
            # Convert SSH glob pattern to regex pattern
            regex_pattern = pattern.replace('.', '\\.').replace('*', '.*').replace('?', '.')
            if re.match(f"^{regex_pattern}$", hostname):
                host_config.update(config)
    
    return host_config


def parse_ssh_config_file(file_path):
    """Parse SSH config file into a dictionary of host configurations."""
    host_configs = {}
    current_host = None
    
    if not os.path.exists(file_path):
        return host_configs

    try:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                    
                if line.lower().startswith('host ') and not line.lower().startswith('host *'):
                    hosts = line.split()[1:]
                    for host in hosts:
                        current_host = host
                        if current_host not in host_configs:
                            host_configs[current_host] = {}
                elif current_host and ' ' in line:
                    key, value = line.split(None, 1)
                    host_configs[current_host][key.lower()] = value
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    
    return host_configs


def get_ssh_config():
    user_config_path = os.path.expanduser("~/.ssh/config")
    system_config_path = "/etc/ssh/ssh_config"
    
    user_configs = parse_ssh_config_file(user_config_path)
    system_configs = parse_ssh_config_file(system_config_path)
    return user_configs, system_configs


def get_client(hosts, user_ssh_configs=None, system_ssh_configs=None):
    if user_ssh_configs is None or system_ssh_configs is None:
        user_ssh_configs, system_ssh_configs = get_ssh_config()

    to_connect = []
    for hostname in hosts:
        host_ssh_config = get_host_config(hostname, user_ssh_configs)
        if not host_ssh_config:
            host_ssh_config = get_host_config(hostname, system_ssh_configs)
        
        if host_ssh_config:
            host_config = HostConfig(
                user=host_ssh_config.get('user', os.getenv('USER', 'root')),
                port=int(host_ssh_config.get('port', 22)),
                private_key=host_ssh_config.get('identityfile', None),
            )
            host_name = host_ssh_config.get('hostname', hostname)
            to_connect.append((host_name, host_config))
        else:
            print(f"No config found for host {hostname}")

    # Create a ParallelSSHClient with the list of hosts
    client = ParallelSSHClient([host[0] for host in to_connect], host_config=[host[1] for host in to_connect])
    return client


def handle_stream(host, stream_in, stream_name, print_call=None):
    if print_call is None:
        print_call = print
    try:
        if stream_in:
            for line in stream_in:
                prefix = " ERROR" if stream_name == "stderr" else ""
                print_call(f"[{host}]{prefix}: {line}")
                gevent.sleep(0)  # 让出控制权
    except Exception as e:
        print(f"[{host}] {stream_name} Exception: {e}")


def _stdout_log(line):
    """Log the output line."""
    print(line)


def _stderr_log(line):
    """Log the error line."""
    print("ERROR: " + line)


def handle_hosts_outputs(hosts_outputs, out_log=None, err_log=None):
    """Handle the outputs from the SSH command execution."""
    if out_log is None:
        out_log = _stdout_log
    if err_log is None:
        err_log = _stderr_log
    jobs = []
    for output in hosts_outputs:
        host_name = output.host
        if output:
            jobs.append(gevent.spawn(handle_stream, host_name, output.stdout, "stdout", out_log))
            jobs.append(gevent.spawn(handle_stream, host_name, output.stderr, "stderr", err_log))

    gevent.joinall(jobs, raise_error=False)
