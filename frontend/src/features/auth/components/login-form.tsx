import type { FormEvent } from 'react'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

import { errorMessage, useLogIn } from '../api/auth'
import { AuthCard } from './auth-card'

export function LoginForm() {
  const logIn = useLogIn()

  function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const password = String(new FormData(event.currentTarget).get('password'))
    logIn.mutate({ body: { password } })
  }

  return (
    <AuthCard title="Log in to Liasse" description="Enter your password to open your Documents.">
      <form onSubmit={onSubmit} className="flex flex-col gap-4">
        <div className="flex flex-col gap-2">
          <Label htmlFor="password">Password</Label>
          <Input
            id="password"
            name="password"
            type="password"
            autoComplete="current-password"
            required
            autoFocus
          />
        </div>
        {logIn.isError && (
          <p role="alert" className="text-sm text-destructive">
            {errorMessage(logIn.error)}
          </p>
        )}
        <Button type="submit" disabled={logIn.isPending}>
          {logIn.isPending ? 'Logging in…' : 'Log in'}
        </Button>
      </form>
    </AuthCard>
  )
}
