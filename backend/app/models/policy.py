from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON, Text
from datetime import datetime
from app.database.session import Base

class PolicyRule(Base):
    __tablename__ = "policy_rules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=False)
    rule_type = Column(String(50), nullable=False) # ASSET_PROTECTION, QOS_GUARDRAIL, ACTION_RESTRICTION, AUTONOMY_GUARD
    condition_json = Column(JSON, nullable=False) # e.g. {"target_criticality": "CRITICAL", "disallowed_action": "ISOLATE_HOST"}
    enforcement_action = Column(String(20), default="REJECT") # REJECT, RESTRICT, ESCALATE, ALLOW
    is_mandatory = Column(Boolean, default=True) # If True, cannot be overridden by high trust
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=100)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

