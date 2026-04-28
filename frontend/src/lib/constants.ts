import type { AlertSeverity } from '../types/alerts'


export const SEVERITY_COLORS: Record<AlertSeverity, { bg: string; text: string; border: string; glow: string }> = {
  CRITICAL: {
    bg: 'bg-red-500/10',
    text: 'text-red-400',
    border: 'border-red-500/50',
    glow: 'shadow-red-500/20',
  },
  HIGH: {
    bg: 'bg-amber-500/10',
    text: 'text-amber-400',
    border: 'border-amber-500/50',
    glow: 'shadow-amber-500/20',
  },
  MEDIUM: {
    bg: 'bg-yellow-500/10',
    text: 'text-yellow-400',
    border: 'border-yellow-500/50',
    glow: 'shadow-yellow-500/20',
  },
  LOW: {
    bg: 'bg-blue-500/10',
    text: 'text-blue-400',
    border: 'border-blue-500/50',
    glow: 'shadow-blue-500/20',
  },
}

export const TACTIC_COLORS: Record<string, string> = {
  TA0001: 'border-purple-500 text-purple-300 bg-purple-500/10',   // Initial Access
  TA0002: 'border-red-500 text-red-300 bg-red-500/10',            // Execution
  TA0003: 'border-orange-500 text-orange-300 bg-orange-500/10',   // Persistence
  TA0004: 'border-amber-500 text-amber-300 bg-amber-500/10',      // Privilege Escalation
  TA0005: 'border-lime-500 text-lime-300 bg-lime-500/10',         // Defense Evasion
  TA0006: 'border-cyan-500 text-cyan-300 bg-cyan-500/10',         // Credential Access
  TA0007: 'border-blue-500 text-blue-300 bg-blue-500/10',         // Discovery
  TA0008: 'border-violet-500 text-violet-300 bg-violet-500/10',   // Lateral Movement
  TA0009: 'border-pink-500 text-pink-300 bg-pink-500/10',         // Collection
  TA0011: 'border-red-600 text-red-300 bg-red-600/10',            // Command and Control
  TA0010: 'border-amber-700 text-amber-300 bg-amber-700/10',      // Exfiltration
  TA0040: 'border-rose-700 text-rose-300 bg-rose-700/10',         // Impact
}

export const API_BASE = '/api'
export const WS_BASE = typeof window !== 'undefined'
  ? `ws://${window.location.host}/ws`
  : 'ws://localhost:8000/ws'

export const ALERT_POLL_INTERVAL = 2000
export const QUEUE_POLL_INTERVAL = 3000
