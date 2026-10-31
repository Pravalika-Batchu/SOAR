import React from 'react';
import { 
  ShieldAlert, 
  CheckCircle2, 
  Clock, 
  Cpu, 
  Activity, 
  TrendingUp, 
  AlertTriangle,
  ArrowRight
} from 'lucide-react';
import { Incident, MetricsSummary } from '../types';
import { 
  ResponsiveContainer, 
  PieChart, 
  Pie, 
  Cell, 
  Tooltip, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid 
} from 'recharts';

interface OverviewProps {
  metrics: MetricsSummary | null;
  incidents: Incident[];
  onSelectIncident: (id: number) => void;
  onNavigate: (page: any) => void;
}

const AUTONOMY_COLORS = {
  ZERO_TOUCH: '#3B82F6', // Blue
  GUARDED: '#10B981',    // Emerald
  HUMAN_APPROVAL: '#F59E0B' // Amber
};

export const Overview: React.FC<OverviewProps> = ({
  metrics,
  incidents,
  onSelectIncident,
  onNavigate
}) => {
  const autonomyData = metrics ? [
    { name: 'Zero-Touch', value: metrics.autonomy_distribution.ZERO_TOUCH || 0, color: AUTONOMY_COLORS.ZERO_TOUCH },
    { name: 'Guarded', value: metrics.autonomy_distribution.GUARDED || 0, color: AUTONOMY_COLORS.GUARDED },
    { name: 'Human Approval', value: metrics.autonomy_distribution.HUMAN_APPROVAL || 0, color: AUTONOMY_COLORS.HUMAN_APPROVAL }
  ] : [];

  const networkPerformanceData = [
    { name: 'Throughput', value: metrics?.current_throughput_mbps || 94.2, unit: 'Mbps' },
    { name: 'Latency', value: metrics?.current_latency_ms || 1.25, unit: 'ms' },
    { name: 'Loss', value: metrics?.current_packet_loss_pct || 0.1, unit: '%' }
  ];

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-5 rounded-xl bg-gradient-to-r from-blue-900/30 via-slate-900 to-slate-900 border border-blue-500/20">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            SOC Autonomous Response Overview
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Real-time evaluation of threat mitigation, policy validation, and self-trust levels.
          </p>
        </div>
        <div className="flex items-center space-x-3 text-xs">
          <div className="px-3 py-1.5 rounded-lg bg-blue-500/10 border border-blue-500/30 text-blue-300">
            <strong>System Self-Trust Model:</strong> Active (Multi-Factor Scoring)
          </div>
          <div className="px-3 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-300">
            <strong>Safety Policies:</strong> Hard Overrides Enforced
          </div>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <div className="p-4 rounded-xl bg-[#111827] border border-[#1F2937]">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium">Total Alerts</span>
            <ShieldAlert className="w-4 h-4 text-blue-400" />
          </div>
          <div className="text-2xl font-bold text-white">{metrics?.total_alerts || 0}</div>
          <p className="text-[11px] text-slate-500 mt-1">Ingested via NIDS</p>
        </div>

        <div className="p-4 rounded-xl bg-[#111827] border border-[#1F2937]">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium">Active Incidents</span>
            <Activity className="w-4 h-4 text-rose-400" />
          </div>
          <div className="text-2xl font-bold text-rose-400">{metrics?.active_incidents || 0}</div>
          <p className="text-[11px] text-slate-500 mt-1">Requiring action</p>
        </div>

        <div className="p-4 rounded-xl bg-[#111827] border border-[#1F2937]">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium">Pending Approvals</span>
            <Clock className="w-4 h-4 text-amber-400" />
          </div>
          <div className={`text-2xl font-bold ${(metrics?.pending_approvals || 0) > 0 ? 'text-amber-400' : 'text-slate-300'}`}>
            {metrics?.pending_approvals || 0}
          </div>
          <p className="text-[11px] text-slate-500 mt-1">Human-in-the-loop</p>
        </div>

        <div className="p-4 rounded-xl bg-[#111827] border border-[#1F2937]">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium">Auto-Executions</span>
            <Cpu className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-bold text-cyan-400">{metrics?.autonomous_executions || 0}</div>
          <p className="text-[11px] text-slate-500 mt-1">Zero-Touch & Guarded</p>
        </div>

        <div className="p-4 rounded-xl bg-[#111827] border border-[#1F2937]">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium">Throughput</span>
            <TrendingUp className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-emerald-400">{metrics?.current_throughput_mbps?.toFixed(1) || 94.2} <span className="text-xs font-normal text-slate-400">Mbps</span></div>
          <p className="text-[11px] text-slate-500 mt-1">SLA compliant</p>
        </div>

        <div className="p-4 rounded-xl bg-[#111827] border border-[#1F2937]">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium">Packet Loss</span>
            <AlertTriangle className="w-4 h-4 text-slate-400" />
          </div>
          <div className="text-2xl font-bold text-white">{metrics?.current_packet_loss_pct?.toFixed(2) || 0.10} <span className="text-xs font-normal text-slate-400">%</span></div>
          <p className="text-[11px] text-slate-500 mt-1">Latency: {metrics?.current_latency_ms?.toFixed(2) || 1.25} ms</p>
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Autonomy Mode Distribution Chart */}
        <div className="p-5 rounded-xl bg-[#111827] border border-[#1F2937] flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-semibold text-white flex items-center justify-between">
              <span>Autonomy Mode Distribution</span>
              <span className="text-xs text-slate-400 font-normal">Dynamic Autonomy Decisions</span>
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">Ratio of Zero-Touch vs Guarded vs Human Approvals</p>
          </div>
          <div className="h-48 my-3">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={autonomyData}
                  cx="50%"
                  cy="50%"
                  innerRadius={45}
                  outerRadius={70}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {autonomyData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1F2937', borderColor: '#374151', borderRadius: '8px', fontSize: '12px' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="grid grid-cols-3 gap-2 pt-2 border-t border-slate-800 text-center text-xs">
            <div>
              <span className="inline-block w-2.5 h-2.5 rounded-full bg-blue-500 mr-1" />
              <span className="text-slate-400">Zero-Touch:</span>
              <div className="font-bold text-white">{metrics?.autonomy_distribution.ZERO_TOUCH || 0}</div>
            </div>
            <div>
              <span className="inline-block w-2.5 h-2.5 rounded-full bg-emerald-500 mr-1" />
              <span className="text-slate-400">Guarded:</span>
              <div className="font-bold text-white">{metrics?.autonomy_distribution.GUARDED || 0}</div>
            </div>
            <div>
              <span className="inline-block w-2.5 h-2.5 rounded-full bg-amber-500 mr-1" />
              <span className="text-slate-400">Approval:</span>
              <div className="font-bold text-white">{metrics?.autonomy_distribution.HUMAN_APPROVAL || 0}</div>
            </div>
          </div>
        </div>

        {/* Live Network Health Telemetry */}
        <div className="p-5 rounded-xl bg-[#111827] border border-[#1F2937] flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-semibold text-white flex items-center justify-between">
              <span>Network Telemetry & QoS</span>
              <span className={`text-xs font-medium ${(metrics?.current_packet_loss_pct || 0) > 2.0 ? 'text-rose-400' : 'text-emerald-400'}`}>
                ● {(metrics?.current_packet_loss_pct || 0) > 2.0 ? 'Degraded' : 'Normal Nominal'}
              </span>
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">Live simulated network datapath metrics</p>
          </div>
          <div className="space-y-4 my-auto py-2">
            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-slate-400">Throughput ({(metrics?.current_throughput_mbps || 94.2).toFixed(1)} Mbps / 100 Mbps)</span>
                <span className="text-emerald-400 font-semibold">{(metrics?.current_throughput_mbps || 94.2).toFixed(1)}%</span>
              </div>
              <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                <div className="bg-emerald-500 h-full rounded-full transition-all duration-500" style={{ width: `${Math.min(100, metrics?.current_throughput_mbps || 94.2)}%` }} />
              </div>
            </div>
            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-slate-400">Switch Latency ({(metrics?.current_latency_ms || 1.25).toFixed(2)} ms / 15.0 ms max)</span>
                <span className="text-cyan-400 font-semibold">{(metrics?.current_latency_ms || 1.25).toFixed(2)} ms</span>
              </div>
              <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                <div className="bg-cyan-500 h-full rounded-full transition-all duration-500" style={{ width: `${Math.min(100, ((metrics?.current_latency_ms || 1.25) / 15.0) * 100)}%` }} />
              </div>
            </div>
            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-slate-400">Packet Loss ({(metrics?.current_packet_loss_pct || 0.1).toFixed(2)}% / 2.0% max)</span>
                <span className={`font-semibold ${(metrics?.current_packet_loss_pct || 0) > 1.5 ? 'text-rose-400' : 'text-blue-400'}`}>{(metrics?.current_packet_loss_pct || 0.1).toFixed(2)}%</span>
              </div>
              <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                <div className={`h-full rounded-full transition-all duration-500 ${(metrics?.current_packet_loss_pct || 0) > 1.5 ? 'bg-rose-500' : 'bg-blue-500'}`} style={{ width: `${Math.min(100, ((metrics?.current_packet_loss_pct || 0.1) / 2.0) * 100)}%` }} />
              </div>
            </div>
          </div>
          <div className="text-[11px] text-slate-500 border-t border-slate-800 pt-2">
            Simulated via network_simulator.py — updates every 5s
          </div>
        </div>

        {/* Quick Action & System Core Health */}
        <div className="p-5 rounded-xl bg-[#111827] border border-[#1F2937] flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-semibold text-white">Research Architecture Status</h3>
            <p className="text-xs text-slate-500 mt-0.5">Modular engine execution health</p>
          </div>
          <div className="space-y-2.5 my-3 text-xs">
            <div className="flex items-center justify-between p-2 rounded bg-slate-900 border border-slate-800">
              <span className="text-slate-300">1. Response Reliability Engine</span>
              <span className="text-emerald-400 font-semibold">Active</span>
            </div>
            <div className="flex items-center justify-between p-2 rounded bg-slate-900 border border-slate-800">
              <span className="text-slate-300">2. Policy / Constraint Engine</span>
              <span className="text-emerald-400 font-semibold">Active (4 Rules)</span>
            </div>
            <div className="flex items-center justify-between p-2 rounded bg-slate-900 border border-slate-800">
              <span className="text-slate-300">3. Autonomy Trust Engine</span>
              <span className="text-emerald-400 font-semibold">Active</span>
            </div>
            <div className="flex items-center justify-between p-2 rounded bg-slate-900 border border-slate-800">
              <span className="text-slate-300">4. Dynamic Autonomy Controller</span>
              <span className="text-emerald-400 font-semibold">Active (3 Modes)</span>
            </div>
            <div className="flex items-center justify-between p-2 rounded bg-slate-900 border border-slate-800">
              <span className="text-slate-300">5. Outcome Evaluation Engine</span>
              <span className="text-emerald-400 font-semibold">Active</span>
            </div>
            <div className="flex items-center justify-between p-2 rounded bg-slate-900 border border-slate-800">
              <span className="text-slate-300">6. Experience Memory</span>
              <span className="text-emerald-400 font-semibold">Active (CBR)</span>
            </div>
          </div>
          <button
            onClick={() => onNavigate('approvals')}
            className="w-full py-2 rounded-lg bg-blue-600/20 hover:bg-blue-600/30 text-blue-400 border border-blue-500/40 text-xs font-semibold transition flex items-center justify-center space-x-1"
          >
            <span>Review Pending Approvals</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Recent Incidents Table */}
      <div className="p-5 rounded-xl bg-[#111827] border border-[#1F2937]">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-semibold text-white">Recent Security Incidents</h3>
            <p className="text-xs text-slate-500">Traceable incident lifecycle and autonomy assignments</p>
          </div>
          <button
            onClick={() => onNavigate('incidents')}
            className="text-xs text-blue-400 hover:text-blue-300 flex items-center space-x-1 font-medium"
          >
            <span>View All Incidents</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900 text-slate-400 uppercase tracking-wider text-[10px]">
              <tr>
                <th className="px-4 py-2.5 rounded-l-lg">ID</th>
                <th className="px-4 py-2.5">Threat Type</th>
                <th className="px-4 py-2.5">Attacker IP</th>
                <th className="px-4 py-2.5">Target IP</th>
                <th className="px-4 py-2.5">Threat Conf.</th>
                <th className="px-4 py-2.5">Trust Score</th>
                <th className="px-4 py-2.5">Autonomy Mode</th>
                <th className="px-4 py-2.5">Status</th>
                <th className="px-4 py-2.5 rounded-r-lg text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {incidents.length === 0 ? (
                <tr>
                  <td colSpan={9} className="px-4 py-6 text-center text-slate-500">
                    No active incidents. Use the top scenario triggers (e.g. "DoS SYN") to test.
                  </td>
                </tr>
              ) : (
                incidents.slice(0, 6).map((inc) => (
                  <tr key={inc.id} className="hover:bg-slate-800/40 transition">
                    <td className="px-4 py-3 font-mono text-slate-400">#{inc.id}</td>
                    <td className="px-4 py-3 font-semibold text-white">
                      {inc.threat_type.replace(/_/g, ' ')}
                    </td>
                    <td className="px-4 py-3 font-mono text-rose-300">{inc.source_ip}</td>
                    <td className="px-4 py-3 font-mono text-cyan-300">{inc.destination_ip}</td>
                    <td className="px-4 py-3 font-medium text-slate-200">
                      {(inc.threat_confidence * 100).toFixed(0)}%
                    </td>
                    <td className="px-4 py-3 font-bold text-blue-400">
                      {inc.autonomy_trust_score ? (inc.autonomy_trust_score * 100).toFixed(0) + '%' : 'Pending'}
                    </td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        inc.execution_mode === 'ZERO_TOUCH'
                          ? 'bg-blue-500/20 text-blue-300 border border-blue-500/40'
                          : inc.execution_mode === 'GUARDED'
                          ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                          : 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                      }`}>
                        {inc.execution_mode || 'EVALUATING'}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-slate-800 text-slate-300">
                        {inc.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right">
                      <button
                        onClick={() => onSelectIncident(inc.id)}
                        className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-blue-400 hover:text-blue-300 transition text-[11px] font-medium"
                      >
                        Inspect
                      </button>
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

