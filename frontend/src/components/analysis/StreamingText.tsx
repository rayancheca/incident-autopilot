import { clsx } from 'clsx'

interface StreamingTextProps {
  text: string
  isStreaming: boolean
  className?: string
}

export function StreamingText({ text, isStreaming, className }: StreamingTextProps) {
  return (
    <div className={clsx('font-mono text-sm text-gray-300 leading-relaxed whitespace-pre-wrap break-words', className)}>
      {text}
      {isStreaming && (
        <span className="inline-block w-2 h-4 bg-blue-400 ml-0.5 animate-blink align-middle" />
      )}
    </div>
  )
}
