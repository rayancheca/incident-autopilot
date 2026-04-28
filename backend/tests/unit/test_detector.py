from app.models.alerts import AlertFormat
from app.services.parsers.detector import detect_format
from tests.fixtures.cef_samples import VALID_CEF_BRUTE_FORCE
from tests.fixtures.json_samples import C2_BEACON
from tests.fixtures.syslog_samples import VALID_SYSLOG_3164_AUTH, VALID_SYSLOG_5424_FIREWALL


def test_detect_cef():
    assert detect_format(VALID_CEF_BRUTE_FORCE) == AlertFormat.CEF


def test_detect_syslog_3164():
    assert detect_format(VALID_SYSLOG_3164_AUTH) == AlertFormat.SYSLOG_3164


def test_detect_syslog_5424():
    assert detect_format(VALID_SYSLOG_5424_FIREWALL) == AlertFormat.SYSLOG_5424


def test_detect_json():
    assert detect_format(C2_BEACON) == AlertFormat.JSON


def test_detect_plain_json_object():
    assert detect_format('{"key": "value"}') == AlertFormat.JSON
