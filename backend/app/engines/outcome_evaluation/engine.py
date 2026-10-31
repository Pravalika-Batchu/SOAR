from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class TelemetrySnapshot:
    attack_pps: float
    legitimate_throughput_mbps: float
    latency_ms: float
    packet_loss_pct: float
    timestamp_epoch: float = 0.0

@dataclass
class PredictedOutcome:
    expected_attack_reduction_pct: float = 85.0
    tolerable_qos_impact_pct: float = 10.0

@dataclass
class OutcomeEvaluationResult:
    predicted_attack_reduction_pct: float
    actual_attack_reduction_pct: float
    predicted_qos_impact_pct: float
    actual_qos_impact_pct: float
    mitigation_effectiveness: float # 0.0 to 1.0 (higher = better)
    collateral_impact: float # 0.0 to 1.0 (lower = better)
    composite_score: float # 0.0 to 1.0
    classification: str # "SUCCESS", "PARTIAL_SUCCESS", "FAILED_COLLATERAL", "FAILED_INEFFECTIVE"
    rule_execution_succeeded: bool
    security_response_succeeded: bool
    explanation: str

class OutcomeEvaluationEngine:
    """
    Component 5: Outcome Evaluation Engine
    Evaluates whether the security response achieved threat mitigation without
    causing intolerable collateral QoS disruption to legitimate network services.
    
    Distinguishes rule execution success from actual security response success.
    """
    def evaluate(
        self,
        pre: TelemetrySnapshot,
        post: TelemetrySnapshot,
        predicted: Optional[PredictedOutcome] = None,
        rule_execution_ok: bool = True
    ) -> OutcomeEvaluationResult:
        pred = predicted or PredictedOutcome()

        # 1. Calculate Actual Attack Reduction %
        if pre.attack_pps > 0:
            attack_diff = max(0.0, pre.attack_pps - post.attack_pps)
            actual_attack_reduction = (attack_diff / pre.attack_pps) * 100.0
        else:
            actual_attack_reduction = 100.0 if post.attack_pps == 0 else 0.0
        actual_attack_reduction = round(min(100.0, max(0.0, actual_attack_reduction)), 2)

        # 2. Calculate Actual QoS Degradation %
        # Measured through legitimate throughput drop, latency increase, and packet loss
        qos_drops = []
        if pre.legitimate_throughput_mbps > 0:
            tp_loss = max(0.0, pre.legitimate_throughput_mbps - post.legitimate_throughput_mbps)
            tp_drop_pct = (tp_loss / pre.legitimate_throughput_mbps) * 100.0
            qos_drops.append(tp_drop_pct)
        
        if pre.latency_ms > 0 and post.latency_ms > pre.latency_ms:
            lat_increase_pct = ((post.latency_ms - pre.latency_ms) / pre.latency_ms) * 100.0
            qos_drops.append(min(100.0, lat_increase_pct * 0.5)) # Weight latency moderately

        if post.packet_loss_pct > pre.packet_loss_pct:
            qos_drops.append(post.packet_loss_pct - pre.packet_loss_pct)

        actual_qos_impact = round(max(qos_drops) if qos_drops else 0.0, 2)

        # 3. Normalized Effectiveness (0 to 1) and Collateral Impact (0 to 1)
        mitigation_eff = round(actual_attack_reduction / 100.0, 4)
        collateral_imp = round(min(1.0, actual_qos_impact / 100.0), 4)

        # 4. Composite Score = 0.65 * Mitigation - 0.35 * Collateral (bounded to 0..1)
        composite = max(0.0, min(1.0, (0.65 * mitigation_eff) + (0.35 * (1.0 - collateral_imp))))
        composite = round(composite, 4)

        # 5. Success / Failure Classification
        if not rule_execution_ok:
            classification = "FAILED_RULE_EXECUTION"
            sec_success = False
            explanation = "Network OpenFlow rule execution failed at switch datapath level."
        elif actual_attack_reduction < 50.0:
            classification = "FAILED_INEFFECTIVE"
            sec_success = False
            explanation = (
                f"Response ineffective: Attack reduced by only {actual_attack_reduction:.1f}% "
                f"(expected >= {pred.expected_attack_reduction_pct:.1f}%)."
            )
        elif actual_qos_impact > 35.0:
            classification = "FAILED_COLLATERAL"
            sec_success = False
            explanation = (
                f"Rule executed, but caused unacceptable collateral damage: {actual_qos_impact:.1f}% QoS degradation "
                f"on legitimate flows (tolerable was <= {pred.tolerable_qos_impact_pct:.1f}%)."
            )
        elif actual_attack_reduction >= 75.0 and actual_qos_impact <= 15.0:
            classification = "SUCCESS"
            sec_success = True
            explanation = (
                f"Response successful: {actual_attack_reduction:.1f}% attack mitigation with minimal "
                f"QoS degradation ({actual_qos_impact:.1f}%)."
            )
        else:
            classification = "PARTIAL_SUCCESS"
            sec_success = True
            explanation = (
                f"Moderate response efficacy: {actual_attack_reduction:.1f}% mitigation, "
                f"with {actual_qos_impact:.1f}% collateral QoS impact."
            )

        return OutcomeEvaluationResult(
            predicted_attack_reduction_pct=pred.expected_attack_reduction_pct,
            actual_attack_reduction_pct=actual_attack_reduction,
            predicted_qos_impact_pct=pred.tolerable_qos_impact_pct,
            actual_qos_impact_pct=actual_qos_impact,
            mitigation_effectiveness=mitigation_eff,
            collateral_impact=collateral_imp,
            composite_score=composite,
            classification=classification,
            rule_execution_succeeded=rule_execution_ok,
            security_response_succeeded=sec_success,
            explanation=explanation
        )

