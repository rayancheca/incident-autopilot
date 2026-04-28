from app.models.alerts import AlertFormat


def detect_format(raw: str) -> AlertFormat:
    """Heuristic format detection based on known prefixes and patterns."""
    stripped = raw.strip()

    if stripped.startswith("CEF:"):
        return AlertFormat.CEF

    # RFC 5424: starts with <priority>VERSION TIMESTAMP
    if stripped.startswith("<") and "1 " in stripped[:20]:
        try:
            _end = stripped.index(">")
            after = stripped[_end + 1 :].lstrip()
            if after.startswith("1 "):
                return AlertFormat.SYSLOG_5424
        except ValueError:
            pass

    # RFC 3164: starts with <priority> or month name
    if stripped.startswith("<"):
        return AlertFormat.SYSLOG_3164

    months = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
    if any(stripped.startswith(m) for m in months):
        return AlertFormat.SYSLOG_3164

    if stripped.startswith("{") or stripped.startswith("["):
        return AlertFormat.JSON

    return AlertFormat.JSON
