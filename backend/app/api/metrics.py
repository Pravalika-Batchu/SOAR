from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any, List
from app.api.deps import get_db
from app.models.incident import Incident
from app.models.alert import SecurityAlert
from app.models.response import HumanApproval, ResponseExecution
from app.models.metrics import NetworkMetricSample
from app.models.trust import TrustLog
from app.core.config import settings

router = APIRouter(prefix="/metrics", tags=["Metrics"])

@router.get("/summary")
def get_metrics_summary(db: Session = Depends(get_db)):
    total_alerts = db.query(SecurityAlert).count()
    active_incidents = db.query(Incident).filter(Incident.status.notin_(["RESOLVED", "CLOSED", "REJECTED"])).count()
    pending_approvals = db.query(HumanApproval).filter(HumanApproval.status == "PENDING").count()
    autonomous_executions = db.query(ResponseExecution).filter(ResponseExecution.execution_mode.in_(["ZERO_TOUCH", "GUARDED"])).count()
    
    # Autonomy distribution
    zero_touch_count = db.query(TrustLog).filter(TrustLog.autonomy_mode == "ZERO_TOUCH").count()
    guarded_count = db.query(TrustLog).filter(TrustLog.autonomy_mode == "GUARDED").count()
    approval_count = db.query(TrustLog).filter(TrustLog.autonomy_mode == "HUMAN_APPROVAL").count()
    
    # Latest telemetry sample
    latest_metric = db.query(NetworkMetricSample).order_by(NetworkMetricSample.timestamp.desc()).first()
    
    return {
        "system_status": "OPERATIONAL",
        "adapter_mode": settings.NETWORK_ADAPTER_MODE,
        "active_incidents": active_incidents,
        "total_alerts": total_alerts,
        "pending_approvals": pending_approvals,
        "autonomous_executions": autonomous_executions,
        "current_throughput_mbps": latest_metric.throughput_mbps if latest_metric else 94.2,
        "current_packet_loss_pct": latest_metric.packet_loss_pct if latest_metric else 0.1,
        "current_latency_ms": latest_metric.latency_ms if latest_metric else 1.25,
        "autonomy_distribution": {
            "ZERO_TOUCH": zero_touch_count,
            "GUARDED": guarded_count,
            "HUMAN_APPROVAL": approval_count
        }
    }

@router.get("/network")
def get_network_telemetry(db: Session = Depends(get_db)):
    samples = db.query(NetworkMetricSample).order_by(NetworkMetricSample.timestamp.desc()).limit(30).all()
    return samples

