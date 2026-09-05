/**
 * Minimal toast system — no external library dependency.
 * Usage: toastStore.push({ type, message })
 */
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
  type ReactNode,
} from 'react'
import { CheckCircle, XCircle, AlertTriangle, Info, X } from 'lucide-react'
import { cn } from '@/lib/utils'

type ToastType = 'success' | 'error' | 'warning' | 'info'

interface Toast {
  id: string
  type: ToastType
  message: string
}

interface ToastContextValue {
  push: (t: Omit<Toast, 'id'>) => void
}

const ToastContext = createContext<ToastContextValue | null>(null)

let _push: ToastContextValue['push'] | null = null

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([])

  const push = useCallback((t: Omit<Toast, 'id'>) => {
    const id = Math.random().toString(36).slice(2)
    setToasts((prev) => [...prev, { ...t, id }])
    setTimeout(() => setToasts((prev) => prev.filter((x) => x.id !== id)), 4000)
  }, [])

  // Expose imperatively so non-React code can call toast()
  _push = push

  const dismiss = (id: string) => setToasts((prev) => prev.filter((t) => t.id !== id))

  return (
    <ToastContext.Provider value={{ push }}>
      {children}
      <div
        aria-live="polite"
        aria-atomic="false"
        className="fixed bottom-4 right-4 z-[100] flex flex-col gap-2 w-80"
      >
        {toasts.map((t) => (
          <ToastItem key={t.id} toast={t} onDismiss={() => dismiss(t.id)} />
        ))}
      </div>
    </ToastContext.Provider>
  )
}

const icons: Record<ToastType, ReactNode> = {
  success: <CheckCircle className="w-4 h-4 text-emerald-400 flex-none" />,
  error:   <XCircle className="w-4 h-4 text-red-400 flex-none" />,
  warning: <AlertTriangle className="w-4 h-4 text-canary-400 flex-none" />,
  info:    <Info className="w-4 h-4 text-blue-400 flex-none" />,
}

const bg: Record<ToastType, string> = {
  success: 'border-emerald-700/50',
  error:   'border-red-700/50',
  warning: 'border-canary-700/50',
  info:    'border-blue-700/50',
}

function ToastItem({ toast, onDismiss }: { toast: Toast; onDismiss: () => void }) {
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const el = ref.current
    if (el) el.animate([{ opacity: 0, transform: 'translateY(8px)' }, { opacity: 1, transform: 'translateY(0)' }], { duration: 160, fill: 'forwards' })
  }, [])

  return (
    <div
      ref={ref}
      role="alert"
      className={cn('flex items-start gap-3 p-3 rounded-lg bg-surface-700 border shadow-lg text-sm', bg[toast.type])}
    >
      {icons[toast.type]}
      <span className="flex-1 text-slate-200">{toast.message}</span>
      <button onClick={onDismiss} className="text-slate-500 hover:text-slate-300">
        <X className="w-3.5 h-3.5" />
      </button>
    </div>
  )
}

export function useToast() {
  const ctx = useContext(ToastContext)
  if (!ctx) throw new Error('useToast must be used within ToastProvider')
  return ctx
}

/** Imperative helper — works outside React trees */
export const toast = {
  success: (message: string) => _push?.({ type: 'success', message }),
  error:   (message: string) => _push?.({ type: 'error', message }),
  warning: (message: string) => _push?.({ type: 'warning', message }),
  info:    (message: string) => _push?.({ type: 'info', message }),
}
