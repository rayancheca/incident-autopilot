from app.models.alerts import AlertFormat, NormalizedEvent, RawAlertIn
from app.services.parsers.cef import parse_cef
from app.services.parsers.detector import detect_format
from app.services.parsers.json_parser import parse_json
from app.services.parsers.syslog_3164 import parse_syslog_3164
from app.services.parsers.syslog_5424 import parse_syslog_5424


def parse(alert_in: RawAlertIn) -> NormalizedEvent:
    """Detect format and parse a raw alert string into a NormalizedEvent."""
    fmt = alert_in.format_hint or detect_format(alert_in.raw)

    match fmt:
        case AlertFormat.CEF:
            return parse_cef(alert_in.raw)
        case AlertFormat.SYSLOG_3164:
            return parse_syslog_3164(alert_in.raw)
        case AlertFormat.SYSLOG_5424:
            return parse_syslog_5424(alert_in.raw)
        case AlertFormat.JSON | _:
            return parse_json(alert_in.raw)
