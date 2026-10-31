from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.api.deps import get_db
from app.models.outcome import OutcomeEvaluation
from app.schemas.outcome import OutcomeEvaluationResponse

router = APIRouter(prefix="/outcomes", tags=["Outcomes"])

@router.get("", response_model=List[OutcomeEvaluationResponse])
def get_outcomes(
    limit: int = Query(50, ge=1, le=200),
    success_status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(OutcomeEvaluation)
    if success_status:
        query = query.filter(OutcomeEvaluation.success_status == success_status.upper())
    return query.order_by(OutcomeEvaluation.evaluated_at.desc()).limit(limit).all()

@router.get("/{incident_id}", response_model=List[OutcomeEvaluationResponse])
def get_outcomes_for_incident(incident_id: int, db: Session = Depends(get_db)):
    return db.query(OutcomeEvaluation).filter(OutcomeEvaluation.incident_id == incident_id).all()

