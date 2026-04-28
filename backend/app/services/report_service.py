import json
from datetime import datetime, timezone

import structlog

from app.models.alerts import AlertSeverity, NormalizedEvent
from app.models.reports import AffectedAsset, IRReport, MitreTactic, ReportStatus, TimelineEntry
from app.services.ollama_client import OllamaClient
from app.services.prompts import SYSTEM_PROMPT, build_ir_prompt
from app.services.store import InMemoryStore
from app.services.ws_broker import WSBroker
from app.utils.json_repair import parse_json_with_repair

logger = structlog.get_logger(__name__)


def _parse_ir_json(raw_json: str, report_id: str) -> IRReport | None:
    data = parse_json_with_repair(raw_json)
    if not data:
        logger.error("ir_json_parse_failed", report_id=report_id, snippet=raw_json[:200])
        return None

    try:
        tactics = [
            MitreTactic(
                tactic_id=t.get("tactic_id", ""),
                tactic_name=t.get("tactic_name", ""),
                techniques=t.get("techniques", []),
            )
            for t in data.get("mitre_tactics", [])
        ]
        assets = [
            AffectedAsset(
                hostname=a.get("hostname"),
                ip=a.get("ip"),
                role=a.get("role"),
            )
            for a in data.get("affected_assets", [])
        ]
        timeline = []
        for entry in data.get("timeline", []):
            try:
                ts = datetime.fromisoformat(entry.get("timestamp", "").replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                ts = datetime.now(tz=timezone.utc)
            timeline.append(TimelineEntry(timestamp=ts, event=entry.get("event", "")))

        severity_str = data.get("severity", "MEDIUM")
        try:
            severity = AlertSeverity(severity_str)
        except ValueError:
            severity = AlertSeverity.MEDIUM

        return IRReport(
            id=report_id,
            alert_ids=[],
            status=ReportStatus.COMPLETE,
            title=data.get("title", "Unnamed Incident"),
            executive_summary=data.get("executive_summary", ""),
            mitre_tactics=tactics,
            affected_assets=assets,
            confidence=int(data.get("confidence", 50)),
            severity=severity,
            timeline=timeline,
            recommendations=data.get("recommendations", []),
            completed_at=datetime.now(tz=timezone.utc),
        )
    except Exception as exc:
        logger.error("ir_report_build_failed", error=str(exc))
        return None


async def generate_ir_report(
    report_id: str,
    alert_ids: list[str],
    store: InMemoryStore,
    ollama: OllamaClient,
    ws_broker: WSBroker,
) -> IRReport:
    """Orchestrate: build prompt → stream tokens → parse JSON → persist report."""
    events: list[NormalizedEvent] = []
    for aid in alert_ids:
        event = store.get_alert(aid)
        if event:
            events.append(event)

    if not events:
        report = IRReport(
            id=report_id,
            alert_ids=alert_ids,
            status=ReportStatus.FAILED,
            title="No valid alerts found",
        )
        store.upsert_report(report)
        return report

    report = IRReport(id=report_id, alert_ids=alert_ids, status=ReportStatus.STREAMING)
    store.upsert_report(report)

    await ws_broker.publish(
        report_id,
        json.dumps({"type": "status", "report_id": report_id, "status": "streaming"}),
    )

    prompt = build_ir_prompt(events)
    accumulated = ""

    try:
        async for token in ollama.stream_completion(prompt, system=SYSTEM_PROMPT, temperature=0.2):
            accumulated += token
            await ws_broker.publish(
                report_id,
                json.dumps({"type": "token", "report_id": report_id, "token": token}),
            )
    except Exception as exc:
        logger.error("ollama_stream_error", report_id=report_id, error=str(exc))
        report = report.model_copy(update={"status": ReportStatus.FAILED, "raw_stream": accumulated})
        store.upsert_report(report)
        await ws_broker.publish(
            report_id,
            json.dumps({"type": "error", "report_id": report_id, "message": str(exc)}),
        )
        return report

    parsed = _parse_ir_json(accumulated, report_id)

    if not parsed:
        # Retry once with explicit repair instruction
        repair_prompt = f"{prompt}\n\nYour previous response was not valid JSON. Respond ONLY with the JSON object, nothing else."
        accumulated2 = await ollama.complete(repair_prompt, system=SYSTEM_PROMPT)
        parsed = _parse_ir_json(accumulated2, report_id)
        if parsed:
            accumulated = accumulated2

    if not parsed:
        report = report.model_copy(
            update={"status": ReportStatus.FAILED, "raw_stream": accumulated}
        )
        store.upsert_report(report)
        await ws_broker.publish(
            report_id,
            json.dumps({"type": "error", "report_id": report_id, "message": "JSON parse failed after retry"}),
        )
        return report

    final_report = parsed.model_copy(
        update={"id": report_id, "alert_ids": alert_ids, "raw_stream": accumulated}
    )
    store.upsert_report(final_report)

    await ws_broker.publish(
        report_id,
        json.dumps({
            "type": "final",
            "report_id": report_id,
            "report": final_report.model_dump(mode="json"),
        }),
    )

    logger.info("ir_report_complete", report_id=report_id, severity=final_report.severity)
    return final_report
