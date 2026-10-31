import numpy as np
from dataclasses import dataclass
from typing import Dict, Any, List

FEATURE_NAMES = [
    "packets_per_second",
    "bytes_per_second",
    "connection_count",
    "unique_destination_count",
    "avg_packet_size_bytes",
    "mean_connection_duration_sec",
    "failed_connection_ratio",
    "traffic_volume_variation"
]

@dataclass
class FlowFeatureVector:
    packets_per_second: float
    bytes_per_second: float
    connection_count: float
    unique_destination_count: float
    avg_packet_size_bytes: float
    mean_connection_duration_sec: float
    failed_connection_ratio: float
    traffic_volume_variation: float

    def to_array(self) -> np.ndarray:
        return np.array([
            self.packets_per_second,
            self.bytes_per_second,
            self.connection_count,
            self.unique_destination_count,
            self.avg_packet_size_bytes,
            self.mean_connection_duration_sec,
            self.failed_connection_ratio,
            self.traffic_volume_variation
        ], dtype=np.float32).reshape(1, -1)

    def to_dict(self) -> Dict[str, float]:
        return {
            "packets_per_second": self.packets_per_second,
            "bytes_per_second": self.bytes_per_second,
            "connection_count": self.connection_count,
            "unique_destination_count": self.unique_destination_count,
            "avg_packet_size_bytes": self.avg_packet_size_bytes,
            "mean_connection_duration_sec": self.mean_connection_duration_sec,
            "failed_connection_ratio": self.failed_connection_ratio,
            "traffic_volume_variation": self.traffic_volume_variation
        }

def extract_features_from_raw_flow(raw: Dict[str, Any]) -> FlowFeatureVector:
    """
    Extracts numerical ML features from network raw flow or Zeek / Suricata metadata.
    """
    pps = float(raw.get("packets_per_second", raw.get("pps", 15.0)))
    bps = float(raw.get("bytes_per_second", raw.get("bps", 12500.0)))
    conns = float(raw.get("connection_count", raw.get("conns", 1.0)))
    dests = float(raw.get("unique_destinations", raw.get("dests", 1.0)))
    avg_pkt = float(raw.get("avg_packet_size", bps / max(1.0, pps)))
    duration = float(raw.get("duration", 2.5))
    failed_ratio = float(raw.get("failed_ratio", 0.0))
    vol_var = float(raw.get("volume_variation", 0.15))

    return FlowFeatureVector(
        packets_per_second=pps,
        bytes_per_second=bps,
        connection_count=conns,
        unique_destination_count=dests,
        avg_packet_size_bytes=avg_pkt,
        mean_connection_duration_sec=duration,
        failed_connection_ratio=failed_ratio,
        traffic_volume_variation=vol_var
    )

