import { Link } from 'react-router-dom'
import { FolderOpen, Clock, Globe, Upload, GitBranch } from 'lucide-react'
import type { ProjectResponse } from '@/types/api'
import { Badge } from '@/components/ui/Badge'
import { timeAgo } from '@/lib/utils'

const SOURCE_ICONS = {
  local_workspace:    FolderOpen,
  zip_upload:         Upload,
  github_repository:  GitBranch,
}

const SOURCE_LABELS = {
  local_workspace:    'Local',
  zip_upload:         'ZIP',
  github_repository:  'GitHub',
}

interface Props {
  project: ProjectResponse
}

export function ProjectCard({ project }: Props) {
  const SourceIcon = SOURCE_ICONS[project.source_type] ?? Globe

  return (
    <Link
      to={`/projects/${project.id}`}
      className="card p-4 flex flex-col gap-3 hover:border-slate-600 transition-colors group"
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2.5 min-w-0">
          <div className="w-8 h-8 rounded-lg bg-surface-700 flex items-center justify-center flex-none">
            <SourceIcon className="w-4 h-4 text-slate-400" />
          </div>
          <div className="min-w-0">
            <p className="text-sm font-semibold text-slate-100 truncate group-hover:text-canary-400 transition-colors">
              {project.name}
            </p>
            <p className="text-xs text-slate-500">{SOURCE_LABELS[project.source_type]}</p>
          </div>
        </div>
        <Badge label={project.status} isStatus />
      </div>

      {project.description && (
        <p className="text-xs text-slate-500 line-clamp-2">{project.description}</p>
      )}

      <div className="flex items-center gap-1 text-xs text-slate-600 mt-auto">
        <Clock className="w-3 h-3" />
        <span>Updated {timeAgo(project.updated_at)}</span>
      </div>
    </Link>
  )
}
