from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class TrustEngineWeights:
    alpha_reliability: float = 0.40
    beta_threat_confidence: float = 0.20
    gamma_qos_safety: float = 0.20
    delta_uncertainty: float = 0.10
    lambda_failure_penalty: float = 0.10

@dataclass
class TrustEvaluationInput:
    reliability_score: float
    threat_confidence: float
    qos_risk: float
    uncertainty: float
    historical_failure_rate: float = 0.0
    human_override_rate: float = 0.0
    policy_status: str = "ALLOW"

@dataclass
class TrustEvaluationResult:
    trust_score: float
    reliability_contribution: float
    threat_confidence_contribution: float
    qos_safety_contribution: float
    uncertainty_penalty: float
    historical_failure_penalty: float
    recommended_mode: str
    explanation: str
    breakdown: Dict[str, float]

class AutonomyTrustEngine:
    """
    Component 3: Autonomy Trust Engine
    Quantifies the system's self-trust in executing a response autonomously.
    Trust = alpha * Reliability + beta * Threat_Conf + gamma * (1 - QoS_Risk)
          - delta * Uncertainty - lambda * Failure_Penalty
    """
    def __init__(self, weights: Optional[TrustEngineWeights] = None):
        self.weights = weights or TrustEngineWeights()

    def calculate_trust(self, item: TrustEvaluationInput) -> TrustEvaluationResult:
        rel = max(0.0, min(1.0, item.reliability_score))
        conf = max(0.0, min(1.0, item.threat_confidence))
        qos_safe = max(0.0, min(1.0, 1.0 - item.qos_risk))
        unc = max(0.0, min(1.0, item.uncertainty))
        fail_pen = max(0.0, min(1.0, (item.historical_failure_rate * 0.7) + (item.human_override_rate * 0.3)))

        # Term contributions
        c_rel = self.weights.alpha_reliability * rel
        c_conf = self.weights.beta_threat_confidence * conf
        c_qos = self.weights.gamma_qos_safety * qos_safe
        p_unc = self.weights.delta_uncertainty * unc
        p_fail = self.weights.lambda_failure_penalty * fail_pen

        # Raw Trust Calculation
        raw_trust = (c_rel + c_conf + c_qos) - (p_unc + p_fail)

        # Baseline normalized scale: max possible is alpha + beta + gamma = 0.80.
        # Direct bounded normalization to 0.0 - 1.0:
        trust_score = max(0.0, min(1.0, raw_trust / (self.weights.alpha_reliability + self.weights.beta_threat_confidence + self.weights.gamma_qos_safety)))
        trust_score = round(trust_score, 4)

        # Policy-driven damping: if policy is RESTRICT or ESCALATE, trust cannot exceed 0.75 or 0.50 respectively
        if item.policy_status == "RESTRICT" and trust_score > 0.75:
            trust_score = 0.75
        elif item.policy_status in ["ESCALATE", "REJECT"] and trust_score > 0.50:
            trust_score = 0.50

        # Preliminary mode recommendation
        if trust_score >= 0.85 and item.policy_status == "ALLOW":
            recommended_mode = "ZERO_TOUCH"
        elif trust_score >= 0.55:
            recommended_mode = "GUARDED"
        else:
            recommended_mode = "HUMAN_APPROVAL"

        # Explainable rationale
        reasons = []
        if trust_score >= 0.85:
            reasons.append(f"High self-trust ({trust_score:.2f}) verified with reliable response metrics and safety margins.")
        elif trust_score >= 0.55:
            reasons.append(f"Moderate trust ({trust_score:.2f}) warrants guarded or rate-limited execution.")
        else:
            reasons.append(f"Low trust score ({trust_score:.2f}) driven by uncertainty or high operational stakes.")

        if item.historical_failure_rate > 0.25:
            reasons.append(f"Penalized for recent historical execution failures ({item.historical_failure_rate:.0%}).")
        if item.human_override_rate > 0.20:
            reasons.append(f"Adjusted for prior human analyst overrides ({item.human_override_rate:.0%}).")

        explanation = " ".join(reasons)

        breakdown = {
            "reliability_contribution": round(c_rel, 4),
            "threat_confidence_contribution": round(c_conf, 4),
            "qos_safety_contribution": round(c_qos, 4),
            "uncertainty_penalty": round(p_unc, 4),
            "historical_failure_penalty": round(p_fail, 4),
            "final_trust_score": trust_score
        }

        return TrustEvaluationResult(
            trust_score=trust_score,
            reliability_contribution=round(c_rel, 4),
            threat_confidence_contribution=round(c_conf, 4),
            qos_safety_contribution=round(c_qos, 4),
            uncertainty_penalty=round(p_unc, 4),
            historical_failure_penalty=round(p_fail, 4),
            recommended_mode=recommended_mode,
            explanation=explanation,
            breakdown=breakdown
        )

