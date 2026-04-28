import type { AlertSeverity } from './alerts'

export type ReportStatus = 'PENDING' | 'STREAMING' | 'COMPLETE' | 'FAILED'

export interface MitreTactic {
  tactic_id: string
  tactic_name: string
  techniques: string[]
}

export interface TimelineEntry {
  timestamp: string
  event: string
}

export interface AffectedAsset {
  hostname: string | null
  ip: string | null
  role: string | null
}

export interface IRReport {
  id: string
  alert_ids: string[]
  status: ReportStatus
  title: string
  executive_summary: string
  mitre_tactics: MitreTactic[]
  affected_assets: AffectedAsset[]
  confidence: number
  severity: AlertSeverity
  timeline: TimelineEntry[]
  recommendations: string[]
  raw_stream: string
  created_at: string
  completed_at: string | null
}

export interface GenerateReportRequest {
  alert_ids: string[]
}
