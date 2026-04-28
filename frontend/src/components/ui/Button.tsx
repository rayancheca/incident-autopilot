import { clsx } from 'clsx'

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'danger' | 'ghost' | 'outline'
  size?: 'sm' | 'md'
}

export function Button({ variant = 'primary', size = 'md', className, ...props }: ButtonProps) {
  return (
    <button
      className={clsx(
        'inline-flex items-center justify-center gap-1.5 rounded font-medium transition-all focus:outline-none focus:ring-2 focus:ring-offset-1 focus:ring-offset-navy-800 disabled:opacity-50 disabled:cursor-not-allowed',
        size === 'sm' && 'px-3 py-1.5 text-xs',
        size === 'md' && 'px-4 py-2 text-sm',
        variant === 'primary' && 'bg-blue-600 text-white hover:bg-blue-500 focus:ring-blue-500',
        variant === 'danger' && 'bg-red-600 text-white hover:bg-red-500 focus:ring-red-500',
        variant === 'ghost' && 'bg-transparent text-gray-400 hover:text-gray-200 hover:bg-white/5 focus:ring-gray-500',
        variant === 'outline' && 'border border-gray-600 text-gray-300 hover:border-gray-400 hover:text-gray-100 bg-transparent focus:ring-gray-500',
        className,
      )}
      {...props}
    />
  )
}
