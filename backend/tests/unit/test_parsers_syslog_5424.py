from app.models.alerts import AlertFormat
from app.services.parsers.syslog_5424 import parse_syslog_5424
from tests.fixtures.syslog_samples import VALID_SYSLOG_5424_FIREWALL


def test_parse_firewall_block():
    event = parse_syslog_5424(VALID_SYSLOG_5424_FIREWALL)
    assert event.source_format == AlertFormat.SYSLOG_5424
    assert event.source_host == "firewall01"
    assert event.process_name == "iptables"
    assert event.message == "Blocked inbound connection"


def test_structured_data_parsed():
    event = parse_syslog_5424(VALID_SYSLOG_5424_FIREWALL)
    # src field from SD-PARAMS should be extracted
    assert event.source_ip == "194.165.16.11"
