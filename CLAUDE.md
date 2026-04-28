# Agent Instructions — Read Before Every Action

Read in this order, every session:

1. `~/daily-builder/prompts/rules/session_protocol.md`
2. `~/daily-builder/prompts/rules/quality_bar.md`
3. `~/daily-builder/prompts/rules/code_rules.md`
4. `state.md` in this directory
5. This file

---

# Project: Incident Autopilot — LLM-Powered SOC IR Sandbox

**Repo name:** `incident-autopilot`

**Tagline:** Feeds raw SIEM alerts into a local LLM that writes the incident report and the remediation script in one shot.

**Tech stack:** Python 3.11 + FastAPI + Ollama (Llama 3), React 18 + TypeScript 5.4 + Vite, WebSockets, Tailwind CSS, Zustand, TanStack Query, Prism.js

**Problem:** SOC analysts spend 30–90 minutes per alert chain translating cryptic multi-format log output (CEF, Syslog, JSON) into incident response narratives, then another 20–40 minutes hand-authoring iptables/PowerShell remediation stubs. Incident Autopilot ingests raw alert streams, uses a local Llama 3 model (zero cloud dependency) to produce structured IR reports (MITRE ATT&CK tagging, assets, confidence score) and auto-generates Bash remediation scripts in one shot — streamed token-by-token to the dashboard.

**Target user:** SOC analysts, blue team engineers, IR consultants, security hiring managers reviewing public GitHub portfolios.

---

# Architecture Overview

## Components

1. **Frontend (React + TypeScript + Vite)** — SPA on `localhost:5173`. Two-column layout: left=alert feed, right=LLM analysis stream, bottom drawer=remediation approval queue. REST for mutations, WebSocket for streaming.

2. **Backend (FastAPI + Uvicorn)** — Python ASGI on `localhost:8000`. REST endpoints + WebSocket for LLM streaming.

3. **Ingestion / Normalization Layer** — pure-Python parsers for CEF, Syslog RFC 3164/5424, JSON. Produces unified `NormalizedEvent`. Enrichment adds mock GeoIP, threat-intel reputation, asset criticality.

4. **In-Memory Store** — thread-safe dict-of-lists. No persistence (sandbox). Ring buffer cap: 10,000 alerts.

5. **Ollama Service Layer** — async httpx talking to `http://localhost:11434`. Two prompts: `IR_REPORT_PROMPT` (→ structured JSON with MITRE tactics) and `REMEDIATION_PROMPT` (→ Bash script). Streams JSON-Lines, fans tokens to `asyncio.Queue` for WebSocket delivery.

6. **Remediation Engine** — severity gate: LOW/MEDIUM auto-approve, HIGH/CRITICAL go to approval queue. Simulated executor (no real shell exec) records what would have run.

## Data Flow

```
Raw alert (CEF | Syslog | JSON)
    → POST /api/alerts/ingest
    → Format detector → parser → NormalizedEvent
    → Enrichment (GeoIP mock, threat-intel mock, asset criticality)
    → In-memory store
    → GET /api/alerts (left panel polling)

Selected alerts
    → POST /api/reports/generate { alert_ids }
    → IR_REPORT_PROMPT + Ollama streaming
    → WebSocket /ws/reports/{report_id} → frontend typewriter
    → Parsed IRReport → auto-trigger remediation

IRReport
    → REMEDIATION_PROMPT + Ollama
    → BashScript + severity gate
    → LOW/MEDIUM: auto-approve → SimulatedExecutor
    → HIGH/CRITICAL: ApprovalQueue → operator action
    → GET /api/remediation/queue (drawer)
    → POST /api/remediation/{id}/approve | /reject
```

## Key Design Decisions

- **Local-first LLM:** privacy, no per-token cost. Trade-off: slower (8–30 tok/sec on consumer hardware).
- **In-memory store:** removes Elasticsearch infra dependency for sandbox. Trade-off: no persistence.
- **WebSocket over SSE:** bidirectional allows future cancel/regenerate messages.
- **Single-prompt structured JSON output:** one LLM round-trip. Retry-with-repair on malformed JSON.
- **Pydantic v2 everywhere:** runtime validation at every boundary.

---

# Complete Tech Stack

## Backend
- Python 3.11, FastAPI 0.110+, Uvicorn, Pydantic v2
- httpx (async streaming to Ollama), structlog (JSON logging)
- python-dateutil (Syslog timestamp parsing)
- pytest 8.x + pytest-asyncio, ruff, mypy --strict

