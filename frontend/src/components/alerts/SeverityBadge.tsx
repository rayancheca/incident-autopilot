import { clsx } from 'clsx'
import { SEVERITY_COLORS } from '../../lib/constants'
import type { AlertSeverity } from '../../types/alerts'

interface SeverityBadgeProps {
  severity: AlertSeverity
  pulse?: boolean
}

export function SeverityBadge({ severity, pulse }: SeverityBadgeProps) {
  const colors = SEVERITY_COLORS[severity]
  return (
    <span
      className={clsx(
        'inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold border tracking-wide uppercase',
        colors.bg,
        colors.text,
        colors.border,
        pulse && severity === 'CRITICAL' && 'animate-pulse-slow',
      )}
    >
      {severity}
    </span>
  )
}
