from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.session import Base

class OutcomeEvaluation(Base):
    __tablename__ = "outcome_evaluations"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    candidate_response_id = Column(Integer, ForeignKey("candidate_responses.id"), nullable=False)
    action_type = Column(String(50), nullable=False)
    
    # Pre-execution baseline telemetry
    pre_attack_pps = Column(Float, default=0.0)
    pre_legitimate_throughput_mbps = Column(Float, default=0.0)
    pre_latency_ms = Column(Float, default=0.0)
    pre_packet_loss_pct = Column(Float, default=0.0)
    
    # Post-execution measured telemetry
    post_attack_pps = Column(Float, default=0.0)
    post_legitimate_throughput_mbps = Column(Float, default=0.0)
    post_latency_ms = Column(Float, default=0.0)
    post_packet_loss_pct = Column(Float, default=0.0)
    
    # Predicted vs Actual
    predicted_attack_reduction_pct = Column(Float, default=0.0)
    actual_attack_reduction_pct = Column(Float, default=0.0)
    predicted_qos_impact_pct = Column(Float, default=0.0)
    actual_qos_impact_pct = Column(Float, default=0.0)
    
    # Overall Scores
    mitigation_effectiveness = Column(Float, default=0.0) # 0 to 1
    collateral_impact = Column(Float, default=0.0) # 0 to 1 (lower is better)
    composite_success_score = Column(Float, default=0.0) # 0 to 1
    
    success_status = Column(String(30), default="SUCCESS") # SUCCESS, PARTIAL_SUCCESS, FAILED_COLLATERAL, FAILED_INEFFECTIVE
    explanation = Column(Text, nullable=True)
    evaluated_at = Column(DateTime, default=datetime.utcnow)

    incident = relationship("Incident", back_populates="outcomes")

class ExperienceRecord(Base):
    __tablename__ = "experience_records"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, nullable=False, index=True)
    threat_type = Column(String(100), nullable=False, index=True)
    source_ip = Column(String(45), nullable=False)
    destination_ip = Column(String(45), nullable=False)
    network_context = Column(JSON, nullable=True)
    threat_confidence = Column(Float, default=0.0)
    selected_action = Column(String(50), nullable=False, index=True)
    parameters = Column(JSON, nullable=True)
    
    reliability_score = Column(Float, default=0.0)
    trust_score = Column(Float, default=0.0)
    execution_mode = Column(String(30), nullable=False)
    
    predicted_outcome = Column(JSON, nullable=True)
    actual_outcome = Column(JSON, nullable=True)
    qos_impact = Column(Float, default=0.0)
    
    human_override = Column(Boolean, default=False)
    final_success = Column(Boolean, default=True)
    adaptation_weight_delta = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

