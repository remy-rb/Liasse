import { FileText, Inbox, MessageCircleQuestion, Search, Upload } from 'lucide-react'
import { NavLink, Outlet } from 'react-router'

import { HealthStatus } from '@/features/health/components/health-status'
import { cn } from '@/lib/utils'

const navigation = [
  { to: '/', label: 'Documents', icon: FileText },
  { to: '/inbox', label: 'Inbox', icon: Inbox },
  { to: '/upload', label: 'Upload', icon: Upload },
  { to: '/search', label: 'Search', icon: Search },
  { to: '/ask', label: 'Ask', icon: MessageCircleQuestion },
]

export function AppLayout() {
  return (
    <div className="flex min-h-dvh flex-col bg-background text-foreground">
      <header className="flex items-center justify-between gap-4 border-b px-4 py-3">
        <span className="text-lg font-semibold">Liasse</span>
        <nav aria-label="Main" className="hidden gap-1 md:flex">
          <NavItems />
        </nav>
        <HealthStatus />
      </header>
      <main className="flex-1 px-4 py-6 pb-24 md:pb-6">
        <Outlet />
      </main>
      {/* Phones get a bottom tab bar instead of the header links. */}
      <nav
        aria-label="Main"
        className="fixed inset-x-0 bottom-0 grid grid-cols-5 border-t bg-background md:hidden"
      >
        <NavItems compact />
      </nav>
    </div>
  )
}

function NavItems({ compact = false }: { compact?: boolean }) {
  return navigation.map(({ to, label, icon: Icon }) => (
    <NavLink
      key={to}
      to={to}
      end
      className={({ isActive }) =>
        cn(
          'flex items-center gap-2 rounded-md px-3 py-2 text-sm text-muted-foreground hover:text-foreground',
          compact && 'flex-col gap-1 rounded-none py-2 text-xs',
          isActive && 'font-medium text-foreground',
        )
      }
    >
      <Icon className="size-5" aria-hidden />
      {label}
    </NavLink>
  ))
}
