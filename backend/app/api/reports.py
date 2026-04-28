import asyncio

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from app.api.deps import get_broker, get_ollama, get_store
from app.models.reports import IRReport, ReportStatus
from app.services.ollama_client import OllamaClient
from app.services.remediation_service import generate_remediation
from app.services.report_service import generate_ir_report
from app.services.store import InMemoryStore
from app.services.ws_broker import WSBroker
from app.utils.ids import new_id
from pydantic import BaseModel

router = APIRouter()


class GenerateReportRequest(BaseModel):
    alert_ids: list[str]


@router.post("/reports/generate", response_model=IRReport, status_code=202)
async def generate_report(
    req: GenerateReportRequest,
    background_tasks: BackgroundTasks,
    store: InMemoryStore = Depends(get_store),
    ollama: OllamaClient = Depends(get_ollama),
    ws_broker: WSBroker = Depends(get_broker),
) -> IRReport:
    if not req.alert_ids:
        raise HTTPException(status_code=422, detail="alert_ids must not be empty")

    report_id = new_id()
    stub = IRReport(id=report_id, alert_ids=req.alert_ids, status=ReportStatus.PENDING)
    store.upsert_report(stub)

    async def _run() -> None:
        report = await generate_ir_report(report_id, req.alert_ids, store, ollama, ws_broker)
        if report.status == ReportStatus.COMPLETE:
            await generate_remediation(report, store, ollama)

    background_tasks.add_task(_run)
    return stub


@router.get("/reports/{report_id}", response_model=IRReport)
def get_report(
    report_id: str,
    store: InMemoryStore = Depends(get_store),
) -> IRReport:
    report = store.get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.get("/reports", response_model=list[IRReport])
def list_reports(store: InMemoryStore = Depends(get_store)) -> list[IRReport]:
    return store.list_reports()
