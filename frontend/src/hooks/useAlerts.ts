import { useQuery } from '@tanstack/react-query'
import { api } from '../lib/api'
import { ALERT_POLL_INTERVAL } from '../lib/constants'

export function useAlerts(limit = 100) {
  return useQuery({
    queryKey: ['alerts', limit],
    queryFn: () => api.alerts.list(limit),
    refetchInterval: ALERT_POLL_INTERVAL,
    staleTime: 1000,
  })
}
