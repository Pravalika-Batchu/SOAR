from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import math

@dataclass
class ExperienceQuery:
    threat_type: str
    target_ip: Optional[str] = None
    target_criticality: Optional[str] = None
    action_type: Optional[str] = None

@dataclass
class HistoricalPerformanceSummary:
    action_type: str
    sample_count: int
    success_rate: float # 0.0 to 1.0
    average_qos_impact: float # 0.0 to 1.0
    human_override_rate: float # 0.0 to 1.0
    failure_rate: float # 0.0 to 1.0
    adaptation_penalty: float # Reduction to apply to reliability / trust
    explanation: str

class ExperienceMemoryEngine:
    """
    Component 6: Experience Memory
    Stores prior incident outcomes and performs case-based reasoning (CBR) retrieval.
    Quantifies historical success rates and dynamically adapts future reliability
    scores and autonomy trust thresholds based on past empirical outcomes.
    """
    def __init__(self, memory_store: Optional[List[Dict[str, Any]]] = None):
        # In-memory working buffer or synced with SQLAlchemy experience_records table
        self.records: List[Dict[str, Any]] = memory_store or []

    def record_experience(self, record: Dict[str, Any]):
        """Append a completed incident outcome record to experience memory."""
        self.records.append(record)

    def retrieve_similar_cases(self, query: ExperienceQuery, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieves past cases matching threat type and context similarity.
        Computes cosine/Jaccard-like context similarity score.
        """
        matched = []
        for r in self.records:
            # Threat type match is primary filter
            if r.get("threat_type") != query.threat_type:
                continue

            score = 1.0
            if query.action_type and r.get("selected_action") == query.action_type:
                score += 0.5
            
            ctx = r.get("network_context", {})
            if query.target_criticality and ctx.get("criticality") == query.target_criticality:
                score += 0.5

            matched.append((score, r))

        # Sort by relevance score descending
        matched.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in matched[:limit]]

    def get_historical_performance(self, action_type: str, threat_type: str) -> HistoricalPerformanceSummary:
        """
        Calculates empirical historical success rate, QoS risk, and adaptation penalty
        for an action applied to a specific threat type.
        """
        relevant = [
            r for r in self.records 
            if r.get("selected_action") == action_type and r.get("threat_type") == threat_type
        ]

        if not relevant:
            # Neutral Bayesian prior: 0.70 success rate for fresh lab conditions with 0 adaptation penalty
            return HistoricalPerformanceSummary(
                action_type=action_type,
                sample_count=0,
                success_rate=0.70,
                average_qos_impact=0.10,
                human_override_rate=0.0,
                failure_rate=0.0,
                adaptation_penalty=0.0,
                explanation=f"No empirical history for action '{action_type}' against '{threat_type}'. Assigned baseline uninformative prior."
            )

        n = len(relevant)
        successes = sum(1 for r in relevant if r.get("final_success", False))
        overrides = sum(1 for r in relevant if r.get("human_override", False))
        failures = sum(1 for r in relevant if not r.get("final_success", False))
        
        qos_impacts = [r.get("qos_impact", 0.0) for r in relevant]
        avg_qos_impact = (sum(qos_impacts) / n) if n > 0 else 0.0
        
        success_rate = round(successes / n, 4)
        failure_rate = round(failures / n, 4)
        override_rate = round(overrides / n, 4)

        # Dynamic Adaptation Penalty:
        # If past instances suffered high QoS degradation or failed, calculate a dampening penalty
        # Penalty = (Failure_Rate * 0.25) + (Average_QoS_Impact * 0.15)
        adaptation_penalty = round((failure_rate * 0.25) + (avg_qos_impact * 0.15), 4)

        reasons = []
        if success_rate >= 0.80:
            reasons.append(f"Highly reliable history ({success_rate:.0%} success across {n} incidents).")
        elif success_rate < 0.60:
            reasons.append(f"Unfavorable historical efficacy ({success_rate:.0%} success).")

        if avg_qos_impact >= 0.25:
            reasons.append(f"Previously caused notable collateral QoS impact (avg {avg_qos_impact:.1%}). Penalty applied: -{adaptation_penalty:.2f}.")

        if override_rate > 0.20:
            reasons.append(f"Operator overrode or rejected this action in {override_rate:.0%} of historical cases.")

        explanation = " ".join(reasons) if reasons else f"Based on {n} past incidents."

        return HistoricalPerformanceSummary(
            action_type=action_type,
            sample_count=n,
            success_rate=success_rate,
            average_qos_impact=round(avg_qos_impact, 4),
            human_override_rate=override_rate,
            failure_rate=failure_rate,
            adaptation_penalty=adaptation_penalty,
            explanation=explanation
        )

