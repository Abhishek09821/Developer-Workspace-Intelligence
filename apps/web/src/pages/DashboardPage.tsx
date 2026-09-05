import { FolderKanban, Activity, ShieldAlert, Package } from 'lucide-react'
import { PageHeader } from '@/components/ui/PageHeader'
import { StatCard } from '@/components/ui/StatCard'
import { useProjects } from '@/hooks/useProjects'
import { useHealth } from '@/hooks/useHealth'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { useAuth } from '@/contexts/AuthContext'

export function DashboardPage() {
  const { user } = useAuth()
  const { data: projectData, isLoading } = useProjects()
  const { data: health } = useHealth()

  const greeting = user?.full_name ? `Welcome back, ${user.full_name.split(' ')[0]}` : 'Welcome back'

  return (
    <div>
      <PageHeader
        title={greeting}
        description="Here's a summary of your workspace intelligence."
      />

      {/* Stats row */}
      {isLoading ? (
        <div className="flex justify-center py-12">
          <LoadingSpinner size="lg" />
        </div>
      ) : (
        <div className="grid grid-cols-2 xl:grid-cols-4 gap-4 mb-8">
          <StatCard
            label="Total Projects"
            value={projectData?.total ?? 0}
            icon={<FolderKanban className="w-4 h-4" />}
          />
          <StatCard
            label="Active Scans"
            value={0}
            subtext="No scans running"
            icon={<Activity className="w-4 h-4" />}
          />
          <StatCard
            label="Security Findings"
            value={0}
            subtext="Run a scan to detect"
            icon={<ShieldAlert className="w-4 h-4" />}
          />
          <StatCard
            label="Dependencies"
            value={0}
            subtext="Run a scan to detect"
            icon={<Package className="w-4 h-4" />}
          />
        </div>
      )}

      {/* System status */}
      <div className="card p-5 mb-6">
        <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">System Status</h3>
        <div className="flex flex-col gap-2">
          <StatusRow
            label="API Server"
            status={health?.status === 'ok' ? 'operational' : 'offline'}
            detail={health ? `v${health.version} · ${health.environment}` : undefined}
          />
          <StatusRow label="Database" status="operational" detail="PostgreSQL + pgvector" />
          <StatusRow label="Redis / Cache" status="operational" detail="Background job queue" />
          <StatusRow label="AI Provider" status="not_configured" detail="Configure in Settings" />
        </div>
      </div>

      {/* Recent projects */}
      {projectData && projectData.items.length > 0 && (
        <div className="card p-5">
          <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">Recent Projects</h3>
          <div className="space-y-2">
            {projectData.items.slice(0, 5).map((p) => (
              <div key={p.id} className="flex items-center justify-between py-2 border-b border-slate-700/50 last:border-0">
                <p className="text-sm text-slate-300">{p.name}</p>
                <span className="text-xs text-slate-600">{p.source_type.replace('_', ' ')}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

function StatusRow({
  label,
  status,
  detail,
}: {
  label: string
  status: 'operational' | 'offline' | 'not_configured' | 'degraded'
  detail?: string
}) {
  const color = {
    operational:    'bg-emerald-400',
    offline:        'bg-red-400',
    not_configured: 'bg-slate-600',
    degraded:       'bg-canary-400',
  }[status]

  const text = {
    operational:    'Operational',
    offline:        'Offline',
    not_configured: 'Not configured',
    degraded:       'Degraded',
  }[status]

  return (
    <div className="flex items-center justify-between text-sm">
      <div className="flex items-center gap-2.5">
        <span className={`w-2 h-2 rounded-full ${color}`} />
        <span className="text-slate-300">{label}</span>
      </div>
      <div className="flex items-center gap-3">
        {detail && <span className="text-xs text-slate-600">{detail}</span>}
        <span className="text-xs text-slate-400">{text}</span>
      </div>
    </div>
  )
}
