from datetime import datetime, timezone

import structlog

from app.models.remediation import ExecutionLog

logger = structlog.get_logger(__name__)


class SimulatedExecutor:
    """Records remediation actions without invoking any real shell commands."""

    def run(self, remediation_id: str, script_sha256: str, approver: str) -> ExecutionLog:
        log = ExecutionLog(
            remediation_id=remediation_id,
            script_sha256=script_sha256,
            approver=approver,
            simulated_exit_code=0,
            executed_at=datetime.now(tz=timezone.utc),
        )
        logger.info(
            "simulated_execution",
            remediation_id=remediation_id,
            sha256=script_sha256[:16],
            approver=approver,
            note="No real commands executed",
        )
        return log


executor = SimulatedExecutor()