## Frontend
- React 18, TypeScript 5.4 strict, Vite 5
- Tailwind CSS 3.4, Zustand 4, TanStack Query 5
- Prism.js 1.29 (Bash syntax highlight), clsx, lucide-react
- Vitest, @testing-library/react, Playwright

## Infra
- Docker + docker-compose v2, GitHub Actions CI

---

# Complete File and Folder Structure

```
incident-autopilot/
├── README.md                                 # Full project docs
├── CLAUDE.md                                 # Agent instructions (this file)
├── state.md                                  # Session tracker
├── LICENSE                                   # MIT
├── .gitignore
├── .env.example                              # All env vars with safe defaults
├── docker-compose.yml                        # Backend + Frontend + Ollama
│
├── .github/
│   └── workflows/
│       ├── backend-ci.yml                    # ruff + mypy + pytest on push
│       └── frontend-ci.yml                   # tsc + vitest on push
│
├── backend/
│   ├── Dockerfile
│   ├── pyproject.toml                        # Project metadata, ruff/mypy config
│   ├── requirements.txt                      # Pinned runtime deps
│   ├── requirements-dev.txt                  # Test/lint deps
│   ├── pytest.ini
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                           # FastAPI app factory, CORS, router includes
│   │   │
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py                     # Pydantic Settings: OLLAMA_URL, MODEL, etc.
│   │   │   ├── logging.py                    # structlog setup
│   │   │   └── constants.py                  # MITRE tactic ids, store cap, severity colors
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── alerts.py                     # RawAlertIn, NormalizedEvent, AlertSeverity
│   │   │   ├── enrichment.py                 # GeoInfo, ThreatIntelInfo, AssetInfo
│   │   │   ├── reports.py                    # IRReport, MitreTactic, ReportStatus
│   │   │   ├── remediation.py                # BashScript, RemediationItem, ApprovalAction
│   │   │   └── ws_messages.py                # WSToken, WSStatus, WSError, WSFinal
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── deps.py                       # Shared deps: store, ollama_client
│   │   │   ├── health.py                     # GET /api/health
│   │   │   ├── alerts.py                     # POST /api/alerts/ingest, GET /api/alerts
│   │   │   ├── reports.py                    # POST /api/reports/generate
│   │   │   ├── remediation.py                # GET queue, approve, reject
│   │   │   └── ws.py                         # WebSocket /ws/reports/{report_id}
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── parsers/
│   │   │   │   ├── __init__.py               # parse() entrypoint + format detection
│   │   │   │   ├── detector.py               # detect_format(raw) -> AlertFormat
│   │   │   │   ├── cef.py                    # parse_cef(raw) -> NormalizedEvent
│   │   │   │   ├── syslog_3164.py            # parse_syslog_3164
│   │   │   │   ├── syslog_5424.py            # parse_syslog_5424
│   │   │   │   └── json_parser.py            # parse_json
│   │   │   ├── enrichment/
│   │   │   │   ├── __init__.py               # enrich(event) -> NormalizedEvent
│   │   │   │   ├── geoip_mock.py             # Static IP → GeoInfo
│   │   │   │   ├── threat_intel_mock.py      # Static IP/hash → ThreatIntelInfo
│   │   │   │   └── asset_lookup.py           # Hostname → AssetInfo
│   │   │   ├── store.py                      # InMemoryStore
│   │   │   ├── ollama_client.py              # Async streaming Ollama wrapper
│   │   │   ├── prompts.py                    # IR_REPORT_PROMPT, REMEDIATION_PROMPT
│   │   │   ├── report_service.py             # LLM call + JSON parse + repair
│   │   │   ├── remediation_service.py        # Remediation LLM + severity gate
│   │   │   ├── executor.py                   # SimulatedExecutor
│   │   │   └── ws_broker.py                  # Token pub/sub for WebSocket fanout
│   │   │
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── hashing.py                    # sha256_text(s) -> str
│   │       ├── ids.py                        # new_id() -> str
│   │       └── json_repair.py                # extract_json_block + retry helper
│   │
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py                       # Fixtures: client, store, mock ollama
│       ├── unit/
│       │   ├── test_parsers_cef.py
│       │   ├── test_parsers_syslog_3164.py
│       │   ├── test_parsers_syslog_5424.py
│       │   ├── test_parsers_json.py
│       │   ├── test_detector.py
│       │   ├── test_enrichment.py
│       │   ├── test_store.py
│       │   ├── test_json_repair.py
│       │   └── test_severity_gate.py
│       ├── integration/
│       │   ├── test_ingest_endpoint.py
│       │   ├── test_alerts_listing.py
│       │   ├── test_report_endpoint.py
│       │   ├── test_remediation_queue.py
│       │   └── test_websocket_streaming.py
│       └── fixtures/
│           ├── cef_samples.py
│           ├── syslog_samples.py
│           ├── json_samples.py
│           └── mock_ollama_responses.py
│
├── frontend/
│   ├── Dockerfile
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── tsconfig.node.json
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   ├── postcss.config.js
│   │
│   └── src/
│       ├── main.tsx                          # React root mount
│       ├── App.tsx                           # Root layout, routing
│       ├── index.css                         # Tailwind base + custom tokens
│       │
│       ├── components/
│       │   ├── layout/
│       │   │   ├── Header.tsx                # App header with status indicators
│       │   │   └── StatusBar.tsx             # Ollama health, alert count
│       │   ├── alerts/
│       │   │   ├── AlertFeed.tsx             # Left panel: live alert list
│       │   │   ├── AlertCard.tsx             # Single alert entry with severity badge
│       │   │   └── SeverityBadge.tsx         # Color-coded severity pill
│       │   ├── analysis/
│       │   │   ├── AnalysisPanel.tsx         # Right panel: LLM stream + report
│       │   │   ├── StreamingText.tsx         # Typewriter with blinking cursor
│       │   │   ├── IRReportView.tsx          # Rendered structured IR report
│       │   │   └── MitreBadge.tsx            # MITRE ATT&CK tactic pill
│       │   ├── remediation/
│       │   │   ├── RemediationDrawer.tsx     # Bottom slide-up drawer
│       │   │   ├── ScriptViewer.tsx          # Prism.js bash highlight
│       │   │   └── ApprovalButtons.tsx       # Approve / Reject with confirmation
│       │   └── ui/
│       │       ├── Badge.tsx                 # Generic pill badge
│       │       ├── Button.tsx                # Styled button variants
│       │       ├── Spinner.tsx               # Loading spinner
│       │       └── EmptyState.tsx            # No-data placeholder
│       │
│       ├── hooks/
│       │   ├── useAlerts.ts                  # TanStack Query: alert list polling
│       │   ├── useReportStream.ts            # WebSocket hook: token streaming
│       │   ├── useRemediationQueue.ts        # TanStack Query: queue polling
│       │   └── useOllamaHealth.ts            # Ollama reachability check
│       │
│       ├── lib/
│       │   ├── api.ts                        # Typed fetch wrappers for all endpoints
│       │   ├── ws.ts                         # WebSocket connection manager
│       │   └── constants.ts                  # MITRE tactic colors, severity colors
│       │
│       ├── store/
│       │   └── appStore.ts                   # Zustand: selected alerts, active report
│       │
│       └── types/
│           ├── alerts.ts                     # NormalizedEvent, RawAlertIn
│           ├── reports.ts                    # IRReport, MitreTactic
│           ├── remediation.ts                # RemediationItem, BashScript
│           └── ws.ts                         # WS message union types
│
├── sample-alerts/
│   ├── brute_force.cef                       # CEF: SSH brute force event
│   ├── port_scan.cef                         # CEF: nmap port scan detection
│   ├── malware_detected.cef                  # CEF: AV malware detection
│   ├── auth_failure.syslog                   # RFC 3164: auth failure
│   ├── firewall_block.syslog                 # RFC 5424: firewall block
│   ├── sudo_escalation.syslog                # RFC 3164: sudo escalation
│   ├── c2_beacon.json                        # JSON: C2 beacon detection
│   ├── data_exfil.json                       # JSON: data exfiltration alert
│   └── lateral_movement.json                 # JSON: lateral movement detection
│
└── scripts/
    ├── ingest_samples.sh                     # Bash: curl all sample alerts to backend
    └── check_ollama.sh                       # Verify Ollama is running with llama3
```

