from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from enum import Enum

class PolicyDecisionEnum(str, Enum):
    ALLOW = "ALLOW"
    REJECT = "REJECT"
    RESTRICT = "RESTRICT"
    ESCALATE = "ESCALATE"

@dataclass
class PolicyEvaluationResult:
    action_type: str
    target_ip: str
    decision: PolicyDecisionEnum
    is_mandatory_override: bool
    violated_rules: List[str]
    restriction_params: Optional[Dict[str, Any]] = None
    explanation: str = ""

@dataclass
class PolicyContext:
    target_criticality: str # "CRITICAL", "HIGH", "MEDIUM", "LOW"
    target_service: Optional[str] = None
    qos_sensitivity: float = 0.5
    predicted_qos_risk: float = 0.1
    uncertainty: float = 0.1
    is_gateway_or_broadcast: bool = False
    active_policies: List[Dict[str, Any]] = field(default_factory=list)

class PolicyConstraintEngine:
    """
    Component 2: Policy & Constraint Engine
    Validates candidate responses against operational constraints, SLA thresholds,
    and asset criticality rules. Enforces mandatory safety overrides.
    """
    def evaluate_candidate(
        self,
        action_type: str,
        target_ip: str,
        context: PolicyContext
    ) -> PolicyEvaluationResult:
        violations: List[str] = []
        mandatory_override = False
        decision = PolicyDecisionEnum.ALLOW
        restriction_params = {}
        explanations: List[str] = []

        # 1. Hard invariant: Never block or isolate core gateway or broadcast IP
        if context.is_gateway_or_broadcast or target_ip in ["10.0.0.200", "10.0.0.255", "10.0.0.1"]:
            violations.append("Core Gateway / Broadcast Shielding")
            return PolicyEvaluationResult(
                action_type=action_type,
                target_ip=target_ip,
                decision=PolicyDecisionEnum.REJECT,
                is_mandatory_override=True,
                violated_rules=violations,
                explanation=f"Target {target_ip} is essential infrastructure. Disruptive actions strictly prohibited by mandatory safety policy."
            )

        # 2. Ultra-Critical Infrastructure SLA & DNS Guardrail (QoS-Sensitive Scenario):
        # When an asset has ultra-high QoS sensitivity (>= 0.95) or service_type contains 'DNS' / core resolver,
        # any active mitigation (even rate-limiting or blocking) risks dropping enterprise-wide legitimate name lookups.
        # Mandatory policy requires explicit human approval (ESCALATE) for all candidate actions.
        is_dns_or_ultra_critical = (
            (context.target_criticality == "CRITICAL" and context.qos_sensitivity >= 0.95) or
            (context.target_service and "DNS" in context.target_service.upper())
        )
        if is_dns_or_ultra_critical:
            violations.append("Core DNS / Strict SLA Infrastructure Guardrail")
            mandatory_override = True
            decision = PolicyDecisionEnum.ESCALATE
            explanations.append(
                f"Target hosts critical service '{context.target_service or 'Core DNS'}' with strict SLA sensitivity ({context.qos_sensitivity:.0%}). "
                f"Autonomous {action_type} is prohibited by mandatory safety policy to prevent service interruption; requires explicit human authorization."
            )

        # 3. Critical Asset Complete Isolation Guard:
        # Never allow autonomous complete host isolation of ANY critical server (e.g. Web, DB)
        elif context.target_criticality == "CRITICAL" and action_type in ["ISOLATE_HOST"]:
            violations.append("Critical Asset Autonomous Isolation Guard")
            mandatory_override = True
            decision = PolicyDecisionEnum.ESCALATE
            explanations.append(
                f"Target hosts critical service '{context.target_service or 'infrastructure'}'. "
                f"Autonomous {action_type} is barred to prevent catastrophic service outage; requires explicit human authorization."
            )

        # 4. QoS Risk Guardrails: If predicted QoS risk is high on sensitive service, downgrade action to rate limiting
        if decision == PolicyDecisionEnum.ALLOW and context.predicted_qos_risk > 0.40 and context.qos_sensitivity >= 0.70:
            if action_type in ["BLOCK_IP", "ISOLATE_HOST"]:
                violations.append("QoS Disruption SLA Threshold Exceeded")
                decision = PolicyDecisionEnum.RESTRICT
                restriction_params = {"enforced_action": "RATE_LIMIT", "max_rate_kbps": 250, "duration_sec": 180}
                explanations.append(
                    f"High predicted QoS impact ({context.predicted_qos_risk:.0%}) on sensitive asset. "
                    f"Action restricted to reversible, non-disruptive rate-limiting (250 kbps)."
                )

        # 5. Uncertainty Governor: High uncertainty (>0.45) cannot proceed without operator review
        if context.uncertainty > 0.45 and decision not in [PolicyDecisionEnum.REJECT, PolicyDecisionEnum.ESCALATE]:
            violations.append("Epistemic Uncertainty Governor")
            decision = PolicyDecisionEnum.ESCALATE
            mandatory_override = True
            explanations.append(
                f"High epistemic uncertainty ({context.uncertainty:.0%}) mandates SOC analyst review before response dispatch."
            )

        # 6. Check additional dynamic rules configured in database
        for pol in context.active_policies:
            c = pol.get("condition_json", {})
            enforcement = pol.get("enforcement_action", "ESCALATE")
            is_mand = pol.get("is_mandatory", True)
            p_name = pol.get("name", "Custom Policy")

            # Check target criticality rule
            if "target_criticality" in c and c["target_criticality"] == context.target_criticality:
                if "disallowed_action" in c and c["disallowed_action"] == action_type:
                    violations.append(p_name)
                    if is_mand:
                        mandatory_override = True
                    decision = PolicyDecisionEnum(enforcement)
                    explanations.append(f"Policy '{p_name}' enforced: {enforcement}.")

            # Check min_qos_sensitivity rule
            if "min_qos_sensitivity_for_escalation" in c and context.qos_sensitivity >= c["min_qos_sensitivity_for_escalation"]:
                violations.append(p_name)
                if is_mand:
                    mandatory_override = True
                decision = PolicyDecisionEnum(enforcement)
                explanations.append(f"Policy '{p_name}' enforced: {enforcement}.")

        final_explanation = " ".join(explanations) if explanations else "Action complies with all operational safety and QoS constraints."

        return PolicyEvaluationResult(
            action_type=action_type,
            target_ip=target_ip,
            decision=decision,
            is_mandatory_override=mandatory_override,
            violated_rules=violations,
            restriction_params=restriction_params if restriction_params else None,
            explanation=final_explanation
        )
