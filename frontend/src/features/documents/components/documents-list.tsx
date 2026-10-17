import { Link } from 'react-router'

import { buttonVariants } from '@/components/ui/button'

import { useDocuments } from '../api/documents'
import { StatusBadge } from './status-badge'

const dateFormat = new Intl.DateTimeFormat(undefined, { dateStyle: 'medium', timeStyle: 'short' })

export function DocumentsList() {
  const { data, isPending, isError } = useDocuments()

  return (
    <section className="mx-auto flex max-w-3xl flex-col gap-4">
      <div className="flex items-center justify-between gap-4">
        <h1 className="text-2xl font-semibold">Documents</h1>
        <Link to="/upload" className={buttonVariants()}>
          Upload
        </Link>
      </div>
      {isPending && <p className="text-muted-foreground">Loading…</p>}
      {isError && <p className="text-destructive">Your Documents couldn’t be loaded.</p>}
      {data?.length === 0 && (
        <p className="text-muted-foreground">No Documents yet. Upload one to get started.</p>
      )}
      {data && data.length > 0 && (
        <ul className="divide-y rounded-lg border" aria-label="Documents">
          {data.map((document) => (
            <li key={document.id} className="flex items-center justify-between gap-4 px-4 py-3">
              <div className="min-w-0">
                <p className="truncate font-medium">{document.original_filename}</p>
                <p className="text-sm text-muted-foreground">
                  {document.page_count} {document.page_count === 1 ? 'page' : 'pages'} ·{' '}
                  {dateFormat.format(new Date(document.created_at))}
                </p>
                {document.failure_reason && (
                  <p className="text-sm text-destructive">{document.failure_reason}</p>
                )}
              </div>
              <StatusBadge status={document.status} />
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
