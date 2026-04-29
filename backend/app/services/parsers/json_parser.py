import json
from datetime import datetime, timezone

from dateutil import parser as dateutil_parser

from app.models.alerts import AlertFormat, AlertSeverity, NormalizedEvent
from app.utils.ids import new_id


_SEVERITY_STR_MAP: dict[str, AlertSeverity] = {
    "low": AlertSeverity.LOW,
    "medium": AlertSeverity.MEDIUM,
    "med": AlertSeverity.MEDIUM,
    "high": AlertSeverity.HIGH,
    "critical": AlertSeverity.CRITICAL,
    "crit": AlertSeverity.CRITICAL,
    "info": AlertSeverity.LOW,
    "informational": AlertSeverity.LOW,
    "warning": AlertSeverity.MEDIUM,
    "warn": AlertSeverity.MEDIUM,
    "error": AlertSeverity.HIGH,
}


def _resolve_severity(data: dict) -> AlertSeverity:
    for key in ("severity", "level", "priority", "sev"):
        val = data.get(key)
        if isinstance(val, str):
            mapped = _SEVERITY_STR_MAP.get(val.lower())
            if mapped:
                return mapped
        elif isinstance(val, int):
            if val >= 9:
                return AlertSeverity.CRITICAL
            if val >= 7:
                return AlertSeverity.HIGH
            if val >= 4:
                return AlertSeverity.MEDIUM
            return AlertSeverity.LOW
    return AlertSeverity.MEDIUM


def _resolve_timestamp(data: dict) -> datetime:
    for key in ("timestamp", "time", "ts", "@timestamp", "event_time"):
        val = data.get(key)
        if not val:
            continue
        if isinstance(val, (int, float)):
            try:
                return datetime.fromtimestamp(val / 1000 if val > 1e10 else val, tz=timezone.utc)
            except (OSError, OverflowError):
                continue
        if isinstance(val, str):
            try:
                ts = dateutil_parser.parse(val)
                return ts.replace(tzinfo=timezone.utc) if ts.tzinfo is None else ts
            except (ValueError, OverflowError):
                continue
    return datetime.now(tz=timezone.utc)


def _parse_port(raw: object) -> int | None:
    if raw is None:
        return None
    try:
        port = int(str(raw).split("/")[0])
        return port if 0 <= port <= 65535 else None
    except (ValueError, TypeError):
        return None


def parse_json(raw: str) -> NormalizedEvent:
    try:
        data: dict = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON alert: {exc}") from exc

    if not isinstance(data, dict):
        raise ValueError("JSON alert must be a top-level object")

    message = str(
        data.get("message")
        or data.get("msg")
        or data.get("description")
        or data.get("alert_name")
        or "JSON alert"
    )

    src_port_raw = data.get("src_port") or data.get("source_port")
    dst_port_raw = data.get("dst_port") or data.get("dest_port") or data.get("destination_port")

    return NormalizedEvent(
        id=new_id(),
        timestamp=_resolve_timestamp(data),
        source_format=AlertFormat.JSON,
        severity=_resolve_severity(data),
        event_type=str(data.get("event_type") or data.get("type") or data.get("category") or "alert"),
        source_ip=data.get("src_ip") or data.get("source_ip") or data.get("src"),
        dest_ip=data.get("dst_ip") or data.get("dest_ip") or data.get("dst"),
        source_host=data.get("src_host") or data.get("source_host") or data.get("hostname"),
        dest_host=data.get("dst_host") or data.get("dest_host"),
        src_port=_parse_port(src_port_raw),
        dest_port=_parse_port(dst_port_raw),
        username=data.get("username") or data.get("user") or data.get("actor"),
        process_name=data.get("process") or data.get("process_name") or data.get("proc"),
        message=message,
        raw_fields=data,
    )
