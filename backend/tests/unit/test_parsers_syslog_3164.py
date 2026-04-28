from app.models.alerts import AlertFormat, AlertSeverity
from app.services.parsers.syslog_3164 import parse_syslog_3164
from tests.fixtures.syslog_samples import VALID_SYSLOG_3164_AUTH, VALID_SYSLOG_3164_SUDO


def test_auth_failure_high_severity():
    event = parse_syslog_3164(VALID_SYSLOG_3164_AUTH)
    assert event.source_format == AlertFormat.SYSLOG_3164
    assert event.severity in (AlertSeverity.MEDIUM, AlertSeverity.HIGH, AlertSeverity.CRITICAL)
    assert event.source_host == "dc01.corp.local"
    assert event.process_name == "sshd"


def test_sudo_escalation():
    event = parse_syslog_3164(VALID_SYSLOG_3164_SUDO)
    assert event.source_host == "workstation-001.corp.local"
    assert event.process_name == "sudo"


def test_ip_extracted_from_message():
    event = parse_syslog_3164(VALID_SYSLOG_3164_AUTH)
    assert event.source_ip == "185.220.101.47"
