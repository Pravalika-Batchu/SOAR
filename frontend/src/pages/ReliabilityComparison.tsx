import React, { useState, useEffect } from 'react';
import { Incident, CandidateResponse } from '../types';
import { api } from '../services/api';
import { Sliders, CheckCircle, AlertTriangle, ArrowRight } from 'lucide-react';
import { 
  ResponsiveContainer, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend 
} from 'recharts';

interface ReliabilityComparisonProps {
  incidents: Incident[];
  onSelectIncident: (id: number) => void;
}

export const ReliabilityComparison: React.FC<ReliabilityComparisonProps> = ({
  incidents,
  onSelectIncident
}) => {
  const [selectedIncidentId, setSelectedIncidentId] = useState<number | null>(
    incidents.length > 0 ? incidents[0].id : null
  );
  const [candidates, setCandidates] = useState<CandidateResponse[]>([]);
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    if (selectedIncidentId) {
      loadCandidates(selectedIncidentId);
    }
  }, [selectedIncidentId]);

  const loadCandidates = async (id: number) => {
    setLoading(true);
    try {
      const data = await api.getCandidateResponses(id);
      setCandidates(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const chartData = candidates.map((c) => ({
    name: c.action_type,
    Reliability: Number((c.reliability_score * 100).toFixed(1)),
    'Historical Success': Number((c.historical_success_score * 100).toFixed(1)),
    'QoS Risk (Lower is better)': Number((c.qos_risk_score * 100).toFixed(1)),
    'Trust Score': Number((c.trust_score * 100).toFixed(1))
  }));

  const selectedIncident = incidents.find(i => i.id === selectedIncidentId);

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Sliders className="w-5 h-5 text-indigo-400" />
            Response Reliability Comparison Engine
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Compare candidate security responses across weighted mathematical factors: threat confidence, historical success, policy fit, and QoS risk.
          </p>
        </div>

        {/* Incident Selector */}
        <div className="flex items-center space-x-2 text-xs">
          <span className="text-slate-400">Select Incident:</span>
          <select
            value={selectedIncidentId || ''}
            onChange={(e) => setSelectedIncidentId(Number(e.target.value))}
            className="bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 text-slate-200 focus:outline-none focus:border-blue-500 font-medium"
          >
            {incidents.map((inc) => (
              <option key={inc.id} value={inc.id}>
                #{inc.id} - {inc.threat_type} ({inc.source_ip})
              </option>
            ))}
          </select>
        </div>
      </div>

      {selectedIncident && (
        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between text-xs">
          <div className="flex items-center space-x-4">
            <div>
              <span className="text-slate-500">Threat Type:</span>{' '}
              <strong className="text-white">{selectedIncident.threat_type}</strong>
            </div>
            <div>
              <span className="text-slate-500">Target IP:</span>{' '}
              <strong className="text-cyan-400 font-mono">{selectedIncident.destination_ip}</strong>
            </div>
            <div>
              <span className="text-slate-500">ML Confidence:</span>{' '}
              <strong className="text-blue-400">{(selectedIncident.threat_confidence * 100).toFixed(0)}%</strong>
            </div>
          </div>
          <button
            onClick={() => onSelectIncident(selectedIncident.id)}
            className="text-xs text-blue-400 hover:text-blue-300 font-medium flex items-center gap-1"
          >
            <span>Open Incident Details</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      )}

      {/* Comparison Chart */}
      <div className="p-5 rounded-xl bg-[#111827] border border-[#1F2937]">
        <h3 className="text-sm font-semibold text-white mb-2">
          Multi-Factor Candidate Metric Comparison
        </h3>
        <p className="text-xs text-slate-500 mb-4">
          Visual comparison of normalized reliability scores, empirical track record, and disruption risks.
        </p>

        {candidates.length === 0 ? (
          <div className="text-center py-12 text-slate-500 text-xs">
            No candidates evaluated yet for this incident. Open the Incident Details page to trigger evaluation.
          </div>
        ) : (
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 10, right: 20, left: 0, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" />
                <XAxis dataKey="name" stroke="#9CA3AF" fontSize={11} />
                <YAxis stroke="#9CA3AF" fontSize={11} domain={[0, 100]} />
                <Tooltip contentStyle={{ backgroundColor: '#111827', borderColor: '#374151', borderRadius: '8px', fontSize: '12px' }} />
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
                <Bar dataKey="Reliability" fill="#3B82F6" radius={[4, 4, 0, 0]} />
                <Bar dataKey="Historical Success" fill="#10B981" radius={[4, 4, 0, 0]} />
                <Bar dataKey="QoS Risk (Lower is better)" fill="#F43F5E" radius={[4, 4, 0, 0]} />
                <Bar dataKey="Trust Score" fill="#8B5CF6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {/* Candidates Breakdown Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {candidates.map((c) => (
          <div 
            key={c.id} 
            className={`p-4 rounded-xl bg-[#111827] border ${
              c.policy_status === 'REJECT' ? 'border-rose-900/40 opacity-70' :
              c.reliability_score >= 0.75 ? 'border-blue-500/40' : 'border-[#1F2937]'
            } flex flex-col justify-between`}
          >
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="font-bold text-white text-sm">{c.action_type}</span>
                <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                  c.policy_status === 'ALLOW' ? 'bg-emerald-500/20 text-emerald-300' :
                  c.policy_status === 'RESTRICT' ? 'bg-amber-500/20 text-amber-300' :
                  c.policy_status === 'ESCALATE' ? 'bg-orange-500/20 text-orange-300' :
                  'bg-rose-500/20 text-rose-300'
                }`}>
                  {c.policy_status}
                </span>
              </div>

              <div className="space-y-1.5 text-xs text-slate-300 my-3">
                <div className="flex justify-between">
                  <span className="text-slate-500">Reliability Score:</span>
                  <span className="font-bold text-blue-400">{(c.reliability_score * 100).toFixed(1)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Historical Track Record:</span>
                  <span className="font-medium text-emerald-400">{(c.historical_success_score * 100).toFixed(0)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Predicted QoS Risk:</span>
                  <span className="font-medium text-rose-400">{(c.qos_risk_score * 100).toFixed(0)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Autonomy Trust Score:</span>
                  <span className="font-bold text-indigo-400">{(c.trust_score * 100).toFixed(1)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Recommended Mode:</span>
                  <span className="font-semibold text-slate-200">{c.recommended_mode}</span>
                </div>
              </div>

              <p className="text-[11px] text-slate-400 bg-slate-900 p-2 rounded border border-slate-800 line-clamp-3">
                {c.explanation}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

