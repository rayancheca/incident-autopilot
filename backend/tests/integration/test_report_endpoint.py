"""Integration tests for POST /api/reports/generate and GET /api/reports/{id}."""
import asyncio
import json
from collections.abc import AsyncIterator
from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from app.api.deps import get_ollama
from app.main import app
from app.models.alerts import AlertSeverity
from app.models.reports import IRReport, ReportStatus
from tests.fixtures.cef_samples import VALID_CEF_BRUTE_FORCE


# ---------------------------------------------------------------------------
# Mock IR JSON that stream_completion / complete will return
# ---------------------------------------------------------------------------

_VALID_IR_JSON = json.dumps(
    {
        "title": "SSH Brute Force Attack",
        "executive_summary": "Attacker 185.220.101.47 performed repeated SSH login attempts.",
        "severity": "HIGH",
        "confidence": 85,
        "mitre_tactics": [
            {
                "tactic_id": "TA0006",
                "tactic_name": "Credential Access",
                "techniques": ["T1110"],
            }
        ],
        "affected_assets": [
            {"hostname": "web-prod-01.corp.local", "ip": "10.0.0.5", "role": "web server"}
        ],
        "timeline": [
            {"timestamp": "2024-04-28T10:00:00Z", "event": "First failed authentication attempt"}
        ],
        "recommendations": ["Block source IP in firewall", "Enable fail2ban on SSH port"],
    }
)


class _MockOllamaClient:
    """Minimal OllamaClient stand-in that returns valid IR JSON without real network I/O."""

    async def complete(self, *_args: Any, **_kwargs: Any) -> str:
        return _VALID_IR_JSON

    async def stream_completion(  # type: ignore[override]
        self, *_args: Any, **_kwargs: Any
    ) -> AsyncIterator[str]:
        yield _VALID_IR_JSON

    async def health_check(self) -> bool:
        return True

    async def aclose(self) -> None:
        pass


def _make_mock_ollama() -> _MockOllamaClient:
    """Return a lightweight OllamaClient mock that streams valid IR JSON."""
    return _MockOllamaClient()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_generate_report_returns_202_with_report_id(client: AsyncClient) -> None:
    """POST /api/reports/generate returns 202 immediately with a report_id stub."""
    ingest = await client.post("/api/alerts/ingest", json={"raw": VALID_CEF_BRUTE_FORCE})
    alert_id = ingest.json()["id"]

    mock_client = _make_mock_ollama()
    app.dependency_overrides[get_ollama] = lambda: mock_client
    try:
        resp = await client.post("/api/reports/generate", json={"alert_ids": [alert_id]})
    finally:
        app.dependency_overrides.pop(get_ollama, None)

    assert resp.status_code == 202
    data = resp.json()
    assert "id" in data
    assert data["status"] == ReportStatus.PENDING


@pytest.mark.asyncio
async def test_generate_report_empty_alert_ids_returns_422(client: AsyncClient) -> None:
    """POST with an empty alert_ids list must return 422 (validated before background task)."""
    resp = await client.post("/api/reports/generate", json={"alert_ids": []})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_generate_report_nonexistent_alerts_stored_as_failed(client: AsyncClient) -> None:
    """When none of the alert_ids exist, the background task sets the report status to FAILED."""
    fake_id = "nonexistent_alert_xyz"

    # No ollama mock needed — the service short-circuits before calling LLM
    resp = await client.post("/api/reports/generate", json={"alert_ids": [fake_id]})
    assert resp.status_code == 202
    report_id = resp.json()["id"]

    # Allow time for the background task to complete
    await asyncio.sleep(0.1)

    get_resp = await client.get(f"/api/reports/{report_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["status"] == ReportStatus.FAILED


@pytest.mark.asyncio
async def test_generate_report_complete_after_background_task(client: AsyncClient) -> None:
    """After the background task finishes the stored report has status COMPLETE."""
    ingest = await client.post("/api/alerts/ingest", json={"raw": VALID_CEF_BRUTE_FORCE})
    alert_id = ingest.json()["id"]

    mock_client = _make_mock_ollama()
    app.dependency_overrides[get_ollama] = lambda: mock_client
    try:
        resp = await client.post("/api/reports/generate", json={"alert_ids": [alert_id]})
        report_id = resp.json()["id"]
        # Wait long enough for the background task to run while the override is still active
        await asyncio.sleep(0.5)
    finally:
        app.dependency_overrides.pop(get_ollama, None)

    get_resp = await client.get(f"/api/reports/{report_id}")
    assert get_resp.status_code == 200
    body = get_resp.json()
    assert body["status"] == ReportStatus.COMPLETE
    assert body["title"] == "SSH Brute Force Attack"
    assert body["confidence"] == 85


@pytest.mark.asyncio
async def test_get_report_by_id_returns_404_for_unknown(client: AsyncClient) -> None:
    """GET /api/reports/{id} returns 404 when the report does not exist."""
    resp = await client.get("/api/reports/does_not_exist_xyz")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_list_reports_includes_created_stub(client: AsyncClient) -> None:
    """GET /api/reports returns a list that includes the report stub from POST."""
    ingest = await client.post("/api/alerts/ingest", json={"raw": VALID_CEF_BRUTE_FORCE})
    alert_id = ingest.json()["id"]

    mock_client = _make_mock_ollama()
    app.dependency_overrides[get_ollama] = lambda: mock_client
    try:
        create_resp = await client.post("/api/reports/generate", json={"alert_ids": [alert_id]})
    finally:
        app.dependency_overrides.pop(get_ollama, None)

    report_id = create_resp.json()["id"]

    list_resp = await client.get("/api/reports")
    assert list_resp.status_code == 200
    ids = [r["id"] for r in list_resp.json()]
    assert report_id in ids
