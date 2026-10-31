from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

class AlertCreate(BaseModel):
    source: str # "SURICATA", "ZEEK", "TEST_GENERATOR"
    alert_type: str
    severity: str = "MEDIUM"
    source_ip: str
    destination_ip: str
    source_port: Optional[int] = None
    destination_port: Optional[int] = None
    protocol: str = "TCP"
    signature: Optional[str] = None
    raw_payload: Optional[Dict[str, Any]] = None

class AlertResponse(AlertCreate):
    id: int
    incident_id: Optional[int] = None
    timestamp: datetime

    class Config:
        from_attributes = True

class IncidentCreate(BaseModel):
    title: str
    threat_type: str
    severity: str = "MEDIUM"
    source_ip: str
    destination_ip: str
    protocol: str = "TCP"

class IncidentResponse(IncidentCreate):
    id: int
    status: str
    threat_confidence: float
    anomaly_score: float
    is_anomaly: int
    uncertainty: float
    assessment_notes: Optional[str] = None
    selected_response_id: Optional[int] = None
    autonomy_trust_score: Optional[float] = None
    execution_mode: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

