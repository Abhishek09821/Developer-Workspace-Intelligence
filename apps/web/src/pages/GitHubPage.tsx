import { Github } from 'lucide-react'
import { PageHeader } from '@/components/ui/PageHeader'
import { EmptyState } from '@/components/ui/EmptyState'

export function GitHubPage() {
  return (
    <div>
      <PageHeader
        title="GitHub"
        description="Connect your GitHub account to import repositories."
      />
      <EmptyState
        icon={<Github className="w-12 h-12" />}
        title="GitHub not connected"
        description="Connect your GitHub account to browse and import repositories directly into Canary."
      />
    </div>
  )
}
