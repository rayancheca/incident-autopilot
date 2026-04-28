from app.models.alerts import AlertSeverity
from app.services.remediation_service import _severity_requires_approval


def test_low_does_not_require_approval():
    assert _severity_requires_approval(AlertSeverity.LOW) is False


def test_medium_does_not_require_approval():
    assert _severity_requires_approval(AlertSeverity.MEDIUM) is False


def test_high_requires_approval():
    assert _severity_requires_approval(AlertSeverity.HIGH) is True


def test_critical_requires_approval():
    assert _severity_requires_approval(AlertSeverity.CRITICAL) is True
