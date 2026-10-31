import React, { useState, useEffect } from 'react';
import { HumanApproval } from '../types';
import { api } from '../services/api';
import { CheckSquare, Check, X, AlertTriangle, RefreshCw, UserCheck } from 'lucide-react';

interface ApprovalCenterProps {
  onRefresh: () => void;
  onSelectIncident: (id: number) => void;
}

export const ApprovalCenter: React.FC<ApprovalCenterProps> = ({ onRefresh, onSelectIncident }) => {
  const [approvals, setApprovals] = useState<HumanApproval[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [actionLoading, setActionLoading] = useState<boolean>(false);
  const [confirmModal, setConfirmModal] = useState<{
    approval: HumanApproval;
    action: 'APPROVE' | 'REJECT';
  } | null>(null);
  const [operatorComment, setOperatorComment] = useState<string>('');

  const loadApprovals = async () => {
    try {
      setLoading(true);
      const data = await api.getPendingApprovals();
      setApprovals(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadApprovals();
  }, []);

  const handleDecision = async () => {
    if (!confirmModal) return;
    try {
      setActionLoading(true);
      if (confirmModal.action === 'APPROVE') {
        await api.approveResponse(confirmModal.approval.id, operatorComment);
      } else {
        await api.rejectResponse(confirmModal.approval.id, operatorComment);
      }
      setConfirmModal(null);
      setOperatorComment('');
      await loadApprovals();
      onRefresh();
    } catch (e) {
      console.error(e);
    } finally {
      setActionLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <CheckSquare className="w-5 h-5 text-amber-400" />
            Human Approval Center
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Human-in-the-Loop review queue for uncertain, high-impact, or mandatory safety escalated responses.
          </p>
        </div>
        <button
          onClick={loadApprovals}
          className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 self-start"
          title="Refresh Queue"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-blue-400' : ''}`} />
        </button>
      </div>

      {/* Pending Queue List */}
      <div className="space-y-4">
        {approvals.length === 0 ? (
          <div className="p-12 rounded-xl bg-[#111827] border border-[#1F2937] text-center text-slate-400">
            <UserCheck className="w-10 h-10 mx-auto mb-3 text-slate-600" />
            <h3 className="text-sm font-semibold text-white">Queue Empty</h3>
            <p className="text-xs text-slate-500 mt-1">
              No actions currently waiting for human approval. The autonomous controller handles nominal events with Zero-Touch and Guarded modes.
            </p>
          </div>
        ) : (
          approvals.map((appr) => (
            <div 
              key={appr.id} 
              className="p-5 rounded-xl bg-[#111827] border border-amber-500/40 shadow-lg shadow-amber-500/5 space-y-4"
            >
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 pb-3 border-b border-slate-800">
                <div className="flex items-center space-x-3">
                  <div className="p-2 rounded-lg bg-amber-500/20 text-amber-400 border border-amber-500/40">
                    <AlertTriangle className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-white flex items-center gap-2">
                      Approval Request #{appr.id} — Incident #{appr.incident_id}
                    </h3>
                    <span className="text-xs text-slate-400">
                      Requested at: {new Date(appr.requested_at).toLocaleString()}
                    </span>
                  </div>
                </div>

                <button
                  onClick={() => onSelectIncident(appr.incident_id)}
                  className="text-xs text-blue-400 hover:text-blue-300 font-medium self-start md:self-auto"
                >
                  Inspect Complete Incident →
                </button>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 p-3.5 bg-slate-900/80 rounded-lg border border-slate-800 text-xs">
                <div>
                  <span className="text-[10px] uppercase font-bold text-slate-500 block">Threat Type</span>
                  <span className="font-semibold text-rose-300">
                    {(appr.threat_type || appr.incident?.threat_type || 'SECURITY_INCIDENT').replace(/_/g, ' ')}
                  </span>
                </div>
                <div>
                  <span className="text-[10px] uppercase font-bold text-slate-500 block">Proposed Action</span>
                  <span className="font-bold text-amber-300 font-mono">
                    {appr.action_type || appr.candidate?.action_type || `Candidate #${appr.candidate_response_id}`}
                  </span>
                </div>
                <div>
                  <span className="text-[10px] uppercase font-bold text-slate-500 block">Target Asset IP</span>
                  <span className="font-mono text-cyan-300">
                    {appr.target_ip || appr.candidate?.target_ip || 'N/A'}
                  </span>
                </div>
                <div>
                  <span className="text-[10px] uppercase font-bold text-slate-500 block">Trust / Reliability</span>
                  <span className="font-semibold text-indigo-300">
                    {appr.trust_score != null ? (appr.trust_score * 100).toFixed(1) + '%' : '--'} / {appr.reliability_score != null ? (appr.reliability_score * 100).toFixed(1) + '%' : '--'}
                  </span>
                </div>
              </div>

              <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-300 space-y-1.5">
                <div className="flex items-center space-x-2">
                  <span className="text-[10px] uppercase font-bold text-slate-500">Policy Evaluation:</span>
                  <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-orange-500/20 text-orange-300 border border-orange-500/30">
                    {appr.policy_decision || 'ESCALATE'}
                  </span>
                </div>
                <p>
                  <strong>Reason for Approval:</strong>{' '}
                  <span className="text-slate-200">
                    {appr.escalation_reason || 'Epistemic uncertainty or mandatory critical asset safety constraint.'}
                  </span>
                </p>
                <p className="text-slate-400 font-mono text-[11px]">
                  Target Candidate Response ID: #{appr.candidate_response_id}
                </p>
              </div>

              {/* Action Controls */}
              <div className="flex items-center justify-end space-x-3 pt-2">
                <button
                  onClick={() => setConfirmModal({ approval: appr, action: 'REJECT' })}
                  className="px-4 py-2 rounded-lg bg-rose-600/20 hover:bg-rose-600/30 text-rose-300 border border-rose-500/40 text-xs font-semibold transition flex items-center space-x-1.5"
                >
                  <X className="w-4 h-4" />
                  <span>Reject Response</span>
                </button>
                <button
                  onClick={() => setConfirmModal({ approval: appr, action: 'APPROVE' })}
                  className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow transition flex items-center space-x-1.5"
                >
                  <Check className="w-4 h-4" />
                  <span>Approve & Execute</span>
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Confirmation Modal */}
      {confirmModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#111827] border border-[#1F2937] rounded-xl max-w-md w-full p-6 space-y-4 shadow-2xl">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              {confirmModal.action === 'APPROVE' ? (
                <>
                  <Check className="w-5 h-5 text-emerald-400" /> Confirm Response Approval
                </>
              ) : (
                <>
                  <X className="w-5 h-5 text-rose-400" /> Confirm Response Rejection
                </>
              )}
            </h3>

            <p className="text-xs text-slate-300">
              {confirmModal.action === 'APPROVE'
                ? 'You are authorizing the SOAR engine to install SDN OpenFlow rules on the virtual switch datapath.'
                : 'You are halting execution of this security response. The incident will be marked as REJECTED.'}
            </p>

            <div>
              <label className="text-xs text-slate-400 block mb-1 font-medium">Operator Audit Rationale:</label>
              <textarea
                value={operatorComment}
                onChange={(e) => setOperatorComment(e.target.value)}
                placeholder="Enter audit rationale (e.g., Verified false-positive risk is low)..."
                className="w-full h-20 p-2.5 bg-slate-900 border border-slate-800 rounded-lg text-xs text-slate-200 focus:outline-none focus:border-blue-500"
              />
            </div>

            <div className="flex items-center justify-end space-x-3 pt-2">
              <button
                onClick={() => setConfirmModal(null)}
                className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium"
              >
                Cancel
              </button>
              <button
                onClick={handleDecision}
                disabled={actionLoading}
                className={`px-4 py-1.5 rounded-lg text-xs font-semibold text-white ${
                  confirmModal.action === 'APPROVE' ? 'bg-emerald-600 hover:bg-emerald-500' : 'bg-rose-600 hover:bg-rose-500'
                }`}
              >
                {actionLoading ? 'Processing...' : `Confirm ${confirmModal.action}`}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

