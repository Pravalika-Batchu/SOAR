from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.models.asset import Asset, NetworkTopologyNode
from app.core.config import settings

router = APIRouter(prefix="", tags=["System"])

@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "zero_cost_compliant": True,
        "adapter_mode": settings.NETWORK_ADAPTER_MODE
    }

@router.get("/system/status")
def system_status(db: Session = Depends(get_db)):
    asset_count = db.query(Asset).count()
    node_count = db.query(NetworkTopologyNode).count()
    return {
        "status": "ONLINE",
        "environment": "Local Zero-Cost Testbed",
        "database": "SQLite (zero-cost local storage)",
        "network_adapter": settings.NETWORK_ADAPTER_MODE,
        "monitored_assets": asset_count,
        "topology_nodes": node_count,
        "ryu_endpoint": settings.RYU_ENDPOINT
    }

@router.get("/system/topology")
def get_topology(db: Session = Depends(get_db)):
    nodes = db.query(NetworkTopologyNode).all()
    assets = db.query(Asset).all()
    return {
        "nodes": [
            {
                "id": n.node_id,
                "type": n.node_type,
                "ip": n.ip_address,
                "switch": n.connected_switch,
                "port": n.port_number,
                "status": n.status,
                "metadata": n.metadata_json
            }
            for n in nodes
        ],
        "assets": [
            {
                "ip": a.ip_address,
                "hostname": a.hostname,
                "criticality": a.criticality,
                "service": a.service_type,
                "isolated": a.is_isolated,
                "rate_limited": a.is_rate_limited,
                "qos_sensitivity": a.qos_sensitivity
            }
            for a in assets
        ]
    }

