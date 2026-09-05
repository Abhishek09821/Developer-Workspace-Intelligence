import { cn } from '@/lib/utils'
import { statusColor, capitalize } from '@/lib/utils'

interface Props {
  label: string
  /** Use the label as a status key for automatic coloring */
  isStatus?: boolean
  className?: string
}

export function Badge({ label, isStatus = false, className }: Props) {
  const colorClass = isStatus ? statusColor(label) : 'bg-slate-700 text-slate-300'
  return (
    <span className={cn('badge', colorClass, className)}>
      {isStatus ? capitalize(label) : label}
    </span>
  )
}
