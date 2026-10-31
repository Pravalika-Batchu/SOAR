from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.api.deps import get_db
from app.models.trust import TrustLog
from app.schemas.outcome import TrustScoreResponse

router = APIRouter(prefix="/trust", tags=["Trust"])

@router.get("/current", response_model=Optional[TrustScoreResponse])
def get_current_trust(db: Session = Depends(get_db)):
    return db.query(TrustLog).order_by(TrustLog.created_at.desc()).first()

@router.get("/history", response_model=List[TrustScoreResponse])
def get_trust_history(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    return db.query(TrustLog).order_by(TrustLog.created_at.desc()).limit(limit).all()

