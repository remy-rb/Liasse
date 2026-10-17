import { screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { HttpResponse, http } from 'msw'
import { describe, expect, it } from 'vitest'

import { backend, server } from '@/testing/mocks/server'
import { renderApp } from '@/testing/render-app'

const unfiled = { title: null, category: null, correspondent: null, document_date: null }

const pdf = (name: string, size = 10) => new File(['x'.repeat(size)], name, { type: 'application/pdf' })

describe('Documents', () => {
  it('invites the Owner to upload when there are no Documents', async () => {
    renderApp('/')

    expect(await screen.findByText('No Documents yet. Upload one to get started.')).toBeInTheDocument()
  })

  it('shows each Document with its status', async () => {
    backend.documents = [
      {
        id: '1',
        status: 'inbox',
        original_filename: 'edf.pdf',
        ...unfiled,
        page_count: 2,
        failure_reason: null,
        created_at: '2026-10-17T10:00:00Z',
      },
      {
        id: '2',
        status: 'failed',
        original_filename: 'blurry.jpg',
        ...unfiled,
        page_count: 1,
        failure_reason: 'Liasse couldn’t process this file.',
        created_at: '2026-10-17T09:00:00Z',
      },
    ]
    renderApp('/')

    const [first, second] = within(await screen.findByRole('list', { name: 'Documents' })).getAllByRole('listitem')
    expect(first).toHaveTextContent('edf.pdf')
    expect(first).toHaveTextContent('2 pages')
    expect(first).toHaveTextContent('Inbox')
    expect(second).toHaveTextContent('Failed')
    expect(second).toHaveTextContent('Liasse couldn’t process this file.')
  })

  it('shows where a Filed Document went', async () => {
    backend.documents = [
      {
        id: '1',
        status: 'filed',
        original_filename: 'scan.pdf',
        title: 'Facture électricité',
        category: 'Invoices',
        correspondent: 'EDF',
        document_date: '2025-03-14',
        page_count: 2,
        failure_reason: null,
        created_at: '2026-10-17T10:00:00Z',
      },
    ]
    renderApp('/')

    const [item] = within(await screen.findByRole('list', { name: 'Documents' })).getAllByRole('listitem')
    expect(item).toHaveTextContent('Facture électricité')
    expect(item).toHaveTextContent('Invoices › EDF')
    expect(item).toHaveTextContent('2025')
    expect(item).toHaveTextContent('Filed')
    expect(item).not.toHaveTextContent('scan.pdf')
  })

  it('refreshes while a Document is processing', async () => {
    backend.documents = [
      {
        id: '1',
        status: 'processing',
        original_filename: 'edf.pdf',
        ...unfiled,
        page_count: 1,
        failure_reason: null,
        created_at: '2026-10-17T10:00:00Z',
      },
    ]
    renderApp('/')
    expect(await screen.findByText('Processing')).toBeInTheDocument()

    backend.documents = [{ ...backend.documents[0], status: 'inbox' }]

    const list = screen.getByRole('list', { name: 'Documents' })
    expect(await within(list).findByText('Inbox', {}, { timeout: 4000 })).toBeInTheDocument()
  })
})

// Picks files and submits once the upload limits have loaded.
async function uploadFiles(user: ReturnType<typeof userEvent.setup>, files: File[]) {
  await user.upload(await screen.findByLabelText('PDFs or images'), files)
  const button = screen.getByRole('button', { name: 'Upload' })
  await waitFor(() => expect(button).toBeEnabled())
  await user.click(button)
}

describe('Upload', () => {
  it('uploads several files and lists them as processing', async () => {
    const user = userEvent.setup()
    renderApp('/upload')

    await uploadFiles(user, [pdf('a.pdf'), pdf('b.pdf')])

    expect(await screen.findByText(/2 Documents are being processed/)).toBeInTheDocument()
    await user.click(screen.getByRole('link', { name: 'See your Documents' }))
    const items = within(await screen.findByRole('list', { name: 'Documents' })).getAllByRole('listitem')
    expect(items.map((item) => item.textContent)).toEqual([
      expect.stringContaining('b.pdf'),
      expect.stringContaining('a.pdf'),
    ])
    expect(items[0]).toHaveTextContent('Processing')
  })

  it('shows why the server rejected a file', async () => {
    const user = userEvent.setup({ applyAccept: false })
    renderApp('/upload')

    await uploadFiles(user, [
      new File(['hello'], 'notes.txt', { type: 'text/plain' }),
    ])

    expect(await screen.findByRole('status')).toHaveTextContent(
      'notes.txt: Only PDF, JPEG, PNG and HEIC files are supported.',
    )
  })

  it('refuses files over the size limit without sending them', async () => {
    let sent = false
    server.events.on('request:start', ({ request }) => {
      if (request.method === 'POST' && request.url.endsWith('/api/documents')) sent = true
    })
    const user = userEvent.setup()
    renderApp('/upload')

    await uploadFiles(user, [pdf('huge.pdf', 5000)])

    expect(await screen.findByRole('status')).toHaveTextContent('huge.pdf: This file is larger than 1 KB.')
    expect(sent).toBe(false)
    server.events.removeAllListeners()
  })

  it('says when the upload fails', async () => {
    server.use(http.post('/api/documents', () => HttpResponse.error()))
    const user = userEvent.setup()
    renderApp('/upload')

    await uploadFiles(user, [pdf('a.pdf')])

    expect(await screen.findByRole('alert')).toHaveTextContent('The upload failed.')
  })
})
