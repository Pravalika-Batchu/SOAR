from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

class TrustScoreResponse(BaseModel):
    id: int
    incident_id: int
    candidate_id: Optional[int]
    trust_score: float
    autonomy_mode: str
    reliability_contribution: float
    threat_confidence_contribution: float
    qos_safety_contribution: float
    uncertainty_penalty: float
    historical_failure_penalty: float
    rationale: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class OutcomeEvaluationResponse(BaseModel):
    id: int
    incident_id: int
    candidate_response_id: int
    action_type: str
    pre_attack_pps: float
    pre_legitimate_throughput_mbps: float
    pre_latency_ms: float
    pre_packet_loss_pct: float
    post_attack_pps: float
    post_legitimate_throughput_mbps: float
    post_latency_ms: float
    post_packet_loss_pct: float
    predicted_attack_reduction_pct: float
    actual_attack_reduction_pct: float
    predicted_qos_impact_pct: float
    actual_qos_impact_pct: float
    mitigation_effectiveness: float
    collateral_impact: float
    composite_success_score: float
    success_status: str
    explanation: Optional[str]
    evaluated_at: datetime

    class Config:
        from_attributes = True

class ExperienceRecordResponse(BaseModel):
    id: int
    incident_id: int
    threat_type: str
    source_ip: str
    destination_ip: str
    network_context: Optional[Dict[str, Any]]
    threat_confidence: float
    selected_action: str
    parameters: Optional[Dict[str, Any]]
    reliability_score: float
    trust_score: float
    execution_mode: str
    predicted_outcome: Optional[Dict[str, Any]]
    actual_outcome: Optional[Dict[str, Any]]
    qos_impact: float
    human_override: bool
    final_success: bool
    adaptation_weight_delta: float
    created_at: datetime

    class Config:
        from_attributes = True

class NetworkMetricsSummary(BaseModel):
    system_status: str
    adapter_mode: str
    active_incidents: int
    total_alerts: int
    pending_approvals: int
    autonomous_executions: int
    current_throughput_mbps: float
    current_packet_loss_pct: float
    current_latency_ms: float
    autonomy_distribution: Dict[str, int]

