import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.session import SessionLocal
from app.models import AuditLog

client = TestClient(app)

def test_a_critical_dns_incident_creates_pending_approval():
    """
    Test A: Generate a critical DNS incident (10.0.0.53), evaluate candidates,
    and verify that policy constraint escalates to HUMAN_APPROVAL and creates a
    pending approval request with complete metadata in the Human Approval Center.
    """
    # 1. Ingest alert targeting Core DNS Server 10.0.0.53
    alert_resp = client.post("/api/alerts", json={
        "source": "SURICATA",
        "alert_type": "DNS_AMPLIFICATION_FLOOD",
        "severity": "CRITICAL",
        "source_ip": "198.51.100.42",
        "destination_ip": "10.0.0.53",
        "destination_port": 53,
        "protocol": "UDP",
        "signature": "ET DOS DNS Amplification Reflection Query Response Flood"
    })
    assert alert_resp.status_code == 200
    incident_id = alert_resp.json()["incident_id"]
    assert incident_id is not None

    # 2. Analyze threat
    analyze_resp = client.post(f"/api/incidents/{incident_id}/analyze")
    assert analyze_resp.status_code == 200

    # 3. Evaluate Candidate Responses
    eval_resp = client.post(f"/api/incidents/{incident_id}/evaluate-responses")
    assert eval_resp.status_code == 200
    candidates = eval_resp.json()
    assert len(candidates) >= 3

    # Every action on 10.0.0.53 must be ESCALATE / HUMAN_APPROVAL due to critical DNS QoS sensitivity
    for c in candidates:
        assert c["policy_status"] == "ESCALATE"
        assert c["recommended_mode"] == "HUMAN_APPROVAL"

    # Incident status must be PENDING_APPROVAL
    inc_resp = client.get(f"/api/incidents/{incident_id}")
    assert inc_resp.status_code == 200
    inc_data = inc_resp.json()
    assert inc_data["status"] == "PENDING_APPROVAL"
    assert inc_data["execution_mode"] == "HUMAN_APPROVAL"

    # 4. Human Approval Center query
    pending_resp = client.get("/api/approvals/pending")
    assert pending_resp.status_code == 200
    pending_list = pending_resp.json()
    target_appr = next((a for a in pending_list if a["incident_id"] == incident_id), None)
    assert target_appr is not None, "Pending approval request was not created in the database!"

    # Verify all metadata fields required by Task 1 & 2
    assert target_appr["status"] == "PENDING"
    assert target_appr["target_ip"] == "198.51.100.42"
    assert target_appr["threat_type"] == "DNS_AMPLIFICATION_FLOOD"
    assert target_appr["action_type"] in ["RATE_LIMIT", "BLOCK_IP", "ISOLATE_HOST"]
    assert target_appr["trust_score"] is not None
    assert target_appr["reliability_score"] is not None
    assert target_appr["policy_decision"] == "ESCALATE"
    assert "Critical DNS Infrastructure" in target_appr["escalation_reason"] or "DNS" in target_appr["escalation_reason"]

    # Verify Candidate Response table status
    cand_resp = client.get(f"/api/incidents/{incident_id}/candidates")
    assert cand_resp.status_code == 200
    cand_list = cand_resp.json()
    sel_cand = next((c for c in cand_list if c["id"] == inc_data["selected_response_id"]), None)
    assert sel_cand is not None
    assert sel_cand["candidate_status"] == "PENDING_APPROVAL"


def test_b_reject_approval_request_halts_execution():
    """
    Test B: Reject the pending request, verify database updates to REJECTED,
    verify that execution is blocked, and verify audit log record.
    """
    # 1. Ingest & evaluate critical incident
    alert_resp = client.post("/api/alerts", json={
        "source": "ZEEK",
        "alert_type": "DNS_CACHE_POISONING",
        "severity": "CRITICAL",
        "source_ip": "198.51.100.88",
        "destination_ip": "10.0.0.53",
        "destination_port": 53,
        "protocol": "UDP",
        "signature": "ET DNS Suspicious Transaction ID Mismatch"
    })
    incident_id = alert_resp.json()["incident_id"]
    client.post(f"/api/incidents/{incident_id}/analyze")
    client.post(f"/api/incidents/{incident_id}/evaluate-responses")

    # Retrieve pending approval
    pending_list = client.get("/api/approvals/pending").json()
    appr = next((a for a in pending_list if a["incident_id"] == incident_id), None)
    assert appr is not None

    # 2. Reject request
    reject_resp = client.post(f"/api/approvals/{appr['id']}/reject", json={
        "operator_comment": "SOC Analyst rejected: Risk of collateral disruption exceeds threat severity."
    })
    assert reject_resp.status_code == 200
    rejection_data = reject_resp.json()
    assert rejection_data["status"] == "REJECTED"
    assert rejection_data["operator_comment"] == "SOC Analyst rejected: Risk of collateral disruption exceeds threat severity."

    # 3. Verify incident status changed to REJECTED
    inc_check = client.get(f"/api/incidents/{incident_id}").json()
    assert inc_check["status"] == "REJECTED"

    # 4. Verify candidate table shows REJECTED status
    candidates = client.get(f"/api/incidents/{incident_id}/candidates").json()
    cand = next((c for c in candidates if c["id"] == appr["candidate_response_id"]), None)
    assert cand is not None
    assert cand["candidate_status"] == "REJECTED"

    # 5. Direct execution attempt must be blocked with HTTP 403 Forbidden
    exec_resp = client.post(f"/api/incidents/{incident_id}/execute", json={})
    assert exec_resp.status_code == 403
    assert "rejected" in exec_resp.json()["detail"].lower()

    # 6. Verify audit log entry exists
    db = SessionLocal()
    try:
        audit = db.query(AuditLog).filter(
            AuditLog.resource_type == "HUMAN_APPROVAL",
            AuditLog.resource_id == str(appr["id"])
        ).first()
        assert audit is not None
        assert audit.details["decision"] in ["REJECT", "REJECTED"]
        assert "SOC Analyst rejected" in audit.details["comment"]
    finally:
        db.close()


