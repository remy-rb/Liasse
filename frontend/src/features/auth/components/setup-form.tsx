import { type FormEvent, useState } from 'react'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

import { errorMessage, useSetUp } from '../api/auth'
import { AuthCard } from './auth-card'

const MIN_LENGTH = 8

export function SetupForm() {
  const setUp = useSetUp()
  const [mismatch, setMismatch] = useState(false)

  function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    const password = String(form.get('password'))
    const same = password === String(form.get('confirm'))
    setMismatch(!same)
    if (same) setUp.mutate({ body: { password } })
  }

  const error = mismatch ? 'The passwords don’t match.' : setUp.isError && errorMessage(setUp.error)

  return (
    <AuthCard
      title="Welcome to Liasse"
      description="Choose the password you’ll use to open your Documents."
    >
      <form onSubmit={onSubmit} className="flex flex-col gap-4">
        <div className="flex flex-col gap-2">
          <Label htmlFor="password">Password</Label>
          <Input
            id="password"
            name="password"
            type="password"
            autoComplete="new-password"
            minLength={MIN_LENGTH}
            required
            aria-describedby="password-hint"
          />
          <p id="password-hint" className="text-sm text-muted-foreground">
            At least {MIN_LENGTH} characters.
          </p>
        </div>
        <div className="flex flex-col gap-2">
          <Label htmlFor="confirm">Confirm password</Label>
          <Input
            id="confirm"
            name="confirm"
            type="password"
            autoComplete="new-password"
            required
          />
        </div>
        {error && (
          <p role="alert" className="text-sm text-destructive">
            {error}
          </p>
        )}
        <Button type="submit" disabled={setUp.isPending}>
          {setUp.isPending ? 'Setting up…' : 'Set password'}
        </Button>
      </form>
    </AuthCard>
  )
}
