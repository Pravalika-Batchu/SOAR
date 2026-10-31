"""
Unknown / Out-of-Distribution Network Behavior Generator
Generates unexpected protocol patterns to evaluate Isolation Forest uncertainty and autonomy dampening.
"""
import ipaddress
from typing import Dict, Any

AUTHORIZED_NET = ipaddress.ip_network("10.0.0.0/24")

def generate_unknown_anomaly_payload(
    attacker_ip: str = "10.0.0.99",
    target_ip: str = "10.0.0.102"
) -> Dict[str, Any]:
    if ipaddress.ip_address(attacker_ip) not in AUTHORIZED_NET or ipaddress.ip_address(target_ip) not in AUTHORIZED_NET:
        raise ValueError(f"Security Safeguard: Target/source IP outside lab subnet {AUTHORIZED_NET}")

    return {
        "scenario": "UNKNOWN_ANOMALY",
        "attacker_ip": attacker_ip,
        "target_ip": target_ip,
        "protocol": "UDP",
        "packets_per_second": 880.0,
        "bytes_per_second": 980000.0,
        "connection_count": 40.0,
        "unique_destinations": 12.0,
        "failed_ratio": 0.50, # High ambiguity
        "volume_variation": 0.95,
        "signature": "Statistical Out-of-Distribution Packet Velocity Spike"
    }

def generate_normal_background_payload(
    client_ip: str = "10.0.0.101",
    server_ip: str = "10.0.0.10"
) -> Dict[str, Any]:
    return {
        "scenario": "NORMAL_BACKGROUND",
        "client_ip": client_ip,
        "server_ip": server_ip,
        "protocol": "TCP",
        "packets_per_second": 18.0,
        "bytes_per_second": 15000.0,
        "connection_count": 3.0,
        "unique_destinations": 1.0,
        "failed_ratio": 0.0,
        "volume_variation": 0.12,
        "signature": "HTTP 200 OK Nominal Traffic Flow"
    }

