import json
from typing import Dict, Any, Optional
from app.integrations.suricata.ingest import UnifiedSecurityEvent

def parse_zeek_conn_log_line(line: str) -> Optional[UnifiedSecurityEvent]:
    """
    Parses a Zeek conn.log JSON record into a UnifiedSecurityEvent.
    Calculates behavioral metrics: duration, bytes transferred, connection states.
    """
    line = line.strip()
    if not line or line.startswith("#"):
        return None
    try:
        data = json.loads(line)
        orig_h = data.get("id.orig_h") or data.get("src_ip", "0.0.0.0")
        resp_h = data.get("id.resp_h") or data.get("dest_ip", "0.0.0.0")
        orig_p = data.get("id.orig_p") or data.get("src_port")
        resp_p = data.get("id.resp_p") or data.get("dest_port")
        proto = data.get("proto", "tcp").upper()
        
        orig_bytes = float(data.get("orig_bytes") or 0.0)
        resp_bytes = float(data.get("resp_bytes") or 0.0)
        orig_pkts = float(data.get("orig_pkts") or 1.0)
        duration = float(data.get("duration") or 0.1)
        conn_state = data.get("conn_state", "S0") # S0 = SYN with no ACK, REJ = rejected

        pps = orig_pkts / max(0.01, duration)
        bps = (orig_bytes + resp_bytes) / max(0.01, duration)
        failed = 1.0 if conn_state in ["S0", "REJ", "RSTO", "RSTR"] else 0.0

        # Threat classification from network telemetry
        if pps > 1000.0 or (conn_state == "S0" and orig_pkts > 50):
            threat = "DOS_SYN_FLOOD"
            sev = "HIGH"
        elif failed == 1.0 and pps > 20:
            threat = "PORT_SCAN"
            sev = "MEDIUM"
        else:
            threat = "ANOMALOUS_CONN"
            sev = "LOW"

        flow_features = {
            "packets_per_second": pps,
            "bytes_per_second": bps,
            "duration": duration,
            "failed_ratio": failed
        }

        return UnifiedSecurityEvent(
            source_tool="ZEEK",
            event_type="FLOW",
            threat_category=threat,
            severity=sev,
            source_ip=orig_h,
            destination_ip=resp_h,
            source_port=int(orig_p) if orig_p else None,
            destination_port=int(resp_p) if resp_p else None,
            protocol=proto,
            signature=f"Zeek conn.log {conn_state} State",
            raw_payload=data,
            flow_features=flow_features
        )
    except Exception:
        return None

