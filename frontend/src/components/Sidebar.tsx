import React from 'react';
import { 
  LayoutDashboard, 
  ShieldAlert, 
  FileText, 
  Sliders, 
  CheckSquare, 
  Cpu, 
  CheckCircle2, 
  History, 
  Scale, 
  Network 
} from 'lucide-react';

export type PageId = 
  | 'overview'
  | 'alerts'
  | 'incidents'
  | 'reliability'
  | 'approvals'
  | 'autonomy'
  | 'outcomes'
  | 'experience'
  | 'policies'
  | 'topology';

interface SidebarProps {
  activePage: PageId;
  onSelectPage: (page: PageId) => void;
  pendingApprovalsCount: number;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activePage,
  onSelectPage,
  pendingApprovalsCount
}) => {
  const navItems = [
    { id: 'overview' as PageId, label: 'Overview SOC', icon: LayoutDashboard },
    { id: 'alerts' as PageId, label: 'Security Alerts', icon: ShieldAlert },
    { id: 'incidents' as PageId, label: 'Incident Lifecycle', icon: FileText },
    { id: 'reliability' as PageId, label: 'Reliability Scoring', icon: Sliders },
    { 
      id: 'approvals' as PageId, 
      label: 'Human Approval', 
      icon: CheckSquare, 
      badge: pendingApprovalsCount > 0 ? pendingApprovalsCount : undefined 
    },
    { id: 'autonomy' as PageId, label: 'Autonomy Monitor', icon: Cpu },
    { id: 'outcomes' as PageId, label: 'Outcome Evaluation', icon: CheckCircle2 },
    { id: 'experience' as PageId, label: 'Experience Memory', icon: History },
    { id: 'policies' as PageId, label: 'Policy Rules', icon: Scale },
    { id: 'topology' as PageId, label: 'Network Topology', icon: Network },
  ];

  return (
    <aside className="w-64 bg-[#111827] border-r border-[#1F2937] flex flex-col justify-between py-4">
      <div className="space-y-1 px-3">
        <div className="px-3 pb-2 text-[11px] font-semibold tracking-wider uppercase text-slate-500">
          SOC Operations & Control
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activePage === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelectPage(item.id)}
              className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition ${
                isActive
                  ? 'bg-blue-600 text-white shadow-md shadow-blue-500/20'
                  : 'text-slate-300 hover:bg-slate-800/80 hover:text-white'
              }`}
            >
              <div className="flex items-center space-x-3">
                <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                <span>{item.label}</span>
              </div>
              {item.badge !== undefined && (
                <span className={`px-2 py-0.5 text-xs rounded-full font-bold ${
                  isActive ? 'bg-white text-blue-600' : 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                }`}>
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Footer Info */}
      <div className="px-4 py-3 mx-3 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-400">
        <div className="flex items-center justify-between mb-1">
          <span className="font-medium text-slate-300">Mininet & Ryu SDN</span>
          <span className="inline-block w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
        </div>
        <p className="text-[11px] text-slate-500">OpenFlow 1.3 Active Telemetry</p>
      </div>
    </aside>
  );
};

