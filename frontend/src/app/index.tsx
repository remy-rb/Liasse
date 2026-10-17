import { createBrowserRouter, RouterProvider } from 'react-router'

import { AppProvider } from './provider'
import { routes } from './routes'

const router = createBrowserRouter(routes)

export function App() {
  return (
    <AppProvider>
      <RouterProvider router={router} />
    </AppProvider>
  )
}
