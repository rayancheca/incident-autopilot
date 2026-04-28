import type { IRReport } from './reports'

export type WSMessageType = 'token' | 'status' | 'error' | 'final'

export interface WSToken {
  type: 'token'
  report_id: string
  token: string
}

export interface WSStatus {
  type: 'status'
  report_id: string
  status: string
}

export interface WSError {
  type: 'error'
  report_id: string
  message: string
}

export interface WSFinal {
  type: 'final'
  report_id: string
  report: IRReport
}

export type WSMessage = WSToken | WSStatus | WSError | WSFinal
