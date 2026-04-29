import { describe, it, expect, beforeEach } from 'vitest'
import { useAppStore } from '../store/appStore'
import type { IRReport } from '../types/reports'

// Helper to reset the store to its initial state between tests
function resetStore() {
  useAppStore.setState({
    selectedAlertIds: new Set(),
    activeReport: null,
    streamingText: '',
    isStreaming: false,
    drawerOpen: false,
    pendingQueueCount: 0,
  })
}

const sampleReport: IRReport = {
  id: 'rep-test-1',
  alert_ids: ['alert-1', 'alert-2'],
  status: 'COMPLETE',
  title: 'SSH Brute Force Attack Detected',
  executive_summary: 'An attacker attempted to brute-force SSH credentials on prod-server-01.',
  mitre_tactics: [
    { tactic_id: 'TA0006', tactic_name: 'Credential Access', techniques: ['T1110'] },
  ],
  affected_assets: [{ hostname: 'prod-server-01', ip: '10.0.0.5', role: 'database' }],
  confidence: 0.92,
  severity: 'HIGH',
  timeline: [{ timestamp: '2024-01-01T00:00:00Z', event: 'First failed login attempt' }],
  recommendations: ['Block source IP', 'Rotate SSH keys'],
  raw_stream: '',
  created_at: '2024-01-01T00:01:00Z',
  completed_at: '2024-01-01T00:02:00Z',
}

describe('appStore — initial state', () => {
  beforeEach(resetStore)

  it('selectedAlertIds starts as an empty Set', () => {
    const { selectedAlertIds } = useAppStore.getState()
    expect(selectedAlertIds).toBeInstanceOf(Set)
    expect(selectedAlertIds.size).toBe(0)
  })

  it('activeReport starts as null', () => {
    expect(useAppStore.getState().activeReport).toBeNull()
  })

  it('streamingText starts as empty string', () => {
    expect(useAppStore.getState().streamingText).toBe('')
  })

  it('isStreaming starts as false', () => {
    expect(useAppStore.getState().isStreaming).toBe(false)
  })

  it('drawerOpen starts as false', () => {
    expect(useAppStore.getState().drawerOpen).toBe(false)
  })

  it('pendingQueueCount starts as 0', () => {
    expect(useAppStore.getState().pendingQueueCount).toBe(0)
  })
})

describe('appStore — toggleAlertSelection', () => {
  beforeEach(resetStore)

  it('adds an ID when it is not already selected', () => {
    useAppStore.getState().toggleAlertSelection('alert-abc')
    expect(useAppStore.getState().selectedAlertIds.has('alert-abc')).toBe(true)
  })

  it('removes an ID when it is already selected', () => {
    useAppStore.getState().toggleAlertSelection('alert-abc')
    useAppStore.getState().toggleAlertSelection('alert-abc')
    expect(useAppStore.getState().selectedAlertIds.has('alert-abc')).toBe(false)
  })

  it('can select multiple IDs independently', () => {
    useAppStore.getState().toggleAlertSelection('alert-1')
    useAppStore.getState().toggleAlertSelection('alert-2')
    useAppStore.getState().toggleAlertSelection('alert-3')

    const { selectedAlertIds } = useAppStore.getState()
    expect(selectedAlertIds.size).toBe(3)
    expect(selectedAlertIds.has('alert-1')).toBe(true)
    expect(selectedAlertIds.has('alert-2')).toBe(true)
    expect(selectedAlertIds.has('alert-3')).toBe(true)
  })

  it('removes one ID without affecting others', () => {
    useAppStore.getState().toggleAlertSelection('alert-1')
    useAppStore.getState().toggleAlertSelection('alert-2')
    useAppStore.getState().toggleAlertSelection('alert-1')

    const { selectedAlertIds } = useAppStore.getState()
    expect(selectedAlertIds.has('alert-1')).toBe(false)
    expect(selectedAlertIds.has('alert-2')).toBe(true)
  })

  it('produces a new Set reference on each call (immutability)', () => {
    const before = useAppStore.getState().selectedAlertIds
    useAppStore.getState().toggleAlertSelection('alert-x')
    const after = useAppStore.getState().selectedAlertIds
    expect(after).not.toBe(before)
  })
})

