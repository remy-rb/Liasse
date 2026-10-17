import { type FormEvent, useState } from 'react'
import { Link } from 'react-router'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

import { type UploadResult, useUploadDocuments, useUploadLimits } from '../api/documents'

const ACCEPT = '.pdf,.jpg,.jpeg,.png,.heic,application/pdf,image/jpeg,image/png,image/heic'

function readableSize(bytes: number) {
  return bytes >= 1024 ** 2 ? `${Math.floor(bytes / 1024 ** 2)} MB` : `${Math.floor(bytes / 1024)} KB`
}

export function UploadForm() {
  const limits = useUploadLimits()
  const uploadDocuments = useUploadDocuments()
  const [result, setResult] = useState<UploadResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const form = event.currentTarget
    const input = form.elements.namedItem('files') as HTMLInputElement
    const files = Array.from(input.files ?? [])
    setResult(null)
    setError(null)
    if (files.length === 0) return setError('Choose at least one file.')
    if (!limits.data) return
    const { max_bytes, max_files } = limits.data
    if (files.length > max_files) return setError(`Upload at most ${max_files} files at once.`)

    // Oversized files are refused here, so nobody waits for an upload that will fail.
    const tooBig = files.filter((file) => file.size > max_bytes)
    const toSend = files.filter((file) => file.size <= max_bytes)
    const rejectedHere = tooBig.map((file) => ({
      filename: file.name,
      reason: `This file is larger than ${readableSize(max_bytes)}.`,
    }))
    const sent = toSend.length
      ? await uploadDocuments.upload(toSend).catch(() => null)
      : { accepted: [], rejected: [] }
    if (!sent) return setError('The upload failed. Check your connection and try again.')
    setResult({ accepted: sent.accepted, rejected: [...rejectedHere, ...sent.rejected] })
    form.reset()
  }

  return (
    <section className="mx-auto flex max-w-xl flex-col gap-6">
      <h1 className="text-2xl font-semibold">Upload</h1>
      <form onSubmit={onSubmit} className="flex flex-col gap-4">
        <div className="flex flex-col gap-2">
          <Label htmlFor="files">PDFs or images</Label>
          <Input id="files" name="files" type="file" multiple accept={ACCEPT} />
          {limits.data && (
            <p className="text-sm text-muted-foreground">
              PDF, JPEG, PNG or HEIC, up to {readableSize(limits.data.max_bytes)} each and{' '}
              {limits.data.max_files} files at once. Each file becomes one Document.
            </p>
          )}
        </div>
        {error && (
          <p role="alert" className="text-sm text-destructive">
            {error}
          </p>
        )}
        <Button type="submit" disabled={uploadDocuments.isPending || !limits.data}>
          {uploadDocuments.isPending ? 'Uploading…' : 'Upload'}
        </Button>
      </form>
      {result && (
        <div className="flex flex-col gap-3" role="status">
          {result.accepted.length > 0 && (
            <p>
              {result.accepted.length === 1
                ? '1 Document is being processed.'
                : `${result.accepted.length} Documents are being processed.`}{' '}
              <Link to="/" className="underline">
                See your Documents
              </Link>
            </p>
          )}
          {result.rejected.length > 0 && (
            <div>
              <p className="font-medium text-destructive">Not uploaded:</p>
              <ul className="list-disc pl-5 text-sm">
                {result.rejected.map((rejected, index) => (
                  <li key={index}>
                    <span className="font-medium">{rejected.filename}</span>: {rejected.reason}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </section>
  )
}
