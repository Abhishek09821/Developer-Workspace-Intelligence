import { Code2 } from 'lucide-react'
import { PageHeader } from '@/components/ui/PageHeader'
import { EmptyState } from '@/components/ui/EmptyState'

export function CodebasePage() {
  return (
    <div>
      <PageHeader
        title="Codebase"
        description="Explore files, languages, and code entities across your projects."
      />
      <EmptyState
        icon={<Code2 className="w-12 h-12" />}
        title="Select a project to explore its codebase"
        description="Run a scan on a project first. File-level analysis and code entity exploration will appear here."
      />
    </div>
  )
}
