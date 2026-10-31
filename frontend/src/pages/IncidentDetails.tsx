import React, { useState, useEffect } from 'react';
import { Incident, CandidateResponse, OutcomeEvaluation } from '../types';
import { api } from '../services/api';
import { 
  ShieldAlert, 
  Cpu, 
  Sliders, 
  Scale, 
  Play, 
  CheckCircle2, 
  AlertTriangle, 
  RefreshCw,
  Info
} from 'lucide-react';

interface IncidentDetailsProps {
  incidentId: number;
  onBack: () => void;
  onRefresh: () => void;
}

export const IncidentDetails: React.FC<IncidentDetailsProps> = ({
  incidentId,
  onBack,
  onRefresh
}) => {
  const [incident, setIncident] = useState<Incident | null>(null);
  const [candidates, setCandidates] = useState<CandidateResponse[]>([]);
  const [outcomes, setOutcomes] = useState<OutcomeEvaluation[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [actionLoading, setActionLoading] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const loadData = async () => {
    try {
      setLoading(true);
      setErrorMsg(null);
      const inc = await api.getIncident(incidentId);
      setIncident(inc);

      const cands = await api.getCandidateResponses(incidentId);
      setCandidates(cands);

      const outs = await api.getOutcomes(incidentId);
      setOutcomes(outs.filter(o => o.incident_id === incidentId));
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to load incident details');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [incidentId]);

  const handleAnalyze = async () => {
    try {
      setActionLoading(true);
      await api.analyzeIncident(incidentId);
      await loadData();
      onRefresh();
    } catch (err: any) {
      setErrorMsg(err.message);
    } finally {
      setActionLoading(false);
    }
  };

  const handleEvaluate = async () => {
    try {
      setActionLoading(true);
      await api.evaluateResponses(incidentId);
      await loadData();
      onRefresh();
    } catch (err: any) {
      setErrorMsg(err.message);
    } finally {
      setActionLoading(false);
    }
  };

  const handleExecute = async (candidateId?: number) => {
    try {
      setActionLoading(true);
      await api.executeResponse(incidentId, candidateId);
      await loadData();
      onRefresh();
    } catch (err: any) {
      setErrorMsg(err.message);
    } finally {
      setActionLoading(false);
    }
  };

  const handleRequestApproval = async (candidateId: number) => {
    try {
      setActionLoading(true);
      await api.requestApproval(incidentId, candidateId);
      await loadData();
      onRefresh();
    } catch (err: any) {
      setErrorMsg(err.message);
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-24 text-slate-400">
        <RefreshCw className="w-6 h-6 animate-spin text-blue-500 mr-2" />
        <span>Loading Incident Lifecycle Telemetry...</span>
      </div>
    );
  }

  if (!incident) {
    return (
      <div className="p-8 text-center text-slate-400">
        <p>Incident #{incidentId} not found.</p>
        <button onClick={onBack} className="mt-4 px-4 py-2 bg-slate-800 rounded-lg text-xs">Go Back</button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header & Pipeline Actions */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-5 rounded-xl bg-[#111827] border border-[#1F2937]">
        <div>
          <div className="flex items-center space-x-3">
            <button onClick={onBack} className="text-xs text-blue-400 hover:text-blue-300">
              ← Back to List
            </button>
            <span className="text-slate-600">/</span>
            <span className="font-mono text-xs text-slate-400">INCIDENT #{incident.id}</span>
          </div>
          <h2 className="text-xl font-bold text-white mt-1">{incident.title}</h2>
          <div className="flex flex-wrap items-center gap-2 mt-2 text-xs">
            <span className="px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 font-semibold border border-rose-500/40">
              {incident.threat_type.replace(/_/g, ' ')}
            </span>
            <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300">
              Status: <strong className="text-white">{incident.status}</strong>
            </span>
            <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300">
              Source: <strong className="text-rose-400 font-mono">{incident.source_ip}</strong> → Target: <strong className="text-cyan-400 font-mono">{incident.destination_ip}</strong>
            </span>
          </div>
        </div>

        {/* Workflow Lifecycle Action Buttons */}
        <div className="flex flex-wrap items-center gap-2">
          {incident.status === 'NEW' && (
            <button
              onClick={handleAnalyze}
              disabled={actionLoading}
              className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow transition flex items-center space-x-1.5"
            >
              <Cpu className="w-4 h-4" />
              <span>Step 1: Run ML Threat Analysis</span>
            </button>
          )}

          {incident.status === 'EVALUATING' && (
            <button
              onClick={handleEvaluate}
              disabled={actionLoading}
              className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow transition flex items-center space-x-1.5"
            >
              <Sliders className="w-4 h-4" />
              <span>Step 2: Evaluate Candidate Responses</span>
            </button>
          )}

          {incident.status === 'READY_TO_EXECUTE' && (
            <button
              onClick={() => handleExecute()}
              disabled={actionLoading}
              className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow transition flex items-center space-x-1.5"
            >
              <Play className="w-4 h-4" />
              <span>Step 3: Execute Autonomous Response</span>
            </button>
          )}

          {incident.status === 'PENDING_APPROVAL' && (
            <div className="px-3 py-2 rounded-lg bg-amber-500/20 text-amber-300 border border-amber-500/40 text-xs font-semibold flex items-center space-x-1.5">
              <AlertTriangle className="w-4 h-4 text-amber-400 animate-bounce" />
              <span>Pending SOC Human Approval</span>
            </div>
          )}

          {incident.status === 'REJECTED' && (
            <div className="px-3 py-2 rounded-lg bg-rose-500/20 text-rose-300 border border-rose-500/40 text-xs font-semibold flex items-center space-x-1.5">
              <AlertTriangle className="w-4 h-4 text-rose-400" />
              <span>Response Rejected by Operator</span>
            </div>
          )}

          {incident.status === 'COMPLETED' && (
            <div className="px-3 py-2 rounded-lg bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 text-xs font-semibold flex items-center space-x-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>Response Executed & Active</span>
            </div>
          )}

          <button
            onClick={loadData}
            className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300"
            title="Reload incident"
          >
            <RefreshCw className={`w-4 h-4 ${actionLoading ? 'animate-spin text-blue-400' : ''}`} />
          </button>
        </div>
      </div>

      {errorMsg && (
        <div className="p-4 rounded-xl bg-rose-900/30 border border-rose-700/50 text-rose-300 text-xs flex items-center space-x-2">
          <AlertTriangle className="w-4 h-4 flex-shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* 4 Pipeline Stages Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* Stage 1: Threat Assessment */}
        <div className="p-4 rounded-xl bg-[#111827] border border-[#1F2937]">
          <span className="text-[10px] font-bold tracking-wider uppercase text-blue-400 block mb-1">
            STAGE 1: ML ASSESSMENT
          </span>
          <div className="text-xl font-bold text-white mb-2">
            {(incident.threat_confidence * 100).toFixed(0)}% <span className="text-xs text-slate-400 font-normal">Confidence</span>
          </div>
          <div className="space-y-1.5 text-xs text-slate-300">
            <div className="flex justify-between">
              <span className="text-slate-500">Anomaly Score:</span>
              <span className="font-mono text-cyan-300">{(incident.anomaly_score * 100).toFixed(0)}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Uncertainty:</span>
              <span className="font-mono text-amber-300">{(incident.uncertainty * 100).toFixed(0)}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Isolation Forest:</span>
              <span className="font-semibold text-emerald-400">
                {incident.is_anomaly ? 'Out-of-Distribution' : 'Nominal'}
              </span>
            </div>
          </div>
        </div>

        {/* Stage 2: Reliability Evaluation */}
        <div className="p-4 rounded-xl bg-[#111827] border border-[#1F2937]">
          <span className="text-[10px] font-bold tracking-wider uppercase text-indigo-400 block mb-1">
            STAGE 2: CANDIDATES
          </span>
          <div className="text-xl font-bold text-white mb-2">
            {candidates.length} <span className="text-xs text-slate-400 font-normal">Generated</span>
          </div>
          <div className="text-xs text-slate-400">
            Weighted multi-factor reliability scoring evaluated across QoS risk, uncertainty, and historical experience.
          </div>
        </div>

        {/* Stage 3: Autonomy Decision */}
        <div className="p-4 rounded-xl bg-[#111827] border border-[#1F2937]">
          <span className="text-[10px] font-bold tracking-wider uppercase text-emerald-400 block mb-1">
            STAGE 3: AUTONOMY TRUST
          </span>
          <div className="text-xl font-bold text-white mb-2">
            {incident.autonomy_trust_score ? (incident.autonomy_trust_score * 100).toFixed(0) + '%' : 'N/A'}
          </div>
          <div className="text-xs">
            <span className={`px-2 py-0.5 rounded font-bold ${
              incident.execution_mode === 'ZERO_TOUCH' ? 'bg-blue-500/20 text-blue-300' :
              incident.execution_mode === 'GUARDED' ? 'bg-emerald-500/20 text-emerald-300' :
              'bg-amber-500/20 text-amber-300'
            }`}>
              {incident.execution_mode || 'Pending Evaluation'}
            </span>
          </div>
        </div>

        {/* Stage 4: Outcome Evaluation */}
        <div className="p-4 rounded-xl bg-[#111827] border border-[#1F2937]">
          <span className="text-[10px] font-bold tracking-wider uppercase text-cyan-400 block mb-1">
            STAGE 4: OUTCOME STATUS
          </span>
          <div className="text-xl font-bold text-white mb-2">
            {outcomes.length > 0 ? outcomes[0].success_status : 'Pending Execution'}
          </div>
          <div className="text-xs text-slate-400">
            {outcomes.length > 0 
              ? `${outcomes[0].actual_attack_reduction_pct.toFixed(0)}% mitigation vs ${outcomes[0].actual_qos_impact_pct.toFixed(0)}% collateral`
              : 'Telemetry will measure pre vs post throughput.'}
          </div>
        </div>
      </div>

      {/* Candidate Responses Table */}
      <div className="p-5 rounded-xl bg-[#111827] border border-[#1F2937]">
        <h3 className="text-sm font-semibold text-white mb-3">
          Candidate Response Comparison (Engines 1, 2, 3 & 4)
        </h3>

        {candidates.length === 0 ? (
          <div className="text-center py-8 text-slate-500 text-xs">
            No candidate responses evaluated yet. Click "Step 2: Evaluate Candidate Responses" above.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-900 text-slate-400 uppercase text-[10px] tracking-wider">
                <tr>
                  <th className="px-3 py-2.5 rounded-l-lg">Action Type</th>
                  <th className="px-3 py-2.5">Target</th>
                  <th className="px-3 py-2.5">Reliability</th>
                  <th className="px-3 py-2.5">QoS Risk</th>
                  <th className="px-3 py-2.5">Policy Status</th>
                  <th className="px-3 py-2.5">Trust Score</th>
                  <th className="px-3 py-2.5">Autonomy Mode</th>
                  <th className="px-3 py-2.5 rounded-r-lg text-right">Execution</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {candidates.map((c) => (
                  <tr 
                    key={c.id} 
                    className={`hover:bg-slate-800/40 transition ${
                      incident.selected_response_id === c.id ? 'bg-blue-950/20' : ''
                    }`}
                  >
                    <td className="px-3 py-3 font-semibold text-white">
                      {c.action_type}
                      {incident.selected_response_id === c.id && (
                        <span className="ml-2 text-[10px] font-bold text-blue-400 bg-blue-900/40 px-1.5 py-0.5 rounded border border-blue-700/50">
                          RECOMMENDED
                        </span>
                      )}
                    </td>
                    <td className="px-3 py-3 font-mono text-cyan-300">{c.target_ip}</td>
                    <td className="px-3 py-3 font-bold text-blue-400">
                      {(c.reliability_score * 100).toFixed(1)}%
                    </td>
                    <td className="px-3 py-3 font-mono text-rose-300">
                      {(c.qos_risk_score * 100).toFixed(0)}%
                    </td>
                    <td className="px-3 py-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        c.policy_status === 'ALLOW' ? 'bg-emerald-500/20 text-emerald-300' :
                        c.policy_status === 'RESTRICT' ? 'bg-amber-500/20 text-amber-300' :
                        c.policy_status === 'ESCALATE' ? 'bg-orange-500/20 text-orange-300' :
                        'bg-rose-500/20 text-rose-300'
                      }`}>
                        {c.policy_status}
                      </span>
                    </td>
                    <td className="px-3 py-3 font-bold text-indigo-400">
                      {(c.trust_score * 100).toFixed(1)}%
                    </td>
                    <td className="px-3 py-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        c.recommended_mode === 'ZERO_TOUCH' ? 'bg-blue-500/20 text-blue-300' :
                        c.recommended_mode === 'GUARDED' ? 'bg-emerald-500/20 text-emerald-300' :
                        'bg-amber-500/20 text-amber-300'
                      }`}>
                        {c.recommended_mode}
                      </span>
                    </td>
                    <td className="px-3 py-3 text-right">
                      {c.candidate_status === 'EXECUTED' ? (
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
                          EXECUTED
                        </span>
                      ) : c.candidate_status === 'PENDING_APPROVAL' ? (
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40">
                          PENDING APPROVAL
                        </span>
                      ) : c.candidate_status === 'REJECTED' ? (
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500/20 text-rose-300 border border-rose-500/40">
                          REJECTED
                        </span>
                      ) : c.candidate_status === 'NOT_SELECTED' ? (
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-800 text-slate-400 border border-slate-700/50">
                          NOT SELECTED
                        </span>
                      ) : incident.status === 'READY_TO_EXECUTE' ? (
                        c.recommended_mode === 'HUMAN_APPROVAL' ? (
                          <button
                            onClick={() => handleRequestApproval(c.id)}
                            disabled={actionLoading}
                            className="px-2.5 py-1 rounded bg-amber-600 hover:bg-amber-500 text-white font-medium text-[11px] shadow transition"
                          >
                            Request Approval
                          </button>
                        ) : (
                          <button
                            onClick={() => handleExecute(c.id)}
                            disabled={actionLoading}
                            className="px-2.5 py-1 rounded bg-blue-600 hover:bg-blue-500 text-white font-medium text-[11px] shadow transition"
                          >
                            Execute This
                          </button>
                        )
                      ) : (
                        <span className="text-slate-500 text-[11px]">
                          {c.candidate_status || 'Locked'}
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Outcome Evaluation Details (if executed) */}
      {outcomes.length > 0 && (
        <div className="p-5 rounded-xl bg-[#111827] border border-[#1F2937] space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <h3 className="text-sm font-semibold text-white flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              Outcome Evaluation & Experience Feedback (Engines 5 & 6)
            </h3>
            <span className="px-2.5 py-1 rounded font-bold text-xs bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
              {outcomes[0].success_status}
            </span>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
            <div className="p-3 rounded bg-slate-900 border border-slate-800">
              <span className="text-slate-500 block text-[10px]">PRE ATTACK TRAFFIC</span>
              <span className="text-lg font-bold text-rose-400">{outcomes[0].pre_attack_pps.toFixed(0)} pps</span>
            </div>
            <div className="p-3 rounded bg-slate-900 border border-slate-800">
              <span className="text-slate-500 block text-[10px]">POST ATTACK TRAFFIC</span>
              <span className="text-lg font-bold text-emerald-400">{outcomes[0].post_attack_pps.toFixed(0)} pps</span>
              <span className="text-[10px] text-slate-400 block mt-0.5">(-{outcomes[0].actual_attack_reduction_pct.toFixed(1)}% reduction)</span>
            </div>
            <div className="p-3 rounded bg-slate-900 border border-slate-800">
              <span className="text-slate-500 block text-[10px]">LEGITIMATE THROUGHPUT</span>
              <span className="text-lg font-bold text-white">{outcomes[0].post_legitimate_throughput_mbps.toFixed(1)} Mbps</span>
              <span className="text-[10px] text-slate-400 block mt-0.5">(Pre: {outcomes[0].pre_legitimate_throughput_mbps.toFixed(1)} Mbps)</span>
            </div>
            <div className="p-3 rounded bg-slate-900 border border-slate-800">
              <span className="text-slate-500 block text-[10px]">COLLATERAL QoS IMPACT</span>
              <span className="text-lg font-bold text-amber-300">{outcomes[0].actual_qos_impact_pct.toFixed(1)}%</span>
              <span className="text-[10px] text-slate-400 block mt-0.5">(Composite Score: {outcomes[0].composite_success_score.toFixed(2)})</span>
            </div>
          </div>

          <p className="p-3 rounded bg-slate-900 border border-slate-800 text-slate-300 text-xs font-mono">
            <strong>Outcome Analysis:</strong> {outcomes[0].explanation}
          </p>
        </div>
      )}
    </div>
  );
};

