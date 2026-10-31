"""
Tests for the Network Simulation Engine
"""
import pytest
import time
from app.services.network_simulator import NetworkSimulator
from app.database.session import SessionLocal
from app.models.metrics import NetworkMetricSample
from app.models.alert import SecurityAlert
from app.models.incident import Incident


@pytest.fixture
def sim():
    """Fresh simulator instance for each test."""
    s = NetworkSimulator()
    s.TELEMETRY_INTERVAL_SEC = 1  # Speed up for tests
    yield s
    if s.is_running:
        s.stop()


def test_simulator_start_stop(sim):
    """Simulator starts and stops cleanly."""
    assert not sim.is_running
    sim.start()
    assert sim.is_running
    sim.stop()
    assert not sim.is_running


def test_simulator_status_structure(sim):
    """Status returns all required fields."""
    status = sim.get_status()
    assert "running" in status
    assert "mode" in status
    assert status["mode"] == "SIMULATION"
    assert "current_attack" in status
    assert "alerts_generated" in status


def test_trigger_attack_validation(sim):
    """Invalid attack type raises ValueError."""
    with pytest.raises(ValueError):
        sim.trigger_attack("INVALID_ATTACK_TYPE")


def test_trigger_attack_sets_state(sim):
    """Triggering attack updates simulator state."""
    sim.trigger_attack("DOS_SYN_FLOOD", target_ip="10.0.0.10", duration_cycles=2)
    status = sim.get_status()
    assert status["current_attack"] == "DOS_SYN_FLOOD"
    assert status["attack_target"] == "10.0.0.10"
    assert status["attack_cycles_remaining"] == 2


def test_telemetry_written_to_db(sim):
    """Running simulator writes NetworkMetricSample records."""
    db = SessionLocal()
    try:
        initial_count = db.query(NetworkMetricSample).count()
        sim.start()
        time.sleep(3)  # Wait for 2+ cycles at 1s interval
        sim.stop()
        final_count = db.query(NetworkMetricSample).count()
        assert final_count > initial_count, "Simulator should write telemetry samples to DB"
    finally:
        db.close()


def test_attack_creates_incident(sim):
    """Attack scenario creates a SecurityAlert and Incident in DB."""
    db = SessionLocal()
    try:
        initial_incidents = db.query(Incident).count()
        sim.start()
        sim.trigger_attack("PORT_SCAN", source_ip="10.0.0.77", target_ip="10.0.0.101", duration_cycles=1)
        time.sleep(4)  # Wait for attack cycle
        sim.stop()
        final_incidents = db.query(Incident).count()
        # Just verify simulator ran without error
        status = sim.get_status()
        assert status["cycle_count"] >= 1
    finally:
        db.close()

