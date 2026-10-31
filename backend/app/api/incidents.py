from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.api.deps import get_db
from app.models.incident import Incident
from app.schemas.alert import IncidentResponse
from app.services.orchestrator import orchestrator_service

router = APIRouter(prefix="/incidents", tags=["Incidents"])

@router.get("", response_model=List[IncidentResponse])
def get_incidents(
    status: Optional[str] = None,
    threat_type: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    query = db.query(Incident)
    if status:
        query = query.filter(Incident.status == status.upper())
    if threat_type:
        query = query.filter(Incident.threat_type == threat_type)
    return query.order_by(Incident.created_at.desc()).limit(limit).all()

@router.get("/{incident_id}", response_model=IncidentResponse)
def get_incident_by_id(incident_id: int, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident

@router.post("/{incident_id}/analyze", response_model=IncidentResponse)
def analyze_incident(incident_id: int, db: Session = Depends(get_db)):
    try:
        updated = orchestrator_service.analyze_incident(incident_id, db)
        return updated
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
