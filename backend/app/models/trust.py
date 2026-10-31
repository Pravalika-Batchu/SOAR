from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey, Text
from datetime import datetime
from app.database.session import Base

class TrustLog(Base):
    __tablename__ = "trust_logs"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    candidate_id = Column(Integer, ForeignKey("candidate_responses.id"), nullable=True)
    trust_score = Column(Float, nullable=False)
    autonomy_mode = Column(String(30), nullable=False) # ZERO_TOUCH, GUARDED, HUMAN_APPROVAL
    reliability_contribution = Column(Float, default=0.0)
    threat_confidence_contribution = Column(Float, default=0.0)
    qos_safety_contribution = Column(Float, default=0.0)
    uncertainty_penalty = Column(Float, default=0.0)
    historical_failure_penalty = Column(Float, default=0.0)
    rationale = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

