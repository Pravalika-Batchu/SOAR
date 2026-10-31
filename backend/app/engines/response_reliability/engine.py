from dataclasses import dataclass, field
from typing import Dict, Any, Optional

@dataclass
class ReliabilityWeights:
    w_threat_confidence: float = 0.25
    w_historical_success: float = 0.25
    w_policy_fit: float = 0.20
    w_qos_risk: float = 0.15
    w_resource_risk: float = 0.05
    w_uncertainty: float = 0.10

    def validate(self):
        total = (
            self.w_threat_confidence +
            self.w_historical_success +
            self.w_policy_fit +
            self.w_qos_risk +
            self.w_resource_risk +
            self.w_uncertainty
        )
        if abs(total - 1.0) > 1e-4:
            raise ValueError(f"Reliability weights must sum to 1.0, current sum is {total:.4f}")

@dataclass
class CandidateEvaluationInput:
    action_type: str
    target_ip: str
    threat_confidence: float
    historical_success_rate: float
    policy_fit_score: float
    predicted_qos_risk: float
    resource_risk: float
    uncertainty: float
    has_history: bool = True
    context: Optional[Dict[str, Any]] = None

@dataclass
class ReliabilityResult:
    action_type: str
    target_ip: str
    reliability_score: float
    breakdown: Dict[str, float]
    explanation: str

class ResponseReliabilityEngine:
    """
    Component 1: Response Reliability Engine
    Computes an explainable, multi-factor reliability score for candidate security responses.
    Reliability Score = (w1 * Threat_Conf) + (w2 * Hist_Success) + (w3 * Policy_Fit) 
                      - (w4 * QoS_Risk) - (w5 * Resource_Risk) - (w6 * Uncertainty)
    """
    def __init__(self, weights: Optional[ReliabilityWeights] = None):
        self.weights = weights or ReliabilityWeights()
        self.weights.validate()

    def evaluate(self, item: CandidateEvaluationInput) -> ReliabilityResult:
        # If no history exists, use Bayesian neutral prior (0.50) with slight uncertainty penalty
        hist_success = item.historical_success_rate if item.has_history else 0.50
        uncertainty = item.uncertainty if item.has_history else min(1.0, item.uncertainty + 0.10)

        # Ensure all components are in [0, 1]
        c_threat = max(0.0, min(1.0, item.threat_confidence))
        s_hist = max(0.0, min(1.0, hist_success))
        p_fit = max(0.0, min(1.0, item.policy_fit_score))
        q_risk = max(0.0, min(1.0, item.predicted_qos_risk))
        r_risk = max(0.0, min(1.0, item.resource_risk))
        u_val = max(0.0, min(1.0, uncertainty))

        # Weighted calculation
        pos_contrib = (
            self.weights.w_threat_confidence * c_threat +
            self.weights.w_historical_success * s_hist +
            self.weights.w_policy_fit * p_fit
        )
        neg_contrib = (
            self.weights.w_qos_risk * q_risk +
            self.weights.w_resource_risk * r_risk +
            self.weights.w_uncertainty * u_val
        )

        raw_score = pos_contrib - neg_contrib
        
        # Scale raw score to [0, 1] interval. Maximum theoretical is sum of positive weights (0.70), minimum is -0.30.
        # Direct bounded normalization:
        max_pos = self.weights.w_threat_confidence + self.weights.w_historical_success + self.weights.w_policy_fit
        normalized_score = max(0.0, min(1.0, (raw_score + (1.0 - max_pos)) / 1.0))
        normalized_score = round(normalized_score, 4)

        breakdown = {
            "threat_confidence_term": round(self.weights.w_threat_confidence * c_threat, 4),
            "historical_success_term": round(self.weights.w_historical_success * s_hist, 4),
            "policy_fit_term": round(self.weights.w_policy_fit * p_fit, 4),
            "qos_risk_penalty": round(self.weights.w_qos_risk * q_risk, 4),
            "resource_risk_penalty": round(self.weights.w_resource_risk * r_risk, 4),
            "uncertainty_penalty": round(self.weights.w_uncertainty * u_val, 4),
            "raw_score": round(raw_score, 4),
            "normalized_score": normalized_score
        }

        # Generate transparent, explainable rationale
        reasons = []
        if c_threat >= 0.75:
            reasons.append(f"High threat confidence ({c_threat:.0%}) strongly supports action.")
        elif c_threat < 0.50:
            reasons.append(f"Low threat confidence ({c_threat:.0%}) dampens score.")

        if item.has_history and s_hist >= 0.70:
            reasons.append(f"Historical track record is favorable ({s_hist:.0%} success).")
        elif item.has_history and s_hist < 0.50:
            reasons.append(f"Past deployment failures for this action reduced reliability.")
        elif not item.has_history:
            reasons.append("No prior incident history; evaluated with uninformative prior.")

        if q_risk >= 0.40:
            reasons.append(f"High collateral QoS impact risk ({q_risk:.0%}) penalizes reliability.")
        if u_val >= 0.40:
            reasons.append(f"Model/telemetry uncertainty ({u_val:.0%}) imposes penalty.")

        explanation = " ".join(reasons) if reasons else "Action evaluation within standard nominal parameters."

        return ReliabilityResult(
            action_type=item.action_type,
            target_ip=item.target_ip,
            reliability_score=normalized_score,
            breakdown=breakdown,
            explanation=explanation
        )

