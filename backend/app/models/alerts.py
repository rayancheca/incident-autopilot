from datetime import datetime, timezone
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from app.models.enrichment import AssetInfo, GeoInfo, ThreatIntelInfo


class AlertFormat(StrEnum):
    CEF = "cef"
    SYSLOG_3164 = "syslog_3164"
    SYSLOG_5424 = "syslog_5424"
    JSON = "json"


class AlertSeverity(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RawAlertIn(BaseModel):
    raw: str = Field(..., max_length=65_536, description="Raw alert string in any supported format")
    format_hint: AlertFormat | None = Field(
        None, description="Optional format hint; auto-detected if omitted"
    )


class NormalizedEvent(BaseModel):
    id: str
    timestamp: datetime
    source_format: AlertFormat
    severity: AlertSeverity
    event_type: str
    source_ip: str | None = None
    dest_ip: str | None = None
    source_host: str | None = None
    dest_host: str | None = None
    src_port: int | None = None
    dest_port: int | None = None
    username: str | None = None
    process_name: str | None = None
    message: str
    raw_fields: dict[str, Any] = Field(default_factory=dict)
    geo: GeoInfo | None = None
    threat_intel: ThreatIntelInfo | None = None
    asset: AssetInfo | None = None
    ingested_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))
