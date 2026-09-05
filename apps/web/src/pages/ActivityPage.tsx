import { Activity } from 'lucide-react'
import { PageHeader } from '@/components/ui/PageHeader'
import { EmptyState } from '@/components/ui/EmptyState'

export function ActivityPage() {
  return (
    <div>
      <PageHeader
        title="Activity"
        description="A chronological log of scans, imports, and system events."
      />
      <EmptyState
        icon={<Activity className="w-12 h-12" />}
        title="No activity yet"
        description="Events will appear here as you create projects, run scans, and interact with the platform."
      />
    </div>
  )
}
