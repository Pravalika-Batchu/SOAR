import React, { useState, useEffect } from 'react';
import { OutcomeEvaluation } from '../types';
import { api } from '../services/api';
import { CheckCircle2, TrendingDown, Activity, AlertOctagon, RefreshCw } from 'lucide-react';
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

export const OutcomeEvaluationView: React.FC = () => {
  const [outcomes, setOutcomes] = useState<OutcomeEvaluation[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  const loadOutcomes = async () => {
    try {
      setLoading(true);
      const data = await api.getOutcomes(50);
      setOutcomes(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadOutcomes();
  }, []);

  const chartData = outcomes.map((o) => ({
    name: `Inc #${o.incident_id} (${o.action_type})`,
    'Mitigation %': Number(o.actual_attack_reduction_pct.toFixed(1)),
    'QoS Collateral % (Lower better)': Number(o.actual_qos_impact_pct.toFixed(1)),
    'Composite Efficacy': Number((o.composite_success_score * 100).toFixed(1))
  }));

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <CheckCircle2 className="w-5 h-5 text-emerald-400" />
            Outcome-Based Evaluation Engine (Engine 5)
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Empirical post-execution verification comparing predicted versus actual threat reduction and detecting collateral service degradation.
          </p>
        </div>
        <button
          onClick={loadOutcomes}
          className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 self-start"
          title="Refresh Outcomes"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-blue-400' : ''}`} />
        </button>
      </div>

      {/* Comparison Chart */}
      <div className="p-5 rounded-xl bg-[#111827] border border-[#1F2937]">
        <h3 className="text-sm font-semibold text-white mb-2">
          Empirical Mitigation vs Collateral QoS Degradation
        </h3>
        <p className="text-xs text-slate-500 mb-4">
          Core Research Invariant: An action executing successfully on OpenFlow does NOT equal security success if legitimate service SLA was compromised.
        </p>

        {outcomes.length === 0 ? (
          <div className="text-center py-12 text-slate-500 text-xs">
            No outcome evaluations recorded yet. Execute an approved incident response to observe telemetry metrics.
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
                <Bar dataKey="Mitigation %" fill="#10B981" radius={[4, 4, 0, 0]} />
                <Bar dataKey="QoS Collateral % (Lower better)" fill="#F43F5E" radius={[4, 4, 0, 0]} />
                <Bar dataKey="Composite Efficacy" fill="#3B82F6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {/* Outcomes Table */}
      <div className="p-5 rounded-xl bg-[#111827] border border-[#1F2937]">
        <h3 className="text-sm font-semibold text-white mb-3">Historical Outcome Evaluations</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900 text-slate-400 uppercase text-[10px] tracking-wider">
              <tr>
                <th className="px-3 py-2.5 rounded-l-lg">Time</th>
                <th className="px-3 py-2.5">Inc ID</th>
                <th className="px-3 py-2.5">Action Executed</th>
                <th className="px-3 py-2.5">Pre/Post Attack PPS</th>
                <th className="px-3 py-2.5">Mitigation %</th>
                <th className="px-3 py-2.5">Throughput</th>
                <th className="px-3 py-2.5">QoS Impact %</th>
                <th className="px-3 py-2.5">Classification</th>
                <th className="px-3 py-2.5 rounded-r-lg">Efficacy Score</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {outcomes.map((o) => (
                <tr key={o.id} className="hover:bg-slate-800/40 transition">
                  <td className="px-3 py-3 text-slate-400 font-mono text-[11px]">
                    {new Date(o.evaluated_at).toLocaleTimeString()}
                  </td>
                  <td className="px-3 py-3 font-mono text-cyan-300">#{o.incident_id}</td>
                  <td className="px-3 py-3 font-semibold text-white">{o.action_type}</td>
                  <td className="px-3 py-3 font-mono text-slate-300">
                    {o.pre_attack_pps.toFixed(0)} → {o.post_attack_pps.toFixed(0)}
                  </td>
                  <td className="px-3 py-3 font-bold text-emerald-400">
                    {o.actual_attack_reduction_pct.toFixed(1)}%
                  </td>
                  <td className="px-3 py-3 font-mono text-slate-200">
                    {o.post_legitimate_throughput_mbps.toFixed(1)} Mbps
                  </td>
                  <td className="px-3 py-3 font-mono text-rose-400">
                    {o.actual_qos_impact_pct.toFixed(1)}%
                  </td>
                  <td className="px-3 py-3">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      o.success_status === 'SUCCESS' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40' :
                      o.success_status === 'PARTIAL_SUCCESS' ? 'bg-blue-500/20 text-blue-300 border border-blue-500/40' :
                      'bg-rose-500/20 text-rose-300 border border-rose-500/40'
                    }`}>
                      {o.success_status}
                    </span>
                  </td>
                  <td className="px-3 py-3 font-bold text-cyan-400">
                    {o.composite_success_score.toFixed(2)}
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