---

# Implementation Steps (strict order)

## Step 1 — Project scaffolding
**Build:** Create all directories, requirements.txt, pyproject.toml, .gitignore, .env.example, pytest.ini
**Verify:** `cd backend && pip install -r requirements.txt` succeeds; `cd frontend && npm install` succeeds
**Commit:** `chore: scaffold project structure and dependencies`

## Step 2 — Pydantic models
**Build:** All models in `backend/app/models/`: alerts.py, enrichment.py, reports.py, remediation.py, ws_messages.py
**Verify:** `python -c "from app.models.alerts import NormalizedEvent; print('ok')"` succeeds
**Commit:** `feat: add Pydantic models for alerts, reports, and remediation`

## Step 3 — Alert parsers
**Build:** All parsers in `backend/app/services/parsers/`: CEF state-machine parser, Syslog RFC 3164, RFC 5424, JSON passthrough, format detector
**Verify:** Unit tests `pytest tests/unit/test_parsers_*.py` all pass
**Commit:** `feat: implement CEF, Syslog RFC 3164/5424, and JSON alert parsers`

## Step 4 — Enrichment services
**Build:** `geoip_mock.py`, `threat_intel_mock.py`, `asset_lookup.py`, `enrichment/__init__.py`
**Verify:** `pytest tests/unit/test_enrichment.py` passes
**Commit:** `feat: add mock GeoIP, threat-intel, and asset enrichment services`

