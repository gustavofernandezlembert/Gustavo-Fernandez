#!/home/ubuntu/networking/network-health-scripts/myenv/bin/python3

import sys
print("Python executable:", sys.executable)
print("Python version:", sys.version)

import time
import paramiko
import socket
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import yaml
import os

def load_credentials(yaml_path: str) -> dict:
    with open(yaml_path, 'r') as file:
        return yaml.safe_load(file)

# Load SSH credentials from the YAML file
credentials = load_credentials('/etc/networking/credentials.yaml')
print("Loaded credentials:", credentials)  # Add this line for debugging
ssh_username = 'pi'
ssh_password = credentials['password']

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file(
    "/home/ubuntu/networking/network-health-scripts/fluid-tuner-421013-11e48e146622.json", scopes=scope)
client = gspread.authorize(creds)
sheet = client.open_by_key("1gWu3IcvLq6UUSnSvIWk1o5OZOEtNZPIFw2xyxoKbgzc").worksheet("ping")  # Use the specific worksheet name

# Add headers if the sheet is empty
if sheet.row_count == 1 and sheet.col_count == 1:
    sheet.append_row(["Time", "Network", "VPN Port", "IP", "Status"])

# List of networks with their respective VPN ports and IPs
networks = {
    "C2015": {"vpn_port": 20051, "intermediate_radio_ip": "10.223.184.29", "robot_radio_ip": "10.223.188.187", "node1_radio_ip": "10.223.204.46","node2_radio_ip": "10.223.204.46"},
   # "C2011": {"vpn_port": 20032, "intermediate_radio_ip": "10.223.184.41", "robot_radio_ip": "10.223.184.14", "node1_radio_ip": "10.223.146.97", "node2_radio_ip": "10.223.146.88"},
   # "C2012": {"vpn_port": 20054, "intermediate_radio_ip": "10.223.204.13", "robot_radio_ip": "10.223.16.142", "node1_radio_ip": "10.223.204.7", "node2_radio_ip": "10.223.204.10"},
   # "C2013": {"vpn_port": 20057, "intermediate_radio_ip": "10.223.184.26", "robot_radio_ip": "10.223.250.146", "node1_radio_ip": "10.223.204.4", "node2_radio_ip": "10.223.204.22"},
   # "C2009": {"vpn_port": 20057, "intermediate_radio_ip": "10.223.184.59", "robot_radio_ip": "10.223.203.147", "node1_radio_ip": "10.223.184.62", "node2_radio_ip": "10.223.204.49"},
    "C2003": {"vpn_port": 20044, "intermediate_radio_ip": "10.223.64.186", "robot_radio_ip": "10.223.224.95", "node1_radio_ip": "10.223.127.96", "node2_radio_ip": "10.223.64.195"},
            "C2006": {"vpn_port": 20035, "intermediate_radio_ip": "10.223.204.52", "robot_radio_ip": "10.223.183.252", "node1_radio_ip": "10.223.146.85", "node2_radio_ip": "10.223.146.106"},
            "R2003": {"vpn_port": 20059, "intermediate_radio_ip": "10.223.204.28", "robot_radio_ip": "10.223.183.253", "node1_radio_ip": "10.223.184.47", "node2_radio_ip": "10.223.204.37"},
             "C2017": {"vpn_port": 20072, "intermediate_radio_ip": "10.223.204.19", "robot_radio_ip": "10.223.184.2", "node1_radio_ip": "10.223.64.237", "node2_radio_ip": "10.223.122.248"},
            # "C2010": {"vpn_port": 20058, "intermediate_radio_ip": "10.223.146.79", "robot_radio_ip": "10.223.250.152", "node1_radio_ip": "10.223.204.25", "node2_radio_ip": "10.223.146.103"},
             "C2014": {"vpn_port": 20077, "intermediate_radio_ip": "10.223.204.43", "robot_radio_ip": "10.223.184.17", "node1_radio_ip": "10.223.68.27", "node2_radio_ip": "10.223.68.27"}
}


def ping_device(ip):
    """Ping device by opening a socket to port 80."""
    try:
        socket.setdefaulttimeout(1)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((ip, 80))
        return True
    except Exception as e:
        print(f"Ping device error: {e}")
        return False


import paramiko
import time

def ssh_and_ping(vpn_port, ip, retries=3):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    for attempt in range(retries):
        try:
            print(f"Attempt {attempt + 1}: Connecting to vpn.nexnet.global on port {vpn_port}...")
            ssh.connect('vpn.nexnet.global', port=vpn_port, username=ssh_username, password=ssh_password, timeout=20, banner_timeout=30)
            print(f"Connection established. Pinging {ip}...")
            stdin, stdout, stderr = ssh.exec_command(f"ping -c 1 -W 2 {ip}")
            exit_status = stdout.channel.recv_exit_status()
            ssh.close()

            if exit_status == 0:
                print(f"Ping successful: {ip}")
                return True
            else:
                print(f"Ping failed with exit status: {exit_status}")
        except Exception as e:
            print(f"SSH connection failed (attempt {attempt + 1}): {e}")
        time.sleep(2)  # Wait before retrying
    return False

def update_sheet():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rows = [["Time", "Network", "VPN Port", "IP", "Status"]]  # Add headers

    for network, details in networks.items():
        vpn_port = details["vpn_port"]
        intermediate_radio_ip = details["intermediate_radio_ip"]
        robot_radio_ip = details["robot_radio_ip"]
        node1_radio_ip = details["node1_radio_ip"]
        node2_radio_ip = details["node2_radio_ip"]

        print(f"Processing {network}...")
        intermediate_status = "on" if ssh_and_ping(vpn_port, intermediate_radio_ip) else "off"
        print(f"{network} - Intermediate Radio {intermediate_radio_ip} status: {intermediate_status}")
        robot_status = "on" if ssh_and_ping(vpn_port, robot_radio_ip) else "off"
        print(f"{network} - Robot Radio {robot_radio_ip} status: {robot_status}")
        node1_status = "on" if ssh_and_ping(vpn_port, node1_radio_ip) else "off"
        print(f"{network} - Node1 Radio {node1_radio_ip} status: {node1_status}")
        node2_status = "on" if ssh_and_ping(vpn_port, node2_radio_ip) else "off"
        print(f"{network} - Node2 Radio {node2_radio_ip} status: {node2_status}")

        rows.append([current_time, network, vpn_port, intermediate_radio_ip, intermediate_status])
        rows.append([current_time, network, vpn_port, robot_radio_ip, robot_status])
        rows.append([current_time, network, vpn_port, node1_radio_ip, node1_status])
        rows.append([current_time, network, vpn_port, node2_radio_ip, node2_status])

        print(f"Updated {network} - Intermediate Radio {intermediate_radio_ip} with status {intermediate_status}")
        print(f"Updated {network} - Robot Radio {robot_radio_ip} with status {robot_status}")
        print(f"Updated {network} - Node1 Radio {node1_radio_ip} with status {node1_status}")
        print(f"Updated {network} - Node2 Radio {node2_radio_ip} with status {node2_status}")

    # Clear the sheet and update with new data
    sheet.clear()
    sheet.append_rows(rows)

while True:
    update_sheet()
    time.sleep(60)  # Wait for 1 minute before next ping
