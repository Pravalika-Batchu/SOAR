import React, { useState, useEffect } from 'react';
import { Play, Square, Zap, AlertTriangle, Activity, Wifi } from 'lucide-react';
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

const API_BASE = '/api';

interface SimulationStatus {
  running: boolean;
  mode: string;
  current_attack: string | null;
  attack_target: string | null;
  attack_source: string | null;
  attack_cycles_remaining: number;
  cycle_count: number;
  alerts_generated: number;
  incidents_created: number;
  last_telemetry: Record<string, any>;
}

interface TelemetrySample {
  id: number;
  timestamp: string;
  throughput_mbps: number;
  packet_loss_pct: number;
  latency_ms: number;
  packets_per_sec: number;
  active_flows: number;
}

const ATTACK_SCENARIOS = [
  { id: 'DOS_SYN_FLOOD', label: 'DoS SYN Flood', color: 'rose', severity: 'HIGH', icon: '🌊', target: '10.0.0.10 (Web)' },
  { id: 'PORT_SCAN', label: 'Port Scan', color: 'yellow', severity: 'MEDIUM', icon: '🔍', target: '10.0.0.101 (Desktop)' },
  { id: 'BRUTE_FORCE', label: 'Brute Force', color: 'orange', severity: 'HIGH', icon: '🔓', target: '10.0.0.20 (DB)' },
  { id: 'UNKNOWN_ANOMALY', label: 'Unknown Anomaly', color: 'purple', severity: 'MEDIUM', icon: '❓', target: '10.0.0.102 (Client)' },
  { id: 'DNS_AMPLIFICATION_FLOOD', label: 'DNS Flood (QoS)', color: 'red', severity: 'HIGH', icon: '📡', target: '10.0.0.53 (DNS)' },
];

