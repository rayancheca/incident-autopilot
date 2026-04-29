import re

import structlog

from app.models.alerts import AlertSeverity
from app.models.remediation import ApprovalStatus, BashScript, RemediationItem
from app.models.reports import IRReport
from app.services.ollama_client import OllamaClient
from app.services.prompts import REMEDIATION_SYSTEM_PROMPT, build_remediation_prompt
from app.services.store import InMemoryStore
from app.utils.hashing import sha256_text
from app.utils.ids import new_id
from app.utils.json_repair import parse_json_with_repair

logger = structlog.get_logger(__name__)

# Patterns that indicate potentially dangerous script content
_DANGEROUS_PATTERNS = re.compile(
    r"curl\s+.*\|\s*(bash|sh)|"
    r"wget\s+.*\|\s*(bash|sh)|"
    r"\beval\b|"
    r"base64\s+-d.*\|\s*(bash|sh)",
    re.IGNORECASE,
)

_MAX_SCRIPT_BYTES = 32_768

_AUTO_APPROVE_SEVERITIES = {AlertSeverity.LOW, AlertSeverity.MEDIUM}


def _severity_requires_approval(severity: AlertSeverity) -> bool:
    return severity not in _AUTO_APPROVE_SEVERITIES


async def generate_remediation(
    report: IRReport,
    store: InMemoryStore,
    ollama: OllamaClient,
) -> RemediationItem:
    """Generate a Bash remediation script for the IR report and enqueue or auto-approve it."""
    asset_list = [
        str(a.hostname or a.ip or "unknown") for a in report.affected_assets
    ]
    prompt = build_remediation_prompt(
        report_title=report.title,
        summary=report.executive_summary,
        affected_assets=asset_list,
        severity=report.severity,
    )

    try:
        raw = await ollama.complete(prompt, system=REMEDIATION_SYSTEM_PROMPT, temperature=0.15)
    except Exception as exc:
        logger.error("remediation_llm_error", report_id=report.id, error=str(exc))
        fallback_body = _fallback_script(report, asset_list)
        raw_data = {
            "body": fallback_body,
            "rationale": "Fallback script generated due to LLM error",
            "target_hosts": asset_list,
            "requires_root": True,
        }
        return _build_item(raw_data, report)

    parsed = parse_json_with_repair(raw)
    if not parsed:
        logger.warning("remediation_json_parse_failed", report_id=report.id, snippet=raw[:200])
        parsed = {
            "body": _fallback_script(report, asset_list),
            "rationale": "Fallback: JSON parsing failed",
            "target_hosts": asset_list,
            "requires_root": True,
        }

    item = _build_item(parsed, report)
    store.add_remediation(item)
    logger.info(
        "remediation_created",
        item_id=item.id,
        severity=report.severity,
        auto_approved=item.auto_approved,
    )
    return item


def _validate_script_body(body: str) -> str:
    """Reject scripts with dangerous patterns; truncate oversized bodies."""
    if len(body.encode()) > _MAX_SCRIPT_BYTES:
        logger.warning("remediation_script_oversized", size=len(body.encode()))
        body = body[:_MAX_SCRIPT_BYTES]
    if _DANGEROUS_PATTERNS.search(body):
        logger.error("remediation_script_dangerous_pattern_detected")
        return "#!/bin/bash\necho 'Script rejected: dangerous pattern detected' >&2\nexit 1"
    return body


def _build_item(data: dict, report: IRReport) -> RemediationItem:
    body = _validate_script_body(
        str(data.get("body", "#!/bin/bash\necho 'No script generated'"))
    )
    script = BashScript(
        body=body,
        rationale=str(data.get("rationale", "")),
        target_hosts=list(data.get("target_hosts", [])),
        requires_root=bool(data.get("requires_root", True)),
        sha256=sha256_text(body),
    )
    requires_approval = _severity_requires_approval(report.severity)
    return RemediationItem(
        id=new_id(),
        report_id=report.id,
        severity=report.severity,
        script=script,
        approval_status=ApprovalStatus.PENDING if requires_approval else ApprovalStatus.APPROVED,
        auto_approved=not requires_approval,
    )


def _fallback_script(report: IRReport, assets: list[str]) -> str:
    hosts = " ".join(assets[:5]) if assets else "unknown"
    return f"""#!/bin/bash
set -euo pipefail

LOG=/var/log/incident-autopilot.log
echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Incident: {report.title}" | tee -a "$LOG"
echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Severity: {report.severity}" | tee -a "$LOG"
echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Affected hosts: {hosts}" | tee -a "$LOG"

# Block known malicious IPs (placeholders — replace with actual IPs from IR report)
# iptables -I INPUT -s <MALICIOUS_IP> -j DROP
# iptables -I OUTPUT -d <MALICIOUS_IP> -j DROP

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Remediation script completed (FALLBACK)" | tee -a "$LOG"
"""
