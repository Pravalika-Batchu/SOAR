import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { Sidebar, PageId } from './components/Sidebar';
import { Overview } from './pages/Overview';
import { SecurityMonitoring } from './pages/SecurityMonitoring';
import { IncidentDetails } from './pages/IncidentDetails';
import { ReliabilityComparison } from './pages/ReliabilityComparison';
import { ApprovalCenter } from './pages/ApprovalCenter';
import { AutonomyMonitoring } from './pages/AutonomyMonitoring';
import { OutcomeEvaluationView } from './pages/OutcomeEvaluationView';
import { ExperienceMemoryView } from './pages/ExperienceMemoryView';
import { PolicyManagement } from './pages/PolicyManagement';
import { NetworkTopologyView } from './pages/NetworkTopologyView';
import { SimulationControl } from './pages/SimulationControl';

import { api } from './services/api';
import { MetricsSummary, SystemStatus, SecurityAlert, Incident } from './types';

export const App: React.FC = () => {
  const [activePage, setActivePage] = useState<PageId>('overview');
  const [selectedIncidentId, setSelectedIncidentId] = useState<number | null>(null);

  const [metrics, setMetrics] = useState<MetricsSummary | null>(null);
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [alerts, setAlerts] = useState<SecurityAlert[]>([]);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const fetchGlobalData = async () => {
    setIsLoading(true);
    try {
      const [m, s, a, inc] = await Promise.all([
        api.getMetricsSummary(),
        api.getSystemStatus(),
        api.getAlerts(50),
        api.getIncidents(50)
      ]);
      setMetrics(m);
      setStatus(s);
      setAlerts(a);
      setIncidents(inc);
    } catch (err) {
      console.error('Failed to fetch SOC telemetry:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchGlobalData();
    const interval = setInterval(fetchGlobalData, 10000); // 10s auto refresh
    return () => clearInterval(interval);
  }, []);

  const handleTriggerScenario = async (scenario: string) => {
    const attackMap: Record<string, string> = {
      'DOS': 'DOS_SYN_FLOOD',
      'PORT_SCAN': 'PORT_SCAN',
      'BRUTE_FORCE': 'BRUTE_FORCE',
      'UNKNOWN': 'UNKNOWN_ANOMALY',
      'QOS_SENSITIVE': 'DNS_AMPLIFICATION_FLOOD',
    };

    const attackType = attackMap[scenario];
    if (!attackType) return;

    try {
      await fetch('/api/simulation/start', { method: 'POST' });
      await fetch(`/api/simulation/trigger/${attackType}?duration_cycles=2`, { method: 'POST' });

      // Poll slightly after attack generation to catch the dynamic incident
      setTimeout(async () => {
        await fetchGlobalData();
        try {
          const incRes = await fetch('/api/incidents?limit=5');
          const incs = await incRes.json();
          if (incs.length > 0) {
            setSelectedIncidentId(incs[0].id);
            setActivePage('incidents');
          }
        } catch (e) {
          console.error(e);
        }
      }, 1500);

      await fetchGlobalData();
    } catch (e) {
      console.error(e);
    }
  };

  const handleSelectIncident = (id: number) => {
    setSelectedIncidentId(id);
    setActivePage('incidents');
  };

  return (
    <div className="min-h-screen bg-[#0B0F17] flex flex-col font-sans">
      <Navbar
        metrics={metrics}
        status={status}
        onRefresh={fetchGlobalData}
        isLoading={isLoading}
        onTriggerScenario={handleTriggerScenario}
      />

      <div className="flex flex-1 overflow-hidden">
        <Sidebar
          activePage={activePage}
          onSelectPage={(page) => {
            setActivePage(page);
            if (page !== 'incidents') {
              setSelectedIncidentId(null);
            }
          }}
          pendingApprovalsCount={metrics?.pending_approvals || 0}
        />

        <main className="flex-1 overflow-y-auto p-6">
          {activePage === 'overview' && (
            <Overview
              metrics={metrics}
              incidents={incidents}
              onSelectIncident={handleSelectIncident}
              onNavigate={(page) => setActivePage(page)}
            />
          )}

          {activePage === 'alerts' && (
            <SecurityMonitoring
              alerts={alerts}
              onTriggerAlert={(type) => handleTriggerScenario(type === 'PORT_SCAN' ? 'PORT_SCAN' : 'DOS')}
            />
          )}

          {activePage === 'incidents' && (
            selectedIncidentId ? (
              <IncidentDetails
                incidentId={selectedIncidentId}
                onBack={() => setSelectedIncidentId(null)}
                onRefresh={fetchGlobalData}
              />
            ) : (
              <Overview
                metrics={metrics}
                incidents={incidents}
                onSelectIncident={handleSelectIncident}
                onNavigate={(page) => setActivePage(page)}
              />
            )
          )}

          {activePage === 'reliability' && (
            <ReliabilityComparison
              incidents={incidents}
              onSelectIncident={handleSelectIncident}
            />
          )}

          {activePage === 'approvals' && (
            <ApprovalCenter
              onRefresh={fetchGlobalData}
              onSelectIncident={handleSelectIncident}
            />
          )}

          {activePage === 'autonomy' && <AutonomyMonitoring />}

          {activePage === 'outcomes' && <OutcomeEvaluationView />}

          {activePage === 'experience' && <ExperienceMemoryView />}

          {activePage === 'policies' && <PolicyManagement />}

          {activePage === 'topology' && <NetworkTopologyView />}

          {activePage === 'simulation' && <SimulationControl />}
        </main>
      </div>
    </div>
  );
};
export default App;

