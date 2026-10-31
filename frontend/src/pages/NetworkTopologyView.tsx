import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { Network, Server, Shield, Laptop, RefreshCw } from 'lucide-react';

export const NetworkTopologyView: React.FC = () => {
  const [topology, setTopology] = useState<{ nodes: any[]; assets: any[] }>({ nodes: [], assets: [] });
  const [loading, setLoading] = useState<boolean>(true);

  const loadTopology = async () => {
    try {
      setLoading(true);
      const data = await api.getTopology();
      setTopology(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTopology();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Network className="w-5 h-5 text-cyan-400" />
            Mininet Virtual SDN Network Topology
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Software-Defined Network testbed topology managed by OpenFlow 1.3 Ryu controller across Open vSwitch bridges.
          </p>
        </div>
        <button
          onClick={loadTopology}
          className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 self-start"
          title="Refresh Topology"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-blue-400' : ''}`} />
        </button>
      </div>

      {/* Visual Diagram Representation */}
      <div className="p-6 rounded-xl bg-[#111827] border border-[#1F2937]">
        <h3 className="text-sm font-semibold text-white mb-4">
          Virtual Switch Fabric & Host Bindings (10.0.0.0/24)
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 py-4">
          {/* Core Switch s1 Area */}
          <div className="p-5 rounded-xl bg-slate-900/80 border border-blue-500/30 space-y-4">
            <div className="flex items-center justify-between pb-2 border-b border-slate-800">
              <span className="font-bold text-blue-400 text-sm flex items-center gap-2">
                <Network className="w-4 h-4" /> Switch s1 (Core Service Switch)
              </span>
              <span className="text-[10px] bg-blue-900/60 text-blue-300 px-2 py-0.5 rounded font-mono">
                DPID: 0000000000000001
              </span>
            </div>

            <div className="space-y-2">
              <div className="p-3 rounded-lg bg-[#111827] border border-emerald-500/40 flex items-center justify-between text-xs">
                <div>
                  <span className="font-semibold text-white block">h1 (Web Server 01)</span>
                  <span className="font-mono text-cyan-400">10.0.0.10:80</span>
                </div>
                <span className="px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 font-bold text-[10px]">
                  CRITICAL ASSET
                </span>
              </div>

              <div className="p-3 rounded-lg bg-[#111827] border border-emerald-500/40 flex items-center justify-between text-xs">
                <div>
                  <span className="font-semibold text-white block">h2 (DNS Core Server)</span>
                  <span className="font-mono text-cyan-400">10.0.0.53:53</span>
                </div>
                <span className="px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 font-bold text-[10px]">
                  CRITICAL ASSET
                </span>
              </div>

              <div className="p-3 rounded-lg bg-[#111827] border border-blue-500/30 flex items-center justify-between text-xs">
                <div>
                  <span className="font-semibold text-white block">h3 (Database Cluster)</span>
                  <span className="font-mono text-cyan-400">10.0.0.20:5432</span>
                </div>
                <span className="px-2 py-0.5 rounded bg-orange-500/20 text-orange-300 font-bold text-[10px]">
                  HIGH CRITICALITY
                </span>
              </div>
            </div>
          </div>

          {/* Access Switch s2 Area */}
          <div className="p-5 rounded-xl bg-slate-900/80 border border-purple-500/30 space-y-4">
            <div className="flex items-center justify-between pb-2 border-b border-slate-800">
              <span className="font-bold text-purple-400 text-sm flex items-center gap-2">
                <Network className="w-4 h-4" /> Switch s2 (Access Switch)
              </span>
              <span className="text-[10px] bg-purple-900/60 text-purple-300 px-2 py-0.5 rounded font-mono">
                DPID: 0000000000000002
              </span>
            </div>

            <div className="space-y-2">
              <div className="p-3 rounded-lg bg-[#111827] border border-slate-800 flex items-center justify-between text-xs">
                <div>
                  <span className="font-semibold text-white block">h4 (Corporate Workstation)</span>
                  <span className="font-mono text-slate-300">10.0.0.101</span>
                </div>
                <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-400 text-[10px]">
                  LOW (Desktop)
                </span>
              </div>

              <div className="p-3 rounded-lg bg-[#111827] border border-rose-500/50 flex items-center justify-between text-xs">
                <div>
                  <span className="font-semibold text-rose-300 block">h5 (Attacker Simulation Node)</span>
                  <span className="font-mono text-rose-400">10.0.0.99</span>
                </div>
                <span className="px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 font-bold text-[10px]">
                  ATTACK INJECTOR
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Asset Inventory Table */}
      <div className="p-5 rounded-xl bg-[#111827] border border-[#1F2937]">
        <h3 className="text-sm font-semibold text-white mb-3">Monitored Lab Asset Inventory</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900 text-slate-400 uppercase text-[10px] tracking-wider">
              <tr>
                <th className="px-3 py-2.5 rounded-l-lg">IP Address</th>
                <th className="px-3 py-2.5">Hostname</th>
                <th className="px-3 py-2.5">Service Type</th>
                <th className="px-3 py-2.5">Criticality</th>
                <th className="px-3 py-2.5">QoS Sensitivity SLA</th>
                <th className="px-3 py-2.5 rounded-r-lg">Isolation State</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {topology.assets.map((a) => (
                <tr key={a.ip} className="hover:bg-slate-800/40 transition">
                  <td className="px-3 py-3 font-mono text-cyan-400">{a.ip}</td>
                  <td className="px-3 py-3 font-semibold text-white">{a.hostname}</td>
                  <td className="px-3 py-3 text-slate-300">{a.service}</td>
                  <td className="px-3 py-3">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      a.criticality === 'CRITICAL' ? 'bg-rose-500/20 text-rose-300' :
                      a.criticality === 'HIGH' ? 'bg-orange-500/20 text-orange-300' :
                      'bg-slate-700 text-slate-300'
                    }`}>
                      {a.criticality}
                    </span>
                  </td>
                  <td className="px-3 py-3 font-mono text-slate-200">
                    {(a.qos_sensitivity * 100).toFixed(0)}%
                  </td>
                  <td className="px-3 py-3">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                      a.isolated ? 'bg-rose-500/20 text-rose-300' : 'bg-emerald-500/20 text-emerald-300'
                    }`}>
                      {a.isolated ? 'ISOLATED' : 'ONLINE'}
                    </span>
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

