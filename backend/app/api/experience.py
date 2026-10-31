from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.api.deps import get_db
from app.models.outcome import ExperienceRecord
from app.models.incident import Incident
from app.schemas.outcome import ExperienceRecordResponse

router = APIRouter(prefix="/experience", tags=["Experience Memory"])

@router.get("", response_model=List[ExperienceRecordResponse])
def get_experience_records(
    limit: int = Query(50, ge=1, le=200),
    threat_type: Optional[str] = None,
    action: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(ExperienceRecord)
    if threat_type:
        query = query.filter(ExperienceRecord.threat_type == threat_type)
    if action:
        query = query.filter(ExperienceRecord.selected_action == action)
    return query.order_by(ExperienceRecord.created_at.desc()).limit(limit).all()

@router.get("/similar/{incident_id}", response_model=List[ExperienceRecordResponse])
def get_similar_experience(incident_id: int, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
        
    # Match on same threat type or destination
    similar = db.query(ExperienceRecord).filter(
        ExperienceRecord.threat_type == incident.threat_type
    ).order_by(ExperienceRecord.created_at.desc()).limit(10).all()
    return similar

