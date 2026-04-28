import type { AlertSeverity } from './alerts'

export type ApprovalStatus = 'PENDING' | 'APPROVED' | 'REJECTED' | 'EXECUTED'

export interface BashScript {
  body: string
  rationale: string
  target_hosts: string[]
  requires_root: boolean
  sha256: string
}

export interface RemediationItem {
  id: string
  report_id: string
  severity: AlertSeverity
  script: BashScript
  approval_status: ApprovalStatus
  auto_approved: boolean
  approver: string | null
  rejection_reason: string | null
  created_at: string
  actioned_at: string | null
}

export interface ApprovalAction {
  approver: string
  reason?: string
}