## Step 5 — In-memory store + utilities
**Build:** `store.py` (InMemoryStore with threading.Lock, ring buffer), `utils/ids.py`, `utils/hashing.py`, `utils/json_repair.py`
**Verify:** `pytest tests/unit/test_store.py` passes
**Commit:** `feat: implement thread-safe in-memory store with ring buffer`

## Step 6 — FastAPI backend skeleton
**Build:** `app/main.py`, `app/core/config.py`, `app/core/logging.py`, `app/core/constants.py`, `app/api/deps.py`, `app/api/health.py`
**Verify:** `uvicorn app.main:app --reload` starts; `curl http://localhost:8000/api/health` returns `{"status":"ok",...}`
**Commit:** `feat: FastAPI app skeleton with health endpoint and structured logging`

## Step 7 — Alert ingestion endpoint
**Build:** `app/api/alerts.py`: POST /api/alerts/ingest (parse + enrich + store), GET /api/alerts (paginated), GET /api/alerts/{id}
**Verify:** `pytest tests/integration/test_ingest_endpoint.py` passes; manual curl with CEF sample succeeds
**Commit:** `feat: alert ingestion, parsing, and listing endpoints`

## Step 8 — Ollama client + prompts
**Build:** `services/ollama_client.py` (async httpx streaming), `services/prompts.py` (IR_REPORT_PROMPT and REMEDIATION_PROMPT templates with JSON schema instructions), `services/ws_broker.py`
**Verify:** `python -m app.services.ollama_client` smoke test (with Ollama running) streams tokens to stdout
**Commit:** `feat: Ollama async streaming client and LLM prompt templates`

## Step 9 — IR report generation + WebSocket streaming
**Build:** `services/report_service.py` (orchestrates LLM call, JSON parse with repair retry), `api/reports.py` (POST /api/reports/generate), `api/ws.py` (WebSocket /ws/reports/{report_id})
**Verify:** `pytest tests/integration/test_report_endpoint.py` passes with mocked Ollama; `pytest tests/integration/test_websocket_streaming.py` passes
**Commit:** `feat: IR report generation with WebSocket token streaming`

## Step 10 — Remediation service + approval queue
**Build:** `services/remediation_service.py` (LLM call → BashScript, severity gate), `services/executor.py` (SimulatedExecutor), `api/remediation.py` (queue list, approve, reject)
**Verify:** `pytest tests/unit/test_severity_gate.py` passes; `pytest tests/integration/test_remediation_queue.py` passes
**Commit:** `feat: remediation script generation with severity-gated approval queue`

## Step 11 — React frontend setup
**Build:** Vite + React + TypeScript strict + Tailwind config, `src/types/` all type files, `src/lib/api.ts`, `src/lib/ws.ts`, `src/lib/constants.ts`, `src/store/appStore.ts`
**Verify:** `npm run dev` starts; `npm run build` succeeds with zero TypeScript errors
**Commit:** `feat: React frontend scaffold with TypeScript types, API client, and Zustand store`

## Step 12 — Alert feed panel
**Build:** `AlertFeed.tsx`, `AlertCard.tsx`, `SeverityBadge.tsx`, `useAlerts.ts` (TanStack Query polling every 2s), wire into `App.tsx`
**Verify:** Start backend + frontend; ingest a sample alert via curl; see it appear in left panel within 2 seconds
**Commit:** `feat: real-time alert feed panel with severity-color-coded cards`

