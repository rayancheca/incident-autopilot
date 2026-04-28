import re
from datetime import datetime, timezone

from app.models.alerts import AlertFormat, AlertSeverity, NormalizedEvent
from app.utils.ids import new_id


_SEVERITY_MAP: dict[int, AlertSeverity] = {
    0: AlertSeverity.LOW,
    1: AlertSeverity.LOW,
    2: AlertSeverity.LOW,
    3: AlertSeverity.LOW,
    4: AlertSeverity.MEDIUM,
    5: AlertSeverity.MEDIUM,
    6: AlertSeverity.MEDIUM,
    7: AlertSeverity.HIGH,
    8: AlertSeverity.HIGH,
    9: AlertSeverity.HIGH,
    10: AlertSeverity.CRITICAL,
}


def _parse_extensions(ext_string: str) -> dict[str, str]:
    result: dict[str, str] = {}
    pattern = re.compile(r"(\w+)=(.*?)(?=\s+\w+=|$)", re.DOTALL)
    for match in pattern.finditer(ext_string):
        result[match.group(1)] = match.group(2).strip()
    return result


def parse_cef(raw: str) -> NormalizedEvent:
    """Parse an ArcSight CEF v0/v1 string into a NormalizedEvent."""
    # CEF:Version|Device Vendor|Device Product|Device Version|Signature ID|Name|Severity|Extensions
    parts = raw.split("|", 7)
    if len(parts) < 7:
        raise ValueError(f"Malformed CEF — expected 7+ pipe-separated fields, got {len(parts)}")

    try:
        raw_severity = int(parts[6].strip())
        severity = _SEVERITY_MAP.get(raw_severity, AlertSeverity.MEDIUM)
    except ValueError:
        severity = AlertSeverity.MEDIUM

    event_name = parts[5].strip()
    extensions: dict[str, str] = {}
    if len(parts) == 8:
        extensions = _parse_extensions(parts[7])

    raw_ts = extensions.get("rt") or extensions.get("start") or extensions.get("end")
    if raw_ts:
        try:
            timestamp = datetime.fromtimestamp(int(raw_ts) / 1000, tz=timezone.utc)
        except (ValueError, OSError):
            timestamp = datetime.now(tz=timezone.utc)
    else:
        timestamp = datetime.now(tz=timezone.utc)

    src_port_str = extensions.get("spt")
    dest_port_str = extensions.get("dpt")

    return NormalizedEvent(
        id=new_id(),
        timestamp=timestamp,
        source_format=AlertFormat.CEF,
        severity=severity,
        event_type=event_name,
        source_ip=extensions.get("src") or extensions.get("sourceAddress"),
        dest_ip=extensions.get("dst") or extensions.get("destinationAddress"),
        source_host=extensions.get("shost") or extensions.get("sourceHostName"),
        dest_host=extensions.get("dhost") or extensions.get("destinationHostName"),
        src_port=int(src_port_str) if src_port_str and src_port_str.isdigit() else None,
        dest_port=int(dest_port_str) if dest_port_str and dest_port_str.isdigit() else None,
        username=extensions.get("suser") or extensions.get("duser"),
        process_name=extensions.get("sproc") or extensions.get("dproc"),
        message=event_name,
        raw_fields={
            "vendor": parts[1].strip(),
            "product": parts[2].strip(),
            "version": parts[3].strip(),
            "signature_id": parts[4].strip(),
            **extensions,
        },
    )
