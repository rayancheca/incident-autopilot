from enum import StrEnum

from pydantic import BaseModel


class AssetTier(StrEnum):
    CROWN_JEWEL = "CROWN_JEWEL"
    STANDARD = "STANDARD"
    LOW = "LOW"
    UNKNOWN = "UNKNOWN"


class GeoInfo(BaseModel):
    country_code: str
    country_name: str
    city: str | None = None
    asn: str | None = None
    is_known_vpn: bool = False


class ThreatIntelInfo(BaseModel):
    reputation_score: int  # 0 (clean) – 100 (malicious)
    is_known_bad: bool
    categories: list[str] = []
    source: str = "mock"


class AssetInfo(BaseModel):
    hostname: str
    tier: AssetTier
    owner_team: str | None = None
    os: str | None = None
