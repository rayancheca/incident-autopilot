from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from app.models.alerts import AlertSeverity


class ReportStatus(StrEnum):
    PENDING = "PENDING"
    STREAMING = "STREAMING"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"


class MitreTactic(BaseModel):
    tactic_id: str
    tactic_name: str
    techniques: list[str] = []


class TimelineEntry(BaseModel):
    timestamp: datetime
    event: str


class AffectedAsset(BaseModel):
    hostname: str | None = None
    ip: str | None = None
    role: str | None = None


class IRReport(BaseModel):
    id: str
    alert_ids: list[str]
    status: ReportStatus = ReportStatus.PENDING
    title: str = ""
    executive_summary: str = ""
    mitre_tactics: list[MitreTactic] = []
    affected_assets: list[AffectedAsset] = []
    confidence: int = Field(0, ge=0, le=100)
    severity: AlertSeverity = AlertSeverity.LOW
    timeline: list[TimelineEntry] = []
    recommendations: list[str] = []
    raw_stream: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None
