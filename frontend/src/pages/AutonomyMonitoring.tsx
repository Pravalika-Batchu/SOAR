import React, { useState, useEffect } from 'react';
import { TrustLog } from '../types';
import { api } from '../services/api';
import { Cpu, TrendingUp, ShieldCheck, RefreshCw } from 'lucide-react';
import { 
  ResponsiveContainer, 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend 
} from 'recharts';

export const AutonomyMonitoring: React.FC = () => {
  const [logs, setLogs] = useState<TrustLog[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  const loadLogs = async () => {
    try {
      setLoading(true);
      const data = await api.getTrustHistory(50);
      setLogs(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLogs();
  }, []);

  const chartData = [...logs].reverse().map((l) => ({
    time: new Date(l.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
    'Trust Score': Number((l.trust_score * 100).toFixed(1)),
    'Reliability Contribution': Number((l.reliability_contribution * 100).toFixed(1)),
    'Uncertainty Penalty': Number((l.uncertainty_penalty * 100).toFixed(1)),
    'Failure Penalty': Number((l.historical_failure_penalty * 100).toFixed(1))
  }));

  const latest = logs.length > 0 ? logs[0] : null;

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Cpu className="w-5 h-5 text-cyan-400" />
            Dynamic Autonomy & System Self-Trust Monitoring
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Real-time quantification of how much the system trusts itself to dispatch responses autonomously versus requesting human authorization.
          </p>
        </div>
        <button
          onClick={loadLogs}
          className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 self-start"
          title="Refresh Trust History"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-blue-400' : ''}`} />
        </button>
      </div>

      {/* Threshold Status Banner */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
        <div className="p-4 rounded-xl bg-blue-950/30 border border-blue-500/40">
          <span className="font-bold text-blue-400 block mb-1">ZERO-TOUCH AUTOMATION</span>
          <p className="text-slate-300">
            Trust Score <strong>≥ 85.0%</strong> and Policy <strong>ALLOW</strong>. Complete autonomous flow execution.
          </p>
        </div>
        <div className="p-4 rounded-xl bg-emerald-950/30 border border-emerald-500/40">
          <span className="font-bold text-emerald-400 block mb-1">GUARDED AUTOMATION</span>
          <p className="text-slate-300">
            Trust Score <strong>55.0% - 84.9%</strong> or Policy <strong>RESTRICT</strong>. Time-limited rules & rate throttling.
          </p>
        </div>
        <div className="p-4 rounded-xl bg-amber-950/30 border border-amber-500/40">
          <span className="font-bold text-amber-400 block mb-1">HUMAN APPROVAL</span>
          <p className="text-slate-300">
            Trust Score <strong>&lt; 55.0%</strong> or Policy <strong>ESCALATE / REJECT</strong>. Mandatory SOC analyst sign-off.
          </p>
        </div>
      </div>

      {/* Historical Trust Trend Chart */}
      <div className="p-5 rounded-xl bg-[#111827] border border-[#1F2937]">
        <h3 className="text-sm font-semibold text-white mb-2">
          System Self-Trust & Factor Penalties Over Time
        </h3>
        <p className="text-xs text-slate-500 mb-4">
          Time-series of dynamic trust score adjustments influenced by model uncertainty and historical failure penalties.
        </p>

        {logs.length === 0 ? (
          <div className="text-center py-12 text-slate-500 text-xs">
            No trust log entries recorded yet. Trigger an incident to observe real-time trust scoring.
          </div>
        ) : (
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData} margin={{ top: 10, right: 20, left: 0, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" />
                <XAxis dataKey="time" stroke="#9CA3AF" fontSize={11} />
                <YAxis stroke="#9CA3AF" fontSize={11} domain={[0, 100]} />
                <Tooltip contentStyle={{ backgroundColor: '#111827', borderColor: '#374151', borderRadius: '8px', fontSize: '12px' }} />
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
                <Line type="monotone" dataKey="Trust Score" stroke="#06B6D4" strokeWidth={3} dot={{ r: 4 }} />
                <Line type="monotone" dataKey="Reliability Contribution" stroke="#3B82F6" strokeWidth={2} />
                <Line type="monotone" dataKey="Uncertainty Penalty" stroke="#F59E0B" strokeWidth={2} strokeDasharray="4 4" />
                <Line type="monotone" dataKey="Failure Penalty" stroke="#EF4444" strokeWidth={2} strokeDasharray="3 3" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {/* Trust Logs Table */}
      <div className="p-5 rounded-xl bg-[#111827] border border-[#1F2937]">
        <h3 className="text-sm font-semibold text-white mb-3">Audit Log of Autonomy Decisions</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900 text-slate-400 uppercase text-[10px] tracking-wider">
              <tr>
                <th className="px-3 py-2.5 rounded-l-lg">Time</th>
                <th className="px-3 py-2.5">Incident ID</th>
                <th className="px-3 py-2.5">Trust Score</th>
                <th className="px-3 py-2.5">Autonomy Mode</th>
                <th className="px-3 py-2.5">Reliability Contrib.</th>
                <th className="px-3 py-2.5">Uncertainty Pen.</th>
                <th className="px-3 py-2.5">Failure Pen.</th>
                <th className="px-3 py-2.5 rounded-r-lg">Decision Rationale</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {logs.map((log) => (
                <tr key={log.id} className="hover:bg-slate-800/40 transition">
                  <td className="px-3 py-3 text-slate-400 font-mono text-[11px]">
                    {new Date(log.created_at).toLocaleTimeString()}
                  </td>
                  <td className="px-3 py-3 font-mono text-cyan-300">#{log.incident_id}</td>
                  <td className="px-3 py-3 font-bold text-cyan-400">
                    {(log.trust_score * 100).toFixed(1)}%
                  </td>
                  <td className="px-3 py-3">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      log.autonomy_mode === 'ZERO_TOUCH' ? 'bg-blue-500/20 text-blue-300' :
                      log.autonomy_mode === 'GUARDED' ? 'bg-emerald-500/20 text-emerald-300' :
                      'bg-amber-500/20 text-amber-300'
                    }`}>
                      {log.autonomy_mode}
                    </span>
                  </td>
                  <td className="px-3 py-3 font-mono text-slate-300">
                    {(log.reliability_contribution * 100).toFixed(1)}%
                  </td>
                  <td className="px-3 py-3 font-mono text-amber-400">
                    -{(log.uncertainty_penalty * 100).toFixed(1)}%
                  </td>
                  <td className="px-3 py-3 font-mono text-rose-400">
                    -{(log.historical_failure_penalty * 100).toFixed(1)}%
                  </td>
                  <td className="px-3 py-3 text-slate-400 max-w-xs truncate">
                    {log.rationale}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

