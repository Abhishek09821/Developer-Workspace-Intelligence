import { useState } from 'react'
import { Modal } from '@/components/ui/Modal'
import { useCreateProject } from '@/hooks/useProjects'
import type { ProjectSourceType } from '@/types/api'

interface Props {
  open: boolean
  onClose: () => void
}

const SOURCE_OPTIONS: { value: ProjectSourceType; label: string; description: string }[] = [
  { value: 'local_workspace', label: 'Local Workspace', description: 'Import a folder from this machine' },
  { value: 'zip_upload',      label: 'ZIP Upload',      description: 'Upload a zipped project archive' },
  { value: 'github_repository', label: 'GitHub Repository', description: 'Connect a GitHub repository' },
]

export function CreateProjectModal({ open, onClose }: Props) {
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [sourceType, setSourceType] = useState<ProjectSourceType>('local_workspace')
  const [error, setError] = useState<string | null>(null)

  const { mutateAsync, isPending } = useCreateProject()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    try {
      await mutateAsync({ name: name.trim(), source_type: sourceType, description: description.trim() || undefined })
      handleClose()
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { message?: string } } })?.response?.data?.message
      setError(msg ?? 'Failed to create project')
    }
  }

  const handleClose = () => {
    setName('')
    setDescription('')
    setSourceType('local_workspace')
    setError(null)
    onClose()
  }

  return (
    <Modal
      open={open}
      onClose={handleClose}
      title="Create Project"
      footer={
        <>
          <button type="button" onClick={handleClose} className="btn-ghost">Cancel</button>
          <button type="submit" form="create-project-form" className="btn-primary" disabled={isPending || !name.trim()}>
            {isPending ? 'Creating…' : 'Create Project'}
          </button>
        </>
      }
    >
      <form id="create-project-form" onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="project-name" className="block text-xs font-medium text-slate-400 mb-1.5">
            Project Name <span className="text-red-400">*</span>
          </label>
          <input
            id="project-name"
            className="input"
            placeholder="my-awesome-app"
            value={name}
            onChange={(e) => setName(e.target.value)}
            maxLength={255}
            required
            autoFocus
          />
        </div>

        <div>
          <label className="block text-xs font-medium text-slate-400 mb-1.5">Source Type</label>
          <div className="space-y-2">
            {SOURCE_OPTIONS.map((opt) => (
              <label
                key={opt.value}
                className={`flex items-start gap-3 p-3 rounded-lg border cursor-pointer transition-colors ${
                  sourceType === opt.value
                    ? 'border-canary-500/50 bg-canary-500/5'
                    : 'border-slate-700 hover:border-slate-600'
                }`}
              >
                <input
                  type="radio"
                  name="source_type"
                  value={opt.value}
                  checked={sourceType === opt.value}
                  onChange={() => setSourceType(opt.value)}
                  className="mt-0.5 accent-canary-500"
                />
                <div>
                  <p className="text-sm font-medium text-slate-200">{opt.label}</p>
                  <p className="text-xs text-slate-500">{opt.description}</p>
                </div>
              </label>
            ))}
          </div>
        </div>

        <div>
          <label htmlFor="project-description" className="block text-xs font-medium text-slate-400 mb-1.5">
            Description <span className="text-slate-600">(optional)</span>
          </label>
          <textarea
            id="project-description"
            className="input resize-none"
            rows={2}
            placeholder="Brief description of this project…"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            maxLength={4000}
          />
        </div>

        {error && (
          <p className="text-xs text-red-400 bg-red-900/20 border border-red-800/40 rounded-lg px-3 py-2">
            {error}
          </p>
        )}
      </form>
    </Modal>
  )
}
