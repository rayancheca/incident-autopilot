from app.models.alerts import NormalizedEvent
from app.services.enrichment.asset_lookup import lookup_asset
from app.services.enrichment.geoip_mock import lookup_geo
from app.services.enrichment.threat_intel_mock import lookup_ip


def enrich(event: NormalizedEvent) -> NormalizedEvent:
    """Augment a NormalizedEvent with GeoIP, threat-intel, and asset data."""
    geo = lookup_geo(event.source_ip)
    threat_intel = lookup_ip(event.source_ip)
    asset = lookup_asset(event.source_host or event.dest_host)

    return event.model_copy(update={"geo": geo, "threat_intel": threat_intel, "asset": asset})
