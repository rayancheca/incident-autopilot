from app.models.enrichment import AssetInfo, AssetTier


_ASSET_DB: dict[str, AssetInfo] = {
    "dc01.corp.local": AssetInfo(hostname="dc01.corp.local", tier=AssetTier.CROWN_JEWEL, owner_team="infra", os="Windows Server 2022"),
    "dc02.corp.local": AssetInfo(hostname="dc02.corp.local", tier=AssetTier.CROWN_JEWEL, owner_team="infra", os="Windows Server 2022"),
    "vault.corp.local": AssetInfo(hostname="vault.corp.local", tier=AssetTier.CROWN_JEWEL, owner_team="security", os="Linux"),
    "db-prod-01.corp.local": AssetInfo(hostname="db-prod-01.corp.local", tier=AssetTier.CROWN_JEWEL, owner_team="dba", os="Linux"),
    "web-prod-01.corp.local": AssetInfo(hostname="web-prod-01.corp.local", tier=AssetTier.STANDARD, owner_team="engineering", os="Linux"),
    "web-prod-02.corp.local": AssetInfo(hostname="web-prod-02.corp.local", tier=AssetTier.STANDARD, owner_team="engineering", os="Linux"),
    "workstation-001.corp.local": AssetInfo(hostname="workstation-001.corp.local", tier=AssetTier.STANDARD, owner_team="hr", os="Windows 11"),
    "dev-box-07.corp.local": AssetInfo(hostname="dev-box-07.corp.local", tier=AssetTier.LOW, owner_team="engineering", os="Linux"),
}

_UNKNOWN = AssetInfo(hostname="unknown", tier=AssetTier.UNKNOWN)


def lookup_asset(hostname: str | None) -> AssetInfo | None:
    if not hostname:
        return None
    asset = _ASSET_DB.get(hostname)
    if asset:
        return asset
    # Fuzzy: check if hostname contains a known key
    hostname_lower = hostname.lower()
    for key, info in _ASSET_DB.items():
        if key in hostname_lower or hostname_lower in key:
            return info
    return _UNKNOWN
