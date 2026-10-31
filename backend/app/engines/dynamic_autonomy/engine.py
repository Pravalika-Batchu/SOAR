from dataclasses import dataclass
from typing import Optional, Dict, Any
from enum import Enum
from app.engines.policy_constraint.engine import PolicyDecisionEnum

class AutonomyExecutionMode(str, Enum):
    ZERO_TOUCH = "ZERO_TOUCH"
    GUARDED = "GUARDED"
    HUMAN_APPROVAL = "HUMAN_APPROVAL"

@dataclass
class AutonomyControllerConfig:
    threshold_high: float = 0.85
    threshold_low: float = 0.55

@dataclass
class AutonomyDecision:
    mode: AutonomyExecutionMode
    trust_score: float
    policy_decision: PolicyDecisionEnum
    is_mandatory_override_applied: bool
    requires_operator_action: bool
    execution_parameters: Dict[str, Any]
    rationale: str

class DynamicAutonomyController:
    """
    Component 4: Dynamic Autonomy Controller
    Synthesizes the Autonomy Trust Score with Policy / Constraint Engine decisions
    to select the final execution mode: ZERO_TOUCH, GUARDED, or HUMAN_APPROVAL.
    
    Mandatory safety constraints ALWAYS strictly override trust scores.
    """
    def __init__(self, config: Optional[AutonomyControllerConfig] = None):
        self.config = config or AutonomyControllerConfig()

    def determine_autonomy_mode(
        self,
        trust_score: float,
        policy_decision: PolicyDecisionEnum,
        is_mandatory_override: bool = False,
        restriction_params: Optional[Dict[str, Any]] = None,
        action_type: str = "BLOCK_IP"
    ) -> AutonomyDecision:
        t_high = self.config.threshold_high
        t_low = self.config.threshold_low
        params = restriction_params.copy() if restriction_params else {}

        # Rule 1: Hard Policy Rejection always halts execution completely
        if policy_decision == PolicyDecisionEnum.REJECT:
            return AutonomyDecision(
                mode=AutonomyExecutionMode.HUMAN_APPROVAL,
                trust_score=trust_score,
                policy_decision=policy_decision,
                is_mandatory_override_applied=True,
                requires_operator_action=True,
                execution_parameters={},
                rationale=f"Mandatory safety policy REJECT strictly halts automated execution regardless of trust score ({trust_score:.2f})."
            )

        # Rule 2: Mandatory Policy Escalation always requires operator approval
        if is_mandatory_override or policy_decision == PolicyDecisionEnum.ESCALATE:
            return AutonomyDecision(
                mode=AutonomyExecutionMode.HUMAN_APPROVAL,
                trust_score=trust_score,
                policy_decision=policy_decision,
                is_mandatory_override_applied=True,
                requires_operator_action=True,
                execution_parameters=params,
                rationale=f"Mandatory safety policy override triggered escalation. SOC analyst approval is required despite trust score ({trust_score:.2f})."
            )

        # Rule 3: Policy Restriction forces Guarded mode with guardrail parameters
        if policy_decision == PolicyDecisionEnum.RESTRICT:
            if "duration_sec" not in params:
                params["duration_sec"] = 180
            if "max_rate_kbps" not in params:
                params["max_rate_kbps"] = 500
            params["guarded_rollback_enabled"] = True

            return AutonomyDecision(
                mode=AutonomyExecutionMode.GUARDED,
                trust_score=trust_score,
                policy_decision=policy_decision,
                is_mandatory_override_applied=False,
                requires_operator_action=False,
                execution_parameters=params,
                rationale=f"Policy RESTRICT enforced Guarded Automation with time-limited rollback ({params.get('duration_sec')}s) and rate throttling."
            )

        # Rule 4: Standard Trust Thresholding when Policy is ALLOW
        if trust_score >= t_high and policy_decision == PolicyDecisionEnum.ALLOW:
            # Zero-Touch Autonomous Execution
            params["autonomous"] = True
            params["monitoring_interval_sec"] = 10
            return AutonomyDecision(
                mode=AutonomyExecutionMode.ZERO_TOUCH,
                trust_score=trust_score,
                policy_decision=policy_decision,
                is_mandatory_override_applied=False,
                requires_operator_action=False,
                execution_parameters=params,
                rationale=f"High trust ({trust_score:.2f} >= {t_high}) and complete policy compliance. System authorized for Zero-Touch autonomous execution."
            )
        elif trust_score >= t_low:
            # Guarded Automation
            params["guarded_rollback_enabled"] = True
            params["duration_sec"] = 300
            params["extra_monitoring"] = True
            return AutonomyDecision(
                mode=AutonomyExecutionMode.GUARDED,
                trust_score=trust_score,
                policy_decision=policy_decision,
                is_mandatory_override_applied=False,
                requires_operator_action=False,
                execution_parameters=params,
                rationale=f"Moderate trust ({t_low} <= {trust_score:.2f} < {t_high}). System authorized for Guarded Automation with strict telemetry monitoring."
            )
        else:
            # Human Approval
            return AutonomyDecision(
                mode=AutonomyExecutionMode.HUMAN_APPROVAL,
                trust_score=trust_score,
                policy_decision=policy_decision,
                is_mandatory_override_applied=False,
                requires_operator_action=True,
                execution_parameters=params,
                rationale=f"Insufficient trust ({trust_score:.2f} < {t_low}). Incident routed to Human Approval Center for SOC verification."
            )

