import { clsx } from 'clsx'
import { AlertTriangle, Radio, Shield } from 'lucide-react'
import { useOllamaHealth } from '../../hooks/useOllamaHealth'

export function Header() {
  const { data: health, isError } = useOllamaHealth()

  const ollamaOk = !isError && health?.ollama_reachable === true

  return (
    <header className="h-14 border-b border-gray-700/50 bg-navy-900/90 backdrop-blur-sm flex items-center justify-between px-6 shrink-0">
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2">
          <Shield size={20} className="text-blue-400" />
          <span className="text-base font-bold text-gray-100 tracking-tight">
            Incident Autopilot
          </span>
        </div>
        <span className="text-xs text-gray-500 font-mono border border-gray-700 px-1.5 py-0.5 rounded">
          v0.1.0
        </span>
      </div>

      <div className="flex items-center gap-4">
        {health && (
          <div className="flex items-center gap-3 text-xs text-gray-500">
            <span className="flex items-center gap-1">
              <AlertTriangle size={11} className="text-gray-600" />
              {health.alert_count} alerts
            </span>
          </div>
        )}
        <div className={clsx(
          'flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-full border',
          ollamaOk
            ? 'text-green-400 border-green-400/30 bg-green-400/10'
            : 'text-red-400 border-red-400/30 bg-red-400/10',
        )}>
          <Radio size={10} className={ollamaOk ? 'animate-pulse' : ''} />
          {ollamaOk ? 'Ollama connected' : 'Ollama offline'}
        </div>
      </div>
    </header>
  )
}
