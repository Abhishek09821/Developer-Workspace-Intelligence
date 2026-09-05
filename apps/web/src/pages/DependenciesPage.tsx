import { Package } from 'lucide-react'
import { PageHeader } from '@/components/ui/PageHeader'
import { EmptyState } from '@/components/ui/EmptyState'

export function DependenciesPage() {
  return (
    <div>
      <PageHeader
        title="Dependencies"
        description="Analyze third-party packages, versions, and known vulnerabilities."
      />
      <EmptyState
        icon={<Package className="w-12 h-12" />}
        title="No dependency data yet"
        description="Run a scan to parse package manifests and surface outdated or vulnerable dependencies."
      />
    </div>
  )
}
