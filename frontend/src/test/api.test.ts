import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { api } from '../lib/api'
import { API_BASE } from '../lib/constants'
import type { RawAlertIn } from '../types/alerts'
import type { ApprovalAction } from '../types/remediation'
import type { GenerateReportRequest } from '../types/reports'

function mockFetch(body: unknown, ok = true, status = 200) {
  return vi.fn().mockResolvedValue({
    ok,
    status,
    text: () => Promise.resolve(JSON.stringify(body)),
    json: () => Promise.resolve(body),
  })
}

describe('api.health', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('calls /api/health with GET', async () => {
    const payload = { status: 'ok', ollama_reachable: true, alert_count: 5 }
    global.fetch = mockFetch(payload)

    const result = await api.health()

    expect(global.fetch).toHaveBeenCalledOnce()
    const [url] = (global.fetch as ReturnType<typeof vi.fn>).mock.calls[0] as [string, RequestInit?]
    expect(url).toBe(`${API_BASE}/health`)
    expect(result).toEqual(payload)
  })

  it('throws when response is not ok', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 503,
      text: () => Promise.resolve('Service Unavailable'),
      json: () => Promise.resolve({}),
    })

    await expect(api.health()).rejects.toThrow('HTTP 503')
  })
})

describe('api.alerts.list', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('calls /api/alerts with default limit and offset', async () => {
    global.fetch = mockFetch([])

    await api.alerts.list()

    const [url] = (global.fetch as ReturnType<typeof vi.fn>).mock.calls[0] as [string]
    expect(url).toBe(`${API_BASE}/alerts?limit=100&offset=0`)
  })

  it('calls /api/alerts with custom limit', async () => {
    global.fetch = mockFetch([])

    await api.alerts.list(50)

    const [url] = (global.fetch as ReturnType<typeof vi.fn>).mock.calls[0] as [string]
    expect(url).toBe(`${API_BASE}/alerts?limit=50&offset=0`)
  })

  it('calls /api/alerts with custom limit and offset', async () => {
    global.fetch = mockFetch([])

    await api.alerts.list(25, 50)

    const [url] = (global.fetch as ReturnType<typeof vi.fn>).mock.calls[0] as [string]
    expect(url).toBe(`${API_BASE}/alerts?limit=25&offset=50`)
  })
})

describe('api.alerts.ingest', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('sends POST to /api/alerts/ingest with JSON body', async () => {
    const payload: RawAlertIn = { raw: 'CEF:0|Security|...' }
    global.fetch = mockFetch({ id: 'evt-1' })

    await api.alerts.ingest(payload)

    const [url, options] = (global.fetch as ReturnType<typeof vi.fn>).mock.calls[0] as [string, RequestInit]
    expect(url).toBe(`${API_BASE}/alerts/ingest`)
    expect(options.method).toBe('POST')
    expect(options.body).toBe(JSON.stringify(payload))
  })

  it('sends Content-Type header', async () => {
    global.fetch = mockFetch({ id: 'evt-1' })

    await api.alerts.ingest({ raw: 'test' })

    const [, options] = (global.fetch as ReturnType<typeof vi.fn>).mock.calls[0] as [string, RequestInit]
    expect((options.headers as Record<string, string>)['Content-Type']).toBe('application/json')
  })

  it('includes format_hint when provided', async () => {
    const payload: RawAlertIn = { raw: 'some raw cef data', format_hint: 'cef' }
    global.fetch = mockFetch({ id: 'evt-2' })

    await api.alerts.ingest(payload)

    const [, options] = (global.fetch as ReturnType<typeof vi.fn>).mock.calls[0] as [string, RequestInit]
    const body = JSON.parse(options.body as string) as RawAlertIn
    expect(body.format_hint).toBe('cef')
  })
})

describe('api.alerts.get', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('calls /api/alerts/:id with correct id', async () => {
    global.fetch = mockFetch({ id: 'abc-123' })

    await api.alerts.get('abc-123')

    const [url] = (global.fetch as ReturnType<typeof vi.fn>).mock.calls[0] as [string]
    expect(url).toBe(`${API_BASE}/alerts/abc-123`)
  })
})

