import pandas as pd
import pickle
import numpy as np
import argparse
import paramiko
import os
import json
from collections import Counter
from datetime import datetime
from sklearn.preprocessing import LabelEncoder

# SSH Configuration for Remote Machine
REMOTE_HOST = "192.168.228.129"
REMOTE_USER = "iotdevice"
REMOTE_PASSWORD = "1qaz2wsx"
NETWORK_INTERFACE = "ens33"
SUDO_PASSWORD = "1qaz2wsx"

# Load the trained model
with open('xgboost_model.pkl', 'rb') as file:
    svc_clf = pickle.load(file)

# Load the scaler
with open('scaler.pkl', 'rb') as file:
    scaler = pickle.load(file)

def hex_to_int(value):
    """Convert hexadecimal port values to integers."""
    try:
        if isinstance(value, str) and value.startswith("0x"):
            return int(value, 16)
        return int(value)
    except ValueError:
        return np.nan

def disable_remote_network():
    """Connects to the remote machine via SSH and disables its network interface."""
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(REMOTE_HOST, username=REMOTE_USER, password=REMOTE_PASSWORD)

        command = f"echo '{SUDO_PASSWORD}' | sudo -S ifconfig {NETWORK_INTERFACE} down"

        stdin, stdout, stderr = ssh.exec_command(command)
        stdout_data = stdout.read().decode()
        stderr_data = stderr.read().decode()

        print(f"[SSH STDOUT]:\n{stdout_data}")
        print(f"[SSH STDERR]:\n{stderr_data}")

        if stderr_data:
            print("⚠️ Error shutting down network interface on remote device.")
        else:
            print("✅ Network interface shut down successfully.")

        ssh.close()
    except Exception as e:
        print(f"❌ SSH Error: {e}")

def log_result(file_name, label, count, total=100):
    """Logs prediction result to a JSONL file for dashboard access."""
    result = {
        "timestamp": datetime.now().isoformat(),
        "file": os.path.basename(file_name),
        "label": label,
        "count": int(count),
        "total": int(total)
    }
    log_path = os.path.join("backend", "detection_log.jsonl")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, "a") as f:
        f.write(json.dumps(result) + "\n")
    print(f"Logged result: {result}")

def process_data_batch(new_data, file_path, total=100):
    """Processes a batch of network traffic records and makes predictions."""
    new_data.dropna(how='all', inplace=True)

    new_data['Sport'] = new_data['Sport'].apply(hex_to_int)
    new_data['Dport'] = new_data['Dport'].apply(hex_to_int)

    label_encoder = LabelEncoder()
    new_data['Proto'] = label_encoder.fit_transform(new_data['Proto'].astype(str))

    numerical_columns = ['Dur', 'Sport', 'Dport', 'TotPkts', 'TotBytes', 'SrcBytes']
    new_data[numerical_columns] = new_data[numerical_columns].apply(pd.to_numeric, errors='coerce')
    new_data[numerical_columns] = new_data[numerical_columns].fillna(new_data[numerical_columns].mean())
    new_data[numerical_columns] = scaler.transform(new_data[numerical_columns])

    new_data['Bytes_per_Pkt'] = new_data['TotBytes'] / new_data['TotPkts'].replace(0, 1)
    new_data['Pkt_Rate'] = new_data['TotPkts'] / new_data['Dur'].replace(0, 1)
    new_data.dropna(inplace=True)

    if new_data.empty:
        print(f"⚠️ Skipping {file_path}: No valid rows after preprocessing.")
        return

    predictions = svc_clf.predict(new_data)
    class_counts = Counter(predictions)

    if not class_counts:
        print(f"⚠️ No predictions could be made from {file_path}. Skipping...")
        return

    most_frequent_class, frequency = class_counts.most_common(1)[0]

    print("Predictions:", predictions)
    print(f"Most Frequent Class: {most_frequent_class} (Predicted {frequency} times out of {total})")

    label = "WannaCry" if most_frequent_class == 1 else "Normal"
    log_result(file_path, label, frequency, total)

    # Set interface status
    if label == "WannaCry":
        print("🚨 WannaCry attack detected! Disabling remote network interface...")
        disable_remote_network()

def main():
    parser = argparse.ArgumentParser(description="Network Traffic Classifier")
    parser.add_argument("file_path", type=str, help="Path to the input dataset file")
    args = parser.parse_args()

    file_path = args.file_path
    batch_size = 100

    for chunk in pd.read_csv(file_path, delimiter=',', usecols=['Dur', 'Proto', 'Sport', 'Dport', 'TotPkts', 'TotBytes', 'SrcBytes'], chunksize=batch_size):
        process_data_batch(chunk, file_path, total=batch_size)

if __name__ == "__main__":
    main()

