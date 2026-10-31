import pytest
from app.engines import (
    ResponseReliabilityEngine,
    CandidateEvaluationInput,
    ReliabilityWeights,
    PolicyConstraintEngine,
    PolicyContext,
    PolicyDecisionEnum,
    AutonomyTrustEngine,
    TrustEvaluationInput,
    DynamicAutonomyController,
    AutonomyExecutionMode,
    OutcomeEvaluationEngine,
    TelemetrySnapshot,
    PredictedOutcome,
    ExperienceMemoryEngine,
    ExperienceQuery
)

# 1. Test Component 1: Response Reliability Engine
def test_response_reliability_engine_scoring_variations():
    engine = ResponseReliabilityEngine()

    # Highly reliable candidate (high confidence, strong history, low risk)
    good_cand = CandidateEvaluationInput(
        action_type="RATE_LIMIT",
        target_ip="10.0.0.99",
        threat_confidence=0.90,
        historical_success_rate=0.85,
        policy_fit_score=0.90,
        predicted_qos_risk=0.10,
        resource_risk=0.05,
        uncertainty=0.10
    )
    good_res = engine.evaluate(good_cand)

    # Poor candidate (low confidence, poor history, high QoS risk)
    risky_cand = CandidateEvaluationInput(
        action_type="ISOLATE_HOST",
        target_ip="10.0.0.99",
        threat_confidence=0.40,
        historical_success_rate=0.30,
        policy_fit_score=0.50,
        predicted_qos_risk=0.60,
        resource_risk=0.50,
        uncertainty=0.50
    )
    risky_res = engine.evaluate(risky_cand)

    assert good_res.reliability_score > risky_res.reliability_score
    assert 0.0 <= good_res.reliability_score <= 1.0
    assert 0.0 <= risky_res.reliability_score <= 1.0
    assert "High threat confidence" in good_res.explanation
    assert good_res.breakdown["threat_confidence_term"] > risky_res.breakdown["threat_confidence_term"]

# 2. Test Component 2: Policy / Constraint Engine
def test_policy_constraint_engine_safety_overrides():
    engine = PolicyConstraintEngine()

    # Test hard rejection of gateway / broadcast IPs
    gw_ctx = PolicyContext(target_criticality="CRITICAL", is_gateway_or_broadcast=True)
    gw_res = engine.evaluate_candidate("BLOCK_IP", "10.0.0.200", gw_ctx)
    assert gw_res.decision == PolicyDecisionEnum.REJECT
    assert gw_res.is_mandatory_override is True

    # Test escalation on critical asset isolation
    crit_ctx = PolicyContext(target_criticality="CRITICAL", target_service="DNS Resolver", qos_sensitivity=0.95)
    crit_res = engine.evaluate_candidate("ISOLATE_HOST", "10.0.0.53", crit_ctx)
    assert crit_res.decision == PolicyDecisionEnum.ESCALATE
    assert crit_res.is_mandatory_override is True

    # Test QoS restriction downgrade
    qos_ctx = PolicyContext(
        target_criticality="HIGH",
        target_service="Web Portal",
        qos_sensitivity=0.85,
        predicted_qos_risk=0.55
    )
    qos_res = engine.evaluate_candidate("BLOCK_IP", "10.0.0.10", qos_ctx)
    assert qos_res.decision == PolicyDecisionEnum.RESTRICT
    assert qos_res.restriction_params["enforced_action"] == "RATE_LIMIT"

    # Test nominal allow on non-critical client
    norm_ctx = PolicyContext(target_criticality="LOW", qos_sensitivity=0.20, predicted_qos_risk=0.05)
    norm_res = engine.evaluate_candidate("RATE_LIMIT", "10.0.0.102", norm_ctx)
    assert norm_res.decision == PolicyDecisionEnum.ALLOW
    assert norm_res.is_mandatory_override is False

# 3. Test Component 3: Autonomy Trust Engine
def test_autonomy_trust_engine_scoring():
    engine = AutonomyTrustEngine()

    # High trust scenario
    high_input = TrustEvaluationInput(
        reliability_score=0.92,
        threat_confidence=0.90,
        qos_risk=0.10,
        uncertainty=0.10,
        historical_failure_rate=0.0,
        policy_status="ALLOW"
    )
    high_res = engine.calculate_trust(high_input)
    assert high_res.trust_score >= 0.85
    assert high_res.recommended_mode == "ZERO_TOUCH"

    # Low trust with uncertainty and historical failures
    low_input = TrustEvaluationInput(
        reliability_score=0.50,
        threat_confidence=0.60,
        qos_risk=0.45,
        uncertainty=0.50,
        historical_failure_rate=0.40,
        human_override_rate=0.30,
        policy_status="ALLOW"
    )
    low_res = engine.calculate_trust(low_input)
    assert low_res.trust_score < 0.55
    assert low_res.recommended_mode == "HUMAN_APPROVAL"
    assert low_res.historical_failure_penalty > 0

