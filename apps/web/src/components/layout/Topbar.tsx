import { useLocation } from 'react-router-dom'
import { LogOut, User } from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import { useHealth } from '@/hooks/useHealth'

const PAGE_TITLES: Record<string, string> = {
  '/dashboard':    'Overview',
  '/projects':     'Projects',
  '/codebase':     'Codebase',
  '/architecture': 'Architecture',
  '/security':     'Security',
  '/dependencies': 'Dependencies',
  '/ai':           'AI Assistant',
  '/github':       'GitHub',
  '/activity':     'Activity',
  '/settings':     'Settings',
}

export function Topbar() {
  const { pathname } = useLocation()
  const { user, logout } = useAuth()
  const { data: health } = useHealth()

  // Match the longest prefix
  const title =
    Object.entries(PAGE_TITLES)
      .filter(([path]) => pathname.startsWith(path))
      .sort((a, b) => b[0].length - a[0].length)[0]?.[1] ?? 'Canary'

  return (
    <header className="flex-none h-12 bg-surface-800 border-b border-slate-700/60 flex items-center justify-between px-5">
      <h1 className="text-sm font-semibold text-slate-200">{title}</h1>

      <div className="flex items-center gap-3">
        {/* API health indicator */}
        <div className="flex items-center gap-1.5 text-xs">
          <span
            className={`w-1.5 h-1.5 rounded-full ${health?.status === 'ok' ? 'bg-emerald-400' : 'bg-red-400'}`}
          />
          <span className="text-slate-500">
            {health?.status === 'ok' ? 'API connected' : 'API offline'}
          </span>
        </div>

        {/* User */}
        <div className="flex items-center gap-2 border-l border-slate-700/60 pl-3">
          <div className="w-6 h-6 rounded-full bg-surface-600 flex items-center justify-center">
            <User className="w-3.5 h-3.5 text-slate-400" />
          </div>
          <span className="text-xs text-slate-400 max-w-[120px] truncate">
            {user?.full_name ?? user?.email ?? 'User'}
          </span>
          <button
            onClick={logout}
            className="p-1 rounded text-slate-500 hover:text-slate-300 hover:bg-surface-700 transition-colors"
            title="Sign out"
          >
            <LogOut className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </header>
  )
}
