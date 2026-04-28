import { clsx } from 'clsx'
import { TACTIC_COLORS } from '../../lib/constants'
import type { MitreTactic } from '../../types/reports'

interface MitreBadgeProps {
  tactic: MitreTactic
}

export function MitreBadge({ tactic }: MitreBadgeProps) {
  const colorClass = TACTIC_COLORS[tactic.tactic_id] ?? 'border-gray-500 text-gray-300 bg-gray-500/10'

  return (
    <div className={clsx('inline-flex flex-col px-2.5 py-1.5 rounded-md border text-xs', colorClass)}>
      <span className="font-mono font-bold opacity-70">{tactic.tactic_id}</span>
      <span className="font-medium">{tactic.tactic_name}</span>
      {tactic.techniques.length > 0 && (
        <div className="flex flex-wrap gap-1 mt-1">
          {tactic.techniques.map((t) => (
            <span key={t} className="font-mono text-[10px] opacity-60 border border-current/30 px-1 rounded">
              {t}
            </span>
          ))}
        </div>
      )}
    </div>
  )
}
