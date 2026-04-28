import re
from datetime import datetime, timezone

from dateutil import parser as dateutil_parser

from app.models.alerts import AlertFormat, AlertSeverity, NormalizedEvent
from app.utils.ids import new_id


_FACILITY_MAP: dict[int, str] = {
    0: "kern", 1: "user", 2: "mail", 3: "daemon", 4: "auth",
    5: "syslog", 6: "lpr", 7: "news", 8: "uucp", 9: "cron",
    10: "security", 11: "ftp", 16: "local0", 17: "local1",
    18: "local2", 19: "local3", 20: "local4", 21: "local5",
    22: "local6", 23: "local7",
}

_PRIORITY_TO_SEVERITY: dict[int, AlertSeverity] = {
    0: AlertSeverity.CRITICAL,  # Emergency
    1: AlertSeverity.CRITICAL,  # Alert
    2: AlertSeverity.CRITICAL,  # Critical
    3: AlertSeverity.HIGH,      # Error
    4: AlertSeverity.HIGH,      # Warning
    5: AlertSeverity.MEDIUM,    # Notice
    6: AlertSeverity.LOW,       # Informational
    7: AlertSeverity.LOW,       # Debug
}

# Matches <PRI>Mmm DD HH:MM:SS hostname process[pid]: message
_RFC3164_RE = re.compile(
    r"^(?:<(?P<pri>\d{1,3})>)?"
    r"(?P<timestamp>[A-Z][a-z]{2}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+"
    r"(?P<hostname>\S+)\s+"
    r"(?:(?P<process>\S+?)(?:\[(?P<pid>\d+)\])?:\s*)?"
    r"(?P<message>.*)"
)

_IP_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")


def parse_syslog_3164(raw: str) -> NormalizedEvent:
    raw = raw.strip()
    m = _RFC3164_RE.match(raw)
    if not m:
        raise ValueError(f"Cannot parse RFC 3164 syslog: {raw[:80]!r}")

    pri_str = m.group("pri")
    if pri_str is not None:
        pri = int(pri_str)
        severity_level = pri % 8
        severity = _PRIORITY_TO_SEVERITY.get(severity_level, AlertSeverity.MEDIUM)
    else:
        severity = AlertSeverity.MEDIUM

    ts_str = m.group("timestamp")
    try:
        ts = dateutil_parser.parse(ts_str, default=datetime(datetime.now().year, 1, 1))
        timestamp = ts.replace(tzinfo=timezone.utc) if ts.tzinfo is None else ts
    except (ValueError, OverflowError):
        timestamp = datetime.now(tz=timezone.utc)

    message = m.group("message") or ""
    ips = _IP_RE.findall(message)

    return NormalizedEvent(
        id=new_id(),
        timestamp=timestamp,
        source_format=AlertFormat.SYSLOG_3164,
        severity=severity,
        event_type="syslog",
        source_host=m.group("hostname"),
        source_ip=ips[0] if ips else None,
        dest_ip=ips[1] if len(ips) > 1 else None,
        process_name=m.group("process"),
        message=message,
        raw_fields={
            "pri": pri_str,
            "pid": m.group("pid"),
            "hostname": m.group("hostname"),
        },
    )
