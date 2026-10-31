from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from datetime import datetime
from app.database.session import Base

class NetworkMetricSample(Base):
    __tablename__ = "network_metrics"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    switch_id = Column(String(50), nullable=True)
    host_ip = Column(String(45), nullable=True)
    throughput_mbps = Column(Float, default=0.0)
    packet_loss_pct = Column(Float, default=0.0)
    latency_ms = Column(Float, default=0.0)
    jitter_ms = Column(Float, default=0.0)
    packets_per_sec = Column(Float, default=0.0)
    bytes_per_sec = Column(Float, default=0.0)
    active_flows = Column(Integer, default=0)
    drop_count = Column(Integer, default=0)

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    user_id = Column(Integer, nullable=True)
    username = Column(String(50), default="SYSTEM")
    action = Column(String(100), nullable=False) # e.g. "POLICY_UPDATE", "RULE_EXECUTION", "APPROVAL_DECISION"
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(String(50), nullable=True)
    details = Column(JSON, nullable=True)

