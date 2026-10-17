import { Navigate, Outlet } from 'react-router'

import { useAuthStatus } from '../api/auth'

function StatusMessage({ children }: { children: string }) {
  return (
    <main className="flex min-h-dvh items-center justify-center px-4 text-muted-foreground">
      <p>{children}</p>
    </main>
  )
}

// Wraps every screen that needs a logged-in Owner.
export function RequireOwner() {
  const { data, isPending, isError } = useAuthStatus()

  if (isPending) return <StatusMessage>Loading…</StatusMessage>
  if (isError) return <StatusMessage>Liasse can’t reach its server. Try again shortly.</StatusMessage>
  if (data.setup_required) return <Navigate to="/setup" replace />
  if (!data.authenticated) return <Navigate to="/login" replace />
  return <Outlet />
}

// Wraps first-run setup and login: sends the Owner to the screen that fits their state.
export function RequireGuest({ screen }: { screen: 'setup' | 'login' }) {
  const { data, isPending, isError } = useAuthStatus()

  if (isPending) return <StatusMessage>Loading…</StatusMessage>
  if (isError) return <StatusMessage>Liasse can’t reach its server. Try again shortly.</StatusMessage>
  if (data.authenticated) return <Navigate to="/" replace />
  if (data.setup_required && screen === 'login') return <Navigate to="/setup" replace />
  if (!data.setup_required && screen === 'setup') return <Navigate to="/login" replace />
  return <Outlet />
}
