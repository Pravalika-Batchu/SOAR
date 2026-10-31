import React, { useState } from 'react';
import { SecurityAlert } from '../types';
import { ShieldAlert, Filter, Search, Terminal, AlertCircle } from 'lucide-react';

interface SecurityMonitoringProps {
  alerts: SecurityAlert[];
  onTriggerAlert: (alertType: string) => void;
}

export const SecurityMonitoring: React.FC<SecurityMonitoringProps> = ({ alerts, onTriggerAlert }) => {
  const [filterSeverity, setFilterSeverity] = useState<string>('ALL');
  const [filterSource, setFilterSource] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedAlert, setSelectedAlert] = useState<SecurityAlert | null>(null);

  const filteredAlerts = alerts.filter((alert) => {
    if (filterSeverity !== 'ALL' && alert.severity !== filterSeverity) return false;
    if (filterSource !== 'ALL' && alert.source !== filterSource) return false;
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      return (
        alert.alert_type.toLowerCase().includes(q) ||
        alert.source_ip.toLowerCase().includes(q) ||
        alert.destination_ip.toLowerCase().includes(q) ||
        (alert.signature && alert.signature.toLowerCase().includes(q))
      );
    }
    return true;
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-rose-500" />
            Security Monitoring & NIDS Ingestion
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Unified ingestion stream aggregating Suricata EVE JSON alerts, Zeek flow metadata, and simulated test traffic.
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => onTriggerAlert('DOS_SYN_FLOOD')}
            className="px-3 py-1.5 rounded-lg bg-rose-600/20 hover:bg-rose-600/30 text-rose-300 border border-rose-500/40 text-xs font-medium transition"
          >
            + Ingest Suricata Alert
          </button>
          <button
            onClick={() => onTriggerAlert('PORT_SCAN')}
            className="px-3 py-1.5 rounded-lg bg-amber-600/20 hover:bg-amber-600/30 text-amber-300 border border-amber-500/40 text-xs font-medium transition"
          >
            + Ingest Zeek Flow
          </button>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="flex flex-wrap items-center gap-3 p-4 rounded-xl bg-[#111827] border border-[#1F2937] text-xs">
        <div className="flex-1 min-w-[200px] relative">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search by IP, threat signature, or category..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-3 py-2 bg-slate-900 border border-slate-800 rounded-lg text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500"
          />
        </div>

        <div className="flex items-center space-x-2">
          <Filter className="w-4 h-4 text-slate-400" />
          <select
            value={filterSeverity}
            onChange={(e) => setFilterSeverity(e.target.value)}
            className="bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-slate-300 focus:outline-none focus:border-blue-500"
          >
            <option value="ALL">All Severities</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
          </select>
          <select
            value={filterSource}
            onChange={(e) => setFilterSource(e.target.value)}
            className="bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-slate-300 focus:outline-none focus:border-blue-500"
          >
            <option value="ALL">All Sources</option>
            <option value="SURICATA">Suricata EVE</option>
            <option value="ZEEK">Zeek Network</option>
            <option value="TEST_GENERATOR">Testbed Generator</option>
          </select>
        </div>
      </div>

      {/* Alerts Grid & Detail Split */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 p-5 rounded-xl bg-[#111827] border border-[#1F2937]">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-900 text-slate-400 uppercase text-[10px] tracking-wider">
                <tr>
                  <th className="px-3 py-2.5 rounded-l-lg">Time</th>
                  <th className="px-3 py-2.5">Source</th>
                  <th className="px-3 py-2.5">Threat</th>
                  <th className="px-3 py-2.5">Severity</th>
                  <th className="px-3 py-2.5">Source IP</th>
                  <th className="px-3 py-2.5">Target IP</th>
                  <th className="px-3 py-2.5 rounded-r-lg text-right">Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {filteredAlerts.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="px-3 py-6 text-center text-slate-500">
                      No security alerts matching the current filter.
                    </td>
                  </tr>
                ) : (
                  filteredAlerts.map((alert) => (
                    <tr 
                      key={alert.id}
                      onClick={() => setSelectedAlert(alert)}
                      className={`cursor-pointer transition hover:bg-slate-800/50 ${
                        selectedAlert?.id === alert.id ? 'bg-blue-900/20' : ''
                      }`}
                    >
                      <td className="px-3 py-3 text-slate-400 font-mono text-[11px]">
                        {new Date(alert.timestamp).toLocaleTimeString()}
                      </td>
                      <td className="px-3 py-3">
                        <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-slate-800 text-slate-300">
                          {alert.source}
                        </span>
                      </td>
                      <td className="px-3 py-3 font-semibold text-white">
                        {alert.alert_type.replace(/_/g, ' ')}
                      </td>
                      <td className="px-3 py-3">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          alert.severity === 'CRITICAL' ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40' :
                          alert.severity === 'HIGH' ? 'bg-orange-500/20 text-orange-300 border border-orange-500/40' :
                          alert.severity === 'MEDIUM' ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40' :
                          'bg-slate-700 text-slate-300'
                        }`}>
                          {alert.severity}
                        </span>
                      </td>
                      <td className="px-3 py-3 font-mono text-rose-400">{alert.source_ip}</td>
                      <td className="px-3 py-3 font-mono text-cyan-400">{alert.destination_ip}</td>
                      <td className="px-3 py-3 text-right">
                        <button className="text-blue-400 hover:text-blue-300 text-xs font-medium">
                          View
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Selected Alert JSON / Telemetry Inspector */}
        <div className="p-5 rounded-xl bg-[#111827] border border-[#1F2937] flex flex-col">
          <div className="flex items-center justify-between mb-3 pb-2 border-b border-slate-800">
            <h3 className="text-sm font-semibold text-white flex items-center gap-1.5">
              <Terminal className="w-4 h-4 text-cyan-400" />
              Alert Telemetry Payload
            </h3>
            {selectedAlert && (
              <span className="font-mono text-xs text-slate-400">ID: #{selectedAlert.id}</span>
            )}
          </div>

          {selectedAlert ? (
            <div className="space-y-4 text-xs overflow-y-auto max-h-[500px]">
              <div>
                <span className="text-slate-500 block mb-1">Signature Description:</span>
                <p className="p-2.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-200 font-mono">
                  {selectedAlert.signature || 'Generic anomaly classification from behavioral heuristics'}
                </p>
              </div>

              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="p-2.5 rounded bg-slate-900 border border-slate-800">
                  <span className="text-slate-500 block text-[10px]">PROTOCOL</span>
                  <span className="font-semibold text-white">{selectedAlert.protocol}</span>
                </div>
                <div className="p-2.5 rounded bg-slate-900 border border-slate-800">
                  <span className="text-slate-500 block text-[10px]">PORTS</span>
                  <span className="font-mono text-white">
                    {selectedAlert.source_port || '*'}:{selectedAlert.destination_port || '*'}
                  </span>
                </div>
              </div>

              <div>
                <span className="text-slate-500 block mb-1">Raw Ingestion Metadata:</span>
                <pre className="p-3 rounded-lg bg-slate-950 border border-slate-800 text-[11px] font-mono text-emerald-400 overflow-x-auto">
                  {JSON.stringify(selectedAlert.raw_payload || {
                    source: selectedAlert.source,
                    alert_type: selectedAlert.alert_type,
                    source_ip: selectedAlert.source_ip,
                    destination_ip: selectedAlert.destination_ip,
                    severity: selectedAlert.severity,
                    timestamp: selectedAlert.timestamp
                  }, null, 2)}
                </pre>
              </div>
            </div>
          ) : (
            <div className="my-auto text-center py-12 text-slate-500 text-xs">
              <AlertCircle className="w-8 h-8 mx-auto mb-2 text-slate-600" />
              Click any alert row on the left to inspect signature details, port bindings, and raw EVE telemetry.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

