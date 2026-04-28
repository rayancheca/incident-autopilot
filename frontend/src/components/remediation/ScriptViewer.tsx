import { useEffect } from 'react'
import Prism from 'prismjs'
import 'prismjs/components/prism-bash'

interface ScriptViewerProps {
  script: string
  sha256: string
}

export function ScriptViewer({ script, sha256 }: ScriptViewerProps) {
  useEffect(() => {
    Prism.highlightAll()
  }, [script])

  return (
    <div className="rounded-lg overflow-hidden border border-gray-700/60">
      <div className="flex items-center justify-between px-3 py-1.5 bg-gray-800/80 border-b border-gray-700/60">
        <span className="text-xs text-gray-400 font-mono">remediation.sh</span>
        <span className="text-xs text-gray-600 font-mono">{sha256.slice(0, 16)}…</span>
      </div>
      <pre className="!m-0 !rounded-none overflow-x-auto max-h-72 text-xs">
        <code className="language-bash">{script}</code>
      </pre>
    </div>
  )
}
