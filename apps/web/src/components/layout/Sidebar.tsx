import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  FolderKanban,
  Code2,
  Network,
  ShieldAlert,
  Package,
  Bot,
  Github,
  Activity,
  Settings,
  Bird,
} from 'lucide-react'
import { cn } from '@/lib/utils'

interface NavItem {
  label: string
  to: string
  icon: React.ComponentType<{ className?: string }>
}

const navItems: NavItem[] = [
  { label: 'Overview',      to: '/dashboard',     icon: LayoutDashboard },
  { label: 'Projects',      to: '/projects',      icon: FolderKanban },
  { label: 'Codebase',      to: '/codebase',      icon: Code2 },
  { label: 'Architecture',  to: '/architecture',  icon: Network },
  { label: 'Security',      to: '/security',      icon: ShieldAlert },
  { label: 'Dependencies',  to: '/dependencies',  icon: Package },
  { label: 'AI Assistant',  to: '/ai',            icon: Bot },
  { label: 'GitHub',        to: '/github',        icon: Github },
  { label: 'Activity',      to: '/activity',      icon: Activity },
  { label: 'Settings',      to: '/settings',      icon: Settings },
]

export function Sidebar() {
  return (
    <aside className="w-56 flex-none bg-surface-800 border-r border-slate-700/60 flex flex-col">
      {/* Logo */}
      <div className="flex items-center gap-2.5 px-4 py-5 border-b border-slate-700/60">
        <div className="flex-none w-8 h-8 rounded-lg bg-canary-500 flex items-center justify-center">
          <Bird className="w-4.5 h-4.5 text-surface-900" />
        </div>
        <div className="leading-none">
          <p className="text-sm font-semibold text-slate-100">Canary</p>
          <p className="text-[10px] text-slate-500 mt-0.5">Workspace Intelligence</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-3 px-2 space-y-0.5">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                isActive
                  ? 'bg-canary-500/10 text-canary-400'
                  : 'text-slate-400 hover:bg-surface-700 hover:text-slate-200',
              )
            }
          >
            <item.icon className="w-4 h-4 flex-none" />
            {item.label}
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="px-4 py-3 border-t border-slate-700/60">
        <p className="text-[10px] text-slate-600">v0.1.0 · foundation</p>
      </div>
    </aside>
  )
}
