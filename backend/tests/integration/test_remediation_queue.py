"""Integration tests for the remediation queue endpoints."""
import pytest
from httpx import AsyncClient

import app.api.deps as deps
from app.models.alerts import AlertSeverity
from app.models.remediation import ApprovalStatus, BashScript, RemediationItem
from app.services.store import InMemoryStore
from app.utils.hashing import sha256_text
from app.utils.ids import new_id


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_SCRIPT_BODY = "#!/bin/bash\necho 'block attacker'\niptables -I INPUT -s 1.2.3.4 -j DROP"


def _make_item(
    severity: AlertSeverity = AlertSeverity.HIGH,
    status: ApprovalStatus = ApprovalStatus.PENDING,
    report_id: str = "report-001",
) -> RemediationItem:
    body = _SCRIPT_BODY
    script = BashScript(
        body=body,
        rationale="Block malicious IP detected in IR report.",
        target_hosts=["web-prod-01.corp.local"],
        requires_root=True,
        sha256=sha256_text(body),
    )
    return RemediationItem(
        id=new_id(),
        report_id=report_id,
        severity=severity,
        script=script,
        approval_status=status,
        auto_approved=(status == ApprovalStatus.APPROVED),
    )


def _inject_item(item: RemediationItem) -> None:
    """Add the item directly to the singleton store used by the live app."""
    deps._store.add_remediation(item)


def _clear_remediation() -> None:
    """Remove all remediation items from the singleton store."""
    with deps._store._lock:
        deps._store._remediation.clear()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_queue_returns_empty_list_initially(client: AsyncClient) -> None:
    """GET /api/remediation/queue returns [] when no items exist."""
    _clear_remediation()
    resp = await client.get("/api/remediation/queue")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_auto_approved_item_visible_in_queue(client: AsyncClient) -> None:
    """A LOW-severity auto-approved item injected into the store appears in the queue."""
    _clear_remediation()
    item = _make_item(severity=AlertSeverity.LOW, status=ApprovalStatus.APPROVED)
    _inject_item(item)

    resp = await client.get("/api/remediation/queue")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["id"] == item.id
    assert data[0]["approval_status"] == ApprovalStatus.APPROVED
    assert data[0]["auto_approved"] is True


@pytest.mark.asyncio
async def test_approve_pending_item_transitions_to_executed(client: AsyncClient) -> None:
    """POST /api/remediation/{id}/approve changes a PENDING item to EXECUTED."""
    _clear_remediation()
    item = _make_item(severity=AlertSeverity.HIGH, status=ApprovalStatus.PENDING)
    _inject_item(item)

    resp = await client.post(
        f"/api/remediation/{item.id}/approve",
        json={"approver": "analyst@corp.local"},
    )
    assert resp.status_code == 200
    log = resp.json()
    assert log["remediation_id"] == item.id
    assert log["approver"] == "analyst@corp.local"
    assert log["simulated_exit_code"] == 0

    # Verify store state
    updated = deps._store.get_remediation(item.id)
    assert updated is not None
    assert updated.approval_status == ApprovalStatus.EXECUTED


@pytest.mark.asyncio
async def test_reject_pending_item_transitions_to_rejected(client: AsyncClient) -> None:
    """POST /api/remediation/{id}/reject changes a PENDING item to REJECTED."""
    _clear_remediation()
    item = _make_item(severity=AlertSeverity.CRITICAL, status=ApprovalStatus.PENDING)
    _inject_item(item)

    resp = await client.post(
        f"/api/remediation/{item.id}/reject",
        json={"approver": "analyst@corp.local", "reason": "Script is too destructive"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "rejected"
    assert body["id"] == item.id

    updated = deps._store.get_remediation(item.id)
    assert updated is not None
    assert updated.approval_status == ApprovalStatus.REJECTED
    assert updated.rejection_reason == "Script is too destructive"


@pytest.mark.asyncio
async def test_approve_already_executed_item_returns_409(client: AsyncClient) -> None:
    """Approving an item that is already EXECUTED returns 409 Conflict."""
    _clear_remediation()
    # First insert as PENDING and approve it
    item = _make_item(severity=AlertSeverity.HIGH, status=ApprovalStatus.PENDING)
    _inject_item(item)

    await client.post(
        f"/api/remediation/{item.id}/approve",
        json={"approver": "analyst@corp.local"},
    )

    # Try to approve again
    resp = await client.post(
        f"/api/remediation/{item.id}/approve",
        json={"approver": "analyst@corp.local"},
    )
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_reject_nonexistent_item_returns_404(client: AsyncClient) -> None:
    """Rejecting an item that does not exist returns 404."""
    resp = await client.post(
        "/api/remediation/no_such_item_xyz/reject",
        json={"approver": "analyst@corp.local"},
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_approve_nonexistent_item_returns_404(client: AsyncClient) -> None:
    """Approving an item that does not exist returns 404."""
    resp = await client.post(
        "/api/remediation/no_such_item_xyz/approve",
        json={"approver": "analyst@corp.local"},
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_reject_already_rejected_item_returns_409(client: AsyncClient) -> None:
    """Rejecting an already-REJECTED item returns 409 (only PENDING is rejectable)."""
    _clear_remediation()
    item = _make_item(severity=AlertSeverity.HIGH, status=ApprovalStatus.PENDING)
    _inject_item(item)

    await client.post(
        f"/api/remediation/{item.id}/reject",
        json={"approver": "analyst@corp.local"},
    )

    resp = await client.post(
        f"/api/remediation/{item.id}/reject",
        json={"approver": "analyst@corp.local"},
    )
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_queue_lists_multiple_items(client: AsyncClient) -> None:
    """The queue endpoint returns all items regardless of status."""
    _clear_remediation()
    items = [
        _make_item(severity=AlertSeverity.LOW, status=ApprovalStatus.APPROVED),
        _make_item(severity=AlertSeverity.HIGH, status=ApprovalStatus.PENDING),
        _make_item(severity=AlertSeverity.CRITICAL, status=ApprovalStatus.PENDING),
    ]
    for it in items:
        _inject_item(it)

    resp = await client.get("/api/remediation/queue")
    assert resp.status_code == 200
    assert len(resp.json()) == 3
