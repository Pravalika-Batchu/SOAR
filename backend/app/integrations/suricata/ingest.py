import json
from dataclasses import dataclass
from typing import Dict, Any, Optional, List

@dataclass
class UnifiedSecurityEvent:
    source_tool: str # "SURICATA" or "ZEEK"
    event_type: str # "ALERT" or "FLOW"
    threat_category: str # "DOS", "PORT_SCAN", "BRUTE_FORCE", "ANOMALY"
    severity: str # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    source_ip: str
    destination_ip: str
    source_port: Optional[int]
    destination_port: Optional[int]
    protocol: str
    signature: Optional[str]
    raw_payload: Dict[str, Any]
    flow_features: Optional[Dict[str, float]] = None

def parse_suricata_eve_line(line: str) -> Optional[UnifiedSecurityEvent]:
    """
    Parses a single line of Suricata EVE JSON log into a UnifiedSecurityEvent.
    """
    line = line.strip()
    if not line:
        return None
    try:
        data = json.loads(line)
        if data.get("event_type") != "alert":
            return None

        alert_info = data.get("alert", {})
        sig = alert_info.get("signature", "Unknown Signature")
        category = alert_info.get("category", "")
        sev_num = alert_info.get("severity", 3)

        # Map Suricata severity number (1=high, 2=medium, 3=low) to standard string
        severity_map = {1: "CRITICAL", 2: "HIGH", 3: "MEDIUM", 4: "LOW"}
        severity = severity_map.get(sev_num, "MEDIUM")

        # Classify threat type from signature or category
        sig_lower = sig.lower()
        if "dos" in sig_lower or "flood" in sig_lower or "denial" in sig_lower:
            threat_type = "DOS_SYN_FLOOD"
            severity = "HIGH"
        elif "scan" in sig_lower or "sweep" in sig_lower or "nmap" in sig_lower:
            threat_type = "PORT_SCAN"
        elif "brute" in sig_lower or "login" in sig_lower or "attempt" in sig_lower:
            threat_type = "BRUTE_FORCE"
        else:
            threat_type = "UNKNOWN_ANOMALY"

        return UnifiedSecurityEvent(
            source_tool="SURICATA",
            event_type="ALERT",
            threat_category=threat_type,
            severity=severity,
            source_ip=data.get("src_ip", "0.0.0.0"),
            destination_ip=data.get("dest_ip", "0.0.0.0"),
            source_port=data.get("src_port"),
            destination_port=data.get("dest_port"),
            protocol=data.get("proto", "TCP").upper(),
            signature=sig,
            raw_payload=data
        )
    except Exception:
        return None

