import React from 'react';
import { Shield, Activity, Bell, RefreshCw, Cpu, Layers } from 'lucide-react';
import { MetricsSummary, SystemStatus } from '../types';

interface NavbarProps {
  metrics: MetricsSummary | null;
  status: SystemStatus | null;
  onRefresh: () => void;
  isLoading: boolean;
  onTriggerScenario: (scenario: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  metrics,
  status,
  onRefresh,
  isLoading,
  onTriggerScenario
}) => {
  return (
    <header className="h-16 bg-[#111827] border-b border-[#1F2937] px-6 flex items-center justify-between sticky top-0 z-50">
      {/* Brand & Title */}
      <div className="flex items-center space-x-3">
        <div className="p-2 bg-blue-600/20 border border-blue-500/40 rounded-lg text-blue-400">
          <Shield className="w-6 h-6 text-blue-400 animate-pulse" />
        </div>
        <div>
          <p className="text-xs text-slate-400">Adaptive Cybersecurity Response & Dynamic Autonomy</p>
        </div>
      </div>

      {/* Quick Scenario Triggers */}
      <div className="hidden lg:flex items-center space-x-2 bg-slate-900/80 p-1.5 rounded-lg border border-slate-800 text-xs">
        <span className="text-slate-400 font-medium px-2 flex items-center">
          <Cpu className="w-3.5 h-3.5 mr-1 text-slate-400" /> Test Scenario:
        </span>
        <button
          onClick={() => onTriggerScenario('DOS')}
          className="px-2.5 py-1 rounded bg-rose-500/20 hover:bg-rose-500/30 text-rose-300 border border-rose-500/40 transition font-medium"
        >
          DoS SYN
        </button>
        <button
          onClick={() => onTriggerScenario('PORT_SCAN')}
          className="px-2.5 py-1 rounded bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 border border-amber-500/40 transition font-medium"
        >
          Port Scan
        </button>
        <button
          onClick={() => onTriggerScenario('BRUTE_FORCE')}
          className="px-2.5 py-1 rounded bg-purple-500/20 hover:bg-purple-500/30 text-purple-300 border border-purple-500/40 transition font-medium"
        >
          Brute Force
        </button>
        <button
          onClick={() => onTriggerScenario('UNKNOWN')}
          className="px-2.5 py-1 rounded bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 border border-cyan-500/40 transition font-medium"
        >
          Unknown Anomaly
        </button>
        <button
          onClick={() => onTriggerScenario('QOS_SENSITIVE')}
          className="px-2.5 py-1 rounded bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 border border-emerald-500/40 transition font-medium"
        >
          QoS Sensitive
        </button>
      </div>

      {/* Network Adapter Mode & Operational Status */}
      <div className="flex items-center space-x-4">
        {/* Adapter Mode Badge */}
        <div className="flex items-center space-x-2 px-3 py-1.5 rounded-md bg-slate-900 border border-slate-800 text-xs">
          <Layers className="w-4 h-4 text-cyan-400" />
          <span className="text-slate-400">Adapter:</span>
          <span className="font-semibold text-cyan-300">
            {metrics?.adapter_mode === 'RYU' ? 'LIVE RYU SDN' : 'SIMULATED ADAPTER'}
          </span>
        </div>

        {/* Pending Approvals Indicator */}
        {metrics && metrics.pending_approvals > 0 && (
          <div className="flex items-center space-x-1.5 px-3 py-1.5 rounded-md bg-amber-500/20 border border-amber-500/50 text-amber-300 text-xs font-semibold animate-pulse">
            <Bell className="w-4 h-4 text-amber-400" />
            <span>{metrics.pending_approvals} Approval Required</span>
          </div>
        )}

        {/* Refresh Button */}
        <button
          onClick={onRefresh}
          disabled={isLoading}
          className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white border border-slate-700 transition"
          title="Refresh SOC Telemetry"
        >
          <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin text-blue-400' : ''}`} />
        </button>
      </div>
    </header>
  );
};

