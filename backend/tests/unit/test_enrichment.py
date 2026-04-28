from app.services.enrichment.asset_lookup import lookup_asset
from app.services.enrichment.geoip_mock import lookup_geo
from app.services.enrichment.threat_intel_mock import lookup_ip


def test_known_bad_ip_has_high_reputation_score():
    result = lookup_ip("185.220.101.47")
    assert result is not None
    assert result.is_known_bad is True
    assert result.reputation_score >= 90
    assert "tor_exit_node" in result.categories


def test_clean_ip_returns_low_score():
    result = lookup_ip("8.8.8.8")
    assert result is not None
    assert result.reputation_score == 0
    assert result.is_known_bad is False


def test_none_ip_returns_none():
    assert lookup_ip(None) is None
    assert lookup_geo(None) is None
    assert lookup_asset(None) is None


def test_geo_russia():
    result = lookup_geo("194.165.16.11")
    assert result is not None
    assert result.country_code == "RU"


def test_geo_rfc1918():
    result = lookup_geo("192.168.1.100")
    assert result is not None
    assert result.country_code == "RFC1918"


def test_crown_jewel_asset():
    result = lookup_asset("dc01.corp.local")
    assert result is not None
    assert result.tier.value == "CROWN_JEWEL"


def test_unknown_asset():
    result = lookup_asset("random-host.example.com")
    assert result is not None
    assert result.tier.value == "UNKNOWN"
