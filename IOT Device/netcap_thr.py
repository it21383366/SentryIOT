from scapy.all import sniff, IP, TCP, UDP, ARP, LLC, IPv6
import pandas as pd
import os
import paramiko
from scp import SCPClient
from datetime import datetime

# Hardcoded network interface and destination machine details
NETWORK_INTERFACE = "ens33"  # Change this to the desired network interface
DESTINATION_HOST = '192.168.228.130'  # Replace with the destination machine IP address
DESTINATION_USERNAME = 'iotdevice'  # Replace with the destination machine username
DESTINATION_PASSWORD = '1qaz2wsx'  # Replace with the destination machine password or use a key
DESTINATION_PATH = '/home/iotdevice/Desktop/Server/backend/captured_data'  # Replace with the directory path on the remote machine

def create_ssh_client(host, port=22, username=None, password=None):
    """Create an SSH client for SCP transfer."""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, port, username, password)
    return client

def upload_file(file_path, destination_path):
    """Upload a file to the destination machine using SCP."""
    try:
        ssh_client = create_ssh_client(DESTINATION_HOST, username=DESTINATION_USERNAME, password=DESTINATION_PASSWORD)
        scp_client = SCPClient(ssh_client.get_transport())
        scp_client.put(file_path, destination_path)
        scp_client.close()
        ssh_client.close()
        print(f"File {file_path} uploaded successfully.")
    except Exception as e:
        print(f"Error uploading file: {e}")

def packet_handler(packet_list, file_count, first_timestamp):
    """Process packets and save them to a text file."""
    data = []
    for pkt in packet_list:
        # StartTime is the timestamp of the first packet in the capture
        start_time = datetime.utcfromtimestamp(pkt.time).strftime('%Y/%m/%d %H:%M:%S.%f') if hasattr(pkt, 'time') else 'NaN'
        
        # Calculate duration by subtracting the first packet's timestamp
        duration = pkt.time - first_timestamp if hasattr(pkt, 'time') else 'NaN'
        
        # Determine the protocol type
        if LLC in pkt:
            proto = "llc"
        elif IP in pkt:
            proto = "ipv4"
        elif IPv6 in pkt:
            proto = "ipv6"
        elif ARP in pkt:
            proto = "arp"
        elif UDP in pkt:
            proto = "udp"
        elif TCP in pkt:
            proto = "tcp"
        else:
            proto = "unknown"
        
        # Get source and destination IP addresses and ports
        src_addr = pkt[IP].src if IP in pkt else (pkt[IPv6].src if IPv6 in pkt else 'NaN')
        dst_addr = pkt[IP].dst if IP in pkt else (pkt[IPv6].dst if IPv6 in pkt else 'NaN')
        sport = pkt.sport if hasattr(pkt, 'sport') else 'NaN'
        dport = pkt.dport if hasattr(pkt, 'dport') else 'NaN'
        
        # Determine the direction of the traffic (simplified to a local network assumption)
        dir_traffic = "->" if src_addr != 'NaN' else "<-"
        
        # Extract Type of Service (ToS) fields from the IP header (if available)
        s_tos = pkt[IP].tos if IP in pkt else ('NaN' if IPv6 not in pkt else 'NaN')
        d_tos = pkt[IP].tos if IP in pkt else ('NaN' if IPv6 not in pkt else 'NaN')

        # Assume connection state is not available for most packets; placeholder (e.g., "MHR", "NNS")
        state = 'MHR' if proto == 'ipv6' else 'NaN'

        # Totals: Total packet length and source bytes
        tot_bytes = len(pkt) if pkt else 'NaN'
        src_bytes = len(pkt.payload) if pkt.payload else 'NaN'

        # Create the row with the required columns
        row = {
            'StartTime': start_time,
            'Dur': duration,
            'Proto': proto,
            'SrcAddr': src_addr,
            'Sport': sport,
            'Dir': dir_traffic,
            'DstAddr': dst_addr,
            'Dport': dport,
            'State': state,
            'sTos': s_tos,
            'dTos': d_tos,
            'TotPkts': 1,  # Always 1 for each packet
            'TotBytes': tot_bytes,
            'SrcBytes': src_bytes,
            'Label': 0  # This field can be set to 0 as a placeholder for labeling
        }
        data.append(row)
    
    df = pd.DataFrame(data)
    filename = f'networktrafic_{file_count}.txt'  # Changed to .txt format
    df.to_csv(filename, sep=',', index=False, header=True)  # Save as .txt using commas to separate values
    print(f"Saved: {filename}")

    # Upload file to destination machine
    upload_file(filename, DESTINATION_PATH)
    os.remove(filename)  # Optionally remove the file after uploading

def capture_traffic(interface):
    """Capture packets in chunks of 100 and save them on a specific interface."""
    file_count = 1
    while True:
        # Capture 100 packets
        packets = sniff(count=100, iface=interface, timeout=10)  # Added a timeout to avoid indefinite hanging
        if not packets:
            print("No packets captured, retrying...")
            continue  # If no packets are captured, skip to next iteration
        
        # Get the timestamp of the first packet in the capture
        first_timestamp = packets[0].time
        
        packet_handler(packets, file_count, first_timestamp)
        file_count += 1

if __name__ == "__main__":
    capture_traffic(NETWORK_INTERFACE)

