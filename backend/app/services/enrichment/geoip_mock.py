from app.models.enrichment import GeoInfo


_GEO_DB: dict[str, GeoInfo] = {
    "192.168.1.1": GeoInfo(country_code="US", country_name="United States", city="Internal", asn="RFC1918"),
    "10.0.0.1": GeoInfo(country_code="US", country_name="United States", city="Internal", asn="RFC1918"),
    "185.220.101.47": GeoInfo(country_code="NL", country_name="Netherlands", city="Amsterdam", asn="AS60729", is_known_vpn=True),
    "194.165.16.11": GeoInfo(country_code="RU", country_name="Russia", city="Moscow", asn="AS31261"),
    "45.134.144.141": GeoInfo(country_code="RO", country_name="Romania", city="Bucharest", asn="AS206685"),
    "91.108.4.1": GeoInfo(country_code="DE", country_name="Germany", city="Frankfurt", asn="AS62014"),
    "103.21.244.0": GeoInfo(country_code="CN", country_name="China", city="Beijing", asn="AS13335"),
    "8.8.8.8": GeoInfo(country_code="US", country_name="United States", city="Mountain View", asn="AS15169"),
    "1.1.1.1": GeoInfo(country_code="AU", country_name="Australia", city="Sydney", asn="AS13335"),
}

_DEFAULT_GEO = GeoInfo(country_code="XX", country_name="Unknown", city=None, asn=None)


def lookup_geo(ip: str | None) -> GeoInfo | None:
    if not ip:
        return None
    # Exact match first, then prefix match
    if ip in _GEO_DB:
        return _GEO_DB[ip]
    # RFC1918 ranges
    if ip.startswith(("10.", "192.168.", "172.16.", "172.17.", "172.18.", "172.19.", "172.2", "172.3")):
        return GeoInfo(country_code="RFC1918", country_name="Private Network", city="Internal", asn="RFC1918")
    return _DEFAULT_GEO
