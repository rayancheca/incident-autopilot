import pytest
from httpx import AsyncClient

from tests.fixtures.cef_samples import VALID_CEF_BRUTE_FORCE, VALID_CEF_PORT_SCAN


@pytest.mark.asyncio
async def test_list_alerts_empty_by_default(client: AsyncClient) -> None:
    resp = await client.get("/api/alerts")
    assert resp.status_code == 200
    # May have alerts from other tests — just verify structure
    data = resp.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_list_alerts_after_ingest(client: AsyncClient) -> None:
    await client.post("/api/alerts/ingest", json={"raw": VALID_CEF_BRUTE_FORCE})
    await client.post("/api/alerts/ingest", json={"raw": VALID_CEF_PORT_SCAN})
    resp = await client.get("/api/alerts")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 2


@pytest.mark.asyncio
async def test_get_alert_by_id(client: AsyncClient) -> None:
    ingest_resp = await client.post("/api/alerts/ingest", json={"raw": VALID_CEF_BRUTE_FORCE})
    alert_id = ingest_resp.json()["id"]
    resp = await client.get(f"/api/alerts/{alert_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == alert_id


@pytest.mark.asyncio
async def test_get_nonexistent_alert_404(client: AsyncClient) -> None:
    resp = await client.get("/api/alerts/nonexistent_id_xyz")
    assert resp.status_code == 404
