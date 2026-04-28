import structlog
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.api.deps import get_broker, get_store
from app.services.store import InMemoryStore
from app.services.ws_broker import WSBroker

router = APIRouter()
logger = structlog.get_logger(__name__)


@router.websocket("/ws/reports/{report_id}")
async def report_ws(report_id: str, ws: WebSocket) -> None:
    store: InMemoryStore = get_store()
    ws_broker: WSBroker = get_broker()

    await ws.accept()
    await ws_broker.subscribe(report_id, ws)

    logger.info("ws_client_connected", report_id=report_id)

    # If report already complete, send the final state immediately
    report = store.get_report(report_id)
    if report and report.status.value in ("COMPLETE", "FAILED"):
        import json
        await ws.send_text(json.dumps({
            "type": "final",
            "report_id": report_id,
            "report": report.model_dump(mode="json"),
        }))

    try:
        while True:
            # Keep connection alive — client sends pings, we discard
            await ws.receive_text()
    except WebSocketDisconnect:
        logger.info("ws_client_disconnected", report_id=report_id)
    finally:
        await ws_broker.unsubscribe(report_id, ws)
