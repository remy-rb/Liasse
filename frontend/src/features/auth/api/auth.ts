import { useQueryClient } from '@tanstack/react-query'

import { api } from '@/lib/api-client'

export function useAuthStatus() {
  return api.useQuery('get', '/api/auth/status')
}

// Every auth change re-reads the status; the route guards redirect from it.
function useRefreshAuthStatus() {
  const queryClient = useQueryClient()
  return () => queryClient.invalidateQueries({ queryKey: ['get', '/api/auth/status'] })
}

export function useSetUp() {
  const refresh = useRefreshAuthStatus()
  return api.useMutation('post', '/api/auth/setup', { onSuccess: refresh })
}

export function useLogIn() {
  const refresh = useRefreshAuthStatus()
  return api.useMutation('post', '/api/auth/login', { onSuccess: refresh })
}

export function useLogOut() {
  const queryClient = useQueryClient()
  return api.useMutation('post', '/api/auth/logout', {
    // Drop everything cached for the Owner, then re-read the status.
    onSuccess: () => queryClient.resetQueries(),
  })
}

export function errorMessage(error: unknown): string {
  const detail = (error as { detail?: unknown } | null)?.detail
  return typeof detail === 'string' ? detail : 'Something went wrong. Please try again.'
}
