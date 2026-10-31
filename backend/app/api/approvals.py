from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.api.deps import get_db, get_current_user
from app.models.response import HumanApproval, CandidateResponse, ResponseExecution
from app.models.incident import Incident
from app.models.user import User
from app.models.metrics import AuditLog
from app.schemas.response import HumanApprovalResponse, HumanApprovalRequest
from app.services.orchestrator import orchestrator_service

router = APIRouter(prefix="/approvals", tags=["Human Approvals"])

@router.get("/pending", response_model=List[HumanApprovalResponse])
def get_pending_approvals(db: Session = Depends(get_db)):
    approvals = db.query(HumanApproval).filter(HumanApproval.status == "PENDING").all()
    # Backfill missing metadata from candidate or incident if necessary
    for a in approvals:
        if not a.action_type or not a.target_ip:
            cand = db.query(CandidateResponse).filter(CandidateResponse.id == a.candidate_response_id).first()
            inc = db.query(Incident).filter(Incident.id == a.incident_id).first()
            if cand:
                a.action_type = cand.action_type
                a.target_ip = cand.target_ip
                a.trust_score = cand.trust_score
                a.reliability_score = cand.reliability_score
                a.policy_decision = cand.policy_status
                a.escalation_reason = cand.policy_reason or cand.explanation
            if inc:
                a.threat_type = inc.threat_type
    db.commit()
    return approvals

@router.post("/{approval_id}/approve", response_model=HumanApprovalResponse)
def approve_response(
    approval_id: int,
    request: HumanApprovalRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    approval = db.query(HumanApproval).filter(HumanApproval.id == approval_id).first()
    if not approval:
        raise HTTPException(status_code=404, detail="Approval request not found")
    if approval.status != "PENDING":
        raise HTTPException(status_code=400, detail=f"Approval request already {approval.status}")
        
    approval.status = "APPROVED"
    approval.operator_username = current_user.username if current_user else "analyst"
    approval.operator_comment = request.operator_comment or "Manually approved by operator"
    approval.decided_at = datetime.utcnow()
    
    # Audit log
    audit = AuditLog(
        action="APPROVAL_DECISION",
        resource_type="HUMAN_APPROVAL",
        resource_id=str(approval.id),
        username=approval.operator_username,
        details={
            "decision": "APPROVED",
            "incident_id": approval.incident_id,
            "candidate_id": approval.candidate_response_id,
            "action_type": approval.action_type,
            "comment": approval.operator_comment
        }
    )
    db.add(audit)

    # Update incident status to READY_TO_EXECUTE
    incident = db.query(Incident).filter(Incident.id == approval.incident_id).first()
    if incident:
        incident.status = "READY_TO_EXECUTE"
        incident.execution_mode = "HUMAN_APPROVED"
        incident.selected_response_id = approval.candidate_response_id
        
    db.commit()
    db.refresh(approval)

    # Auto-execute the approved action on the network adapter if auto_execute is True (default)
    if request.auto_execute:
        try:
            orchestrator_service.execute_incident_response(approval.incident_id, approval.candidate_response_id, db)
        except Exception as e:
            # If execution fails, state remains logged
            pass

    return approval

@router.post("/{approval_id}/reject", response_model=HumanApprovalResponse)
def reject_response(
    approval_id: int,
    request: HumanApprovalRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    approval = db.query(HumanApproval).filter(HumanApproval.id == approval_id).first()
    if not approval:
        raise HTTPException(status_code=404, detail="Approval request not found")
    if approval.status != "PENDING":
        raise HTTPException(status_code=400, detail=f"Approval request already {approval.status}")
        
    approval.status = "REJECTED"
    approval.operator_username = current_user.username if current_user else "analyst"
    approval.operator_comment = request.operator_comment or "Manually rejected by operator"
    approval.decided_at = datetime.utcnow()
    
    # Audit log
    audit = AuditLog(
        action="APPROVAL_DECISION",
        resource_type="HUMAN_APPROVAL",
        resource_id=str(approval.id),
        username=approval.operator_username,
        details={
            "decision": "REJECTED",
            "incident_id": approval.incident_id,
            "candidate_id": approval.candidate_response_id,
            "action_type": approval.action_type,
            "comment": approval.operator_comment
        }
    )
    db.add(audit)

    # Update incident status to REJECTED
    incident = db.query(Incident).filter(Incident.id == approval.incident_id).first()
    if incident:
        incident.status = "REJECTED"
        
    db.commit()
    db.refresh(approval)
    return approval
