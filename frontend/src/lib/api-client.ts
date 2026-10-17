import createFetchClient from 'openapi-fetch'
import createClient from 'openapi-react-query'

import type { paths } from '@/types/api'

export const fetchClient = createFetchClient<paths>({
  // Absolute base URL: the API is served from the same origin (Vite proxy in dev, nginx in Docker).
  baseUrl: window.location.origin,
  // Look up fetch per request so test mocks installed after import still apply.
  fetch: (request) => globalThis.fetch(request),
})

export const api = createClient(fetchClient)
