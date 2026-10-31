from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime

class CandidateResponseSchema(BaseModel):
    id: int
    incident_id: int
    action_type: str
    target_ip: str
    parameters: Optional[Dict[str, Any]] = None
    reliability_score: float
    threat_confidence_score: float
    historical_success_score: float
    policy_fit_score: float
    qos_risk_score: float
    resource_risk_score: float
    uncertainty_score: float
    score_breakdown: Optional[Dict[str, Any]] = None
    explanation: Optional[str] = None
    policy_status: str
    policy_reason: Optional[str] = None
    trust_score: float
    recommended_mode: str
    candidate_status: Optional[str] = "READY" # EXECUTED, PENDING_APPROVAL, NOT_SELECTED, REJECTED, READY
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class HumanApprovalRequest(BaseModel):
    operator_comment: Optional[str] = None

class HumanApprovalResponse(BaseModel):
    id: int
    incident_id: int
    candidate_response_id: int
    status: str
    action_type: Optional[str] = None
    target_ip: Optional[str] = None
    threat_type: Optional[str] = None
    trust_score: Optional[float] = None
    reliability_score: Optional[float] = None
    policy_decision: Optional[str] = None
    escalation_reason: Optional[str] = None
    operator_username: Optional[str] = None
    operator_comment: Optional[str] = None
    requested_at: datetime
    decided_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class ExecutionRequest(BaseModel):
    candidate_id: Optional[int] = None
    force_mode: Optional[str] = None

class ExecutionResponse(BaseModel):
    id: int
    incident_id: int
    candidate_response_id: int
    action_type: str
    target_ip: str
    execution_mode: str
    adapter_used: str
    flow_rule_id: Optional[str] = None
    status: str
    execution_log: Optional[str] = None
    is_reverted: bool
    expires_at: Optional[datetime] = None
    executed_at: datetime
    reverted_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
