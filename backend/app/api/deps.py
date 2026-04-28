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
