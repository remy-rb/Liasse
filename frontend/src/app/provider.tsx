import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { type ReactNode, useState } from 'react'

type AppProviderProps = { children: ReactNode; queryClient?: QueryClient }

export function AppProvider({ children, queryClient: given }: AppProviderProps) {
  const [queryClient] = useState(() => given ?? new QueryClient())
  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
}
