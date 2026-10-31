from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON
from datetime import datetime
from app.database.session import Base

class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String(45), unique=True, index=True, nullable=False)
    hostname = Column(String(100), nullable=False)
    mac_address = Column(String(20), nullable=True)
    subnet = Column(String(50), nullable=False)
    criticality = Column(String(20), default="MEDIUM") # CRITICAL, HIGH, MEDIUM, LOW
    service_type = Column(String(100), nullable=True) # e.g. "DNS", "Web Server", "Database"
    is_isolated = Column(Boolean, default=False)
    is_rate_limited = Column(Boolean, default=False)
    qos_sensitivity = Column(Float, default=0.5) # 0.0 (tolerant) to 1.0 (strict SLA)
    created_at = Column(DateTime, default=datetime.utcnow)

class NetworkTopologyNode(Base):
    __tablename__ = "topology_nodes"

    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(String(50), unique=True, index=True, nullable=False)
    node_type = Column(String(30), nullable=False) # "SWITCH", "HOST", "ROUTER"
    ip_address = Column(String(45), nullable=True)
    mac_address = Column(String(20), nullable=True)
    connected_switch = Column(String(50), nullable=True)
    port_number = Column(Integer, nullable=True)
    status = Column(String(20), default="ONLINE") # ONLINE, DEGRADED, ISOLATED
    metadata_json = Column(JSON, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

