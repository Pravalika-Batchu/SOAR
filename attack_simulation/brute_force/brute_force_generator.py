"""
Controlled Brute Force Simulation Generator
Generates repetitive authentication attempt flows against SSH/Database nodes.
"""
import ipaddress
from typing import Dict, Any

AUTHORIZED_NET = ipaddress.ip_network("10.0.0.0/24")

def generate_brute_force_payload(
    attacker_ip: str = "10.0.0.99",
    target_ip: str = "10.0.0.20",
    service_port: int = 22
) -> Dict[str, Any]:
    if ipaddress.ip_address(attacker_ip) not in AUTHORIZED_NET or ipaddress.ip_address(target_ip) not in AUTHORIZED_NET:
        raise ValueError(f"Security Safeguard: Target/source IP outside lab subnet {AUTHORIZED_NET}")

    return {
        "scenario": "BRUTE_FORCE",
        "attacker_ip": attacker_ip,
        "target_ip": target_ip,
        "target_port": service_port,
        "protocol": "TCP",
        "packets_per_second": 45.0,
        "bytes_per_second": 32000.0,
        "connection_count": 80.0,
        "unique_destinations": 1.0,
        "failed_ratio": 0.92,
        "volume_variation": 0.35,
        "signature": "ET SCAN Potential SSH Brute Force Authentication"
    }

