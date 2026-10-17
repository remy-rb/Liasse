import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it } from 'vitest'

import { backend } from '@/testing/mocks/server'
import { renderApp } from '@/testing/render-app'

const PASSWORD = 'correct horse battery staple'

describe('first-run setup', () => {
  it('sends a fresh install to setup, then into the app', async () => {
    backend.password = null
    backend.loggedIn = false
    const user = userEvent.setup()
    renderApp('/')

    await user.type(await screen.findByLabelText('Password'), 'a new password')
    await user.type(screen.getByLabelText('Confirm password'), 'a new password')
    await user.click(screen.getByRole('button', { name: 'Set password' }))

    expect(await screen.findByRole('heading', { name: 'Documents' })).toBeInTheDocument()
    expect(backend.password).toBe('a new password')
  })

  it('refuses mismatched passwords', async () => {
    backend.password = null
    backend.loggedIn = false
    const user = userEvent.setup()
    renderApp('/setup')

    await user.type(await screen.findByLabelText('Password'), 'a new password')
    await user.type(screen.getByLabelText('Confirm password'), 'another password')
    await user.click(screen.getByRole('button', { name: 'Set password' }))

    expect(screen.getByRole('alert')).toHaveTextContent('The passwords don’t match.')
    expect(backend.password).toBeNull()
  })

  it('sends setup to login once an Owner exists', async () => {
    backend.loggedIn = false
    renderApp('/setup')

    expect(await screen.findByRole('heading', { name: 'Log in to Liasse' })).toBeInTheDocument()
  })
})

describe('login', () => {
  it('sends a logged-out Owner to login, then back into the app', async () => {
    backend.loggedIn = false
    const user = userEvent.setup()
    renderApp('/inbox')

    await user.type(await screen.findByLabelText('Password'), PASSWORD)
    await user.click(screen.getByRole('button', { name: 'Log in' }))

    expect(await screen.findByRole('heading', { name: 'Documents' })).toBeInTheDocument()
  })

  it('shows an error for a wrong password', async () => {
    backend.loggedIn = false
    const user = userEvent.setup()
    renderApp('/login')

    await user.type(await screen.findByLabelText('Password'), 'wrong password')
    await user.click(screen.getByRole('button', { name: 'Log in' }))

    expect(await screen.findByRole('alert')).toHaveTextContent('Incorrect password')
  })

  it('logs out back to the login screen', async () => {
    const user = userEvent.setup()
    renderApp('/')

    await user.click(await screen.findByRole('button', { name: 'Log out' }))

    expect(await screen.findByRole('heading', { name: 'Log in to Liasse' })).toBeInTheDocument()
    expect(backend.loggedIn).toBe(false)
  })
})