describe('appStore — clearSelection', () => {
  beforeEach(resetStore)

  it('empties the selected alert IDs', () => {
    useAppStore.getState().toggleAlertSelection('alert-1')
    useAppStore.getState().toggleAlertSelection('alert-2')
    useAppStore.getState().clearSelection()

    expect(useAppStore.getState().selectedAlertIds.size).toBe(0)
  })

  it('is idempotent when already empty', () => {
    useAppStore.getState().clearSelection()
    expect(useAppStore.getState().selectedAlertIds.size).toBe(0)
  })
})

describe('appStore — setActiveReport', () => {
  beforeEach(resetStore)

  it('sets the active report', () => {
    useAppStore.getState().setActiveReport(sampleReport)
    expect(useAppStore.getState().activeReport).toEqual(sampleReport)
  })

  it('clears the active report when called with null', () => {
    useAppStore.getState().setActiveReport(sampleReport)
    useAppStore.getState().setActiveReport(null)
    expect(useAppStore.getState().activeReport).toBeNull()
  })

  it('replaces the active report with a new one', () => {
    const other: IRReport = { ...sampleReport, id: 'rep-test-2', title: 'New Report' }
    useAppStore.getState().setActiveReport(sampleReport)
    useAppStore.getState().setActiveReport(other)
    expect(useAppStore.getState().activeReport?.id).toBe('rep-test-2')
  })
})

describe('appStore — appendStreamToken', () => {
  beforeEach(resetStore)

  it('appends a token to empty streamingText', () => {
    useAppStore.getState().appendStreamToken('Hello')
    expect(useAppStore.getState().streamingText).toBe('Hello')
  })

  it('accumulates multiple tokens in order', () => {
    useAppStore.getState().appendStreamToken('Hello')
    useAppStore.getState().appendStreamToken(' ')
    useAppStore.getState().appendStreamToken('world')
    expect(useAppStore.getState().streamingText).toBe('Hello world')
  })

  it('handles empty string tokens without error', () => {
    useAppStore.getState().appendStreamToken('abc')
    useAppStore.getState().appendStreamToken('')
    expect(useAppStore.getState().streamingText).toBe('abc')
  })
})

describe('appStore — resetStream', () => {
  beforeEach(resetStore)

  it('clears streamingText', () => {
    useAppStore.getState().appendStreamToken('some tokens')
    useAppStore.getState().resetStream()
    expect(useAppStore.getState().streamingText).toBe('')
  })

  it('sets isStreaming to false', () => {
    useAppStore.getState().setStreaming(true)
    useAppStore.getState().resetStream()
    expect(useAppStore.getState().isStreaming).toBe(false)
  })
})

describe('appStore — setStreaming', () => {
  beforeEach(resetStore)

  it('sets isStreaming to true', () => {
    useAppStore.getState().setStreaming(true)
    expect(useAppStore.getState().isStreaming).toBe(true)
  })

  it('sets isStreaming to false', () => {
    useAppStore.getState().setStreaming(true)
    useAppStore.getState().setStreaming(false)
    expect(useAppStore.getState().isStreaming).toBe(false)
  })
})

describe('appStore — setDrawerOpen', () => {
  beforeEach(resetStore)

  it('opens the drawer', () => {
    useAppStore.getState().setDrawerOpen(true)
    expect(useAppStore.getState().drawerOpen).toBe(true)
  })

  it('closes the drawer', () => {
    useAppStore.getState().setDrawerOpen(true)
    useAppStore.getState().setDrawerOpen(false)
    expect(useAppStore.getState().drawerOpen).toBe(false)
  })
})

describe('appStore — setPendingQueueCount', () => {
  beforeEach(resetStore)

  it('updates pendingQueueCount', () => {
    useAppStore.getState().setPendingQueueCount(7)
    expect(useAppStore.getState().pendingQueueCount).toBe(7)
  })

  it('can set back to zero', () => {
    useAppStore.getState().setPendingQueueCount(5)
    useAppStore.getState().setPendingQueueCount(0)
    expect(useAppStore.getState().pendingQueueCount).toBe(0)
  })
})
