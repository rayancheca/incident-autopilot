import { clsx } from 'clsx'
import { ChevronDown, ChevronUp, Shield, Terminal } from 'lucide-react'
import { useRemediationQueue } from '../../hooks/useRemediationQueue'
import { useAppStore } from '../../store/appStore'
import { SEVERITY_COLORS } from '../../lib/constants'
import { EmptyState } from '../ui/EmptyState'
import { Spinner } from '../ui/Spinner'
import { ApprovalButtons } from './ApprovalButtons'
import { ScriptViewer } from './ScriptViewer'

export function RemediationDrawer() {
  const { drawerOpen, setDrawerOpen } = useAppStore()
  const { data: queue, isLoading } = useRemediationQueue()

  const pendingCount = queue?.filter((i) => i.approval_status === 'PENDING').length ?? 0

  return (
    <div
      className={clsx(
        'border-t border-gray-700/50 bg-navy-900 transition-all duration-300 ease-out',
        drawerOpen ? 'h-96' : 'h-12',
      )}
    >
      <button
        onClick={() => setDrawerOpen(!drawerOpen)}
        className="w-full h-12 flex items-center justify-between px-4 hover:bg-white/5 transition-colors"
      >
        <div className="flex items-center gap-2">
          <Terminal size={15} className="text-green-400" />
          <span className="text-sm font-semibold text-gray-200">Remediation Queue</span>
          {pendingCount > 0 && (
            <span className="text-xs font-bold bg-amber-500 text-black px-1.5 py-0.5 rounded-full">
              {pendingCount}
            </span>
          )}
        </div>
        {drawerOpen ? (
          <ChevronDown size={15} className="text-gray-400" />
        ) : (
          <ChevronUp size={15} className="text-gray-400" />
        )}
      </button>

      {drawerOpen && (
        <div className="h-80 overflow-y-auto px-4 pb-4 animate-slide-up">
          {isLoading ? (
            <div className="flex justify-center py-6">
              <Spinner />
            </div>
          ) : !queue || queue.length === 0 ? (
            <EmptyState
              icon={<Shield size={28} />}
              title="No remediation scripts yet"
              description="Generate an IR report to auto-create remediation scripts"
            />
          ) : (
            <div className="space-y-4">
              {queue.map((item) => {
                const colors = SEVERITY_COLORS[item.severity]
                return (
                  <div
                    key={item.id}
                    className={clsx('rounded-lg border p-3', colors.border, colors.bg)}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <span className={clsx('text-xs font-bold uppercase', colors.text)}>
                          {item.severity}
                        </span>
                        <span className="text-xs text-gray-500 font-mono">
                          {new Date(item.created_at).toLocaleTimeString()}
                        </span>
                        {item.auto_approved && (
                          <span className="text-xs text-green-500">auto-approved</span>
                        )}
                      </div>
                      <ApprovalButtons item={item} />
                    </div>
                    <p className="text-xs text-gray-400 mb-2">{item.script.rationale}</p>
                    <ScriptViewer script={item.script.body} sha256={item.script.sha256} />
                  </div>
                )
              })}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
