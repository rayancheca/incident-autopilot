from fastapi import APIRouter, Depends

from app.api.deps import get_ollama, get_store
from app.services.ollama_client import OllamaClient
from app.services.store import InMemoryStore

router = APIRouter()


@router.get("/health")
async def health_check(
    store: InMemoryStore = Depends(get_store),
    ollama: OllamaClient = Depends(get_ollama),
) -> dict:
    ollama_reachable = await ollama.health_check()
    return {
        "status": "ok",
        "ollama_reachable": ollama_reachable,
        "alert_count": store.alert_count(),
        "report_count": len(store.list_reports()),
        "queue_count": len(store.list_remediation_queue()),
    }
