import { QueryClient } from '@tanstack/react-query'
import { render } from '@testing-library/react'
import { createMemoryRouter, RouterProvider } from 'react-router'

import { AppProvider } from '@/app/provider'
import { routes } from '@/app/routes'

export function renderApp(path = '/') {
  const router = createMemoryRouter(routes, { initialEntries: [path] })
  // No retries, so error states show up immediately.
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <AppProvider queryClient={queryClient}>
      <RouterProvider router={router} />
    </AppProvider>,
  )
}
