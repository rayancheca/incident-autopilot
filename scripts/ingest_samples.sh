#!/bin/bash
# Ingest all sample alerts into the Incident Autopilot backend
set -euo pipefail

BASE_URL="${BACKEND_URL:-http://localhost:8000}"
SAMPLES_DIR="$(dirname "$0")/../sample-alerts"

ingest() {
    local raw="$1"
    local fmt="${2:-}"
    local payload
    if [[ -n "$fmt" ]]; then
        payload=$(printf '{"raw": %s, "format_hint": "%s"}' "$(echo "$raw" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read().strip()))')" "$fmt")
    else
        payload=$(printf '{"raw": %s}' "$(echo "$raw" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read().strip()))')")
    fi
    curl -sf -X POST "$BASE_URL/api/alerts/ingest" \
        -H "Content-Type: application/json" \
        -d "$payload" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'  ✓ [{d[\"severity\"]}] {d[\"id\"][:20]}... {d[\"message\"][:60]}')"
}

echo "Ingesting sample alerts into $BASE_URL..."
echo

echo "→ CEF alerts"
ingest "$(cat "$SAMPLES_DIR/brute_force.cef")" "cef"
ingest "$(cat "$SAMPLES_DIR/port_scan.cef")" "cef"
ingest "$(cat "$SAMPLES_DIR/malware_detected.cef")" "cef"

echo
echo "→ Syslog alerts"
ingest "$(cat "$SAMPLES_DIR/auth_failure.syslog")" "syslog_3164"
ingest "$(cat "$SAMPLES_DIR/firewall_block.syslog")" "syslog_5424"
ingest "$(cat "$SAMPLES_DIR/sudo_escalation.syslog")" "syslog_3164"

echo
echo "→ JSON alerts"
ingest "$(cat "$SAMPLES_DIR/c2_beacon.json")" "json"
ingest "$(cat "$SAMPLES_DIR/data_exfil.json")" "json"
ingest "$(cat "$SAMPLES_DIR/lateral_movement.json")" "json"

echo
echo "Done. Open http://localhost:5173 to view the dashboard."
