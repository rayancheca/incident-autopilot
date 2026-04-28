import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.services.store import InMemoryStore


@pytest.fixture
def store() -> InMemoryStore:
    return InMemoryStore(alert_cap=100)


@pytest.fixture
async def client() -> AsyncClient:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
