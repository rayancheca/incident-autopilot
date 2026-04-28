import { useState } from 'react'
import { AnalysisPanel } from './components/analysis/AnalysisPanel'
import { AlertFeed } from './components/alerts/AlertFeed'
import { Header } from './components/layout/Header'
import { RemediationDrawer } from './components/remediation/RemediationDrawer'
import { useAppStore } from './store/appStore'

export default function App() {
  const [activeReportId, setActiveReportId] = useState<string | null>(null)
  const { resetStream } = useAppStore()

  const handleAnalyze = (reportId: string) => {
    resetStream()
    setActiveReportId(reportId)
  }

  return (
    <div className="flex flex-col h-screen bg-navy-950 overflow-hidden">
      <Header />

      <main className="flex-1 flex overflow-hidden min-h-0">
        {/* Left panel — Alert feed (40%) */}
        <section
          aria-label="Alert stream"
          className="w-[38%] shrink-0 border-r border-gray-700/50 flex flex-col overflow-hidden"
        >
          <AlertFeed onAnalyze={handleAnalyze} />
        </section>

        {/* Right panel — LLM analysis (60%) */}
        <section
          aria-label="LLM analysis"
          className="flex-1 flex flex-col overflow-hidden"
        >
          <AnalysisPanel activeReportId={activeReportId} />
        </section>
      </main>

      {/* Bottom drawer — Remediation queue */}
      <RemediationDrawer />
    </div>
  )
}
