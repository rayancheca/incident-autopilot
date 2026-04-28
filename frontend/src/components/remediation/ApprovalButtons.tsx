import { Check, X } from 'lucide-react'
import { useApproveRemediation, useRejectRemediation } from '../../hooks/useRemediationQueue'
import type { RemediationItem } from '../../types/remediation'
import { Button } from '../ui/Button'

interface ApprovalButtonsProps {
  item: RemediationItem
}

export function ApprovalButtons({ item }: ApprovalButtonsProps) {
  const approveMutation = useApproveRemediation()
  const rejectMutation = useRejectRemediation()

  if (item.approval_status !== 'PENDING') {
    return (
      <span className={`text-xs font-semibold px-2 py-1 rounded border ${
        item.approval_status === 'EXECUTED'
          ? 'text-green-400 bg-green-400/10 border-green-400/30'
          : item.approval_status === 'REJECTED'
          ? 'text-red-400 bg-red-400/10 border-red-400/30'
          : 'text-blue-400 bg-blue-400/10 border-blue-400/30'
      }`}>
        {item.approval_status}
      </span>
    )
  }

  return (
    <div className="flex gap-2">
      <Button
        variant="primary"
        size="sm"
        onClick={() => approveMutation.mutate({ id: item.id, action: { approver: 'analyst@local' } })}
        disabled={approveMutation.isPending}
      >
        <Check size={12} />
        Approve
      </Button>
      <Button
        variant="danger"
        size="sm"
        onClick={() =>
          rejectMutation.mutate({ id: item.id, action: { approver: 'analyst@local', reason: 'Rejected by analyst' } })
        }
        disabled={rejectMutation.isPending}
      >
        <X size={12} />
        Reject
      </Button>
    </div>
  )
}
