import { CheckCircle, Clock, Shield, Target, Users } from 'lucide-react'
import { SEVERITY_COLORS } from '../../lib/constants'
import type { IRReport } from '../../types/reports'
import { SeverityBadge } from '../alerts/SeverityBadge'
import { MitreBadge } from './MitreBadge'

interface IRReportViewProps {
  report: IRReport
}

export function IRReportView({ report }: IRReportViewProps) {
  const colors = SEVERITY_COLORS[report.severity]

  return (
    <div className="space-y-5">
      {/* Header */}
      <div className={`p-4 rounded-lg border ${colors.border} ${colors.bg}`}>
        <div className="flex items-start justify-between gap-3 mb-2">
          <h2 className="text-base font-bold text-gray-100 leading-tight">{report.title}</h2>
          <SeverityBadge severity={report.severity} pulse />
        </div>
        <div className="flex items-center gap-3 text-xs text-gray-500">
          <span>Confidence: <span className="text-gray-300 font-bold">{report.confidence}%</span></span>
          <span>Alerts: <span className="text-gray-300">{report.alert_ids.length}</span></span>
        </div>
      </div>

      {/* Summary */}
      <div>
        <div className="flex items-center gap-1.5 text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
          <Shield size={12} />
          Executive Summary
        </div>
        <p className="text-sm text-gray-300 leading-relaxed">{report.executive_summary}</p>
      </div>

      {/* MITRE Tactics */}
      {report.mitre_tactics.length > 0 && (
        <div>
          <div className="flex items-center gap-1.5 text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
            <Target size={12} />
            MITRE ATT&CK Tactics
          </div>
          <div className="flex flex-wrap gap-2">
            {report.mitre_tactics.map((tactic) => (
              <MitreBadge key={tactic.tactic_id} tactic={tactic} />
            ))}
          </div>
        </div>
      )}

      {/* Affected Assets */}
      {report.affected_assets.length > 0 && (
        <div>
          <div className="flex items-center gap-1.5 text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
            <Users size={12} />
            Affected Assets
          </div>
          <div className="space-y-1">
            {report.affected_assets.map((asset, i) => (
              <div key={i} className="flex items-center gap-2 text-sm">
                <span className="text-blue-400 font-mono">{asset.hostname || asset.ip || 'Unknown'}</span>
                {asset.role && <span className="text-gray-500 text-xs">— {asset.role}</span>}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Timeline */}
      {report.timeline.length > 0 && (
        <div>
          <div className="flex items-center gap-1.5 text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
            <Clock size={12} />
            Timeline
          </div>
          <div className="space-y-2 border-l border-gray-700 pl-3">
            {report.timeline.map((entry, i) => (
              <div key={i} className="relative">
                <div className="absolute -left-[17px] top-1 w-2 h-2 rounded-full bg-gray-600 border border-gray-500" />
                <div className="text-xs text-gray-500 font-mono">
                  {new Date(entry.timestamp).toLocaleTimeString()}
                </div>
                <div className="text-sm text-gray-300">{entry.event}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recommendations */}
      {report.recommendations.length > 0 && (
        <div>
          <div className="flex items-center gap-1.5 text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
            <CheckCircle size={12} />
            Recommendations
          </div>
          <ul className="space-y-1">
            {report.recommendations.map((rec, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-gray-300">
                <span className="text-green-400 mt-0.5 shrink-0">→</span>
                {rec}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
