"""
Controlled Port Scan Simulation Generator
Generates multi-destination / multi-port TCP SYN/FIN sweeps inside 10.0.0.0/24.
"""
import ipaddress
from typing import Dict, Any

AUTHORIZED_NET = ipaddress.ip_network("10.0.0.0/24")

def generate_port_scan_payload(
    attacker_ip: str = "10.0.0.99",
    target_ip: str = "10.0.0.101",
    scanned_ports_count: int = 250
) -> Dict[str, Any]:
    if ipaddress.ip_address(attacker_ip) not in AUTHORIZED_NET or ipaddress.ip_address(target_ip) not in AUTHORIZED_NET:
        raise ValueError(f"Security Safeguard: Target/source IP outside lab subnet {AUTHORIZED_NET}")

    return {
        "scenario": "PORT_SCAN",
        "attacker_ip": attacker_ip,
        "target_ip": target_ip,
        "scanned_ports_count": scanned_ports_count,
        "protocol": "TCP",
        "packets_per_second": 350.0,
        "bytes_per_second": 24500.0,
        "connection_count": float(scanned_ports_count),
        "unique_destinations": 35.0,
        "failed_ratio": 0.95,
        "volume_variation": 0.60,
        "signature": "Zeek Port Sweep Detection (SYN scan 100+ ports)"
    }

