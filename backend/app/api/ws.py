import json

import structlog
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.api.deps import get_broker, get_store
from app.models.reports import ReportStatus
from app.services.store import InMemoryStore
from app.services.ws_broker import WSBroker

router = APIRouter()
logger = structlog.get_logger(__name__)

_WS_CLOSE_POLICY_VIOLATION = 1008


@router.websocket("/ws/reports/{report_id}")
async def report_ws(report_id: str, ws: WebSocket) -> None:
    store: InMemoryStore = get_store()
    ws_broker: WSBroker = get_broker()

    report = store.get_report(report_id)
    if not report:
        await ws.close(code=_WS_CLOSE_POLICY_VIOLATION)
        return

    accepted = await ws_broker.subscribe(report_id, ws)
    if not accepted:
        await ws.close(code=_WS_CLOSE_POLICY_VIOLATION)
        return

    await ws.accept()
    logger.info("ws_client_connected", report_id=report_id)

    # If report already complete, send the final state immediately
    if report.status in (ReportStatus.COMPLETE, ReportStatus.FAILED):
        await ws.send_text(json.dumps({
            "type": "final",
            "report_id": report_id,
            "report": report.model_dump(mode="json"),
        }))

    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        logger.info("ws_client_disconnected", report_id=report_id)
    finally:
        await ws_broker.unsubscribe(report_id, ws)
