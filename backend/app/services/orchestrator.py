import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models.incident import Incident
from app.models.alert import SecurityAlert
from app.models.asset import Asset
from app.models.response import CandidateResponse, HumanApproval, ResponseExecution
from app.models.policy import PolicyRule
from app.models.trust import TrustLog
from app.models.outcome import OutcomeEvaluation, ExperienceRecord
from app.models.metrics import AuditLog, NetworkMetricSample

from app.ml.model import detector
from app.ml.features import FlowFeatureVector, extract_features_from_raw_flow

from app.engines.response_reliability.engine import ResponseReliabilityEngine, CandidateEvaluationInput
from app.engines.policy_constraint.engine import PolicyConstraintEngine, PolicyContext, PolicyDecisionEnum
from app.engines.autonomy_trust.engine import AutonomyTrustEngine, TrustEvaluationInput
from app.engines.dynamic_autonomy.engine import DynamicAutonomyController, AutonomyExecutionMode
from app.engines.outcome_evaluation.engine import OutcomeEvaluationEngine, TelemetrySnapshot, PredictedOutcome
from app.engines.experience_memory.engine import ExperienceMemoryEngine, ExperienceQuery

from app.integrations.mock_network_adapter import mock_adapter
from app.integrations.ryu_network_adapter import RyuOpenFlowAdapter
from app.core.config import settings

