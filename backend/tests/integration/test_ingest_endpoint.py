import pytest
from httpx import AsyncClient

from tests.fixtures.cef_samples import VALID_CEF_BRUTE_FORCE
from tests.fixtures.json_samples import C2_BEACON
from tests.fixtures.syslog_samples import VALID_SYSLOG_3164_AUTH


@pytest.mark.asyncio
async def test_ingest_cef_returns_201(client: AsyncClient) -> None:
    resp = await client.post("/api/alerts/ingest", json={"raw": VALID_CEF_BRUTE_FORCE})
    assert resp.status_code == 201
    data = resp.json()
    assert data["source_format"] == "cef"
    assert data["severity"] == "HIGH"
    assert data["source_ip"] == "185.220.101.47"


@pytest.mark.asyncio
async def test_ingest_json_returns_201(client: AsyncClient) -> None:
    resp = await client.post("/api/alerts/ingest", json={"raw": C2_BEACON})
    assert resp.status_code == 201
    data = resp.json()
    assert data["source_format"] == "json"
    assert data["severity"] == "CRITICAL"


@pytest.mark.asyncio
async def test_ingest_syslog_returns_201(client: AsyncClient) -> None:
    resp = await client.post("/api/alerts/ingest", json={"raw": VALID_SYSLOG_3164_AUTH})
    assert resp.status_code == 201
    data = resp.json()
    assert data["source_format"] == "syslog_3164"


@pytest.mark.asyncio
async def test_ingest_with_format_hint(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/alerts/ingest",
        json={"raw": VALID_CEF_BRUTE_FORCE, "format_hint": "cef"},
    )
    assert resp.status_code == 201


@pytest.mark.asyncio
async def test_ingest_enriches_with_geo(client: AsyncClient) -> None:
    resp = await client.post("/api/alerts/ingest", json={"raw": VALID_CEF_BRUTE_FORCE})
    data = resp.json()
    # 185.220.101.47 is in the mock GeoIP DB
    assert data["geo"] is not None
    assert data["geo"]["country_code"] == "NL"


@pytest.mark.asyncio
async def test_ingest_invalid_json_returns_422(client: AsyncClient) -> None:
    resp = await client.post("/api/alerts/ingest", json={"raw": '{"bad": true'})
    assert resp.status_code == 422
