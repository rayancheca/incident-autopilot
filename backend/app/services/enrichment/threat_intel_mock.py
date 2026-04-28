from app.models.enrichment import ThreatIntelInfo


_TI_DB: dict[str, ThreatIntelInfo] = {
    "185.220.101.47": ThreatIntelInfo(
        reputation_score=95, is_known_bad=True,
        categories=["tor_exit_node", "brute_force", "scanner"]
    ),
    "194.165.16.11": ThreatIntelInfo(
        reputation_score=88, is_known_bad=True,
        categories=["c2", "botnet", "malware_distribution"]
    ),
    "45.134.144.141": ThreatIntelInfo(
        reputation_score=72, is_known_bad=True,
        categories=["port_scanner", "vulnerability_scanner"]
    ),
    "91.108.4.1": ThreatIntelInfo(
        reputation_score=30, is_known_bad=False,
        categories=["anonymous_proxy"]
    ),
    "103.21.244.0": ThreatIntelInfo(
        reputation_score=60, is_known_bad=False,
        categories=["hosting_provider"]
    ),
}

_HASH_DB: dict[str, ThreatIntelInfo] = {
    "44d88612fea8a8f36de82e1278abb02f": ThreatIntelInfo(
        reputation_score=100, is_known_bad=True,
        categories=["malware", "ransomware"], source="VirusTotal-mock"
    ),
    "a3f3df49f69d2a8f27f5c3c5b6d8b9c2": ThreatIntelInfo(
        reputation_score=85, is_known_bad=True,
        categories=["trojan", "keylogger"], source="VirusTotal-mock"
    ),
}

_CLEAN = ThreatIntelInfo(reputation_score=0, is_known_bad=False, categories=[])


def lookup_ip(ip: str | None) -> ThreatIntelInfo | None:
    if not ip:
        return None
    return _TI_DB.get(ip, _CLEAN)


def lookup_hash(file_hash: str | None) -> ThreatIntelInfo | None:
    if not file_hash:
        return None
    return _HASH_DB.get(file_hash.lower())
