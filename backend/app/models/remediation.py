from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from app.models.alerts import AlertSeverity


class ApprovalStatus(StrEnum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXECUTED = "EXECUTED"


class BashScript(BaseModel):
    body: str
    rationale: str
    target_hosts: list[str] = []
    requires_root: bool = True
    sha256: str = ""


class RemediationItem(BaseModel):
    id: str
    report_id: str
    severity: AlertSeverity
    script: BashScript
    approval_status: ApprovalStatus = ApprovalStatus.PENDING
    auto_approved: bool = False
    approver: str | None = None
    rejection_reason: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    actioned_at: datetime | None = None


class ApprovalAction(BaseModel):
    approver: str = "analyst@local"
    reason: str | None = None


class ExecutionLog(BaseModel):
    remediation_id: str
    script_sha256: str
    approver: str
    simulated_exit_code: int = 0
    executed_at: datetime = Field(default_factory=datetime.utcnow)
    note: str = "Simulated — no real shell commands were executed"
