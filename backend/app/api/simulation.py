# backend/app/api/simulation.py
"""
Simulation Control API
Endpoints to control the network simulation engine and retrieve telemetry.
All data generated is clearly labeled as SIMULATION MODE.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from app.api.deps import get_db
from app.models.metrics import NetworkMetricSample
from app.services.network_simulator import network_simulator

router = APIRouter(prefix="/simulation", tags=["Simulation"])

VALID_ATTACK_TYPES = [
    "DOS_SYN_FLOOD",
    "PORT_SCAN",
    "BRUTE_FORCE",
    "UNKNOWN_ANOMALY",
    "DNS_AMPLIFICATION_FLOOD",
]


@router.get("/status")
def get_simulation_status():
    """Returns current simulation engine state and last telemetry sample."""
    return network_simulator.get_status()


@router.post("/start")
def start_simulation():
    """Starts the background network simulation engine."""
    if network_simulator.is_running:
        return {"message": "Simulation already running.", "status": "RUNNING"}
    network_simulator.start()
    return {"message": "Simulation engine started.", "status": "RUNNING", "note": "SIMULATION MODE - synthetic traffic only"}


@router.post("/stop")
def stop_simulation():
    """Stops the background network simulation engine."""
    if not network_simulator.is_running:
        return {"message": "Simulation not running.", "status": "STOPPED"}
    network_simulator.stop()
    return {"message": "Simulation engine stopped.", "status": "STOPPED"}


@router.post("/trigger/{attack_type}")
def trigger_attack(
    attack_type: str,
    target_ip: Optional[str] = None,
    source_ip: Optional[str] = None,
    duration_cycles: int = 2
):
    """
    Manually trigger an attack scenario.
    
    - **attack_type**: DOS_SYN_FLOOD | PORT_SCAN | BRUTE_FORCE | UNKNOWN_ANOMALY | DNS_AMPLIFICATION_FLOOD
    - **target_ip**: Optional target IP (defaults to preferred target for attack type)
    - **source_ip**: Optional attacker IP (defaults to random)
    - **duration_cycles**: How many 5-second simulation cycles to run the attack (default 2 = ~10s)
    """
    attack_type = attack_type.upper()
    if attack_type not in VALID_ATTACK_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid attack_type '{attack_type}'. Valid: {VALID_ATTACK_TYPES}"
        )

    # Start simulator if not already running
    if not network_simulator.is_running:
        network_simulator.start()

    result = network_simulator.trigger_attack(
        attack_type=attack_type,
        target_ip=target_ip,
        source_ip=source_ip,
        duration_cycles=duration_cycles
    )
    return result


@router.get("/telemetry")
def get_recent_telemetry(limit: int = 30, db: Session = Depends(get_db)):
    """Returns recent network telemetry samples (time series for charts)."""
    samples = db.query(NetworkMetricSample).order_by(
        NetworkMetricSample.timestamp.desc()
    ).limit(limit).all()
    
    return [
        {
            "id": s.id,
            "timestamp": s.timestamp.isoformat() if s.timestamp else None,
            "switch_id": s.switch_id,
            "host_ip": s.host_ip,
            "throughput_mbps": s.throughput_mbps,
            "packet_loss_pct": s.packet_loss_pct,
            "latency_ms": s.latency_ms,
            "jitter_ms": s.jitter_ms,
            "packets_per_sec": s.packets_per_sec,
            "bytes_per_sec": s.bytes_per_sec,
            "active_flows": s.active_flows,
            "drop_count": s.drop_count,
        }
        for s in reversed(samples)  # Return in chronological order
    ]


@router.get("/attack-types")
def get_attack_types():
    """Returns available attack scenario types for the frontend."""
    return {
        "attack_types": [
            {"id": "DOS_SYN_FLOOD", "label": "DoS SYN Flood", "severity": "HIGH", "target": "Web Server (10.0.0.10)"},
            {"id": "PORT_SCAN", "label": "Port Scan", "severity": "MEDIUM", "target": "Internal Desktop (10.0.0.101)"},
            {"id": "BRUTE_FORCE", "label": "Brute Force SSH", "severity": "HIGH", "target": "Database (10.0.0.20)"},
            {"id": "UNKNOWN_ANOMALY", "label": "Unknown Anomaly", "severity": "MEDIUM", "target": "Client (10.0.0.102)"},
            {"id": "DNS_AMPLIFICATION_FLOOD", "label": "DNS Flood (QoS-Sensitive)", "severity": "HIGH", "target": "DNS Server (10.0.0.53)"},
        ],
        "note": "SIMULATION MODE - triggers synthetic attack telemetry and alert generation"
    }

