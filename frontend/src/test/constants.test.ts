import { describe, it, expect } from 'vitest'
import { SEVERITY_COLORS, TACTIC_COLORS, API_BASE, WS_BASE, ALERT_POLL_INTERVAL, QUEUE_POLL_INTERVAL } from '../lib/constants'
import type { AlertSeverity } from '../types/alerts'

describe('SEVERITY_COLORS', () => {
  const severities: AlertSeverity[] = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']

  it('has entries for all four severity levels', () => {
    for (const severity of severities) {
      expect(SEVERITY_COLORS[severity]).toBeDefined()
    }
  })

  it('each entry has bg, text, border, and glow keys', () => {
    for (const severity of severities) {
      const entry = SEVERITY_COLORS[severity]
      expect(entry).toHaveProperty('bg')
      expect(entry).toHaveProperty('text')
      expect(entry).toHaveProperty('border')
      expect(entry).toHaveProperty('glow')
    }
  })

  it('each value is a non-empty string', () => {
    for (const severity of severities) {
      const entry = SEVERITY_COLORS[severity]
      expect(typeof entry.bg).toBe('string')
      expect(entry.bg.length).toBeGreaterThan(0)
      expect(typeof entry.text).toBe('string')
      expect(entry.text.length).toBeGreaterThan(0)
      expect(typeof entry.border).toBe('string')
      expect(entry.border.length).toBeGreaterThan(0)
      expect(typeof entry.glow).toBe('string')
      expect(entry.glow.length).toBeGreaterThan(0)
    }
  })

  it('CRITICAL uses red color classes', () => {
    expect(SEVERITY_COLORS.CRITICAL.text).toContain('red')
  })

  it('HIGH uses amber color classes', () => {
    expect(SEVERITY_COLORS.HIGH.text).toContain('amber')
  })

  it('MEDIUM uses yellow color classes', () => {
    expect(SEVERITY_COLORS.MEDIUM.text).toContain('yellow')
  })

  it('LOW uses blue color classes', () => {
    expect(SEVERITY_COLORS.LOW.text).toContain('blue')
  })
})

describe('TACTIC_COLORS', () => {
  const knownTacticIds = [
    'TA0001', // Initial Access
    'TA0002', // Execution
    'TA0003', // Persistence
    'TA0004', // Privilege Escalation
    'TA0005', // Defense Evasion
    'TA0006', // Credential Access
    'TA0007', // Discovery
    'TA0008', // Lateral Movement
    'TA0009', // Collection
    'TA0010', // Exfiltration
    'TA0011', // Command and Control
    'TA0040', // Impact
  ]

  it('has entries for all known MITRE tactic IDs', () => {
    for (const id of knownTacticIds) {
      expect(TACTIC_COLORS[id]).toBeDefined()
    }
  })

  it('has exactly 12 tactic entries', () => {
    expect(Object.keys(TACTIC_COLORS).length).toBe(12)
  })

  it('each tactic color value is a non-empty string', () => {
    for (const id of knownTacticIds) {
      const value = TACTIC_COLORS[id]
      expect(typeof value).toBe('string')
      expect(value.length).toBeGreaterThan(0)
    }
  })

  it('each tactic color value contains border, text, and bg classes', () => {
    for (const id of knownTacticIds) {
      const value = TACTIC_COLORS[id]
      expect(value).toMatch(/border-/)
      expect(value).toMatch(/text-/)
      expect(value).toMatch(/bg-/)
    }
  })

  it('TA0001 (Initial Access) uses purple', () => {
    expect(TACTIC_COLORS['TA0001']).toContain('purple')
  })

  it('TA0002 (Execution) uses red', () => {
    expect(TACTIC_COLORS['TA0002']).toContain('red')
  })

  it('TA0006 (Credential Access) uses cyan', () => {
    expect(TACTIC_COLORS['TA0006']).toContain('cyan')
  })
})

describe('API and WS base constants', () => {
  it('API_BASE is /api', () => {
    expect(API_BASE).toBe('/api')
  })

  it('WS_BASE is a string', () => {
    expect(typeof WS_BASE).toBe('string')
  })

  it('WS_BASE starts with ws://', () => {
    expect(WS_BASE).toMatch(/^ws:\/\//)
  })

  it('ALERT_POLL_INTERVAL is 2000ms', () => {
    expect(ALERT_POLL_INTERVAL).toBe(2000)
  })

  it('QUEUE_POLL_INTERVAL is 3000ms', () => {
    expect(QUEUE_POLL_INTERVAL).toBe(3000)
  })

  it('QUEUE_POLL_INTERVAL is greater than ALERT_POLL_INTERVAL', () => {
    expect(QUEUE_POLL_INTERVAL).toBeGreaterThan(ALERT_POLL_INTERVAL)
  })
})
