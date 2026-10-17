import { Badge } from '@/components/ui/badge'

import type { Document } from '../api/documents'

const LABELS: Record<Document['status'], string> = {
  processing: 'Processing',
  filed: 'Filed',
  inbox: 'Inbox',
  failed: 'Failed',
}

export function StatusBadge({ status }: { status: Document['status'] }) {
  const variant =
    status === 'failed'
      ? 'destructive'
      : status === 'filed'
        ? 'default'
        : status === 'inbox'
          ? 'secondary'
          : 'outline'
  return <Badge variant={variant}>{LABELS[status]}</Badge>
}
