import re
from datetime import datetime, timezone

from dateutil import parser as dateutil_parser

from app.models.alerts import AlertFormat, AlertSeverity, NormalizedEvent
from app.utils.ids import new_id


_PRIORITY_TO_SEVERITY: dict[int, AlertSeverity] = {
    0: AlertSeverity.CRITICAL,
    1: AlertSeverity.CRITICAL,
    2: AlertSeverity.CRITICAL,
    3: AlertSeverity.HIGH,
    4: AlertSeverity.HIGH,
    5: AlertSeverity.MEDIUM,
    6: AlertSeverity.LOW,
    7: AlertSeverity.LOW,
}

# RFC 5424: <PRI>VERSION TIMESTAMP HOSTNAME APP-NAME PROCID MSGID [SD-DATA] MESSAGE
_RFC5424_RE = re.compile(
    r"^<(?P<pri>\d{1,3})>(?P<version>\d+)\s+"
    r"(?P<timestamp>\S+)\s+"
    r"(?P<hostname>\S+)\s+"
    r"(?P<appname>\S+)\s+"
    r"(?P<procid>\S+)\s+"
    r"(?P<msgid>\S+)\s+"
    r"(?P<structured_data>-|\[.*?\](?:\[.*?\])*)\s*"
    r"(?P<message>.*)?$",
    re.DOTALL,
)

_IP_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
_KV_RE = re.compile(r'(\w+)="([^"]*)"')


def _parse_sd(sd_str: str) -> dict[str, str]:
    if sd_str == "-":
        return {}
    return dict(_KV_RE.findall(sd_str))


def parse_syslog_5424(raw: str) -> NormalizedEvent:
    raw = raw.strip()
    m = _RFC5424_RE.match(raw)
    if not m:
        raise ValueError(f"Cannot parse RFC 5424 syslog: {raw[:80]!r}")

    pri = int(m.group("pri"))
    severity_level = pri % 8
    severity = _PRIORITY_TO_SEVERITY.get(severity_level, AlertSeverity.MEDIUM)

    ts_str = m.group("timestamp")
    try:
        ts = dateutil_parser.parse(ts_str)
        timestamp = ts.replace(tzinfo=timezone.utc) if ts.tzinfo is None else ts
    except (ValueError, OverflowError):
        timestamp = datetime.now(tz=timezone.utc)

    message = m.group("message") or ""
    sd_fields = _parse_sd(m.group("structured_data"))
    ips = _IP_RE.findall(message)

    return NormalizedEvent(
        id=new_id(),
        timestamp=timestamp,
        source_format=AlertFormat.SYSLOG_5424,
        severity=severity,
        event_type="syslog",
        source_host=m.group("hostname") if m.group("hostname") != "-" else None,
        source_ip=sd_fields.get("src") or (ips[0] if ips else None),
        dest_ip=sd_fields.get("dst") or (ips[1] if len(ips) > 1 else None),
        process_name=m.group("appname") if m.group("appname") != "-" else None,
        message=message or sd_fields.get("msg", ""),
        raw_fields={
            "pri": m.group("pri"),
            "version": m.group("version"),
            "procid": m.group("procid"),
            "msgid": m.group("msgid"),
            **sd_fields,
        },
    )
