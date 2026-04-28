import pytest

from app.models.alerts import AlertFormat, AlertSeverity
from app.services.parsers.json_parser import parse_json
from tests.fixtures.json_samples import C2_BEACON, DATA_EXFIL, INVALID_JSON, LATERAL_MOVEMENT


def test_c2_beacon_critical():
    event = parse_json(C2_BEACON)
    assert event.severity == AlertSeverity.CRITICAL
    assert event.source_format == AlertFormat.JSON
    assert event.source_ip == "194.165.16.11"
    assert event.source_host == "db-prod-01.corp.local"


def test_data_exfil_high():
    event = parse_json(DATA_EXFIL)
    assert event.severity == AlertSeverity.HIGH
    assert event.source_ip == "10.0.0.100"


def test_lateral_movement_alternate_keys():
    event = parse_json(LATERAL_MOVEMENT)
    assert event.severity == AlertSeverity.HIGH
    assert event.source_host == "workstation-001.corp.local"
    assert event.username == "jdoe"


def test_invalid_json_raises():
    with pytest.raises(ValueError, match="Invalid JSON"):
        parse_json(INVALID_JSON)
