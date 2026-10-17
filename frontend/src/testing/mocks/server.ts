import { HttpResponse, http } from 'msw'
import { setupServer } from 'msw/node'

// Fake backend state, reset before each test. Defaults to a logged-in Owner.
export const backend = {
  password: 'correct horse battery staple' as string | null,
  loggedIn: true,
}

export function resetBackend() {
  backend.password = 'correct horse battery staple'
  backend.loggedIn = true
}

const noContent = () => new HttpResponse(null, { status: 204 })

export const handlers = [
  http.get('/api/health', () => HttpResponse.json({ status: 'ok', database: 'ok' })),
  http.get('/api/auth/status', () =>
    HttpResponse.json({ setup_required: backend.password === null, authenticated: backend.loggedIn }),
  ),
  http.post<never, { password: string }>('/api/auth/setup', async ({ request }) => {
    if (backend.password !== null) {
      return HttpResponse.json({ detail: 'Liasse is already set up' }, { status: 409 })
    }
    backend.password = (await request.json()).password
    backend.loggedIn = true
    return noContent()
  }),
  http.post<never, { password: string }>('/api/auth/login', async ({ request }) => {
    if ((await request.json()).password !== backend.password) {
      return HttpResponse.json({ detail: 'Incorrect password' }, { status: 401 })
    }
    backend.loggedIn = true
    return noContent()
  }),
  http.post('/api/auth/logout', () => {
    backend.loggedIn = false
    return noContent()
  }),
]

export const server = setupServer(...handlers)
