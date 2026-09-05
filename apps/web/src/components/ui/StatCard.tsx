import { type ReactNode } from 'react'
import { cn } from '@/lib/utils'

interface Props {
  label: string
  value: string | number
  subtext?: string
  icon?: ReactNode
  trend?: 'up' | 'down' | 'neutral'
  className?: string
}

export function StatCard({ label, value, subtext, icon, className }: Props) {
  return (
    <div className={cn('stat-card', className)}>
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium text-slate-500 uppercase tracking-wider">{label}</span>
        {icon && <span className="text-slate-600">{icon}</span>}
      </div>
      <p className="text-2xl font-bold text-slate-100 mt-1">{value}</p>
      {subtext && <p className="text-xs text-slate-500 mt-0.5">{subtext}</p>}
    </div>
  )
}
