import type { WSMessage } from '../types/ws'

type MessageHandler = (msg: WSMessage) => void
type ErrorHandler = (event: Event) => void

export class ReportWebSocket {
  private ws: WebSocket | null = null
  private reportId: string
  private onMessage: MessageHandler
  private onError: ErrorHandler
  private pingInterval: ReturnType<typeof setInterval> | null = null

  constructor(reportId: string, onMessage: MessageHandler, onError: ErrorHandler) {
    this.reportId = reportId
    this.onMessage = onMessage
    this.onError = onError
  }

  connect(): void {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.host
    this.ws = new WebSocket(`${protocol}//${host}/ws/reports/${this.reportId}`)

    this.ws.onmessage = (event: MessageEvent<string>) => {
      try {
        const msg = JSON.parse(event.data) as WSMessage
        this.onMessage(msg)
      } catch {
        // ignore malformed messages
      }
    }

    this.ws.onerror = (event) => {
      this.onError(event)
    }

    this.ws.onopen = () => {
      this.pingInterval = setInterval(() => {
        if (this.ws?.readyState === WebSocket.OPEN) {
          this.ws.send('ping')
        }
      }, 30_000)
    }
  }

  disconnect(): void {
    if (this.pingInterval) {
      clearInterval(this.pingInterval)
    }
    this.ws?.close()
    this.ws = null
  }
}
