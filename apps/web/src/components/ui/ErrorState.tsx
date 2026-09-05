import { AlertTriangle } from 'lucide-react'

interface Props {
  title?: string
  message?: string
  onRetry?: () => void
}

export function ErrorState({
  title = 'Something went wrong',
  message,
  onRetry,
}: Props) {
  return (
    <div className="flex flex-col items-center justify-center text-center py-16 px-6">
      <AlertTriangle className="w-10 h-10 text-red-500 mb-4" />
      <p className="text-sm font-medium text-slate-300">{title}</p>
      {message && <p className="mt-1 text-xs text-slate-500 max-w-xs">{message}</p>}
      {onRetry && (
        <button onClick={onRetry} className="btn-secondary mt-5 text-xs">
          Try again
        </button>
      )}
    </div>
  )
}
