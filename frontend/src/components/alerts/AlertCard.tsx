import { clsx } from 'clsx'
import { Globe, Server, User } from 'lucide-react'
import { SEVERITY_COLORS } from '../../lib/constants'
import type { NormalizedEvent } from '../../types/alerts'
import { SeverityBadge } from './SeverityBadge'

interface AlertCardProps {
  event: NormalizedEvent
  selected: boolean
  onToggle: (id: string) => void
}

export function AlertCard({ event, selected, onToggle }: AlertCardProps) {
  const colors = SEVERITY_COLORS[event.severity]
  const time = new Date(event.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })

  return (
    <button
      onClick={() => onToggle(event.id)}
      className={clsx(
        'w-full text-left p-3 rounded-lg border transition-all duration-200 animate-slide-in-left',
        'hover:border-gray-500 focus:outline-none focus:ring-1 focus:ring-blue-500',
        selected
          ? clsx('border-blue-500/70 bg-blue-500/10', 'shadow-lg', colors.glow)
          : clsx('border-gray-700/60 bg-navy-700/40 hover:bg-navy-700/60'),
      )}
    >
      <div className="flex items-start justify-between gap-2 mb-1.5">
        <div className="flex items-center gap-2 min-w-0">
          <SeverityBadge severity={event.severity} pulse />
          <span className="text-xs text-gray-500 font-mono shrink-0">{time}</span>
        </div>
        <span className="text-xs font-mono text-gray-500 uppercase bg-navy-800 px-1.5 py-0.5 rounded border border-gray-700/50 shrink-0">
          {event.source_format.replace('_', ' ')}
        </span>
      </div>

      <p className="text-sm text-gray-200 font-medium line-clamp-2 mb-2">
        {event.message}
      </p>

      <div className="flex flex-wrap gap-x-3 gap-y-1 text-xs text-gray-500">
        {event.source_ip && (
          <span className="flex items-center gap-1">
            <Globe size={10} />
            {event.source_ip}
            {event.geo && (
              <span className="text-gray-600">({event.geo.country_code})</span>
            )}
            {event.threat_intel?.is_known_bad && (
              <span className="text-red-400 font-bold">⚠</span>
            )}
          </span>
        )}
        {event.source_host && (
          <span className="flex items-center gap-1">
            <Server size={10} />
            {event.source_host}
            {event.asset?.tier === 'CROWN_JEWEL' && (
              <span className="text-amber-400 text-xs">★</span>
            )}
          </span>
        )}
        {event.username && (
          <span className="flex items-center gap-1">
            <User size={10} />
            {event.username}
          </span>
        )}
      </div>

      {selected && (
        <div className="mt-2 pt-2 border-t border-blue-500/30">
          <span className="text-xs text-blue-400">✓ Selected for analysis</span>
        </div>
      )}
    </button>
  )
}
