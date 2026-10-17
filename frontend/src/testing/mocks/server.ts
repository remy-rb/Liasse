import { HttpResponse, http } from 'msw'
import { setupServer } from 'msw/node'

import type { components } from '@/types/api'

type Document = components['schemas']['DocumentOut']

// Fake backend state, reset before each test. Defaults to a logged-in Owner with no Documents.
export const backend = {
  password: 'correct horse battery staple' as string | null,
  loggedIn: true,
  documents: [] as Document[],
  maxBytes: 1024,
}

export function resetBackend() {
  backend.password = 'correct horse battery staple'
  backend.loggedIn = true
  backend.documents = []
  backend.maxBytes = 1024
}

let nextId = 1

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
  http.get('/api/documents', () => HttpResponse.json(backend.documents)),
  http.get('/api/upload-limits', () =>
    HttpResponse.json({ max_bytes: backend.maxBytes, max_files: 20 }),
  ),
  http.post('/api/documents', async ({ request }) => {
    const files = (await request.formData()).getAll('files') as File[]
    const accepted: Document[] = []
    const rejected = []
    for (const file of files) {
      if (!file.name.endsWith('.pdf')) {
        rejected.push({ filename: file.name, reason: 'Only PDF, JPEG, PNG and HEIC files are supported.' })
        continue
      }
      accepted.push({
        id: String(nextId++),
        status: 'processing',
        original_filename: file.name,
        title: null,
        category: null,
        correspondent: null,
        document_date: null,
        page_count: 1,
        failure_reason: null,
        created_at: '2026-10-17T10:00:00Z',
      })
    }
    // Newest first, like the real backend.
    backend.documents = [...[...accepted].reverse(), ...backend.documents]
    return HttpResponse.json({ accepted, rejected })
  }),
]

export const server = setupServer(...handlers)
