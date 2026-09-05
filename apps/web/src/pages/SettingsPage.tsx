import { PageHeader } from '@/components/ui/PageHeader'
import { useAuth } from '@/contexts/AuthContext'

export function SettingsPage() {
  const { user } = useAuth()

  return (
    <div>
      <PageHeader
        title="Settings"
        description="Manage your account and platform configuration."
      />

      <div className="max-w-xl space-y-5">
        {/* Account */}
        <section className="card p-5">
          <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-4">Account</h3>
          <dl className="space-y-3">
            <div className="flex justify-between text-sm">
              <dt className="text-slate-500">Email</dt>
              <dd className="text-slate-200 font-medium">{user?.email}</dd>
            </div>
            <div className="flex justify-between text-sm">
              <dt className="text-slate-500">Name</dt>
              <dd className="text-slate-200">{user?.full_name ?? '—'}</dd>
            </div>
            <div className="flex justify-between text-sm">
              <dt className="text-slate-500">Status</dt>
              <dd className="text-emerald-400 text-xs font-medium">Active</dd>
            </div>
          </dl>
        </section>

        {/* AI Provider */}
        <section className="card p-5">
          <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">AI Provider</h3>
          <p className="text-xs text-slate-600 mb-4">
            Configure your LLM provider to enable the AI Codebase Assistant.
          </p>
          <div className="space-y-3">
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1.5">Provider</label>
              <select className="input" disabled>
                <option>none</option>
                <option>openai</option>
                <option>anthropic</option>
                <option>bedrock</option>
              </select>
              <p className="text-[10px] text-slate-600 mt-1">Set CANARY_AI_PROVIDER in your .env file</p>
            </div>
          </div>
        </section>

        {/* Danger zone */}
        <section className="card p-5 border-red-900/40">
          <h3 className="text-xs font-semibold text-red-500 uppercase tracking-wider mb-1">Danger Zone</h3>
          <p className="text-xs text-slate-600 mb-4">
            Destructive actions. These will be implemented in a future phase.
          </p>
          <button className="btn-secondary text-red-400 border-red-900/40 opacity-50 cursor-not-allowed" disabled>
            Delete account
          </button>
        </section>
      </div>
    </div>
  )
}