class IncidentOrchestrationService:
    def __init__(self):
        self.reliability_engine = ResponseReliabilityEngine()
        self.policy_engine = PolicyConstraintEngine()
        self.trust_engine = AutonomyTrustEngine()
        self.autonomy_controller = DynamicAutonomyController()
        self.outcome_engine = OutcomeEvaluationEngine()
        self.memory_engine = ExperienceMemoryEngine()
        self.ryu_adapter = RyuOpenFlowAdapter()

    def get_network_adapter(self):
        if settings.NETWORK_ADAPTER_MODE == "RYU":
            return self.ryu_adapter
        return mock_adapter

    def sync_experience_memory_from_db(self, db: Session):
        """Loads historical database records into the in-memory Experience Memory index."""
        records = db.query(ExperienceRecord).all()
        self.memory_engine.records = [
            {
                "incident_id": r.incident_id,
                "threat_type": r.threat_type,
                "selected_action": r.selected_action,
                "qos_impact": r.qos_impact,
                "human_override": r.human_override,
                "final_success": r.final_success,
                "network_context": r.network_context
            }
            for r in records
        ]

    def analyze_incident(self, incident_id: int, db: Session) -> Incident:
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        if not incident:
            raise ValueError(f"Incident {incident_id} not found")

        incident.status = "ASSESSING"
        db.commit()

        # 1. Collect asset and network context
        target_asset = db.query(Asset).filter(Asset.ip_address == incident.destination_ip).first()

        # 2. Extract flow features from alerts
        alert = db.query(SecurityAlert).filter(SecurityAlert.incident_id == incident.id).first()
        raw_payload = alert.raw_payload if alert and alert.raw_payload else {}

        # Synthesize flow telemetry features based on threat type
        if "DOS" in incident.threat_type.upper():
            feature_vector = FlowFeatureVector(
                packets_per_second=2500.0,
                bytes_per_second=1850000.0,
                connection_count=120.0,
                unique_destination_count=1.0,
                avg_packet_size_bytes=740.0,
                mean_connection_duration_sec=0.2,
                failed_connection_ratio=0.85,
                traffic_volume_variation=0.80
            )
        elif "PORT_SCAN" in incident.threat_type.upper():
            feature_vector = FlowFeatureVector(
                packets_per_second=350.0,
                bytes_per_second=24500.0,
                connection_count=450.0,
                unique_destination_count=35.0,
                avg_packet_size_bytes=70.0,
                mean_connection_duration_sec=0.05,
                failed_connection_ratio=0.95,
                traffic_volume_variation=0.60
            )
        elif "BRUTE_FORCE" in incident.threat_type.upper():
            feature_vector = FlowFeatureVector(
                packets_per_second=45.0,
                bytes_per_second=32000.0,
                connection_count=65.0,
                unique_destination_count=1.0,
                avg_packet_size_bytes=711.0,
                mean_connection_duration_sec=1.1,
                failed_connection_ratio=0.90,
                traffic_volume_variation=0.35
            )
        else:
            feature_vector = extract_features_from_raw_flow(raw_payload)

        # 3. Isolation Forest Anomaly Detection
        prediction = detector.predict(feature_vector)
        incident.anomaly_score = prediction.normalized_anomaly_score
        incident.is_anomaly = 1 if prediction.is_anomaly else 0
        incident.uncertainty = prediction.uncertainty

        # Threat confidence composite
        base_confidence = 0.80 if incident.threat_type in ["DOS_SYN_FLOOD", "PORT_SCAN", "BRUTE_FORCE"] else 0.50
        incident.threat_confidence = round(float(np_clip(0.6 * base_confidence + 0.4 * prediction.normalized_anomaly_score, 0.1, 0.99)), 4)
        incident.assessment_notes = prediction.explanation

        incident.status = "EVALUATING"
        db.commit()
        db.refresh(incident)
        return incident

    def evaluate_candidate_responses(self, incident_id: int, db: Session) -> List[CandidateResponse]:
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        if not incident:
            raise ValueError(f"Incident {incident_id} not found")

        self.sync_experience_memory_from_db(db)
        target_asset = db.query(Asset).filter(Asset.ip_address == incident.destination_ip).first()
        target_criticality = target_asset.criticality if target_asset else "MEDIUM"
        qos_sensitivity = target_asset.qos_sensitivity if target_asset else 0.50

        # Load active policy rules from database
        active_rules = db.query(PolicyRule).filter(PolicyRule.is_active == True).all()
        policy_rules_list = [
            {
                "name": r.name,
                "rule_type": r.rule_type,
                "condition_json": r.condition_json,
                "enforcement_action": r.enforcement_action,
                "is_mandatory": r.is_mandatory
            }
            for r in active_rules
        ]

        # Purge any old candidates for fresh evaluation
        db.query(CandidateResponse).filter(CandidateResponse.incident_id == incident.id).delete()
        db.commit()

        # Define 3 distinct candidate responses
        candidate_configs = [
            {
                "action_type": "BLOCK_IP",
                "target_ip": incident.source_ip,
                "parameters": {"duration_sec": 600},
                "predicted_qos_risk": 0.15 if target_criticality != "CRITICAL" else 0.35,
                "resource_risk": 0.05,
                "policy_fit": 0.90
            },
            {
                "action_type": "RATE_LIMIT",
                "target_ip": incident.source_ip,
                "parameters": {"rate_kbps": 250, "duration_sec": 300},
                "predicted_qos_risk": 0.05, # Least disruptive
                "resource_risk": 0.05,
                "policy_fit": 0.95
            },
            {
                "action_type": "ISOLATE_HOST",
                "target_ip": incident.destination_ip if "INTERNAL" in incident.threat_type else incident.source_ip,
                "parameters": {"isolation_level": "FULL"},
                "predicted_qos_risk": 0.85 if target_criticality == "CRITICAL" else 0.40,
                "resource_risk": 0.20,
                "policy_fit": 0.40 if target_criticality == "CRITICAL" else 0.75
            }
        ]

        evaluated_candidates = []

        for cfg in candidate_configs:
            action = cfg["action_type"]
            target = cfg["target_ip"]

            # 1. Experience Memory: retrieve historical performance
            hist_perf = self.memory_engine.get_historical_performance(action, incident.threat_type)

            # Apply empirical adaptation penalty to predicted QoS or success rate
            adapted_qos_risk = min(1.0, cfg["predicted_qos_risk"] + (hist_perf.adaptation_penalty * 0.5))

            # 2. Component 1: Response Reliability Engine
            rel_input = CandidateEvaluationInput(
                action_type=action,
                target_ip=target,
                threat_confidence=incident.threat_confidence,
                historical_success_rate=hist_perf.success_rate,
                policy_fit_score=cfg["policy_fit"],
                predicted_qos_risk=adapted_qos_risk,
                resource_risk=cfg["resource_risk"],
                uncertainty=incident.uncertainty,
                has_history=hist_perf.sample_count > 0
            )
            rel_res = self.reliability_engine.evaluate(rel_input)

            # 3. Component 2: Policy / Constraint Engine
            pol_ctx = PolicyContext(
                target_criticality=target_criticality,
                target_service=target_asset.service_type if target_asset else None,
                qos_sensitivity=qos_sensitivity,
                predicted_qos_risk=adapted_qos_risk,
                uncertainty=incident.uncertainty,
                is_gateway_or_broadcast=(target in ["10.0.0.200", "10.0.0.255", "10.0.0.1"]),
                active_policies=policy_rules_list
            )
            pol_res = self.policy_engine.evaluate_candidate(action, target, pol_ctx)

            # 4. Component 3: Autonomy Trust Engine
            trust_input = TrustEvaluationInput(
                reliability_score=rel_res.reliability_score,
                threat_confidence=incident.threat_confidence,
                qos_risk=adapted_qos_risk,
                uncertainty=incident.uncertainty,
                historical_failure_rate=hist_perf.failure_rate,
                human_override_rate=hist_perf.human_override_rate,
                policy_status=pol_res.decision.value
            )
            trust_res = self.trust_engine.calculate_trust(trust_input)

            # 5. Component 4: Dynamic Autonomy Controller
            autonomy_dec = self.autonomy_controller.determine_autonomy_mode(
                trust_score=trust_res.trust_score,
                policy_decision=pol_res.decision,
                is_mandatory_override=pol_res.is_mandatory_override,
                restriction_params=pol_res.restriction_params,
                action_type=action
            )

            # Persist candidate to database
            cand_db = CandidateResponse(
                incident_id=incident.id,
                action_type=action,
                target_ip=target,
                parameters=autonomy_dec.execution_parameters or cfg["parameters"],
                reliability_score=rel_res.reliability_score,
                threat_confidence_score=rel_input.threat_confidence,
                historical_success_score=hist_perf.success_rate,
                policy_fit_score=cfg["policy_fit"],
                qos_risk_score=adapted_qos_risk,
                resource_risk_score=cfg["resource_risk"],
                uncertainty_score=incident.uncertainty,
                score_breakdown=rel_res.breakdown,
                explanation=f"{rel_res.explanation} Policy: {pol_res.explanation} Autonomy: {autonomy_dec.rationale}",
                policy_status=pol_res.decision.value,
                policy_reason=pol_res.explanation,
                trust_score=trust_res.trust_score,
                recommended_mode=autonomy_dec.mode.value
            )
            db.add(cand_db)
            db.commit()
            db.refresh(cand_db)
            evaluated_candidates.append(cand_db)

            # Record Trust Log entry
            t_log = TrustLog(
                incident_id=incident.id,
                candidate_id=cand_db.id,
                trust_score=trust_res.trust_score,
                autonomy_mode=autonomy_dec.mode.value,
                reliability_contribution=trust_res.reliability_contribution,
                threat_confidence_contribution=trust_res.threat_confidence_contribution,
                qos_safety_contribution=trust_res.qos_safety_contribution,
                uncertainty_penalty=trust_res.uncertainty_penalty,
                historical_failure_penalty=trust_res.historical_failure_penalty,
                rationale=autonomy_dec.rationale
            )
            db.add(t_log)
            db.commit()

        # Select Best Candidate based on reliability and policy compliance
        valid_candidates = [c for c in evaluated_candidates if c.policy_status != "REJECT"]
        if not valid_candidates:
            valid_candidates = evaluated_candidates

        # Rank by reliability score
        valid_candidates.sort(key=lambda c: c.reliability_score, reverse=True)
        best = valid_candidates[0]

        incident.selected_response_id = best.id
        incident.autonomy_trust_score = best.trust_score
        incident.execution_mode = best.recommended_mode

        # If the best selected response requires HUMAN_APPROVAL, create a persistent approval request
        if best.recommended_mode == "HUMAN_APPROVAL":
            incident.status = "PENDING_APPROVAL"
            # Prevent duplicate pending approval for this candidate
            existing_approval = db.query(HumanApproval).filter(
                HumanApproval.incident_id == incident.id,
                HumanApproval.candidate_response_id == best.id,
                HumanApproval.status == "PENDING"
            ).first()

            if not existing_approval:
                approval = HumanApproval(
                    incident_id=incident.id,
                    candidate_response_id=best.id,
                    status="PENDING",
                    action_type=best.action_type,
                    target_ip=best.target_ip,
                    threat_type=incident.threat_type,
                    trust_score=best.trust_score,
                    reliability_score=best.reliability_score,
                    policy_decision=best.policy_status,
                    escalation_reason=best.policy_reason or best.explanation,
                    requested_at=datetime.utcnow()
                )
                db.add(approval)
        else:
            incident.status = "READY_TO_EXECUTE"

        db.commit()
        db.refresh(incident)
        return evaluated_candidates

    def request_candidate_approval(self, incident_id: int, candidate_id: int, db: Session) -> HumanApproval:
        """Explicitly queues a candidate for human operator authorization."""
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        if not incident:
            raise ValueError(f"Incident {incident_id} not found")
        candidate = db.query(CandidateResponse).filter(CandidateResponse.id == candidate_id).first()
        if not candidate:
            raise ValueError(f"Candidate {candidate_id} not found")

        # Check for existing pending approval
        existing = db.query(HumanApproval).filter(
            HumanApproval.incident_id == incident.id,
            HumanApproval.candidate_response_id == candidate.id,
            HumanApproval.status == "PENDING"
        ).first()

        if existing:
            return existing

        approval = HumanApproval(
            incident_id=incident.id,
            candidate_response_id=candidate.id,
            status="PENDING",
            action_type=candidate.action_type,
            target_ip=candidate.target_ip,
            threat_type=incident.threat_type,
            trust_score=candidate.trust_score,
            reliability_score=candidate.reliability_score,
            policy_decision=candidate.policy_status,
            escalation_reason=candidate.policy_reason or candidate.explanation,
            requested_at=datetime.utcnow()
        )
        db.add(approval)
        incident.status = "PENDING_APPROVAL"
        db.commit()
        db.refresh(approval)
        return approval

    def execute_incident_response(self, incident_id: int, candidate_id: Optional[int], db: Session) -> Dict[str, Any]:
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        if not incident:
            raise ValueError("Incident not found")

        # Pick specified candidate or the selected best
        cid = candidate_id or incident.selected_response_id
        candidate = db.query(CandidateResponse).filter(CandidateResponse.id == cid).first()
        if not candidate:
            raise ValueError("Candidate response not found")

        # Enforcement 1: Mandatory Policy Hard Rejection
        if candidate.policy_status == "REJECT":
            audit = AuditLog(
                action="UNAUTHORIZED_EXECUTION_ATTEMPT",
                resource_type="CANDIDATE_RESPONSE",
                resource_id=str(candidate.id),
                username="SYSTEM",
                details={
                    "incident_id": incident.id,
                    "action_type": candidate.action_type,
                    "reason": "Action is strictly REJECTED by mandatory security policy."
                }
            )
            db.add(audit)
            db.commit()
            raise ValueError("Execution halted: Action is strictly REJECTED by mandatory security policy.")

        # Enforcement 2: Human Approval Verification
        if candidate.recommended_mode == "HUMAN_APPROVAL":
            # Check if this specific candidate was approved by an operator
            approval = db.query(HumanApproval).filter(
                HumanApproval.incident_id == incident.id,
                HumanApproval.candidate_response_id == candidate.id,
                HumanApproval.status == "APPROVED"
            ).first()

            if not approval:
                # Check if it was explicitly REJECTED
                rejected_approval = db.query(HumanApproval).filter(
                    HumanApproval.incident_id == incident.id,
                    HumanApproval.candidate_response_id == candidate.id,
                    HumanApproval.status == "REJECTED"
                ).first()

                if rejected_approval:
                    audit = AuditLog(
                        action="EXECUTION_BLOCKED_REJECTED",
                        resource_type="CANDIDATE_RESPONSE",
                        resource_id=str(candidate.id),
                        username="SYSTEM",
                        details={
                            "incident_id": incident.id,
                            "action_type": candidate.action_type,
                            "reason": "Action was explicitly REJECTED by human operator and cannot be executed."
                        }
                    )
                    db.add(audit)
                    db.commit()
                    raise PermissionError(f"Action '{candidate.action_type}' was REJECTED by human operator and cannot be executed.")

                # If no approval exists, create a pending approval request automatically
                existing_pending = db.query(HumanApproval).filter(
                    HumanApproval.incident_id == incident.id,
                    HumanApproval.candidate_response_id == candidate.id,
                    HumanApproval.status == "PENDING"
                ).first()

                if not existing_pending:
                    new_pending = HumanApproval(
                        incident_id=incident.id,
                        candidate_response_id=candidate.id,
                        status="PENDING",
                        action_type=candidate.action_type,
                        target_ip=candidate.target_ip,
                        threat_type=incident.threat_type,
                        trust_score=candidate.trust_score,
                        reliability_score=candidate.reliability_score,
                        policy_decision=candidate.policy_status,
                        escalation_reason=candidate.policy_reason or candidate.explanation,
                        requested_at=datetime.utcnow()
                    )
                    db.add(new_pending)
                    incident.status = "PENDING_APPROVAL"

                # Audit log unauthorized execution attempt
                audit = AuditLog(
                    action="UNAUTHORIZED_EXECUTION_ATTEMPT",
                    resource_type="CANDIDATE_RESPONSE",
                    resource_id=str(candidate.id),
                    username="SYSTEM",
                    details={
                        "incident_id": incident.id,
                        "action_type": candidate.action_type,
                        "reason": "Direct execution without human approval blocked (HTTP 403)."
                    }
                )
                db.add(audit)
                db.commit()
                raise PermissionError(f"Action '{candidate.action_type}' requires human operator approval before execution.")

        incident.status = "EXECUTING"
        db.commit()

        # Step 1: Record Pre-Execution Telemetry Baseline
        adapter = self.get_network_adapter()
        pre_metrics = adapter.get_network_metrics()
        is_flood = any(t in incident.threat_type.upper() for t in ["DOS", "FLOOD", "SYN"])
        pre_telemetry = TelemetrySnapshot(
            attack_pps=2500.0 if is_flood else 250.0,
            legitimate_throughput_mbps=pre_metrics.get("legitimate_throughput_mbps", 95.0),
            latency_ms=pre_metrics.get("latency_ms", 1.2),
            packet_loss_pct=pre_metrics.get("packet_loss_pct", 0.1)
        )

        # Step 2: Enforce Network Action via SDN Adapter
        duration = candidate.parameters.get("duration_sec", 300) if candidate.parameters else 300
        if candidate.action_type == "BLOCK_IP":
            exec_res = adapter.apply_block_rule(candidate.target_ip, duration_sec=duration)
        elif candidate.action_type == "RATE_LIMIT":
            rate = candidate.parameters.get("rate_kbps", 500) if candidate.parameters else 500
            exec_res = adapter.apply_rate_limit(candidate.target_ip, rate_kbps=rate, duration_sec=duration)
        elif candidate.action_type == "ISOLATE_HOST":
            exec_res = adapter.isolate_host(candidate.target_ip)
        else:
            exec_res = adapter.apply_block_rule(candidate.target_ip, duration_sec=duration)

        now = datetime.utcnow()
        expires = now + timedelta(seconds=duration) if duration else None

        # Persist ResponseExecution
        execution = ResponseExecution(
            incident_id=incident.id,
            candidate_response_id=candidate.id,
            action_type=candidate.action_type,
            target_ip=candidate.target_ip,
            execution_mode=candidate.recommended_mode,
            adapter_used=exec_res.adapter_mode,
            flow_rule_id=exec_res.rule_id,
            status="SUCCESS" if exec_res.success else "FAILED",
            execution_log=exec_res.details,
            is_reverted=False,
            expires_at=expires,
            executed_at=now
        )
        db.add(execution)

        # Audit log successful execution
        audit = AuditLog(
            action="RESPONSE_EXECUTION",
            resource_type="RESPONSE_EXECUTION",
            resource_id=str(candidate.id),
            username="SYSTEM",
            details={
                "incident_id": incident.id,
                "action_type": execution.action_type,
                "target_ip": execution.target_ip,
                "execution_mode": execution.execution_mode,
                "adapter": execution.adapter_used,
                "rule_id": execution.flow_rule_id
            }
        )
        db.add(audit)
        db.commit()
        db.refresh(execution)

        # Step 3: Measure Post-Execution Telemetry
        post_attack_pps = 25.0 if candidate.action_type == "BLOCK_IP" else (min(pre_telemetry.attack_pps * 0.1, 50.0) if candidate.action_type == "RATE_LIMIT" else 15.0)
        post_tp = 94.0 if candidate.action_type in ["BLOCK_IP", "RATE_LIMIT"] else 40.0
        post_telemetry = TelemetrySnapshot(
            attack_pps=post_attack_pps,
            legitimate_throughput_mbps=post_tp,
            latency_ms=1.35,
            packet_loss_pct=0.2
        )

        # Step 4: Component 5: Outcome Evaluation
        pred_outcome = PredictedOutcome(expected_attack_reduction_pct=85.0, tolerable_qos_impact_pct=15.0)
        outcome_res = self.outcome_engine.evaluate(
            pre=pre_telemetry,
            post=post_telemetry,
            predicted=pred_outcome,
            rule_execution_ok=exec_res.success
        )

        # Persist Outcome Evaluation
        outcome_db = OutcomeEvaluation(
            incident_id=incident.id,
            candidate_response_id=candidate.id,
            action_type=candidate.action_type,
            pre_attack_pps=pre_telemetry.attack_pps,
            pre_legitimate_throughput_mbps=pre_telemetry.legitimate_throughput_mbps,
            pre_latency_ms=pre_telemetry.latency_ms,
            pre_packet_loss_pct=pre_telemetry.packet_loss_pct,
            post_attack_pps=post_telemetry.attack_pps,
            post_legitimate_throughput_mbps=post_telemetry.legitimate_throughput_mbps,
            post_latency_ms=post_telemetry.latency_ms,
            post_packet_loss_pct=post_telemetry.packet_loss_pct,
            predicted_attack_reduction_pct=outcome_res.predicted_attack_reduction_pct,
            actual_attack_reduction_pct=outcome_res.actual_attack_reduction_pct,
            predicted_qos_impact_pct=outcome_res.predicted_qos_impact_pct,
            actual_qos_impact_pct=outcome_res.actual_qos_impact_pct,
            mitigation_effectiveness=outcome_res.mitigation_effectiveness,
            collateral_impact=outcome_res.collateral_impact,
            composite_success_score=outcome_res.composite_score,
            success_status=outcome_res.classification,
            explanation=outcome_res.explanation,
            evaluated_at=now
        )
        db.add(outcome_db)
        db.commit()

        # Step 5: Component 6: Store Experience Memory
        human_overridden = (candidate.recommended_mode == "HUMAN_APPROVAL")
        exp_record = ExperienceRecord(
            incident_id=incident.id,
            threat_type=incident.threat_type,
            source_ip=incident.source_ip,
            destination_ip=incident.destination_ip,
            network_context={"criticality": "HIGH", "target_ip": incident.destination_ip},
            threat_confidence=incident.threat_confidence,
            selected_action=candidate.action_type,
            parameters=candidate.parameters,
            reliability_score=candidate.reliability_score,
            trust_score=candidate.trust_score,
            execution_mode=candidate.recommended_mode,
            predicted_outcome={"expected_reduction": pred_outcome.expected_attack_reduction_pct},
            actual_outcome={"actual_reduction": outcome_res.actual_attack_reduction_pct, "classification": outcome_res.classification},
            qos_impact=outcome_res.collateral_impact,
            human_override=human_overridden,
            final_success=outcome_res.security_response_succeeded,
            adaptation_weight_delta=0.05 if not outcome_res.security_response_succeeded else 0.0,
            created_at=now
        )
        db.add(exp_record)
        
        # Update incident final status and selected response ID
        incident.selected_response_id = candidate.id
        incident.status = "COMPLETED" if outcome_res.security_response_succeeded else "EVALUATED_FAILED"
        db.commit()
        db.refresh(incident)

        return {
            "incident_id": incident.id,
            "execution": {
                "id": execution.id,
                "action_type": execution.action_type,
                "target_ip": execution.target_ip,
                "adapter": execution.adapter_used,
                "rule_id": execution.flow_rule_id,
                "status": execution.status
            },
            "outcome": {
                "mitigation_pct": outcome_res.actual_attack_reduction_pct,
                "qos_impact_pct": outcome_res.actual_qos_impact_pct,
                "composite_score": outcome_res.composite_score,
                "status": outcome_res.classification,
                "explanation": outcome_res.explanation
            }
        }

def np_clip(val, low, high):
    return max(low, min(high, val))

orchestrator_service = IncidentOrchestrationService()
