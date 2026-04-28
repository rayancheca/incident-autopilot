import { Brain, FileText } from 'lucide-react'
import { useState } from 'react'
import { useReportStream } from '../../hooks/useReportStream'
import { useAppStore } from '../../store/appStore'
import type { IRReport } from '../../types/reports'
import { EmptyState } from '../ui/EmptyState'
import { IRReportView } from './IRReportView'
import { StreamingText } from './StreamingText'

interface AnalysisPanelProps {
  activeReportId: string | null
}

export function AnalysisPanel({ activeReportId }: AnalysisPanelProps) {
  const { activeReport, streamingText, isStreaming, setActiveReport } = useAppStore()
  const [error, setError] = useState<string | null>(null)

  useReportStream(activeReportId, {
    onComplete: (report: IRReport) => {
      setActiveReport(report)
      setError(null)
    },
    onError: (message: string) => {
      setError(message)
    },
  })

  const showStreaming = isStreaming || (streamingText.length > 0 && !activeReport)
  const showReport = activeReport && !isStreaming

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center gap-2 px-4 py-3 border-b border-gray-700/50">
        <Brain size={16} className="text-purple-400" />
        <span className="text-sm font-semibold text-gray-200">LLM Analysis</span>
        {isStreaming && (
          <span className="text-xs text-purple-400 bg-purple-400/10 px-2 py-0.5 rounded-full border border-purple-400/30 animate-pulse">
            Streaming…
          </span>
        )}
        {showReport && (
          <span className="text-xs text-green-400 bg-green-400/10 px-2 py-0.5 rounded-full border border-green-400/30">
            Complete
          </span>
        )}
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        {error && (
          <div className="mb-4 p-3 rounded border border-red-500/30 bg-red-500/10 text-red-400 text-sm">
            Error: {error}
          </div>
        )}

        {!activeReportId && !showStreaming && !showReport && (
          <EmptyState
            icon={<Brain size={40} />}
            title="No analysis running"
            description="Select alerts from the feed and click Analyze to start"
          />
        )}

        {showStreaming && (
          <div>
            <div className="flex items-center gap-1.5 text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">
              <FileText size={12} />
              Raw LLM Output
            </div>
            <StreamingText text={streamingText} isStreaming={isStreaming} />
          </div>
        )}

        {showReport && <IRReportView report={activeReport} />}
      </div>
    </div>
  )
}
