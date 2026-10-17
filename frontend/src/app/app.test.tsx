import { screen } from '@testing-library/react'
import { HttpResponse, http } from 'msw'
import { describe, expect, it } from 'vitest'

import { server } from '@/testing/mocks/server'
import { renderApp } from '@/testing/render-app'

describe('app shell', () => {
  it('shows that the backend is healthy', async () => {
    renderApp()

    expect(await screen.findByText('All systems ok')).toBeInTheDocument()
  })

  it('shows when the database is unreachable', async () => {
    server.use(
      http.get('/api/health', () =>
        HttpResponse.json({ status: 'degraded', database: 'unreachable' }),
      ),
    )
    renderApp()

    expect(await screen.findByText('Database unreachable')).toBeInTheDocument()
  })

  it('shows when the backend is unreachable', async () => {
    server.use(http.get('/api/health', () => HttpResponse.error()))
    renderApp()

    expect(await screen.findByText('Backend unreachable')).toBeInTheDocument()
  })

  it('links to every main screen', async () => {
    renderApp('/inbox')

    expect(await screen.findByRole('heading', { name: 'Inbox' })).toBeInTheDocument()
    const [nav] = screen.getAllByRole('navigation', { name: 'Main' })
    for (const label of ['Documents', 'Inbox', 'Upload', 'Search', 'Ask']) {
      expect(nav).toHaveTextContent(label)
    }
  })
})
