import { ShieldAlert } from 'lucide-react'
import { PageHeader } from '@/components/ui/PageHeader'
import { EmptyState } from '@/components/ui/EmptyState'

export function SecurityPage() {
  return (
    <div>
      <PageHeader
        title="Security"
        description="Track vulnerabilities, secrets, and security risks in your codebase."
      />
      <EmptyState
        icon={<ShieldAlert className="w-12 h-12" />}
        title="No security findings yet"
        description="Run a security scan on a project to detect vulnerabilities, hardcoded secrets, and risky patterns."
      />
    </div>
  )
}
