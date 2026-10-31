from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.api.deps import get_db
from app.models.alert import SecurityAlert
from app.models.incident import Incident
from app.schemas.alert import AlertCreate, AlertResponse

router = APIRouter(prefix="/alerts", tags=["Alerts"])

@router.post("", response_model=AlertResponse)
def create_alert(alert_in: AlertCreate, db: Session = Depends(get_db)):
    # Create the alert record
    alert = SecurityAlert(
        source=alert_in.source,
        alert_type=alert_in.alert_type,
        severity=alert_in.severity,
        source_ip=alert_in.source_ip,
        destination_ip=alert_in.destination_ip,
        source_port=alert_in.source_port,
        destination_port=alert_in.destination_port,
        protocol=alert_in.protocol,
        signature=alert_in.signature,
        raw_payload=alert_in.raw_payload
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    
    # Auto-associate or create an active incident if there is an open one with matching source/dest/type
    existing_incident = db.query(Incident).filter(
        Incident.source_ip == alert.source_ip,
        Incident.destination_ip == alert.destination_ip,
        Incident.status.in_(["NEW", "ASSESSING", "EVALUATING", "PENDING_APPROVAL"])
    ).first()
    
    if existing_incident:
        alert.incident_id = existing_incident.id
        db.commit()
    else:
        # Create a new incident
        new_incident = Incident(
            title=f"{alert.alert_type.replace('_', ' ').title()} from {alert.source_ip}",
            threat_type=alert.alert_type,
            severity=alert.severity,
            status="NEW",
            source_ip=alert.source_ip,
            destination_ip=alert.destination_ip,
            protocol=alert.protocol,
            threat_confidence=0.75 if alert.source in ["SURICATA", "ZEEK"] else 0.60,
            uncertainty=0.20
        )
        db.add(new_incident)
        db.commit()
        db.refresh(new_incident)
        alert.incident_id = new_incident.id
        db.commit()
        
    db.refresh(alert)
    return alert

@router.get("", response_model=List[AlertResponse])
def get_alerts(
    limit: int = Query(50, ge=1, le=200),
    severity: Optional[str] = None,
    source: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(SecurityAlert)
    if severity:
        query = query.filter(SecurityAlert.severity == severity.upper())
    if source:
        query = query.filter(SecurityAlert.source == source.upper())
    return query.order_by(SecurityAlert.timestamp.desc()).limit(limit).all()

