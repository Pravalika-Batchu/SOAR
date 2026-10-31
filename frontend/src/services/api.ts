import { 
  Incident, 
  SecurityAlert, 
  CandidateResponse, 
  HumanApproval, 
  PolicyRule, 
  TrustLog, 
  OutcomeEvaluation, 
  ExperienceRecord, 
  SystemStatus, 
  MetricsSummary 
} from '../types';

const API_BASE = '/api';

export const api = {
  // System & Health
  async getSystemStatus(): Promise<SystemStatus> {
    const res = await fetch(`${API_BASE}/system/status`);
    if (!res.ok) throw new Error('Failed to fetch system status');
    return res.json();
  },

  async getMetricsSummary(): Promise<MetricsSummary> {
    const res = await fetch(`${API_BASE}/metrics/summary`);
    if (!res.ok) throw new Error('Failed to fetch metrics summary');
    return res.json();
  },

  async getTopology(): Promise<{ nodes: any[]; assets: any[] }> {
    const res = await fetch(`${API_BASE}/system/topology`);
    if (!res.ok) throw new Error('Failed to fetch topology');
    return res.json();
  },

  // Alerts
  async getAlerts(limit = 50): Promise<SecurityAlert[]> {
    const res = await fetch(`${API_BASE}/alerts?limit=${limit}`);
    if (!res.ok) throw new Error('Failed to fetch alerts');
    return res.json();
  },

  async createAlert(alert: Partial<SecurityAlert>): Promise<SecurityAlert> {
    const res = await fetch(`${API_BASE}/alerts`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(alert)
    });
    if (!res.ok) throw new Error('Failed to create alert');
    return res.json();
  },

  // Incidents
  async getIncidents(limit = 50): Promise<Incident[]> {
    const res = await fetch(`${API_BASE}/incidents?limit=${limit}`);
    if (!res.ok) throw new Error('Failed to fetch incidents');
    return res.json();
  },

  async getIncident(id: number): Promise<Incident> {
    const res = await fetch(`${API_BASE}/incidents/${id}`);
    if (!res.ok) throw new Error('Failed to fetch incident');
    return res.json();
  },

  async analyzeIncident(id: number): Promise<Incident> {
    const res = await fetch(`${API_BASE}/incidents/${id}/analyze`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to analyze incident');
    return res.json();
  },

  // Responses & Candidates
  async getCandidateResponses(incidentId: number): Promise<CandidateResponse[]> {
    const res = await fetch(`${API_BASE}/incidents/${incidentId}/candidates`);
    if (!res.ok) throw new Error('Failed to fetch candidates');
    return res.json();
  },

  async evaluateResponses(incidentId: number): Promise<CandidateResponse[]> {
    const res = await fetch(`${API_BASE}/incidents/${incidentId}/evaluate-responses`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to evaluate responses');
    return res.json();
  },

  async executeResponse(incidentId: number, candidateId?: number): Promise<any> {
    const res = await fetch(`${API_BASE}/incidents/${incidentId}/execute`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ candidate_id: candidateId })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to execute response');
    }
    return res.json();
  },

  async requestApproval(incidentId: number, candidateId: number): Promise<any> {
    const res = await fetch(`${API_BASE}/incidents/${incidentId}/request-approval/${candidateId}`, {
      method: 'POST'
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to request approval');
    }
    return res.json();
  },

  // Approvals
  async getPendingApprovals(): Promise<HumanApproval[]> {
    const res = await fetch(`${API_BASE}/approvals/pending`);
    if (!res.ok) throw new Error('Failed to fetch approvals');
    return res.json();
  },

  async approveResponse(id: number, comment?: string): Promise<HumanApproval> {
    const res = await fetch(`${API_BASE}/approvals/${id}/approve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ operator_comment: comment })
    });
    if (!res.ok) throw new Error('Failed to approve');
    return res.json();
  },

  async rejectResponse(id: number, comment?: string): Promise<HumanApproval> {
    const res = await fetch(`${API_BASE}/approvals/${id}/reject`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ operator_comment: comment })
    });
    if (!res.ok) throw new Error('Failed to reject');
    return res.json();
  },

  // Trust & Logs
  async getTrustHistory(limit = 50): Promise<TrustLog[]> {
    const res = await fetch(`${API_BASE}/trust/history?limit=${limit}`);
    if (!res.ok) throw new Error('Failed to fetch trust history');
    return res.json();
  },

  // Policies
  async getPolicies(): Promise<PolicyRule[]> {
    const res = await fetch(`${API_BASE}/policies`);
    if (!res.ok) throw new Error('Failed to fetch policies');
    return res.json();
  },

  // Outcomes & Experience
  async getOutcomes(limit = 50): Promise<OutcomeEvaluation[]> {
    const res = await fetch(`${API_BASE}/outcomes?limit=${limit}`);
    if (!res.ok) throw new Error('Failed to fetch outcomes');
    return res.json();
  },

  async getExperience(limit = 50): Promise<ExperienceRecord[]> {
    const res = await fetch(`${API_BASE}/experience?limit=${limit}`);
    if (!res.ok) throw new Error('Failed to fetch experience records');
    return res.json();
  }
};

