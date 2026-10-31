from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.session import Base

class SecurityAlert(Base):
    __tablename__ = "security_alerts"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(50), nullable=False) # "SURICATA", "ZEEK", "TEST_GENERATOR"
    alert_type = Column(String(100), nullable=False) # "DOS_SYN_FLOOD", "PORT_SCAN", "BRUTE_FORCE", "ANOMALY"
    severity = Column(String(20), default="MEDIUM") # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    source_ip = Column(String(45), index=True, nullable=False)
    destination_ip = Column(String(45), index=True, nullable=False)
    source_port = Column(Integer, nullable=True)
    destination_port = Column(Integer, nullable=True)
    protocol = Column(String(20), default="TCP")
    signature = Column(String(255), nullable=True)
    raw_payload = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=True)

    incident = relationship("Incident", back_populates="alerts")

