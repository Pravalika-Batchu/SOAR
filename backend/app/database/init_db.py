import json
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session
from app.database.session import Base, engine, SessionLocal
from app.models.user import User
from app.models.asset import Asset, NetworkTopologyNode
from app.models.policy import PolicyRule
from app.core.security import get_password_hash

def migrate_db():
    """Dynamically applies schema migrations for newly added model columns in SQLite/Postgres."""
    inspector = inspect(engine)
    if "human_approvals" in inspector.get_table_names():
        columns = [c["name"] for c in inspector.get_columns("human_approvals")]
        with engine.connect() as conn:
            if "action_type" not in columns:
                conn.execute(text("ALTER TABLE human_approvals ADD COLUMN action_type VARCHAR(50);"))
            if "target_ip" not in columns:
                conn.execute(text("ALTER TABLE human_approvals ADD COLUMN target_ip VARCHAR(45);"))
            if "threat_type" not in columns:
                conn.execute(text("ALTER TABLE human_approvals ADD COLUMN threat_type VARCHAR(100);"))
            if "trust_score" not in columns:
                conn.execute(text("ALTER TABLE human_approvals ADD COLUMN trust_score FLOAT DEFAULT 0.0;"))
            if "reliability_score" not in columns:
                conn.execute(text("ALTER TABLE human_approvals ADD COLUMN reliability_score FLOAT DEFAULT 0.0;"))
            if "policy_decision" not in columns:
                conn.execute(text("ALTER TABLE human_approvals ADD COLUMN policy_decision VARCHAR(20) DEFAULT 'ESCALATE';"))
            if "escalation_reason" not in columns:
                conn.execute(text("ALTER TABLE human_approvals ADD COLUMN escalation_reason TEXT;"))
            conn.commit()

def init_db():
    Base.metadata.create_all(bind=engine)
    migrate_db()
    db = SessionLocal()
    try:
        # 1. Seed Users
        if not db.query(User).filter(User.username == "admin").first():
            admin = User(
                username="admin",
                email="admin@trustsoar.local",
                hashed_password=get_password_hash("adminpassword123"),
                role="ADMIN",
                is_active=True
            )
            analyst = User(
                username="analyst",
                email="analyst@trustsoar.local",
                hashed_password=get_password_hash("analystpassword123"),
                role="ANALYST",
                is_active=True
            )
            db.add_all([admin, analyst])
            db.commit()

        # 2. Seed Assets
        if db.query(Asset).count() == 0:
            assets = [
                Asset(
                    ip_address="10.0.0.10",
                    hostname="web-server-01",
                    subnet="10.0.0.0/24",
                    criticality="CRITICAL",
                    service_type="Web Portal (HTTP/S)",
                    qos_sensitivity=0.85 # High sensitivity, safe for rate limiting of attackers
                ),
                Asset(
                    ip_address="10.0.0.53",
                    hostname="dns-core-server",
                    subnet="10.0.0.0/24",
                    criticality="CRITICAL",
                    service_type="DNS Resolver",
                    qos_sensitivity=0.95 # Ultra-critical DNS: any intervention mandates human approval
                ),
                Asset(
                    ip_address="10.0.0.20",
                    hostname="db-prod-cluster",
                    subnet="10.0.0.0/24",
                    criticality="HIGH",
                    service_type="Database",
                    qos_sensitivity=0.80
                ),
                Asset(
                    ip_address="10.0.0.101",
                    hostname="workstation-corp-01",
                    subnet="10.0.0.0/24",
                    criticality="LOW",
                    service_type="Internal Desktop",
                    qos_sensitivity=0.30
                ),
                Asset(
                    ip_address="10.0.0.102",
                    hostname="client-testbed-node",
                    subnet="10.0.0.0/24",
                    criticality="LOW",
                    service_type="Client / Test Agent",
                    qos_sensitivity=0.25
                ),
                Asset(
                    ip_address="10.0.0.200",
                    hostname="external-gateway-router",
                    subnet="10.0.0.0/24",
                    criticality="HIGH",
                    service_type="Gateway",
                    qos_sensitivity=0.85
                )
            ]
            db.add_all(assets)
            db.commit()

        # 3. Seed Topology Nodes
        if db.query(NetworkTopologyNode).count() == 0:
            nodes = [
                NetworkTopologyNode(node_id="s1", node_type="SWITCH", status="ONLINE", metadata_json={"dpid": "0000000000000001", "ports": [1, 2, 3, 4]}),
                NetworkTopologyNode(node_id="s2", node_type="SWITCH", status="ONLINE", metadata_json={"dpid": "0000000000000002", "ports": [1, 2, 3]}),
                NetworkTopologyNode(node_id="h1_web", node_type="HOST", ip_address="10.0.0.10", connected_switch="s1", port_number=1, status="ONLINE"),
                NetworkTopologyNode(node_id="h2_dns", node_type="HOST", ip_address="10.0.0.53", connected_switch="s1", port_number=2, status="ONLINE"),
                NetworkTopologyNode(node_id="h3_db", node_type="HOST", ip_address="10.0.0.20", connected_switch="s1", port_number=3, status="ONLINE"),
                NetworkTopologyNode(node_id="h4_client", node_type="HOST", ip_address="10.0.0.101", connected_switch="s2", port_number=1, status="ONLINE"),
                NetworkTopologyNode(node_id="h5_attacker", node_type="HOST", ip_address="10.0.0.99", connected_switch="s2", port_number=2, status="ONLINE")
            ]
            db.add_all(nodes)
            db.commit()

        # 4. Seed Mandatory Research & Safety Policies
        if db.query(PolicyRule).count() == 0:
            policies = [
                PolicyRule(
                    name="Protect Critical Asset From Autonomous Isolation",
                    description="Never allow autonomous isolation of critical infrastructure (e.g. Web/DNS/DB servers). Escalates to human approval.",
                    rule_type="ASSET_PROTECTION",
                    condition_json={"target_criticality": "CRITICAL", "disallowed_action": "ISOLATE_HOST"},
                    enforcement_action="ESCALATE",
                    is_mandatory=True,
                    priority=1
                ),
                PolicyRule(
                    name="Core DNS / Strict SLA Infrastructure Guardrail",
                    description="When target is a Core DNS resolver or has QoS sensitivity >= 0.95, any automated mitigation escalates to human approval.",
                    rule_type="QOS_GUARDRAIL",
                    condition_json={"min_qos_sensitivity_for_escalation": 0.95, "protected_service": "DNS"},
                    enforcement_action="ESCALATE",
                    is_mandatory=True,
                    priority=1
                ),
                PolicyRule(
                    name="Broadcast & Gateway Shielding",
                    description="Hard block any action that isolates or rate-limits network broadcast or default gateway.",
                    rule_type="ACTION_RESTRICTION",
                    condition_json={"protected_ips": ["10.0.0.200", "10.0.0.255", "10.0.0.1"]},
                    enforcement_action="REJECT",
                    is_mandatory=True,
                    priority=1
                ),
                PolicyRule(
                    name="Uncertainty Autonomy Governor",
                    description="When model anomaly or threat uncertainty exceeds 0.45, zero-touch execution is forbidden.",
                    rule_type="AUTONOMY_GUARD",
                    condition_json={"max_uncertainty_for_autonomous": 0.45},
                    enforcement_action="ESCALATE",
                    is_mandatory=True,
                    priority=3
                )
            ]
            db.add_all(policies)
            db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
    print("Database schema migration and baseline seed records successfully updated!")
