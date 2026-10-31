import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.response import CandidateResponse

client = TestClient(app)

def test_complete_end_to_end_orchestration_cycle():
    # 1. Ingest alert
    alert_resp = client.post("/api/alerts", json={
        "source": "SURICATA",
        "alert_type": "DOS_SYN_FLOOD",
        "severity": "HIGH",
        "source_ip": "10.0.0.99",
        "destination_ip": "10.0.0.10",
        "destination_port": 80,
        "protocol": "TCP",
        "signature": "ET DOS Possible SYN Flood against HTTP Server"
    })
    assert alert_resp.status_code == 200
    alert_data = alert_resp.json()
    incident_id = alert_data["incident_id"]
    assert incident_id is not None

    # 2. Analyze incident with Isolation Forest ML
    analyze_resp = client.post(f"/api/incidents/{incident_id}/analyze")
    assert analyze_resp.status_code == 200
    inc_data = analyze_resp.json()
    assert inc_data["status"] == "EVALUATING"
    assert inc_data["threat_confidence"] > 0.5
    assert inc_data["anomaly_score"] > 0.0

    # 3. Evaluate Candidate Responses (Engines 1, 2, 3, 4)
    eval_resp = client.post(f"/api/incidents/{incident_id}/evaluate-responses")
    assert eval_resp.status_code == 200
    candidates = eval_resp.json()
    assert len(candidates) >= 3

    # Check candidate types
    action_types = [c["action_type"] for c in candidates]
    assert "BLOCK_IP" in action_types
    assert "RATE_LIMIT" in action_types
    assert "ISOLATE_HOST" in action_types

    # Ensure all candidates have reliability, policy status, and trust score computed
    for c in candidates:
        assert 0.0 <= c["reliability_score"] <= 1.0
        assert c["policy_status"] in ["ALLOW", "REJECT", "RESTRICT", "ESCALATE"]
        assert 0.0 <= c["trust_score"] <= 1.0
        assert c["recommended_mode"] in ["ZERO_TOUCH", "GUARDED", "HUMAN_APPROVAL"]

    # 4. Check Incident Status & Mode
    inc_check = client.get(f"/api/incidents/{incident_id}").json()
    assert inc_check["selected_response_id"] is not None

    # If mode requires human approval, test that execution is blocked without approval
    if inc_check["execution_mode"] == "HUMAN_APPROVAL":
        # Direct execution attempt must fail with 403 Forbidden
        unauth_exec = client.post(f"/api/incidents/{incident_id}/execute", json={})
        assert unauth_exec.status_code == 403

        # Operator approves in Human Approval Center
        approvals = client.get("/api/approvals/pending").json()
        target_appr = next((a for a in approvals if a["incident_id"] == incident_id), None)
        assert target_appr is not None

        appr_res = client.post(f"/api/approvals/{target_appr['id']}/approve", json={
            "operator_comment": "SOC Analyst authorized after reviewing low-impact rate-limit proposal"
        })
        assert appr_res.status_code == 200

    # 5. Execute Approved Response
    exec_res = client.post(f"/api/incidents/{incident_id}/execute", json={})
    assert exec_res.status_code == 200
    exec_data = exec_res.json()
    assert exec_data["execution"]["status"] == "SUCCESS"
    assert exec_data["outcome"]["mitigation_pct"] >= 80.0
    assert exec_data["outcome"]["status"] in ["SUCCESS", "PARTIAL_SUCCESS"]

    # 6. Verify Outcome Evaluation is recorded in DB
    outcomes = client.get(f"/api/outcomes/{incident_id}").json()
    assert len(outcomes) >= 1
    assert outcomes[0]["actual_attack_reduction_pct"] >= 80.0

    # 7. Verify Experience Memory is updated
    experience = client.get("/api/experience").json()
    assert len(experience) >= 1
    recent_exp = next((e for e in experience if e["incident_id"] == incident_id), None)
    assert recent_exp is not None
    assert recent_exp["threat_type"] == "DOS_SYN_FLOOD"
    assert recent_exp["final_success"] is True