def test_c_approve_request_executes_successfully():
    """
    Test C: Generate incident requiring human approval, approve request in Human Approval Center,
    and verify authorized response executes successfully with audit logging.
    """
    # 1. Ingest & evaluate critical incident
    alert_resp = client.post("/api/alerts", json={
        "source": "SURICATA",
        "alert_type": "DNS_AMPLIFICATION_FLOOD",
        "severity": "CRITICAL",
        "source_ip": "198.51.100.99",
        "destination_ip": "10.0.0.53",
        "destination_port": 53,
        "protocol": "UDP",
        "signature": "ET DOS DNS Flood Attack"
    })
    incident_id = alert_resp.json()["incident_id"]
    client.post(f"/api/incidents/{incident_id}/analyze")
    client.post(f"/api/incidents/{incident_id}/evaluate-responses")

    # 2. Retrieve pending approval
    pending_list = client.get("/api/approvals/pending").json()
    appr = next((a for a in pending_list if a["incident_id"] == incident_id), None)
    assert appr is not None

    # 3. Operator approves request
    appr_resp = client.post(f"/api/approvals/{appr['id']}/approve", json={
        "operator_comment": "SOC Lead authorized rate-limiting on Core DNS port 53"
    })
    assert appr_resp.status_code == 200
    appr_data = appr_resp.json()
    assert appr_data["status"] == "APPROVED"

    # 4. Verify incident completed and response executed
    inc_check = client.get(f"/api/incidents/{incident_id}").json()
    assert inc_check["status"] in ["COMPLETED", "RESOLVED"]

    # 5. Verify candidates table marks the executed candidate as EXECUTED and others NOT_SELECTED
    candidates = client.get(f"/api/incidents/{incident_id}/candidates").json()
    for c in candidates:
        if c["id"] == inc_check["selected_response_id"]:
            assert c["candidate_status"] == "EXECUTED"
        else:
            assert c["candidate_status"] == "NOT_SELECTED"

    # 6. Verify audit logs for both approval and execution
    db = SessionLocal()
    try:
        appr_audit = db.query(AuditLog).filter(
            AuditLog.resource_type == "HUMAN_APPROVAL",
            AuditLog.resource_id == str(appr["id"])
        ).first()
        assert appr_audit is not None
        assert appr_audit.details["decision"] in ["APPROVE", "APPROVED"]

        exec_audits = db.query(AuditLog).filter(
            AuditLog.action == "RESPONSE_EXECUTION",
            AuditLog.resource_type == "RESPONSE_EXECUTION"
        ).all()
        assert any(a.details and a.details.get("incident_id") == incident_id for a in exec_audits)
    finally:
        db.close()


def test_d_direct_execution_without_approval_returns_403():
    """
    Test D: Try executing a HUMAN_APPROVAL action directly without prior human approval.
    Verify that system blocks execution with HTTP 403 Forbidden.
    """
    alert_resp = client.post("/api/alerts", json={
        "source": "SURICATA",
        "alert_type": "DNS_TUNNELING",
        "severity": "CRITICAL",
        "source_ip": "198.51.100.77",
        "destination_ip": "10.0.0.53",
        "destination_port": 53,
        "protocol": "UDP",
        "signature": "ET DNS Tunneling Exfiltration"
    })
    incident_id = alert_resp.json()["incident_id"]
    client.post(f"/api/incidents/{incident_id}/analyze")
    client.post(f"/api/incidents/{incident_id}/evaluate-responses")

    # Direct execution attempt without operator approval
    exec_resp = client.post(f"/api/incidents/{incident_id}/execute", json={})
    assert exec_resp.status_code == 403
    assert "approval" in exec_resp.json()["detail"].lower()


def test_e_safe_nominal_scenario_zero_touch_executes_without_waiting():
    """
    Test E: Generate an incident where a safe response is selected (e.g. Web Server 10.0.0.10).
    Verify that zero-touch automation executes normally without waiting for human approval,
    and does not pollute the Human Approval Center queue.
    """
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
    incident_id = alert_resp.json()["incident_id"]
    client.post(f"/api/incidents/{incident_id}/analyze")
    eval_resp = client.post(f"/api/incidents/{incident_id}/evaluate-responses")
    assert eval_resp.status_code == 200

    inc_check = client.get(f"/api/incidents/{incident_id}").json()
    assert inc_check["execution_mode"] == "ZERO_TOUCH"
    assert inc_check["status"] == "READY_TO_EXECUTE"

    # Pending queue should not have this incident
    pending_list = client.get("/api/approvals/pending").json()
    target_appr = next((a for a in pending_list if a["incident_id"] == incident_id), None)
    assert target_appr is None

    # Execute directly -> must succeed with 200 OK
    exec_resp = client.post(f"/api/incidents/{incident_id}/execute", json={})
    assert exec_resp.status_code == 200
    assert exec_resp.json()["execution"]["status"] == "SUCCESS"
