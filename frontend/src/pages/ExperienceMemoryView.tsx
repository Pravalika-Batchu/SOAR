import React, { useState, useEffect } from 'react';
import { ExperienceRecord } from '../types';
import { api } from '../services/api';
import { History, Search, Filter, RefreshCw, CheckCircle, XCircle } from 'lucide-react';

export const ExperienceMemoryView: React.FC = () => {
  const [records, setRecords] = useState<ExperienceRecord[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [threatFilter, setThreatFilter] = useState<string>('ALL');
  const [actionFilter, setActionFilter] = useState<string>('ALL');

  const loadExperience = async () => {
    try {
      setLoading(true);
      const data = await api.getExperience(50);
      setRecords(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadExperience();
  }, []);

  const filtered = records.filter((r) => {
    if (threatFilter !== 'ALL' && r.threat_type !== threatFilter) return false;
    if (actionFilter !== 'ALL' && r.selected_action !== actionFilter) return false;
    return true;
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <History className="w-5 h-5 text-purple-400" />
            Experience Memory & Adaptive Case-Based Reasoning
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Empirical knowledge store of past incidents. Past failures and QoS degradation dynamically penalize future candidate reliability scores.
          </p>
        </div>
        <button
          onClick={loadExperience}
          className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 self-start"
          title="Refresh Memory Index"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-blue-400' : ''}`} />
        </button>
      </div>

      {/* Filter Bar */}
      <div className="flex flex-wrap items-center gap-3 p-4 rounded-xl bg-[#111827] border border-[#1F2937] text-xs">
        <Filter className="w-4 h-4 text-slate-400" />
        <select
          value={threatFilter}
          onChange={(e) => setThreatFilter(e.target.value)}
          className="bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 text-slate-300 focus:outline-none focus:border-blue-500"
        >
          <option value="ALL">All Threat Types</option>
          <option value="DOS_SYN_FLOOD">DoS SYN Flood</option>
          <option value="PORT_SCAN">Port Scan</option>
          <option value="BRUTE_FORCE">Brute Force</option>
          <option value="UNKNOWN_ANOMALY">Unknown Anomaly</option>
        </select>
        <select
          value={actionFilter}
          onChange={(e) => setActionFilter(e.target.value)}
          className="bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 text-slate-300 focus:outline-none focus:border-blue-500"
        >
          <option value="ALL">All Actions</option>
          <option value="BLOCK_IP">BLOCK_IP</option>
          <option value="RATE_LIMIT">RATE_LIMIT</option>
          <option value="ISOLATE_HOST">ISOLATE_HOST</option>
        </select>
      </div>

      {/* Experience Table */}
      <div className="p-5 rounded-xl bg-[#111827] border border-[#1F2937]">
        <h3 className="text-sm font-semibold text-white mb-3">Case-Based Experience Records</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900 text-slate-400 uppercase text-[10px] tracking-wider">
              <tr>
                <th className="px-3 py-2.5 rounded-l-lg">Time</th>
                <th className="px-3 py-2.5">Inc ID</th>
                <th className="px-3 py-2.5">Threat Type</th>
                <th className="px-3 py-2.5">Attacker IP</th>
                <th className="px-3 py-2.5">Target IP</th>
                <th className="px-3 py-2.5">Selected Action</th>
                <th className="px-3 py-2.5">Trust Score</th>
                <th className="px-3 py-2.5">Mode</th>
                <th className="px-3 py-2.5">Final Outcome</th>
                <th className="px-3 py-2.5 rounded-r-lg">Adaptation Penalty</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={10} className="px-3 py-6 text-center text-slate-500">
                    No experience records matching the filter.
                  </td>
                </tr>
              ) : (
                filtered.map((r) => (
                  <tr key={r.id} className="hover:bg-slate-800/40 transition">
                    <td className="px-3 py-3 text-slate-400 font-mono text-[11px]">
                      {new Date(r.created_at).toLocaleTimeString()}
                    </td>
                    <td className="px-3 py-3 font-mono text-cyan-300">#{r.incident_id}</td>
                    <td className="px-3 py-3 font-semibold text-white">{r.threat_type}</td>
                    <td className="px-3 py-3 font-mono text-rose-400">{r.source_ip}</td>
                    <td className="px-3 py-3 font-mono text-cyan-400">{r.destination_ip}</td>
                    <td className="px-3 py-3 font-semibold text-slate-200">{r.selected_action}</td>
                    <td className="px-3 py-3 font-bold text-blue-400">
                      {(r.trust_score * 100).toFixed(0)}%
                    </td>
                    <td className="px-3 py-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        r.execution_mode === 'ZERO_TOUCH' ? 'bg-blue-500/20 text-blue-300' :
                        r.execution_mode === 'GUARDED' ? 'bg-emerald-500/20 text-emerald-300' :
                        'bg-amber-500/20 text-amber-300'
                      }`}>
                        {r.execution_mode}
                      </span>
                    </td>
                    <td className="px-3 py-3">
                      {r.final_success ? (
                        <span className="flex items-center text-emerald-400 text-xs font-semibold">
                          <CheckCircle className="w-3.5 h-3.5 mr-1" /> Success
                        </span>
                      ) : (
                        <span className="flex items-center text-rose-400 text-xs font-semibold">
                          <XCircle className="w-3.5 h-3.5 mr-1" /> Failed / Collateral
                        </span>
                      )}
                    </td>
                    <td className="px-3 py-3 font-mono">
                      {r.adaptation_weight_delta > 0 ? (
                        <span className="text-rose-400 font-bold">
                          -{r.adaptation_weight_delta.toFixed(2)}
                        </span>
                      ) : (
                        <span className="text-slate-500 font-normal">None (0.00)</span>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

