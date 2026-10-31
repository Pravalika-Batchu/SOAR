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
    let payload: Partial<SecurityAlert> = {};
    if (scenario === 'DOS') {
      payload = {
        source: 'SURICATA',
        alert_type: 'DOS_SYN_FLOOD',
        severity: 'HIGH',
        source_ip: '10.0.0.99',
        destination_ip: '10.0.0.10',
        destination_port: 80,
        protocol: 'TCP',
        signature: 'ET DOS Potential SYN Flood on HTTP Web Server'
      };
    } else if (scenario === 'PORT_SCAN') {
      payload = {
        source: 'ZEEK',
        alert_type: 'PORT_SCAN',
        severity: 'MEDIUM',
        source_ip: '10.0.0.99',
        destination_ip: '10.0.0.101',
        destination_port: 0,
        protocol: 'TCP',
        signature: 'Zeek Port Sweep Detection (SYN scan 100+ ports)'
      };
    } else if (scenario === 'BRUTE_FORCE') {
      payload = {
        source: 'SURICATA',
        alert_type: 'BRUTE_FORCE',
        severity: 'HIGH',
        source_ip: '10.0.0.99',
        destination_ip: '10.0.0.20',
        destination_port: 22,
        protocol: 'TCP',
        signature: 'ET SCAN Potential SSH Brute Force Authentication'
      };
    } else if (scenario === 'UNKNOWN') {
      payload = {
        source: 'TEST_GENERATOR',
        alert_type: 'UNKNOWN_ANOMALY',
        severity: 'MEDIUM',
        source_ip: '10.0.0.99',
        destination_ip: '10.0.0.102',
        destination_port: 4444,
        protocol: 'UDP',
        signature: 'Statistical Out-of-Distribution Packet Velocity Spike'
      };
    } else if (scenario === 'QOS_SENSITIVE') {
      payload = {
        source: 'SURICATA',
        alert_type: 'DOS_SYN_FLOOD',
        severity: 'HIGH',
        source_ip: '10.0.0.99',
        destination_ip: '10.0.0.53',
        destination_port: 53,
        protocol: 'UDP',
        signature: 'ET DOS DNS Amplification Flood Targeting Critical Core DNS'
      };
    }

    try {
      const createdAlert = await api.createAlert(payload);
      await fetchGlobalData();
      if (createdAlert.incident_id) {
        setSelectedIncidentId(createdAlert.incident_id);
        setActivePage('incidents');
      }
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
        </main>
      </div>
    </div>
  );
};
export default App;