# 4. Test Component 4: Dynamic Autonomy Controller
def test_dynamic_autonomy_controller_modes():
    controller = DynamicAutonomyController()

    # High trust + ALLOW -> ZERO_TOUCH
    d1 = controller.determine_autonomy_mode(0.90, PolicyDecisionEnum.ALLOW)
    assert d1.mode == AutonomyExecutionMode.ZERO_TOUCH
    assert d1.requires_operator_action is False

    # Moderate trust -> GUARDED
    d2 = controller.determine_autonomy_mode(0.70, PolicyDecisionEnum.ALLOW)
    assert d2.mode == AutonomyExecutionMode.GUARDED
    assert d2.requires_operator_action is False

    # High trust, but Policy is RESTRICT -> Must be forced to GUARDED
    d3 = controller.determine_autonomy_mode(0.95, PolicyDecisionEnum.RESTRICT)
    assert d3.mode == AutonomyExecutionMode.GUARDED

    # High trust, but Policy is ESCALATE -> Must be forced to HUMAN_APPROVAL
    d4 = controller.determine_autonomy_mode(0.95, PolicyDecisionEnum.ESCALATE, is_mandatory_override=True)
    assert d4.mode == AutonomyExecutionMode.HUMAN_APPROVAL
    assert d4.requires_operator_action is True

    # Low trust -> HUMAN_APPROVAL
    d5 = controller.determine_autonomy_mode(0.40, PolicyDecisionEnum.ALLOW)
    assert d5.mode == AutonomyExecutionMode.HUMAN_APPROVAL
    assert d5.requires_operator_action is True

# 5. Test Component 5: Outcome Evaluation Engine
def test_outcome_evaluation_mitigation_vs_collateral():
    engine = OutcomeEvaluationEngine()

    pre = TelemetrySnapshot(
        attack_pps=50000.0,
        legitimate_throughput_mbps=100.0,
        latency_ms=2.0,
        packet_loss_pct=0.5
    )

    # Scenario A: Great mitigation, no collateral
    post_good = TelemetrySnapshot(
        attack_pps=500.0,
        legitimate_throughput_mbps=98.0,
        latency_ms=2.2,
        packet_loss_pct=0.8
    )
    res_good = engine.evaluate(pre, post_good)
    assert res_good.actual_attack_reduction_pct >= 95.0
    assert res_good.actual_qos_impact_pct <= 5.0
    assert res_good.classification == "SUCCESS"
    assert res_good.security_response_succeeded is True

    # Scenario B: Good mitigation, but high collateral damage
    post_collateral = TelemetrySnapshot(
        attack_pps=100.0,
        legitimate_throughput_mbps=30.0, # Legitimate users dropped by 70%!
        latency_ms=45.0,
        packet_loss_pct=25.0
    )
    res_collateral = engine.evaluate(pre, post_collateral)
    assert res_collateral.actual_attack_reduction_pct >= 95.0
    assert res_collateral.actual_qos_impact_pct >= 50.0
    assert res_collateral.classification == "FAILED_COLLATERAL"
    assert res_collateral.security_response_succeeded is False

# 6. Test Component 6: Experience Memory
def test_experience_memory_adaptation():
    memory = ExperienceMemoryEngine()

    # Initially empty: returns default prior
    perf_init = memory.get_historical_performance("RATE_LIMIT", "DOS_SYN_FLOOD")
    assert perf_init.sample_count == 0
    assert perf_init.adaptation_penalty == 0.0

    # Simulate past poor outcomes where RATE_LIMIT failed with high collateral impact
    memory.record_experience({
        "incident_id": 1,
        "threat_type": "DOS_SYN_FLOOD",
        "selected_action": "RATE_LIMIT",
        "qos_impact": 0.45,
        "human_override": True,
        "final_success": False
    })
    memory.record_experience({
        "incident_id": 2,
        "threat_type": "DOS_SYN_FLOOD",
        "selected_action": "RATE_LIMIT",
        "qos_impact": 0.40,
        "human_override": False,
        "final_success": False
    })

    # Query historical performance again
    perf_updated = memory.get_historical_performance("RATE_LIMIT", "DOS_SYN_FLOOD")
    assert perf_updated.sample_count == 2
    assert perf_updated.failure_rate == 1.0
    assert perf_updated.adaptation_penalty > 0.20 # Adaptation penalty is computed!
    assert "Unfavorable historical efficacy" in perf_updated.explanation

