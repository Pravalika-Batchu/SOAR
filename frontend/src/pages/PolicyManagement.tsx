import React, { useState, useEffect } from 'react';
import { PolicyRule } from '../types';
import { api } from '../services/api';
import { Scale, Plus, ShieldCheck, AlertTriangle, RefreshCw } from 'lucide-react';

export const PolicyManagement: React.FC = () => {
  const [policies, setPolicies] = useState<PolicyRule[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  const loadPolicies = async () => {
    try {
      setLoading(true);
      const data = await api.getPolicies();
      setPolicies(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPolicies();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Scale className="w-5 h-5 text-amber-400" />
            Safety Policy & Constraint Engine (Engine 2)
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Enforces hard operational constraints, QoS service protection, and mandatory safety overrides that strictly supersede autonomy trust scores.
          </p>
        </div>
        <button
          onClick={loadPolicies}
          className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 self-start"
          title="Refresh Policies"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-blue-400' : ''}`} />
        </button>
      </div>

      {/* Policies Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {policies.map((p) => (
          <div 
            key={p.id} 
            className="p-5 rounded-xl bg-[#111827] border border-[#1F2937] flex flex-col justify-between space-y-4"
          >
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="font-bold text-white text-sm">{p.name}</span>
                <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                  p.enforcement_action === 'REJECT' ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40' :
                  p.enforcement_action === 'ESCALATE' ? 'bg-orange-500/20 text-orange-300 border border-orange-500/40' :
                  p.enforcement_action === 'RESTRICT' ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40' :
                  'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                }`}>
                  Action: {p.enforcement_action}
                </span>
              </div>
              <p className="text-xs text-slate-400 mb-3">{p.description}</p>

              <div className="space-y-1.5 text-xs">
                <div className="flex justify-between p-2 rounded bg-slate-900 border border-slate-800">
                  <span className="text-slate-500">Category:</span>
                  <span className="font-semibold text-slate-200">{p.rule_type}</span>
                </div>
                <div className="flex justify-between p-2 rounded bg-slate-900 border border-slate-800">
                  <span className="text-slate-500">Mandatory Override:</span>
                  <span className={p.is_mandatory ? 'text-amber-400 font-bold' : 'text-slate-400'}>
                    {p.is_mandatory ? 'YES (Cannot be bypassed)' : 'Configurable'}
                  </span>
                </div>
                <div className="flex justify-between p-2 rounded bg-slate-900 border border-slate-800">
                  <span className="text-slate-500">Evaluation Priority:</span>
                  <span className="font-mono text-cyan-400">Level {p.priority}</span>
                </div>
              </div>
            </div>

            <div className="pt-2 border-t border-slate-800">
              <span className="text-[10px] text-slate-500 block mb-1">RULE CONDITION PARAMS:</span>
              <pre className="p-2 rounded bg-slate-950 text-[10px] font-mono text-cyan-300 overflow-x-auto">
                {JSON.stringify(p.condition_json, null, 2)}
              </pre>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

