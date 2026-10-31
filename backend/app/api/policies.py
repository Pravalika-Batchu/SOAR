from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.api.deps import get_db
from app.models.policy import PolicyRule
from app.schemas.policy import PolicyRuleCreate, PolicyRuleUpdate, PolicyRuleResponse

router = APIRouter(prefix="/policies", tags=["Policies"])

@router.get("", response_model=List[PolicyRuleResponse])
def get_policies(db: Session = Depends(get_db)):
    return db.query(PolicyRule).order_by(PolicyRule.priority.asc()).all()

@router.post("", response_model=PolicyRuleResponse)
def create_policy(policy_in: PolicyRuleCreate, db: Session = Depends(get_db)):
    existing = db.query(PolicyRule).filter(PolicyRule.name == policy_in.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="A policy with this name already exists")
    
    rule = PolicyRule(
        name=policy_in.name,
        description=policy_in.description,
        rule_type=policy_in.rule_type,
        condition_json=policy_in.condition_json,
        enforcement_action=policy_in.enforcement_action,
        is_mandatory=policy_in.is_mandatory,
        is_active=policy_in.is_active,
        priority=policy_in.priority
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule

@router.put("/{policy_id}", response_model=PolicyRuleResponse)
def update_policy(policy_id: int, policy_in: PolicyRuleUpdate, db: Session = Depends(get_db)):
    rule = db.query(PolicyRule).filter(PolicyRule.id == policy_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Policy not found")
        
    for field, value in policy_in.dict(exclude_unset=True).items():
        setattr(rule, field, value)
        
    db.commit()
    db.refresh(rule)
    return rule

