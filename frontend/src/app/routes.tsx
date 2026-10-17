import type { RouteObject } from 'react-router'

import { ComingSoon } from '@/components/coming-soon'
import { AppLayout } from '@/components/layouts/app-layout'

export const routes: RouteObject[] = [
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
]
