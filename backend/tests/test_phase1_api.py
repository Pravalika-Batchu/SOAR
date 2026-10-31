import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["zero_cost_compliant"] is True

def test_auth_login():
    response = client.post("/api/auth/login", json={
        "username": "admin",
        "password": "adminpassword123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "ADMIN"

def test_get_policies():
    response = client.get("/api/policies")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 4
    # Ensure critical safety policy exists
    critical_policy = next((p for p in data if "Critical" in p["name"]), None)
    assert critical_policy is not None
    assert critical_policy["is_mandatory"] is True

def test_get_system_topology():
    response = client.get("/api/system/topology")
    assert response.status_code == 200
    data = response.json()
    assert len(data["nodes"]) > 0
    assert len(data["assets"]) > 0

def test_create_and_fetch_alert():
    alert_payload = {
        "source": "TEST_GENERATOR",
        "alert_type": "DOS_SYN_FLOOD",
        "severity": "HIGH",
        "source_ip": "10.0.0.99",
        "destination_ip": "10.0.0.10",
        "destination_port": 80,
        "protocol": "TCP",
        "signature": "ET SCAN Potential SYN Flood"
    }
    response = client.post("/api/alerts", json=alert_payload)
    assert response.status_code == 200
    alert_data = response.json()
    assert alert_data["source_ip"] == "10.0.0.99"
    assert alert_data["incident_id"] is not None

    # Verify incident auto-creation
    inc_response = client.get(f"/api/incidents/{alert_data['incident_id']}")
    assert inc_response.status_code == 200
    inc_data = inc_response.json()
    assert inc_data["threat_type"] == "DOS_SYN_FLOOD"
    assert inc_data["destination_ip"] == "10.0.0.10"

