import { useQueryClient } from '@tanstack/react-query'

import { api } from '@/lib/api-client'
import type { components } from '@/types/api'

export type Document = components['schemas']['DocumentOut']
export type UploadResult = components['schemas']['UploadResult']

const POLL_MS = 2000

export function useDocuments() {
  return api.useQuery('get', '/api/documents', undefined, {
    // Keep refreshing while anything is still being processed.
    refetchInterval: (query) =>
      query.state.data?.some((document) => document.status === 'processing') ? POLL_MS : false,
  })
}

export function useUploadLimits() {
  return api.useQuery('get', '/api/upload-limits')
}

export function useUploadDocuments() {
  const queryClient = useQueryClient()
  const mutation = api.useMutation('post', '/api/documents', {
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['get', '/api/documents'] }),
  })
  return {
    ...mutation,
    upload: (files: File[]) =>
      mutation.mutateAsync({
        // The generated type says string[]; the multipart body really carries Files.
        body: { files: files as unknown as string[] },
        bodySerializer: (body) => {
          const form = new FormData()
          for (const file of body.files as unknown as File[]) form.append('files', file)
          return form
        },
      }),
  }
}
