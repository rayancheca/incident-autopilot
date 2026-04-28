import { Activity, Zap } from 'lucide-react'
import { useMutation } from '@tanstack/react-query'
import { useAlerts } from '../../hooks/useAlerts'
import { api } from '../../lib/api'
import { useAppStore } from '../../store/appStore'
import { Button } from '../ui/Button'
import { EmptyState } from '../ui/EmptyState'
import { Spinner } from '../ui/Spinner'
import { AlertCard } from './AlertCard'

interface AlertFeedProps {
  onAnalyze: (reportId: string) => void
}

export function AlertFeed({ onAnalyze }: AlertFeedProps) {
  const { data: alerts, isLoading, isRefetching } = useAlerts()
  const { selectedAlertIds, toggleAlertSelection, clearSelection, resetStream } = useAppStore()

  const generateMutation = useMutation({
    mutationFn: (alertIds: string[]) => api.reports.generate({ alert_ids: alertIds }),
    onSuccess: (report) => {
      clearSelection()
      resetStream()
      onAnalyze(report.id)
    },
  })

  const handleAnalyze = () => {
    if (selectedAlertIds.size === 0) return
    generateMutation.mutate(Array.from(selectedAlertIds))
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-700/50">
        <div className="flex items-center gap-2">
          <Activity size={16} className="text-blue-400" />
          <span className="text-sm font-semibold text-gray-200">Alert Stream</span>
          {alerts && (
            <span className="text-xs text-gray-500 bg-navy-800 px-1.5 py-0.5 rounded border border-gray-700">
              {alerts.length}
            </span>
          )}
          {isRefetching && <Spinner size="sm" />}
        </div>
        <div className="flex items-center gap-2">
          {selectedAlertIds.size > 0 && (
            <>
              <Button variant="ghost" size="sm" onClick={clearSelection}>
                Clear
              </Button>
              <Button
                size="sm"
                onClick={handleAnalyze}
                disabled={generateMutation.isPending}
              >
                <Zap size={12} />
                Analyze {selectedAlertIds.size}
              </Button>
            </>
          )}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {isLoading ? (
          <div className="flex justify-center py-8">
            <Spinner />
          </div>
        ) : !alerts || alerts.length === 0 ? (
          <EmptyState
            icon={<Activity size={32} />}
            title="No alerts yet"
            description="Ingest alerts via the API to see them here"
          />
        ) : (
          alerts.map((event) => (
            <AlertCard
              key={event.id}
              event={event}
              selected={selectedAlertIds.has(event.id)}
              onToggle={toggleAlertSelection}
            />
          ))
        )}
      </div>

      {generateMutation.isPending && (
        <div className="px-4 py-2 border-t border-gray-700/50 flex items-center gap-2 text-xs text-blue-400">
          <Spinner size="sm" />
          Generating IR report…
        </div>
      )}
    </div>
  )
}
