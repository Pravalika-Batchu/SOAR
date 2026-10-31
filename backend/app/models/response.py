from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.session import Base

class CandidateResponse(Base):
    __tablename__ = "candidate_responses"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    action_type = Column(String(50), nullable=False) # BLOCK_IP, TEMP_BLOCK_IP, RATE_LIMIT, ISOLATE_HOST, TRAFFIC_RESTRICT
    target_ip = Column(String(45), nullable=False)
    parameters = Column(JSON, nullable=True) # e.g. {"duration_sec": 300, "rate_kbps": 500}
    
    # Reliability Engine Output
    reliability_score = Column(Float, default=0.0)
    threat_confidence_score = Column(Float, default=0.0)
    historical_success_score = Column(Float, default=0.0)
    policy_fit_score = Column(Float, default=0.0)
    qos_risk_score = Column(Float, default=0.0)
    resource_risk_score = Column(Float, default=0.0)
    uncertainty_score = Column(Float, default=0.0)
    score_breakdown = Column(JSON, nullable=True)
    explanation = Column(Text, nullable=True)

    # Policy Engine Output
    policy_status = Column(String(20), default="PENDING") # ALLOW, REJECT, RESTRICT, ESCALATE
    policy_reason = Column(Text, nullable=True)

    # Trust Engine Output
    trust_score = Column(Float, default=0.0)
    recommended_mode = Column(String(30), default="HUMAN_APPROVAL") # ZERO_TOUCH, GUARDED, HUMAN_APPROVAL

    created_at = Column(DateTime, default=datetime.utcnow)

    incident = relationship("Incident", back_populates="candidates")
    approvals = relationship("HumanApproval", back_populates="candidate", cascade="all, delete-orphan")

class HumanApproval(Base):
    __tablename__ = "human_approvals"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    candidate_response_id = Column(Integer, ForeignKey("candidate_responses.id"), nullable=False)
    status = Column(String(20), default="PENDING", index=True) # PENDING, APPROVED, REJECTED, TIMED_OUT
    action_type = Column(String(50), nullable=True)
    target_ip = Column(String(45), nullable=True)
    threat_type = Column(String(100), nullable=True)
    trust_score = Column(Float, default=0.0)
    reliability_score = Column(Float, default=0.0)
    policy_decision = Column(String(20), default="ESCALATE")
    escalation_reason = Column(Text, nullable=True)
    operator_username = Column(String(50), nullable=True)
    operator_comment = Column(Text, nullable=True)
    requested_at = Column(DateTime, default=datetime.utcnow)
    decided_at = Column(DateTime, nullable=True)

    incident = relationship("Incident", back_populates="approvals")
    candidate = relationship("CandidateResponse", back_populates="approvals")

class ResponseExecution(Base):
    __tablename__ = "response_executions"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    candidate_response_id = Column(Integer, ForeignKey("candidate_responses.id"), nullable=False)
    action_type = Column(String(50), nullable=False)
    target_ip = Column(String(45), nullable=False)
    execution_mode = Column(String(30), nullable=False) # ZERO_TOUCH, GUARDED, HUMAN_APPROVED
    adapter_used = Column(String(30), default="MOCK") # MOCK, RYU_SDN
    flow_rule_id = Column(String(100), nullable=True)
    status = Column(String(20), default="EXECUTING") # SUCCESS, FAILED, ROLLED_BACK
    execution_log = Column(Text, nullable=True)
    is_reverted = Column(Boolean, default=False)
    expires_at = Column(DateTime, nullable=True)
    executed_at = Column(DateTime, default=datetime.utcnow)
    reverted_at = Column(DateTime, nullable=True)

    incident = relationship("Incident", back_populates="executions")
