import { clsx, type ClassValue } from 'clsx'

/** Merge Tailwind class strings conditionally */
export function cn(...inputs: ClassValue[]) {
  return clsx(inputs)
}

/** Format a relative time from an ISO date string */
export function timeAgo(dateString: string): string {
  const date = new Date(dateString)
  const now = new Date()
  const seconds = Math.floor((now.getTime() - date.getTime()) / 1000)

  if (seconds < 60) return 'just now'
  const minutes = Math.floor(seconds / 60)
  if (minutes < 60) return `${minutes}m ago`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}h ago`
  const days = Math.floor(hours / 24)
  if (days < 30) return `${days}d ago`
  return date.toLocaleDateString()
}

/** Capitalise the first letter */
export function capitalize(s: string) {
  return s.charAt(0).toUpperCase() + s.slice(1).toLowerCase()
}

/** Map a project/scan status string to a Tailwind badge color */
export function statusColor(status: string): string {
  const map: Record<string, string> = {
    created:   'bg-slate-700 text-slate-300',
    importing: 'bg-blue-900/60 text-blue-300',
    ready:     'bg-emerald-900/60 text-emerald-300',
    scanning:  'bg-blue-900/60 text-blue-300',
    analyzing: 'bg-violet-900/60 text-violet-300',
    completed: 'bg-emerald-900/60 text-emerald-300',
    failed:    'bg-red-900/60 text-red-400',
    queued:    'bg-slate-700 text-slate-300',
    running:   'bg-blue-900/60 text-blue-300',
  }
  return map[status.toLowerCase()] ?? 'bg-slate-700 text-slate-300'
}
