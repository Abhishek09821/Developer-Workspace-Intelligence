import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, FolderOpen, GitBranch, Upload, Clock } from 'lucide-react'
import { useProject } from '@/hooks/useProjects'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { ErrorState } from '@/components/ui/ErrorState'
import { Badge } from '@/components/ui/Badge'
import { timeAgo } from '@/lib/utils'

export function ProjectDetailPage() {
  const { projectId } = useParams<{ projectId: string }>()
  const { data: project, isLoading, isError } = useProject(projectId ?? '')

  if (isLoading) {
    return (
      <div className="flex justify-center py-16">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  if (isError || !project) {
    return <ErrorState title="Project not found" />
  }

  const sourceIcon = {
    local_workspace:   FolderOpen,
    zip_upload:        Upload,
    github_repository: GitBranch,
  }[project.source_type]
  const SourceIcon = sourceIcon ?? FolderOpen

  return (
    <div>
      {/* Back */}
      <Link to="/projects" className="inline-flex items-center gap-1.5 text-xs text-slate-500 hover:text-slate-300 mb-5 transition-colors">
        <ArrowLeft className="w-3.5 h-3.5" />
        All Projects
      </Link>

      {/* Header */}
      <div className="card p-5 mb-6">
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-surface-700 flex items-center justify-center">
              <SourceIcon className="w-5 h-5 text-slate-400" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-slate-100">{project.name}</h2>
              {project.description && (
                <p className="text-sm text-slate-500 mt-0.5">{project.description}</p>
              )}
            </div>
          </div>
          <Badge label={project.status} isStatus />
        </div>

        <div className="mt-4 pt-4 border-t border-slate-700/60 grid grid-cols-3 gap-4">
          <Metadata label="Source" value={project.source_type.replace(/_/g, ' ')} />
          <Metadata label="Created" value={timeAgo(project.created_at)} />
          <Metadata label="Updated" value={timeAgo(project.updated_at)} />
        </div>
      </div>

      {/* Placeholder panels for analysis results */}
      <div className="grid grid-cols-2 gap-4">
        {['Overview', 'Health', 'Security', 'Dependencies', 'Architecture', 'Recommendations'].map((panel) => (
          <div key={panel} className="card p-5">
            <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">{panel}</h3>
            <div className="flex items-center justify-center py-8 text-slate-700 text-xs">
              <Clock className="w-4 h-4 mr-2" />
              Available after first scan
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function Metadata({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xs text-slate-600">{label}</p>
      <p className="text-sm text-slate-300 capitalize mt-0.5">{value}</p>
    </div>
  )
}
