import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '../lib/api'
import { QUEUE_POLL_INTERVAL } from '../lib/constants'
import type { ApprovalAction } from '../types/remediation'

export function useRemediationQueue() {
  return useQuery({
    queryKey: ['remediation-queue'],
    queryFn: () => api.remediation.queue(),
    refetchInterval: QUEUE_POLL_INTERVAL,
  })
}

export function useApproveRemediation() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, action }: { id: string; action: ApprovalAction }) =>
      api.remediation.approve(id, action),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['remediation-queue'] })
    },
  })
}

export function useRejectRemediation() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, action }: { id: string; action: ApprovalAction }) =>
      api.remediation.reject(id, action),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['remediation-queue'] })
    },
  })
}
