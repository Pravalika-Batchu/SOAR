export type AutonomyMode = 'ZERO_TOUCH' | 'GUARDED' | 'HUMAN_APPROVAL';
export type IncidentSeverity = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
export type PolicyStatus = 'ALLOW' | 'REJECT' | 'RESTRICT' | 'ESCALATE';

export interface SecurityAlert {
  id: number;
  source: string;
  alert_type: string;
  severity: IncidentSeverity;
  source_ip: string;
  destination_ip: string;
  source_port?: number;
  destination_port?: number;
  protocol: string;
  signature?: string;
  raw_payload?: Record<string, any>;
  timestamp: string;
  incident_id?: number;
}

export interface Incident {
  id: number;
  title: string;
  threat_type: string;
  severity: IncidentSeverity;
  status: string;
  source_ip: string;
  destination_ip: string;
  protocol: string;
  threat_confidence: number;
  anomaly_score: number;
  is_anomaly: number;
  uncertainty: number;
  assessment_notes?: string;
  selected_response_id?: number;
  autonomy_trust_score?: number;
  execution_mode?: AutonomyMode;
  created_at: string;
  updated_at?: string;
}

export interface CandidateResponse {
  id: number;
  incident_id: number;
  action_type: string;
  target_ip: string;
  parameters?: Record<string, any>;
  reliability_score: number;
  threat_confidence_score: number;
  historical_success_score: number;
  policy_fit_score: number;
  qos_risk_score: number;
  resource_risk_score: number;
  uncertainty_score: number;
  score_breakdown?: Record<string, any>;
  explanation?: string;
  policy_status: PolicyStatus;
  policy_reason?: string;
  trust_score: number;
  recommended_mode: AutonomyMode;
  candidate_status?: string;
  created_at: string;
}

export interface HumanApproval {
  id: number;
  incident_id: number;
  candidate_response_id: number;
  status: 'PENDING' | 'APPROVED' | 'REJECTED' | 'TIMED_OUT';
  operator_username?: string;
  operator_comment?: string;
  requested_at: string;
  decided_at?: string;
  action_type?: string;
  target_ip?: string;
  threat_type?: string;
  trust_score?: number;
  reliability_score?: number;
  policy_decision?: string;
  escalation_reason?: string;
  candidate?: CandidateResponse;
  incident?: Incident;
}

export interface PolicyRule {
  id: number;
  name: string;
  description: string;
  rule_type: string;
  condition_json: Record<string, any>;
  enforcement_action: PolicyStatus;
  is_mandatory: boolean;
  is_active: boolean;
  priority: number;
  created_at: string;
}

export interface TrustLog {
  id: number;
  incident_id: number;
  candidate_id?: number;
  trust_score: number;
  autonomy_mode: AutonomyMode;
  reliability_contribution: number;
  threat_confidence_contribution: number;
  qos_safety_contribution: number;
  uncertainty_penalty: number;
  historical_failure_penalty: number;
  rationale?: string;
  created_at: string;
}

export interface OutcomeEvaluation {
  id: number;
  incident_id: number;
  candidate_response_id: number;
  action_type: string;
  pre_attack_pps: number;
  pre_legitimate_throughput_mbps: number;
  pre_latency_ms: number;
  pre_packet_loss_pct: number;
  post_attack_pps: number;
  post_legitimate_throughput_mbps: number;
  post_latency_ms: number;
  post_packet_loss_pct: number;
  predicted_attack_reduction_pct: number;
  actual_attack_reduction_pct: number;
  predicted_qos_impact_pct: number;
  actual_qos_impact_pct: number;
  mitigation_effectiveness: number;
  collateral_impact: number;
  composite_success_score: number;
  success_status: string;
  explanation?: string;
  evaluated_at: string;
}

export interface ExperienceRecord {
  id: number;
  incident_id: number;
  threat_type: string;
  source_ip: string;
  destination_ip: string;
  network_context?: Record<string, any>;
  threat_confidence: number;
  selected_action: string;
  parameters?: Record<string, any>;
  reliability_score: number;
  trust_score: number;
  execution_mode: AutonomyMode;
  predicted_outcome?: Record<string, any>;
  actual_outcome?: Record<string, any>;
  qos_impact: number;
  human_override: boolean;
  final_success: boolean;
  adaptation_weight_delta: number;
  created_at: string;
}

export interface SystemStatus {
  status: string;
  environment: string;
  database: string;
  network_adapter: string;
  monitored_assets: number;
  topology_nodes: number;
  ryu_endpoint: string;
}

export interface MetricsSummary {
  system_status: string;
  adapter_mode: string;
  active_incidents: number;
  total_alerts: number;
  pending_approvals: number;
  autonomous_executions: number;
  current_throughput_mbps: number;
  current_packet_loss_pct: number;
  current_latency_ms: number;
  autonomy_distribution: {
    ZERO_TOUCH: number;
    GUARDED: number;
    HUMAN_APPROVAL: number;
  };
}

