import type { RouteObject } from 'react-router'

import { ComingSoon } from '@/components/coming-soon'
import { AppLayout } from '@/components/layouts/app-layout'
import { LoginForm } from '@/features/auth/components/login-form'
import { RequireGuest, RequireOwner } from '@/features/auth/components/route-guards'
import { SetupForm } from '@/features/auth/components/setup-form'

export const routes: RouteObject[] = [
  {
    element: <RequireGuest screen="setup" />,
    children: [{ path: '/setup', element: <SetupForm /> }],
  },
  {
    element: <RequireGuest screen="login" />,
    children: [{ path: '/login', element: <LoginForm /> }],
  },
  {
    element: <RequireOwner />,
    children: [
      {
        element: <AppLayout />,
        children: [
          { path: '/', element: <ComingSoon title="Documents" /> },
          { path: '/inbox', element: <ComingSoon title="Inbox" /> },
          { path: '/upload', element: <ComingSoon title="Upload" /> },
          { path: '/search', element: <ComingSoon title="Search" /> },
          { path: '/ask', element: <ComingSoon title="Ask" /> },
        ],
      },
    ],
  },
]
