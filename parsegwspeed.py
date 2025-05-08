#!/home/ubuntu/networking/network-health-scripts/myenv/bin/python3

import os
import re
import pandas as pd

def parse_file(file_path):
    filename = os.path.basename(file_path)
    project_name, network_name = filename.split('_')[0], filename.split('_')[1]
    with open(file_path, 'r') as file:
        data = file.readlines()

    parsed_data = []
    for line in data:
        print(f"Processing line: {line.strip()}")  # Debug print
        match = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) - Download speed: ([\d\.]+) Mbps, Upload speed: ([\d\.]+) Mbps', line)
        if match:
            timestamp = match.group(1)
            download_speed = match.group(2)
            upload_speed = match.group(3)
            parsed_data.append([timestamp, project_name, network_name, download_speed, upload_speed])

    print(f"Parsed data for {file_path}: {parsed_data}")  # Debug print
    return parsed_data

def consolidate_data(file_paths):
    all_data = []
    for file_path in file_paths:
        file_data = parse_file(file_path)
        all_data.extend(file_data)

    df = pd.DataFrame(all_data, columns=['Timestamp','Project', 'Network', 'Download speed (Mbps)', 'Upload speed (Mbps)'])
    print(f"Consolidated DataFrame:\n{df}")  # Debug print
    return df

def save_to_csv(dataframe, output_filename):
    dataframe.to_csv(output_filename, index=False)

def main():
    # List of uploaded file paths
    file_paths = [
       # '/var/log/network-monitoring/Kaye_SB101-1_gw_speed.log',
       # '/var/log/network-monitoring/Kaye_SB101-2_gw_speed.log',
       # '/var/log/network-monitoring/Kaye_SB102-1_gw_speed.log',
       # '/var/log/network-monitoring/VanAken_SB101-1_gw_speed.log',
       # '/var/log/network-monitoring/VanAken_SB102-1_gw_speed.log',
        '/var/log/network-monitoring/Chop_SB101-1_gw_speed.log',
        '/var/log/network-monitoring/Chop_SB102-1_gw_speed.log',
        '/var/log/network-monitoring/BullardHavens_simpleconfig_gw_speed.log',
         '/var/log/network-monitoring/OrchardBeach_SB101-1_gw_speed.log',
         '/var/log/network-monitoring/Fenton_SB101-1_gw_speed.log',
         '/var/log/network-monitoring/PCCon_SB101-1_gw_speed.log',
    ]

    # Consolidate the data
    consolidated_data = consolidate_data(file_paths)

    # Save to CSV
    output_filename = '/var/data/network-monitoring/Gateway_Speeds.csv'
    save_to_csv(consolidated_data, output_filename)

    print(f"Consolidated data saved to {output_filename}")

if __name__ == '__main__':
    main()
