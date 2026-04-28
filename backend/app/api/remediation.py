from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_store
from app.models.remediation import ApprovalAction, ApprovalStatus, ExecutionLog, RemediationItem
from app.services.executor import executor
from app.services.store import InMemoryStore

router = APIRouter()


@router.get("/remediation/queue", response_model=list[RemediationItem])
def list_queue(store: InMemoryStore = Depends(get_store)) -> list[RemediationItem]:
    return store.list_remediation_queue()


@router.get("/remediation/{item_id}", response_model=RemediationItem)
def get_item(item_id: str, store: InMemoryStore = Depends(get_store)) -> RemediationItem:
    item = store.get_remediation(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Remediation item not found")
    return item


@router.post("/remediation/{item_id}/approve", response_model=ExecutionLog)
def approve(
    item_id: str,
    action: ApprovalAction,
    store: InMemoryStore = Depends(get_store),
) -> ExecutionLog:
    item = store.get_remediation(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Remediation item not found")
    if item.approval_status not in (ApprovalStatus.PENDING, ApprovalStatus.APPROVED):
        raise HTTPException(
            status_code=409,
            detail=f"Item is already {item.approval_status}",
        )

    updated = item.model_copy(
        update={
            "approval_status": ApprovalStatus.EXECUTED,
            "approver": action.approver,
            "actioned_at": datetime.now(tz=timezone.utc),
        }
    )
    store.update_remediation(updated)

    return executor.run(
        remediation_id=item_id,
        script_sha256=item.script.sha256,
        approver=action.approver,
    )


@router.post("/remediation/{item_id}/reject")
def reject(
    item_id: str,
    action: ApprovalAction,
    store: InMemoryStore = Depends(get_store),
) -> dict:
    item = store.get_remediation(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Remediation item not found")
    if item.approval_status not in (ApprovalStatus.PENDING,):
        raise HTTPException(
            status_code=409,
            detail=f"Cannot reject item with status {item.approval_status}",
        )

    updated = item.model_copy(
        update={
            "approval_status": ApprovalStatus.REJECTED,
            "approver": action.approver,
            "rejection_reason": action.reason,
            "actioned_at": datetime.now(tz=timezone.utc),
        }
    )
    store.update_remediation(updated)
    return {"status": "rejected", "id": item_id}