describe('api.reports.generate', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('sends POST to /api/reports/generate with alert_ids', async () => {
    const req: GenerateReportRequest = { alert_ids: ['id-1', 'id-2'] }
    global.fetch = mockFetch({ id: 'rep-1' })

    await api.reports.generate(req)

    const [url, options] = (global.fetch as ReturnType<typeof vi.fn>).mock.calls[0] as [string, RequestInit]
    expect(url).toBe(`${API_BASE}/reports/generate`)
    expect(options.method).toBe('POST')
    const body = JSON.parse(options.body as string) as GenerateReportRequest
    expect(body.alert_ids).toEqual(['id-1', 'id-2'])
  })
})

describe('api.reports.list', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('calls /api/reports', async () => {
    global.fetch = mockFetch([])

    await api.reports.list()

    const [url] = (global.fetch as ReturnType<typeof vi.fn>).mock.calls[0] as [string]
    expect(url).toBe(`${API_BASE}/reports`)
  })
})

describe('api.reports.get', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('calls /api/reports/:id', async () => {
    global.fetch = mockFetch({ id: 'rep-42' })

    await api.reports.get('rep-42')

    const [url] = (global.fetch as ReturnType<typeof vi.fn>).mock.calls[0] as [string]
    expect(url).toBe(`${API_BASE}/reports/rep-42`)
  })
})

describe('api.remediation.queue', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('calls /api/remediation/queue', async () => {
    global.fetch = mockFetch([])

    await api.remediation.queue()

    const [url] = (global.fetch as ReturnType<typeof vi.fn>).mock.calls[0] as [string]
    expect(url).toBe(`${API_BASE}/remediation/queue`)
  })
})

describe('api.remediation.approve', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('sends POST to /api/remediation/:id/approve', async () => {
    const action: ApprovalAction = { approver: 'analyst@soc', reason: 'confirmed malicious' }
    global.fetch = mockFetch({})

    await api.remediation.approve('rem-99', action)

    const [url, options] = (global.fetch as ReturnType<typeof vi.fn>).mock.calls[0] as [string, RequestInit]
    expect(url).toBe(`${API_BASE}/remediation/rem-99/approve`)
    expect(options.method).toBe('POST')
    const body = JSON.parse(options.body as string) as ApprovalAction
    expect(body.approver).toBe('analyst@soc')
  })
})

describe('api.remediation.reject', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('sends POST to /api/remediation/:id/reject', async () => {
    const action: ApprovalAction = { approver: 'analyst@soc', reason: 'false positive' }
    global.fetch = mockFetch({})

    await api.remediation.reject('rem-77', action)

    const [url, options] = (global.fetch as ReturnType<typeof vi.fn>).mock.calls[0] as [string, RequestInit]
    expect(url).toBe(`${API_BASE}/remediation/rem-77/reject`)
    expect(options.method).toBe('POST')
    const body = JSON.parse(options.body as string) as ApprovalAction
    expect(body.reason).toBe('false positive')
  })
})

describe('api.remediation.get', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('calls /api/remediation/:id', async () => {
    global.fetch = mockFetch({ id: 'rem-5' })

    await api.remediation.get('rem-5')

    const [url] = (global.fetch as ReturnType<typeof vi.fn>).mock.calls[0] as [string]
    expect(url).toBe(`${API_BASE}/remediation/rem-5`)
  })
})

describe('request error handling', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('throws with status code when response is not ok', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 404,
      text: () => Promise.resolve('Not Found'),
      json: () => Promise.resolve({}),
    })

    await expect(api.alerts.get('missing-id')).rejects.toThrow('HTTP 404')
  })

  it('throws with error body text when response is not ok', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 422,
      text: () => Promise.resolve('Unprocessable Entity'),
      json: () => Promise.resolve({}),
    })

    await expect(api.alerts.ingest({ raw: 'bad' })).rejects.toThrow('Unprocessable Entity')
  })
})
