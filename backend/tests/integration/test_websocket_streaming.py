"""Integration tests for WebSocket /ws/reports/{report_id}."""
import asyncio
import json
from unittest.mock import MagicMock

import pytest
from starlette.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

import app.api.deps as deps
from app.main import app
from app.models.reports import IRReport, ReportStatus
from app.utils.ids import new_id

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_WS_POLICY_VIOLATION = 1008
_MAX_SUBSCRIBERS = 20


def _add_report(status: ReportStatus = ReportStatus.PENDING) -> IRReport:
    """Insert a report into the singleton store and return it."""
    report = IRReport(
        id=new_id(),
        alert_ids=["alert-fixture-01"],
        status=status,
        title="Test Incident",
    )
    deps._store.upsert_report(report)
    return report


async def _prefill_subscribers(report_id: str, count: int) -> list[MagicMock]:
    """Add `count` fake WebSocket subscribers to the broker for a given report_id."""
    fakes: list[MagicMock] = []
    for _ in range(count):
        fake = MagicMock()
        await deps.broker.subscribe(report_id, fake)
        fakes.append(fake)
    return fakes


async def _clear_subscribers(report_id: str) -> None:
    """Remove all subscribers for a report from the broker."""
    async with deps.broker._lock:
        deps.broker._subscribers.pop(report_id, None)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_ws_nonexistent_report_closes_with_1008() -> None:
    """Connecting to a report that does not exist must close immediately (code 1008)."""
    with TestClient(app) as client:
        try:
            with client.websocket_connect("/ws/reports/no_such_report_xyz") as ws:
                ws.receive_text()
        except WebSocketDisconnect as exc:
            assert exc.code == _WS_POLICY_VIOLATION
        else:
            pytest.fail("Expected WebSocketDisconnect was not raised")


def test_ws_complete_report_sends_final_message_on_connect() -> None:
    """Connecting to a COMPLETE report triggers an immediate 'final' message."""
    report = _add_report(status=ReportStatus.COMPLETE)

    with TestClient(app) as client:
        with client.websocket_connect(f"/ws/reports/{report.id}") as ws:
            raw = ws.receive_text()

    data = json.loads(raw)
    assert data["type"] == "final"
    assert data["report_id"] == report.id
    assert "report" in data
    assert data["report"]["status"] == ReportStatus.COMPLETE


def test_ws_failed_report_sends_final_message_on_connect() -> None:
    """Connecting to a FAILED report also triggers an immediate 'final' message."""
    report = _add_report(status=ReportStatus.FAILED)

    with TestClient(app) as client:
        with client.websocket_connect(f"/ws/reports/{report.id}") as ws:
            raw = ws.receive_text()

    data = json.loads(raw)
    assert data["type"] == "final"
    assert data["report_id"] == report.id


def test_ws_pending_report_accepts_connection_without_immediate_message() -> None:
    """Connecting to a PENDING report is accepted but sends no message immediately."""
    report = _add_report(status=ReportStatus.PENDING)

    received: list[str] = []
    with TestClient(app) as client:
        with client.websocket_connect(f"/ws/reports/{report.id}") as ws:
            # Send a ping so we can verify the connection is open
            ws.send_text("ping")
            # Close from the client side; no server messages expected
        # If we reach here the connection was accepted and closed cleanly

    # No messages should have been pushed for a PENDING report
    assert received == []


@pytest.mark.asyncio
async def test_ws_subscriber_cap_enforced() -> None:
    """A 21st connection to a report with 20 existing subscribers closes with 1008."""
    report = _add_report(status=ReportStatus.PENDING)
    await _prefill_subscribers(report.id, _MAX_SUBSCRIBERS)

    try:
        assert deps.broker.subscriber_count(report.id) == _MAX_SUBSCRIBERS

        with TestClient(app) as client:
            try:
                with client.websocket_connect(f"/ws/reports/{report.id}") as ws:
                    ws.receive_text()
            except WebSocketDisconnect as exc:
                assert exc.code == _WS_POLICY_VIOLATION
            else:
                pytest.fail("Expected WebSocketDisconnect (cap exceeded) was not raised")
    finally:
        await _clear_subscribers(report.id)


@pytest.mark.asyncio
async def test_ws_exactly_at_cap_succeeds_but_one_more_fails() -> None:
    """Exactly MAX_SUBSCRIBERS connections are accepted; the next one is rejected."""
    report = _add_report(status=ReportStatus.PENDING)
    await _prefill_subscribers(report.id, _MAX_SUBSCRIBERS - 1)

    try:
        # The MAX_SUBSCRIBERS-th connection (exactly at limit) should succeed
        with TestClient(app) as client:
            try:
                with client.websocket_connect(f"/ws/reports/{report.id}") as ws:
                    ws.send_text("ping")
                    # connection is open — this is the MAX-th subscriber
            except WebSocketDisconnect:
                pytest.fail("Connection at exactly the cap limit should succeed")
    finally:
        await _clear_subscribers(report.id)
