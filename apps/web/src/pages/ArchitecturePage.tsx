import { Network } from 'lucide-react'
import { PageHeader } from '@/components/ui/PageHeader'
import { EmptyState } from '@/components/ui/EmptyState'

export function ArchitecturePage() {
  return (
    <div>
      <PageHeader
        title="Architecture"
        description="Visualize module dependencies and component relationships."
      />
      <EmptyState
        icon={<Network className="w-12 h-12" />}
        title="Architecture graph coming soon"
        description="Run a scan to generate an interactive dependency graph for your project."
      />
    </div>
  )
}
