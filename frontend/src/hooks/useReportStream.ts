import { useCallback, useEffect, useRef } from 'react'
import { ReportWebSocket } from '../lib/ws'
import { useAppStore } from '../store/appStore'
import type { IRReport } from '../types/reports'
import type { WSMessage } from '../types/ws'

interface UseReportStreamOptions {
  onComplete: (report: IRReport) => void
  onError: (message: string) => void
}

export function useReportStream(reportId: string | null, options: UseReportStreamOptions) {
  const wsRef = useRef<ReportWebSocket | null>(null)
  const { appendStreamToken, setStreaming, setActiveReport } = useAppStore()
  const { onComplete, onError } = options

  const handleMessage = useCallback((msg: WSMessage) => {
    switch (msg.type) {
      case 'token':
        appendStreamToken(msg.token)
        break
      case 'status':
        if (msg.status === 'streaming') {
          setStreaming(true)
        }
        break
      case 'final':
        setStreaming(false)
        setActiveReport(msg.report)
        onComplete(msg.report)
        break
      case 'error':
        setStreaming(false)
        onError(msg.message)
        break
    }
  }, [appendStreamToken, setStreaming, setActiveReport, onComplete, onError])

  useEffect(() => {
    if (!reportId) return

    const ws = new ReportWebSocket(
      reportId,
      handleMessage,
      () => onError('WebSocket connection error'),
    )
    wsRef.current = ws
    ws.connect()

    return () => {
      ws.disconnect()
      wsRef.current = null
    }
  }, [reportId, handleMessage, onError])
}
