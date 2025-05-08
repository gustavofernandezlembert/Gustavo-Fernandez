#!/home/ubuntu/network-health-scripts/myenv/bin/python3

import paramiko
import datetime
import re
import logging
import yaml
import time
from typing import Tuple

# Set up logging
logging.basicConfig(filename='/var/log/network-monitoring/network_monitor.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_credentials(yaml_path: str) -> dict:
    with open(yaml_path, 'r') as file:
        return yaml.safe_load(file)

def create_ssh_client(server: str, port: int, user: str, password: str) -> paramiko.SSHClient:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(server, port=port, username=user, password=password)
    except paramiko.SSHException as e:
        logging.error(f"SSH connection failed: {str(e)}")
        print(f"SSH connection failed: {str(e)}")
        raise
    return client

def run_command_with_timeout(client: paramiko.SSHClient, command: str, timeout: int = 60) -> Tuple[str, str]:
    # Use exec_command to run the command in the background
    transport = client.get_transport()
    channel = transport.open_session()
    channel.exec_command(command)
    channel.settimeout(timeout)

    stdout = b""
    stderr = b""

    try:
        while not channel.exit_status_ready():
            time.sleep(0.1)  # Sleep for 100 milliseconds to reduce CPU usage
            if channel.recv_ready():
                stdout += channel.recv(1024)
            if channel.recv_stderr_ready():
                stderr += channel.recv_stderr(1024)
    except Exception as e:
        logging.error(f"Command execution failed: {str(e)}")
        print(f"Command execution failed: {str(e)}")
        return "", str(e)

    return stdout.decode(), stderr.decode()

def log_to_file(network_name: str, data: str) -> None:
    log_dir = '/var/log/network-monitoring'
    with open(f"{log_dir}/{network_name}_gw_speed.log", "a") as file:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file.write(f"{timestamp} - {data}\n")

def parse_speedtest_output(output: str) -> str:
    download_speed = re.search(r'Download:\s*([\d.]+)\s*Mbit/s', output)
    upload_speed = re.search(r'Upload:\s*([\d.]+)\s*Mbit/s', output)
    if download_speed and upload_speed:
        return f"Download speed: {download_speed.group(1)} Mbps, Upload speed: {upload_speed.group(1)} Mbps"
    return "Speedtest output not found"

def monitor_network(network_name: str, vpn_port: int, credentials: dict) -> None:
    try:
        print(f"Connecting to {network_name}...")
        gw_client = create_ssh_client('vpn.nexnet.global', vpn_port, 'pi', credentials['password'])
        try:
            print(f"Running speed test on {network_name}...")
            speedtest_output, speedtest_error = run_command_with_timeout(gw_client, 'speedtest')
            if speedtest_error:
                logging.error(f"Speedtest error for {network_name}: {speedtest_error}")
                print(f"Speedtest error for {network_name}: {speedtest_error}")
            else:
                logging.info(f"{network_name} speedtest output: {speedtest_output}")
                print(f"{network_name} speedtest output: {speedtest_output}")
                parsed_output = parse_speedtest_output(speedtest_output)
                log_to_file(network_name, parsed_output)
                print(f"Logged speed test results for {network_name}")
        finally:
            gw_client.close()
    except Exception as e:
        logging.error(f"Error monitoring {network_name}: {str(e)}")
        print(f"Error monitoring {network_name}: {str(e)}")

def main() -> None:
    credentials = load_credentials('/etc/networking/credentials.yaml')
    networks = {
       # "Kaye_SB101-1": {"vpn_port": 20054},
       # "Kaye_SB102-1": {"vpn_port": 20055},
       # "Chop_SB101-1": {"vpn_port": 20035},
       # "Chop_SB102-1": {"vpn_port": 20044},
       # "VanAken_SB101-1": {"vpn_port": 20032},
       # "Kaye_SB101-2": {"vpn_port": 20057},
        "OrchardBeach_SB101-1": {"vpn_port": 20051},
        "BullardHavens_simpleconfig": {"vpn_port": 20059},
        "Fenton_SB101-1": {"vpn_port": 20077},
         "PCCon_SB101-1": {"vpn_port": 20072},
    }
    for network_name, settings in networks.items():
        logging.info(f"Monitoring {network_name}...")
        print(f"Monitoring {network_name}...")
        monitor_network(network_name, settings['vpn_port'], credentials)

if __name__ == '__main__':
    main()
