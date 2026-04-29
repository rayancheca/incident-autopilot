from fastapi import Header, HTTPException, status

from app.core.config import settings
from app.services.ollama_client import OllamaClient, get_ollama_client
from app.services.store import InMemoryStore
from app.services.ws_broker import WSBroker, broker

_store = InMemoryStore()


def get_store() -> InMemoryStore:
    return _store


def get_ollama() -> OllamaClient:
    return get_ollama_client()


def get_broker() -> WSBroker:
    return broker


def require_api_key(x_api_key: str = Header(default="")) -> str:
    """Verify X-API-Key header when auth is enabled (settings.api_key is non-empty)."""
    if settings.api_key and x_api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
    return x_api_key
