from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.api.deps import get_db
from app.models.response import CandidateResponse, ResponseExecution, HumanApproval
from app.models.incident import Incident
from app.schemas.response import CandidateResponseSchema, ExecutionRequest, HumanApprovalResponse
from app.services.orchestrator import orchestrator_service

router = APIRouter(prefix="/incidents", tags=["Response Decisions"])

@router.get("/{incident_id}/candidates", response_model=List[CandidateResponseSchema])
def get_candidates(incident_id: int, db: Session = Depends(get_db)):
    candidates = db.query(CandidateResponse).filter(CandidateResponse.incident_id == incident_id).all()
    executions = db.query(ResponseExecution).filter(ResponseExecution.incident_id == incident_id).all()
    approvals = db.query(HumanApproval).filter(HumanApproval.incident_id == incident_id).all()

    executed_cand_ids = {e.candidate_response_id for e in executions if e.status == "SUCCESS"}
    rejected_cand_ids = {a.candidate_response_id for a in approvals if a.status == "REJECTED"}
    pending_cand_ids = {a.candidate_response_id for a in approvals if a.status == "PENDING"}

    results = []
    has_any_execution = len(executed_cand_ids) > 0

    for c in candidates:
        cand_dict = {
            "id": c.id,
            "incident_id": c.incident_id,
            "action_type": c.action_type,
            "target_ip": c.target_ip,
            "parameters": c.parameters,
            "reliability_score": c.reliability_score,
            "threat_confidence_score": c.threat_confidence_score,
            "historical_success_score": c.historical_success_score,
            "policy_fit_score": c.policy_fit_score,
            "qos_risk_score": c.qos_risk_score,
            "resource_risk_score": c.resource_risk_score,
            "uncertainty_score": c.uncertainty_score,
            "score_breakdown": c.score_breakdown,
            "explanation": c.explanation,
            "policy_status": c.policy_status,
            "policy_reason": c.policy_reason,
            "trust_score": c.trust_score,
            "recommended_mode": c.recommended_mode,
            "created_at": c.created_at
        }

        # Calculate exact per-candidate status
        if c.id in executed_cand_ids:
            cand_dict["candidate_status"] = "EXECUTED"
        elif has_any_execution:
            cand_dict["candidate_status"] = "NOT_SELECTED"
        elif c.id in rejected_cand_ids:
            cand_dict["candidate_status"] = "REJECTED"
        elif c.id in pending_cand_ids:
            cand_dict["candidate_status"] = "PENDING_APPROVAL"
        elif c.policy_status == "REJECT":
            cand_dict["candidate_status"] = "POLICY_REJECTED"
        else:
            cand_dict["candidate_status"] = "READY"

        results.append(CandidateResponseSchema(**cand_dict))

    return results

@router.post("/{incident_id}/evaluate-responses", response_model=List[CandidateResponseSchema])
def evaluate_candidates(incident_id: int, db: Session = Depends(get_db)):
    try:
        candidates = orchestrator_service.evaluate_candidate_responses(incident_id, db)
        return get_candidates(incident_id, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{incident_id}/request-approval/{candidate_id}", response_model=HumanApprovalResponse)
def request_candidate_approval(incident_id: int, candidate_id: int, db: Session = Depends(get_db)):
    try:
        approval = orchestrator_service.request_candidate_approval(incident_id, candidate_id, db)
        return approval
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{incident_id}/execute")
def execute_response(incident_id: int, request: ExecutionRequest, db: Session = Depends(get_db)):
    try:
        result = orchestrator_service.execute_incident_response(incident_id, request.candidate_id, db)
        return result
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