export const SimulationControl: React.FC = () => {
  const [status, setStatus] = useState<SimulationStatus | null>(null);
  const [telemetry, setTelemetry] = useState<TelemetrySample[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [lastAction, setLastAction] = useState<string | null>(null);

  const fetchStatus = async () => {
    try {
      const res = await fetch(`${API_BASE}/simulation/status`);
      if (res.ok) setStatus(await res.json());
    } catch (e) {
      console.error('Failed to fetch simulation status:', e);
    }
  };

  const fetchTelemetry = async () => {
    try {
      const res = await fetch(`${API_BASE}/simulation/telemetry?limit=20`);
      if (res.ok) setTelemetry(await res.json());
    } catch (e) {
      console.error('Failed to fetch telemetry:', e);
    }
  };

  useEffect(() => {
    fetchStatus();
    fetchTelemetry();
    const interval = setInterval(() => {
      fetchStatus();
      fetchTelemetry();
    }, 4000);
    return () => clearInterval(interval);
  }, []);

  const handleStart = async () => {
    setIsLoading(true);
    try {
      await fetch(`${API_BASE}/simulation/start`, { method: 'POST' });
      setLastAction('Simulation engine started');
      await fetchStatus();
    } finally {
      setIsLoading(false);
    }
  };

  const handleStop = async () => {
    setIsLoading(true);
    try {
      await fetch(`${API_BASE}/simulation/stop`, { method: 'POST' });
      setLastAction('Simulation engine stopped');
      await fetchStatus();
    } finally {
      setIsLoading(false);
    }
  };

  const handleTriggerAttack = async (attackType: string) => {
    try {
      const res = await fetch(`${API_BASE}/simulation/trigger/${attackType}?duration_cycles=2`, { method: 'POST' });
      const data = await res.json();
      setLastAction(`Triggered: ${attackType} (${data.source_ip} → ${data.target_ip})`);
      await fetchStatus();
    } catch (e) {
      console.error('Failed to trigger attack:', e);
    }
  };

  const chartData = telemetry.map(s => ({
    time: s.timestamp ? new Date(s.timestamp).toLocaleTimeString() : '',
    throughput: s.throughput_mbps,
    pps: s.packets_per_sec / 100, // scale for chart readability
    latency: s.latency_ms,
  }));

  const isRunning = status?.running ?? false;
  const hasAttack = !!status?.current_attack;

  return (
    <div className="space-y-6">
      {/* SIMULATION MODE Banner */}
      <div className="flex items-center gap-3 p-4 rounded-xl bg-amber-500/10 border border-amber-500/40">
        <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0" />
        <div>
          <span className="text-amber-300 font-bold text-sm">SIMULATION MODE</span>
          <p className="text-amber-200/70 text-xs mt-0.5">
            All network traffic, alerts, and incidents generated here are synthetic. 
            They simulate realistic attack patterns for academic evaluation purposes.
            No real network traffic is generated.
          </p>
        </div>
      </div>

      {/* Control Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Engine Status & Control */}
        <div className="p-5 rounded-xl bg-[#111827] border border-[#1F2937]">
          <h3 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
            <Activity className="w-4 h-4 text-blue-400" />
            Simulation Engine
          </h3>
          
          <div className="space-y-3 mb-4">
            <div className="flex items-center justify-between text-sm">
              <span className="text-slate-400">Status</span>
              <span className={`font-bold flex items-center gap-1.5 ${isRunning ? 'text-emerald-400' : 'text-slate-500'}`}>
                <span className={`w-2 h-2 rounded-full ${isRunning ? 'bg-emerald-400 animate-pulse' : 'bg-slate-600'}`} />
                {isRunning ? 'RUNNING' : 'STOPPED'}
              </span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-slate-400">Mode</span>
              <span className="text-blue-300 font-medium">SIMULATION</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-slate-400">Cycles Run</span>
              <span className="text-slate-200 font-mono">{status?.cycle_count ?? 0}</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-slate-400">Alerts Generated</span>
              <span className="text-rose-400 font-bold">{status?.alerts_generated ?? 0}</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-slate-400">Incidents Created</span>
              <span className="text-amber-400 font-bold">{status?.incidents_created ?? 0}</span>
            </div>
          </div>

          <div className="space-y-2">
            {!isRunning ? (
              <button
                onClick={handleStart}
                disabled={isLoading}
                className="w-full py-2.5 rounded-lg bg-emerald-600/20 hover:bg-emerald-600/30 border border-emerald-500/40 text-emerald-300 text-sm font-semibold flex items-center justify-center gap-2 transition"
              >
                <Play className="w-4 h-4" />
                Start Simulation
              </button>
            ) : (
              <button
                onClick={handleStop}
                disabled={isLoading}
                className="w-full py-2.5 rounded-lg bg-rose-600/20 hover:bg-rose-600/30 border border-rose-500/40 text-rose-300 text-sm font-semibold flex items-center justify-center gap-2 transition"
              >
                <Square className="w-4 h-4" />
                Stop Simulation
              </button>
            )}
          </div>

          {lastAction && (
            <p className="text-xs text-slate-500 mt-3 border-t border-slate-800 pt-2">{lastAction}</p>
          )}
        </div>

        {/* Current Attack Status */}
        <div className="p-5 rounded-xl bg-[#111827] border border-[#1F2937]">
          <h3 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
            <Zap className="w-4 h-4 text-rose-400" />
            Active Attack Scenario
          </h3>
          
          {hasAttack ? (
            <div className="space-y-3">
              <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/30">
                <div className="text-rose-300 font-bold text-sm">{status!.current_attack?.replace(/_/g, ' ')}</div>
                <div className="text-xs text-slate-400 mt-2 space-y-1">
                  <div>Attacker: <span className="text-rose-300 font-mono">{status!.attack_source}</span></div>
                  <div>Target: <span className="text-cyan-300 font-mono">{status!.attack_target}</span></div>
                  <div>Remaining cycles: <span className="text-amber-300 font-mono">{status!.attack_cycles_remaining}</span></div>
                </div>
              </div>
              <div className="text-xs text-slate-500 text-center">
                Attack alert + incident being generated...
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center h-32 text-slate-600 text-sm">
              <Wifi className="w-8 h-8 mb-2 opacity-50" />
              <span>No active attack</span>
              <span className="text-xs mt-1">Normal baseline traffic</span>
            </div>
          )}

          {/* Last Telemetry */}
          {status?.last_telemetry && Object.keys(status.last_telemetry).length > 0 && (
            <div className="mt-4 pt-3 border-t border-slate-800 text-xs space-y-1">
              <div className="text-slate-500 font-medium mb-1">Last Telemetry</div>
              <div className="flex justify-between text-slate-400">
                <span>Throughput</span>
                <span className="text-emerald-300">{status.last_telemetry.throughput_mbps?.toFixed(1)} Mbps</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>Pkt/s</span>
                <span className="text-blue-300">{status.last_telemetry.packets_per_sec?.toFixed(0)}</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>Latency</span>
                <span className="text-cyan-300">{status.last_telemetry.latency_ms?.toFixed(1)} ms</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>Pkt Loss</span>
                <span className="text-rose-300">{status.last_telemetry.packet_loss_pct?.toFixed(2)}%</span>
              </div>
            </div>
          )}
        </div>

        {/* Attack Trigger Buttons */}
        <div className="p-5 rounded-xl bg-[#111827] border border-[#1F2937]">
          <h3 className="text-sm font-semibold text-white mb-1 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-amber-400" />
            Trigger Attack Scenario
          </h3>
          <p className="text-xs text-slate-500 mb-4">Generates synthetic traffic + auto-creates alert & incident</p>
          
          <div className="space-y-2">
            {ATTACK_SCENARIOS.map(scenario => (
              <button
                key={scenario.id}
                onClick={() => handleTriggerAttack(scenario.id)}
                disabled={!isRunning}
                className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg border text-xs font-medium transition
                  ${!isRunning
                    ? 'opacity-40 cursor-not-allowed bg-slate-900 border-slate-800 text-slate-500'
                    : 'bg-slate-900 border-slate-700 hover:border-slate-500 text-slate-200 hover:text-white'
                  }`}
              >
                <span className="flex items-center gap-2">
                  <span>{scenario.icon}</span>
                  <span>{scenario.label}</span>
                </span>
                <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold
                  ${scenario.severity === 'HIGH' ? 'bg-rose-500/20 text-rose-400' : 'bg-amber-500/20 text-amber-400'}`}>
                  {scenario.severity}
                </span>
              </button>
            ))}
          </div>
          
          {!isRunning && (
            <p className="text-xs text-amber-400/70 mt-3 text-center">Start simulation to enable triggers</p>
          )}
        </div>
      </div>

      {/* Live Telemetry Chart */}
      <div className="p-5 rounded-xl bg-[#111827] border border-[#1F2937]">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-semibold text-white">Live Network Telemetry</h3>
            <p className="text-xs text-slate-500 mt-0.5">Real-time simulated traffic metrics (updates every 4s)</p>
          </div>
          <span className={`text-xs px-2 py-1 rounded font-medium ${isRunning ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30' : 'bg-slate-800 text-slate-500'}`}>
            {isRunning ? '● LIVE' : '○ PAUSED'}
          </span>
        </div>

        {chartData.length > 0 ? (
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" />
                <XAxis dataKey="time" tick={{ fontSize: 10, fill: '#6B7280' }} interval="preserveStartEnd" />
                <YAxis tick={{ fontSize: 10, fill: '#6B7280' }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#111827', borderColor: '#374151', borderRadius: '8px', fontSize: '11px' }}
                  formatter={(val: number, name: string) => {
                    if (name === 'throughput') return [`${val.toFixed(1)} Mbps`, 'Throughput'];
                    if (name === 'pps') return [`${(val * 100).toFixed(0)} pps`, 'Packets/s (×100)'];
                    if (name === 'latency') return [`${val.toFixed(1)} ms`, 'Latency'];
                    return [val, name];
                  }}
                />
                <Legend wrapperStyle={{ fontSize: '11px' }} />
                <Line type="monotone" dataKey="throughput" stroke="#10B981" strokeWidth={2} dot={false} name="Throughput (Mbps)" />
                <Line type="monotone" dataKey="latency" stroke="#F59E0B" strokeWidth={2} dot={false} name="Latency (ms)" />
                <Line type="monotone" dataKey="pps" stroke="#EF4444" strokeWidth={2} dot={false} name="Pkt/s (÷100)" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <div className="h-56 flex items-center justify-center text-slate-600 text-sm">
            No telemetry data yet. Start simulation to generate live data.
          </div>
        )}
      </div>
    </div>
  );
};

