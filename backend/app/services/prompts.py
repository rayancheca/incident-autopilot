from app.models.alerts import NormalizedEvent

SYSTEM_PROMPT = """You are an elite SOC (Security Operations Center) analyst with deep expertise in MITRE ATT&CK, incident response, and threat intelligence. You analyze security alerts and produce structured incident reports.

CRITICAL: You MUST respond with a single valid JSON object only. No prose, no markdown, no explanation outside the JSON. The JSON must be parseable by Python's json.loads()."""


IR_REPORT_SCHEMA = """{
  "title": "string — concise incident title",
  "executive_summary": "string — 2-4 sentences for a non-technical audience",
  "severity": "LOW | MEDIUM | HIGH | CRITICAL",
  "confidence": number between 0 and 100,
  "mitre_tactics": [
    {"tactic_id": "TA000X", "tactic_name": "string", "techniques": ["T1XXX.XXX"]}
  ],
  "affected_assets": [
    {"hostname": "string or null", "ip": "string or null", "role": "string or null"}
  ],
  "timeline": [
    {"timestamp": "ISO8601 string", "event": "string"}
  ],
  "recommendations": ["string", "string"]
}"""


def build_ir_prompt(events: list[NormalizedEvent]) -> str:
    events_text = "\n\n".join(
        f"[Alert {i + 1}]\n"
        f"Format: {e.source_format}\n"
        f"Time: {e.timestamp.isoformat()}\n"
        f"Severity: {e.severity}\n"
        f"Event: {e.event_type}\n"
        f"Source IP: {e.source_ip or 'N/A'} (GeoIP: {e.geo.country_name if e.geo else 'N/A'})\n"
        f"Dest IP: {e.dest_ip or 'N/A'}\n"
        f"Source Host: {e.source_host or 'N/A'}"
        + (" [CROWN JEWEL asset]" if e.asset and e.asset.tier.value == "CROWN_JEWEL" else "")
        + f"\n"
        f"Username: {e.username or 'N/A'}\n"
        f"Process: {e.process_name or 'N/A'}\n"
        f"Message: {e.message}\n"
        + (f"Threat Intel: score={e.threat_intel.reputation_score}, categories={e.threat_intel.categories}\n" if e.threat_intel and e.threat_intel.reputation_score > 0 else "")
        for i, e in enumerate(events)
    )

    return f"""Analyze these {len(events)} security alert(s) and produce a structured incident response report.

ALERTS:
{events_text}

Respond with ONLY this JSON structure (no extra text):
{IR_REPORT_SCHEMA}"""


REMEDIATION_SYSTEM_PROMPT = """You are a senior Linux security engineer. You write precise, safe, and effective Bash remediation scripts for security incidents. Scripts must be production-quality: idempotent, exit cleanly on error, and include inline comments explaining every non-obvious command."""


def build_remediation_prompt(report_title: str, summary: str, affected_assets: list[str], severity: str) -> str:
    assets_str = "\n".join(f"  - {a}" for a in affected_assets) if affected_assets else "  - Unknown hosts"
    return f"""Generate a Bash remediation script for the following security incident.

INCIDENT: {report_title}
SEVERITY: {severity}
SUMMARY: {summary}
AFFECTED ASSETS:
{assets_str}

Respond with ONLY this JSON structure:
{{
  "body": "#!/bin/bash\\n# full bash script here with real commands",
  "rationale": "string — 1-2 sentences explaining what the script does and why",
  "target_hosts": ["hostname1", "hostname2"],
  "requires_root": true
}}

The script MUST include at minimum:
1. #!/bin/bash shebang and set -euo pipefail
2. iptables DROP rules for any known malicious IPs from the incident
3. Logging of all actions to /var/log/incident-autopilot.log
4. A final echo confirming completion
"""
