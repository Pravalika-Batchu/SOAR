from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class PolicyRuleBase(BaseModel):
    name: str
    description: str
    rule_type: str # ASSET_PROTECTION, QOS_GUARDRAIL, ACTION_RESTRICTION, AUTONOMY_GUARD
    condition_json: Dict[str, Any]
    enforcement_action: str = "REJECT" # REJECT, RESTRICT, ESCALATE, ALLOW
    is_mandatory: bool = True
    is_active: bool = True
    priority: int = 100

class PolicyRuleCreate(PolicyRuleBase):
    pass

class PolicyRuleUpdate(BaseModel):
    description: Optional[str] = None
    condition_json: Optional[Dict[str, Any]] = None
    enforcement_action: Optional[str] = None
    is_mandatory: Optional[bool] = None
    is_active: Optional[bool] = None
    priority: Optional[int] = None

class PolicyRuleResponse(PolicyRuleBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

