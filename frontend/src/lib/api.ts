import type { NormalizedEvent, RawAlertIn } from '../types/alerts'
import type { ApprovalAction, RemediationItem } from '../types/remediation'
import type { GenerateReportRequest, IRReport } from '../types/reports'
import { API_BASE } from './constants'

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const resp = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!resp.ok) {
    const text = await resp.text()
    throw new Error(`HTTP ${resp.status}: ${text}`)
  }
  return resp.json() as Promise<T>
}

export const api = {
  health: () => request<{ status: string; ollama_reachable: boolean; alert_count: number }>('/health'),

  alerts: {
    ingest: (payload: RawAlertIn) =>
      request<NormalizedEvent>('/alerts/ingest', { method: 'POST', body: JSON.stringify(payload) }),
    list: (limit = 100, offset = 0) =>
      request<NormalizedEvent[]>(`/alerts?limit=${limit}&offset=${offset}`),
    get: (id: string) => request<NormalizedEvent>(`/alerts/${id}`),
  },

  reports: {
    generate: (req: GenerateReportRequest) =>
      request<IRReport>('/reports/generate', { method: 'POST', body: JSON.stringify(req) }),
    get: (id: string) => request<IRReport>(`/reports/${id}`),
    list: () => request<IRReport[]>('/reports'),
  },

  remediation: {
    queue: () => request<RemediationItem[]>('/remediation/queue'),
    get: (id: string) => request<RemediationItem>(`/remediation/${id}`),
    approve: (id: string, action: ApprovalAction) =>
      request(`/remediation/${id}/approve`, { method: 'POST', body: JSON.stringify(action) }),
    reject: (id: string, action: ApprovalAction) =>
      request(`/remediation/${id}/reject`, { method: 'POST', body: JSON.stringify(action) }),
  },
}