## Step 13 — LLM analysis streaming panel
**Build:** `StreamingText.tsx` (typewriter + blinking cursor animation), `IRReportView.tsx` (structured report display), `MitreBadge.tsx` (tactic pills), `AnalysisPanel.tsx`, `useReportStream.ts` (WebSocket hook)
**Verify:** Select alerts, click "Analyze" button, see tokens stream in real-time with cursor blinking; see structured report render after stream completes
**Commit:** `feat: LLM analysis panel with real-time token streaming and structured IR report display`

## Step 14 — Remediation approval queue UI
**Build:** `RemediationDrawer.tsx` (bottom slide-up), `ScriptViewer.tsx` (Prism.js bash), `ApprovalButtons.tsx`, `useRemediationQueue.ts`
**Verify:** HIGH severity alert → generate report → see script appear in drawer → approve → see "executed" status
**Commit:** `feat: remediation approval drawer with syntax-highlighted script viewer`

## Step 15 — Sample alerts + ingest script
**Build:** All 9 sample alert files in `sample-alerts/`, `scripts/ingest_samples.sh`, `scripts/check_ollama.sh`
**Verify:** `bash scripts/ingest_samples.sh` ingests all 9; all appear in alert feed
**Commit:** `feat: sample alert files and ingestion helper scripts`

## Step 16 — Docker Compose
**Build:** `backend/Dockerfile`, `frontend/Dockerfile`, `docker-compose.yml` (backend + frontend + ollama services)
**Verify:** `docker compose up --build` brings up all services; full flow works end-to-end
**Commit:** `feat: Docker Compose multi-service setup`

## Step 17 — GitHub Actions CI
**Build:** `.github/workflows/backend-ci.yml` (ruff + mypy + pytest), `.github/workflows/frontend-ci.yml` (tsc + vitest)
**Verify:** Push triggers CI; both workflows pass
**Commit:** `ci: add GitHub Actions for backend and frontend`

## Step 18 — README + final polish
**Build:** Comprehensive README.md with badges, architecture diagram, install instructions, usage examples, technical deep-dive
**Verify:** Read through end-to-end; markdown renders correctly on GitHub
**Commit:** `docs: comprehensive README with architecture and technical deep-dive`

---

# Visual and UX Requirements

## Design Direction: Dark Security Tool

- **Background:** `#0a0e1a` (deep navy almost black)
- **Surface:** `#111827` (dark slate for cards/panels)
- **Surface elevated:** `#1f2937` (slightly lighter for hover/active)
- **Border:** `#374151` (subtle dividers)
- **Text primary:** `#f9fafb` (near white)
- **Text secondary:** `#9ca3af` (medium gray)
- **Accent:** `#3b82f6` (blue — interactive elements)

## Severity Colors
- `CRITICAL` → `#ef4444` (red-500) background badge, red glow on card
- `HIGH` → `#f59e0b` (amber-500)
- `MEDIUM` → `#eab308` (yellow-500)
- `LOW` → `#3b82f6` (blue-500)

## Layout
- Header bar: full width, dark, shows app name + Ollama status dot (green/red) + alert count
- Main content: two-column grid (left 40% / right 60%)
  - Left: alert feed with scrollable card list
  - Right: analysis panel — empty state → streaming → rendered report
- Bottom: remediation drawer (collapsed by default, badge count shows pending)

## MITRE ATT&CK Badge Colors by Tactic Category
- Initial Access: `#7c3aed` (purple)
- Execution: `#dc2626` (red)
- Persistence: `#ea580c` (orange)
- Privilege Escalation: `#d97706` (amber)
- Defense Evasion: `#65a30d` (lime)
- Credential Access: `#0891b2` (cyan)
- Discovery: `#2563eb` (blue)
- Lateral Movement: `#7c3aed` (purple)
- Collection: `#be185d` (pink)
- Command and Control: `#dc2626` (red)
- Exfiltration: `#b45309` (amber dark)
- Impact: `#991b1b` (red dark)

## Typography
- UI text: Inter (system font fallback acceptable)
- Code / script viewer: JetBrains Mono (or Fira Code as fallback)
- Streaming LLM text: monospace with blinking `|` cursor (`animate-pulse`)

## Animations
- Alert cards: slide-in from left on appear
- Streaming text: character-by-character with blinking cursor
- Drawer: slide-up transition (300ms ease-out)
- Severity badge: subtle pulse on CRITICAL
- All transitions: compositor-friendly (transform + opacity only)

---

# userEmail
The user's email address is rayankarimcheca@gmail.com.

# currentDate
Today's date is 2026-04-28.

Estimated sessions: 3
