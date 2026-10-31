from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.session import Base

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    threat_type = Column(String(100), index=True, nullable=False) # DOS, PORT_SCAN, BRUTE_FORCE, UNKNOWN_ANOMALY
    severity = Column(String(20), default="MEDIUM") # LOW, MEDIUM, HIGH, CRITICAL
    status = Column(String(30), default="NEW", index=True) # NEW, ASSESSING, EVALUATING, PENDING_APPROVAL, EXECUTING, EVALUATED, RESOLVED
    
    source_ip = Column(String(45), index=True, nullable=False)
    destination_ip = Column(String(45), index=True, nullable=False)
    protocol = Column(String(20), default="TCP")
    
    # Threat & ML Assessment
    threat_confidence = Column(Float, default=0.5)
    anomaly_score = Column(Float, default=0.0) # From Isolation Forest
    is_anomaly = Column(Integer, default=0) # 1 if anomaly, 0 if normal
    uncertainty = Column(Float, default=0.2)
    assessment_notes = Column(Text, nullable=True)
    
    # Selected Decision & Autonomy
    selected_response_id = Column(Integer, nullable=True)
    autonomy_trust_score = Column(Float, nullable=True)
    execution_mode = Column(String(30), nullable=True) # ZERO_TOUCH, GUARDED, HUMAN_APPROVAL
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    alerts = relationship("SecurityAlert", back_populates="incident")
    candidates = relationship("CandidateResponse", back_populates="incident", cascade="all, delete-orphan")
    approvals = relationship("HumanApproval", back_populates="incident", cascade="all, delete-orphan")
    executions = relationship("ResponseExecution", back_populates="incident", cascade="all, delete-orphan")
    outcomes = relationship("OutcomeEvaluation", back_populates="incident", cascade="all, delete-orphan")

