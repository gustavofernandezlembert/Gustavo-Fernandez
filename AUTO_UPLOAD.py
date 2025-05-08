#!/home/ubuntu/networking/network-health-scripts/myenv/bin/python3

import pandas as pd
import numpy as np
import gspread
import yaml
from google.oauth2.service_account import Credentials
import os

def load_credentials(yaml_path: str) -> dict:
    with open(yaml_path, 'r') as file:
        return yaml.safe_load(file)

def clean_data(data):
    data = data.replace([np.inf, -np.inf], np.nan)
    data = data.fillna("N/A")
    return data

def upload_csv_to_sheets(csv_path, creds_path, sheet_key, worksheet_index):
    creds = Credentials.from_service_account_file(creds_path, scopes=["https://www.googleapis.com/auth/spreadsheets"])
    client = gspread.authorize(creds)
    sheet = client.open_by_key(sheet_key)
    worksheet = sheet.get_worksheet(worksheet_index)
    data = pd.read_csv(csv_path)
    print("Data read from CSV:")
    print(data.head())
    data = clean_data(data)
    worksheet.clear()
    worksheet.update([data.columns.values.tolist()] + data.values.tolist())

def main():
    credentials = load_credentials('/etc/networking/credentials.yaml')
    csv_file_path1 = '/var/data/network-monitoring/Mesh_Network_Data.csv'
    csv_file_path2 = '/var/data/network-monitoring/Gateway_Speeds.csv'
    csv_file_path3 = '/var/data/network-monitoring/consolidated_network_data.csv'
    credentials_path = '/home/ubuntu/networking/network-health-scripts/fluid-tuner-421013-11e48e146622.json'
    google_sheet_key = credentials['google_sheet_key']

    upload_csv_to_sheets(csv_file_path1, credentials_path, google_sheet_key, 0)
    print("Mesh Network Data CSV uploaded successfully.")

    upload_csv_to_sheets(csv_file_path2, credentials_path, google_sheet_key, 1)
    print("Gateway Speeds CSV uploaded successfully.")

    upload_csv_to_sheets(csv_file_path3, credentials_path, google_sheet_key, 2)
    print("Consolidated Network Data CSV uploaded successfully.")

if __name__ == "__main__":
    main()
