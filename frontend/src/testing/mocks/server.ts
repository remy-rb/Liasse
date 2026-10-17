import { HttpResponse, http } from 'msw'
import { setupServer } from 'msw/node'

export const handlers = [
  http.get('/api/health', () => HttpResponse.json({ status: 'ok', database: 'ok' })),
]

export const server = setupServer(...handlers)
