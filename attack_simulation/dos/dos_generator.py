"""
Controlled DoS SYN Flood Simulation Generator
Generates high-rate TCP SYN flows within authorized academic subnet (10.0.0.0/24).
Includes strict IP safeguard to prevent execution outside lab testbed.
"""
import ipaddress
from typing import Dict, Any

AUTHORIZED_NET = ipaddress.ip_network("10.0.0.0/24")

def generate_dos_payload(
    attacker_ip: str = "10.0.0.99",
    target_ip: str = "10.0.0.10",
    target_port: int = 80,
    pps: float = 2500.0
) -> Dict[str, Any]:
    if ipaddress.ip_address(attacker_ip) not in AUTHORIZED_NET or ipaddress.ip_address(target_ip) not in AUTHORIZED_NET:
        raise ValueError(f"Security Safeguard: Target/source IP outside lab subnet {AUTHORIZED_NET}")

    return {
        "scenario": "DOS_SYN_FLOOD",
        "attacker_ip": attacker_ip,
        "target_ip": target_ip,
        "target_port": target_port,
        "protocol": "TCP",
        "flags": "SYN",
        "packets_per_second": pps,
        "bytes_per_second": pps * 740.0,
        "connection_count": 120.0,
        "unique_destinations": 1.0,
        "failed_ratio": 0.85,
        "volume_variation": 0.80,
        "signature": "ET DOS Potential SYN Flood on HTTP Web Server"
    }

if __name__ == "__main__":
    p = generate_dos_payload()
    print("Generated DoS Payload:", p)

