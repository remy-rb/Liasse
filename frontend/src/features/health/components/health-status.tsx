import { Badge } from '@/components/ui/badge'
import { api } from '@/lib/api-client'

export function HealthStatus() {
  const { data, isPending, isError } = api.useQuery('get', '/api/health')

  if (isPending) return <Badge variant="outline">Checking…</Badge>
  if (isError) return <Badge variant="destructive">Backend unreachable</Badge>
  if (data.database !== 'ok') return <Badge variant="destructive">Database unreachable</Badge>
  return <Badge variant="secondary">All systems ok</Badge>
}
