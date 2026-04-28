# Incident Autopilot

**Feeds raw SIEM alerts into a local LLM that writes the incident report and the remediation script in one shot.**

[![Backend CI](https://github.com/rayankarimcheca/incident-autopilot/actions/workflows/backend-ci.yml/badge.svg)](https://github.com/rayankarimcheca/incident-autopilot/actions/workflows/backend-ci.yml)
[![Frontend CI](https://github.com/rayankarimcheca/incident-autopilot/actions/workflows/frontend-ci.yml/badge.svg)](https://github.com/rayankarimcheca/incident-autopilot/actions/workflows/frontend-ci.yml)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue)](https://www.python.org/)
[![TypeScript](https://img.shields.io/badge/typescript-5.4-blue)](https://www.typescriptlang.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## What Is This?

SOC analysts spend 30–90 minutes per alert chain translating cryptic, multi-format log output (CEF, Syslog, JSON) into incident response narratives — then another 20–40 minutes hand-authoring iptables block rules and remediation scripts under pressure.

Incident Autopilot is a self-contained SOC IR sandbox that:

1. **Ingests** raw alerts in any format (CEF, RFC 3164/5424 Syslog, JSON) via REST API
2. **Normalizes and enriches** each event (GeoIP, threat-intel reputation, asset criticality tier)
3. **Streams** a structured IR report token-by-token from a local Llama 3 model — MITRE ATT&CK tactic tagging, affected asset enumeration, confidence score, severity classification
4. **Auto-generates** a context-aware Bash remediation script in the same pipeline
5. **Gates** HIGH/CRITICAL scripts behind a manual approval queue before simulated execution

Zero cloud dependency. Zero per-token cost. Runs entirely on local hardware.

---

## Demo

```
Dashboard layout:
┌─────────────────────────────────────────────────────────────────┐
│ 🛡 Incident Autopilot  v0.1.0        ● 9 alerts   ● Ollama OK   │
├──────────────────────────┬──────────────────────────────────────┤
│  Alert Stream            │  LLM Analysis                        │
│                          │                                      │
│  [CRITICAL] 10:00:01     │  Streaming IR Report...              │
│  C2 beacon to known C2   │  {"title": "Active C2 Communica      │
│  src: 194.165.16.11 (RU) │  tion & Data Exfiltration Incid      │
│  ⚠ threat-intel: score 88│  ent", "severity": "CRITICAL",       │
│                          │  "confidence": 91, "mitre_tac        │
│  [HIGH] 10:05:00 ✓       │  tics": [{"tactic_id": "TA001        │
│  Data exfiltration       │  1", "tactic_name": "Command         │
│  500MB to 185.220.101.47 │  and Control"...▌                    │
│                          │                                      │
│  [HIGH] 10:10:00         │  [TA0011] C&C  [TA0010] Exfil        │
│  Lateral movement SMB    │  [TA0008] Lateral Movement           │
│  workstation → DC        │                                      │
│  ★ CROWN JEWEL target    │  Confidence: 91%  Severity: CRITICAL  │
├──────────────────────────┴──────────────────────────────────────┤
│ ▲ Remediation Queue  [1 pending]                                │
│   ┌────────────────────────────────────────────────────────┐    │
│   │ CRITICAL — remediation.sh  sha256: a3f9b...            │    │
│   │ #!/bin/bash                                            │    │
│   │ set -euo pipefail                                      │    │
│   │ iptables -I INPUT -s 194.165.16.11 -j DROP             │    │
│   │ iptables -I OUTPUT -d 185.220.101.47 -j DROP           │    │
│   │                                     [Approve] [Reject] │    │
│   └────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Architecture

```
Raw alert (CEF | Syslog RFC 3164/5424 | JSON)
        │
        ▼
POST /api/alerts/ingest
        │
Format detector → parser → NormalizedEvent (Pydantic)
        │
Enrichment: GeoIP mock + threat-intel mock + asset criticality
        │
In-memory ring-buffer store (cap: 10,000 events)
        │
GET /api/alerts  ──────────────────────→  Frontend alert feed (2s poll)
        │
POST /api/reports/generate { alert_ids }
        │
Build IR_REPORT_PROMPT with enriched context
        │
Ollama streaming call (llama3:8b, temp=0.2)
        │
Tokens fanned out → WebSocket /ws/reports/{id}  →  Frontend typewriter
        │
Final JSON parsed (with retry-repair on malformed output)
        │
IRReport persisted  →  Auto-trigger remediation
        │
Build REMEDIATION_PROMPT with IR report as context
        │
Ollama completion → BashScript (sha256 hashed)
        │
Severity gate:
  LOW/MEDIUM   → auto-approve → SimulatedExecutor (no real shell)
  HIGH/CRITICAL → ApprovalQueue → operator action required
        │
GET /api/remediation/queue  →  Frontend drawer (3s poll)
POST /api/remediation/{id}/approve | /reject
```

### Key Design Decisions

| Decision | Rationale |
|---|---|
| **Local Ollama instead of hosted LLM** | Zero data leaves the network; mandatory for classified/regulated environments. Trade-off: 8–30 tok/sec vs hosted speed |
| **In-memory store instead of Elasticsearch** | Removes infra dependency for the sandbox. Trade-off: no persistence across restarts |
| **WebSocket over SSE** | Allows future bidirectional control (cancel in-flight, regenerate). Trade-off: slightly more client complexity |
| **Single-prompt structured JSON** | One LLM round-trip for the full report. Retry-with-repair handles occasional malformed output |
| **Severity gate hardcoded** | Keeps demo legible; no policy engine to configure |
| **Pydantic v2 at every boundary** | Runtime validation on HTTP, WebSocket, and LLM output catches issues early |

---

## Tech Stack

### Backend
- **Python 3.11** + **FastAPI 0.115** — async ASGI, automatic OpenAPI, native WebSocket
- **Pydantic v2** — strict type validation at every system boundary
- **httpx** — async streaming client to Ollama daemon
- **Ollama** (llama3:8b) — local LLM inference, zero cloud dependency
- **structlog** — JSON-structured logging (non-negotiable in security tooling)
- **python-dateutil** — robust multi-format timestamp parsing for Syslog
- **pytest + pytest-asyncio** — full async test suite

### Frontend
- **React 18** + **TypeScript 5.4 strict** + **Vite 5**
- **Tailwind CSS 3.4** — dark-theme-first utility CSS
- **Zustand 4** — lightweight client state (selected alerts, streaming tokens)
- **TanStack Query 5** — stale-while-revalidate polling for alert feed and queue
- **Prism.js** — Bash syntax highlighting in the remediation script viewer
- **lucide-react** — security-tool-appropriate icons

---

## Requirements

- **Python 3.11+**
- **Node.js 20+**
- **Ollama** with `llama3:8b` pulled

### Install Ollama and pull the model

```bash
# macOS
brew install ollama
ollama pull llama3:8b

# Linux
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama3:8b
```

---

## Quick Start (local dev)

```bash
git clone https://github.com/rayankarimcheca/incident-autopilot
cd incident-autopilot

# 1. Start Ollama
ollama serve &

# 2. Backend
cd backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# 3. Frontend (new terminal)
cd ../frontend
npm install --legacy-peer-deps
npm run dev

# 4. Ingest sample alerts (new terminal)
bash scripts/ingest_samples.sh

# 5. Open http://localhost:5173
```

---

## Docker Compose

```bash
cp .env.example .env
docker compose up --build
# Open http://localhost:5173

# Pull the model inside the Ollama container (first run only)
docker exec incident-autopilot-ollama ollama pull llama3:8b
```

---

## API Reference

### Ingest an alert
```bash
# CEF format
curl -X POST http://localhost:8000/api/alerts/ingest \
  -H "Content-Type: application/json" \
  -d '{"raw": "CEF:0|Vendor|IDS|1.0|100|SSH Brute Force|8|src=185.220.101.47 dst=10.0.0.5 dpt=22"}'

# JSON format
curl -X POST http://localhost:8000/api/alerts/ingest \
  -H "Content-Type: application/json" \
  -d '{"raw": "{\"event_type\": \"c2_beacon\", \"severity\": \"critical\", \"src_ip\": \"194.165.16.11\", \"message\": \"C2 beacon detected\"}"}'
```

### List alerts
```bash
curl http://localhost:8000/api/alerts
```

### Generate an IR report
```bash
# Get alert IDs first, then:
curl -X POST http://localhost:8000/api/reports/generate \
  -H "Content-Type: application/json" \
  -d '{"alert_ids": ["<id1>", "<id2>"]}'
```

### Connect to the token stream (WebSocket)
```bash
# wscat or websocat
wscat -c ws://localhost:8000/ws/reports/<report_id>
```

### Approve a remediation script
```bash
curl -X POST http://localhost:8000/api/remediation/<id>/approve \
  -H "Content-Type: application/json" \
  -d '{"approver": "analyst@corp.local"}'
```

---

## Ingest All Sample Alerts

```bash
bash scripts/ingest_samples.sh

# Output:
# Ingesting sample alerts into http://localhost:8000...
#
# → CEF alerts
#   ✓ [HIGH] 0019dd64e5cf68... SSH Brute Force Attack
#   ✓ [HIGH] 0019dd64e5dea4... Nmap Port Scan Detected
#   ✓ [CRITICAL] 0019dd64e5f1b0... Trojan.GenericKD Detected
#
# → Syslog alerts
#   ✓ [CRITICAL] 0019dd64e60347... Failed password for root from...
#   ✓ [MEDIUM] 0019dd64e60abc... Blocked inbound connection from known C2 IP
#   ✓ [LOW] 0019dd64e61234... sudo escalation
#
# → JSON alerts
#   ✓ [CRITICAL] 0019dd64e61890... Suspicious outbound HTTPS beacon to known C2
#   ✓ [HIGH] 0019dd64e62001... Anomalous outbound data transfer: 500MB
#   ✓ [HIGH] 0019dd64e62abc... SMB lateral movement attempt
```

---

## Supported Alert Formats

### CEF (ArcSight Common Event Format)
```
CEF:0|Vendor|Product|Version|SignatureID|Name|Severity|Extensions
```
Parsed fields: src, dst, spt, dpt, shost, dhost, suser, sproc, rt

### Syslog RFC 3164 (BSD)
```
<PRI>Mmm DD HH:MM:SS hostname process[pid]: message
```

### Syslog RFC 5424
```
<PRI>VERSION TIMESTAMP HOSTNAME APP-NAME PROCID MSGID [SD-DATA] MSG
```
Structured data key-value pairs are extracted.

### JSON
Any JSON object with recognizable fields. Supports multiple naming conventions:
- Severity: `severity`, `level`, `priority`, `sev`
- Timestamp: `timestamp`, `time`, `ts`, `@timestamp`, `event_time`
- Source IP: `src_ip`, `source_ip`, `src`
- Message: `message`, `msg`, `description`, `alert_name`

---

## Technical Deep-Dive

### Alert Parser Pipeline

The CEF parser uses a state-machine approach: split on the first 7 pipes to extract header fields, then apply a greedy regex over the extension string that handles unescaped spaces within values correctly. RFC 3164 and 5424 Syslog parsers are implemented as separate regexes rather than a shared one — the formats differ enough in their timestamp and structured-data sections that a unified regex would be fragile.

### LLM Output Integrity

Llama 3 at temperature 0.2 reliably produces valid JSON ~85% of the time when given a tight schema instruction in the system prompt. The remaining ~15% produce valid JSON buried in prose ("Here is the report:"). The repair pipeline:
1. Try `json.loads()` on the full response
2. If that fails: scan for `{...}` blocks with a greedy regex, try each
3. If that fails: retry the full LLM call with an explicit "your response was not valid JSON" prefix

### Severity Gate

The approval gate is a pure function `_severity_requires_approval(severity) -> bool`. `LOW` and `MEDIUM` auto-approve and flow through `SimulatedExecutor.run()` which records what *would* have executed without invoking any real shell. `HIGH` and `CRITICAL` sit in the queue and cannot execute until an operator calls `POST /api/remediation/{id}/approve`.

### WebSocket Fan-Out

`WSBroker` maintains a `dict[report_id, list[WebSocket]]`. When the Ollama stream yields a token, `broker.publish()` iterates subscribers, catches dead connections, and removes them. This supports multiple browser tabs watching the same report stream simultaneously.

### In-Memory Store

`InMemoryStore` wraps a `collections.deque(maxlen=cap)` for O(1) append and automatic eviction of the oldest alert. A separate `dict[id → event]` provides O(1) lookup by ID. All methods acquire a `threading.Lock` because FastAPI's background tasks and WebSocket handlers run in different threads.

---

## Running Tests

```bash
cd backend
source .venv/bin/activate
pytest tests/ -v
# 49 tests in 0.06s

# With coverage
pytest tests/ --cov=app --cov-report=term-missing
```

---

## Project Structure

```
incident-autopilot/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI routers: health, alerts, reports, remediation, ws
│   │   ├── core/         # Settings, logging, constants
│   │   ├── models/       # Pydantic models: alerts, reports, remediation, ws messages
│   │   ├── services/     # Parsers, enrichment, store, Ollama client, prompt templates
│   │   └── utils/        # Hashing, ID generation, JSON repair
│   └── tests/            # 49 unit + integration tests
├── frontend/
│   └── src/
│       ├── components/   # Alert feed, analysis panel, remediation drawer, UI primitives
│       ├── hooks/        # useAlerts, useReportStream, useRemediationQueue, useOllamaHealth
│       ├── lib/          # API client, WebSocket manager, constants
│       ├── store/        # Zustand state (selected alerts, streaming text, drawer)
│       └── types/        # TypeScript mirrors of all Pydantic models
├── sample-alerts/        # 9 sample alerts (3 CEF, 3 Syslog, 3 JSON)
├── scripts/              # ingest_samples.sh, check_ollama.sh
└── docker-compose.yml
```

---

## Why This Stands Out

Most AI-assisted security tooling either ships data to a hosted LLM (a non-starter for classified/regulated environments) or provides a simple "summarize this log" wrapper. Incident Autopilot is different:

- **End-to-end local inference**: Llama 3 via Ollama, zero cloud dependency
- **Heterogeneous parser pipeline**: Real CEF state-machine, dual RFC Syslog support, flexible JSON mapping — not a regex-and-hope approach
- **Structured IR output with repair**: Streaming JSON from an LLM with mid-stream parse and retry-repair
- **Severity-gated approval queue**: The kind of control plane a real SOC team would need
- **Privacy-first architecture**: Suitable for air-gapped, FedRAMP, or HIPAA environments

---

## License

MIT — see [LICENSE](LICENSE).

---

Built with [Ollama](https://ollama.ai), [FastAPI](https://fastapi.tiangolo.com), [React](https://react.dev), and local Llama 3.
