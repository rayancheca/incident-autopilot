import pytest

from app.models.alerts import AlertFormat, AlertSeverity
from app.services.parsers.cef import parse_cef
from tests.fixtures.cef_samples import (
    INVALID_CEF_TOO_FEW_PIPES,
    VALID_CEF_BRUTE_FORCE,
    VALID_CEF_MALWARE,
    VALID_CEF_PORT_SCAN,
)


def test_parse_brute_force_severity():
    event = parse_cef(VALID_CEF_BRUTE_FORCE)
    assert event.severity == AlertSeverity.HIGH
    assert event.source_format == AlertFormat.CEF
    assert event.source_ip == "185.220.101.47"
    assert event.dest_ip == "10.0.0.5"


def test_parse_port_scan_high_severity():
    event = parse_cef(VALID_CEF_PORT_SCAN)
    assert event.severity == AlertSeverity.HIGH
    assert event.dest_ip == "10.0.0.1"


def test_parse_malware_critical_severity():
    event = parse_cef(VALID_CEF_MALWARE)
    assert event.severity == AlertSeverity.CRITICAL
    assert event.source_host == "workstation-001.corp.local"
    assert event.process_name == "explorer.exe"


def test_parse_invalid_cef_raises():
    with pytest.raises(ValueError, match="Malformed CEF"):
        parse_cef(INVALID_CEF_TOO_FEW_PIPES)


def test_event_has_id():
    event = parse_cef(VALID_CEF_BRUTE_FORCE)
    assert event.id
    assert len(event.id) > 8
