## Status
IN PROGRESS (Session 2 partially complete — continuing in Session 3)

## Project
incident-autopilot — Feeds raw SIEM alerts into a local LLM that writes the incident report and the remediation script in one shot.

## Session count
2

## Completed steps
- Step 0: Project spec written and embedded in CLAUDE.md
- Step 1: Backend scaffolding — Python 3.11 venv, requirements.txt, pyproject.toml
- Step 2: All Pydantic models (alerts, enrichment, reports, remediation, ws_messages)
- Step 3: Alert parsers — CEF state-machine, Syslog RFC 3164, RFC 5424, JSON passthrough, format detector
- Step 4: Enrichment services — GeoIP mock, threat-intel mock, asset criticality lookup
- Step 5: In-memory ring-buffer store + utils (ids, hashing, json_repair)
- Step 6: FastAPI app skeleton — main.py, config, logging, CORS, health endpoint
- Step 7: Alert ingestion endpoints — POST /api/alerts/ingest, GET /api/alerts, GET /api/alerts/{id}
- Step 8: Ollama client (async streaming) + LLM prompt templates (IR report + remediation)
- Step 9: IR report generation with WebSocket token streaming + JSON parse with repair
- Step 10: Remediation service + severity gate + simulated executor + approval queue API
- Step 11–14: Complete React frontend — types, API client, Zustand store, all hooks, all components
- Step 15: 9 sample alert files (CEF, Syslog, JSON) + helper scripts
- Step 16: Docker Compose (backend + frontend + Ollama services + Dockerfiles)
- Step 17: GitHub Actions CI (backend: ruff + mypy + pytest; frontend: tsc + build)
- Step 18: Comprehensive README with architecture, deep-dive, API reference
- Session 2 — Code review fixes applied (all CRITICAL + HIGH issues from Opus reviewer):
  - [CRITICAL] app/models/alerts.py: max_length=65536 on RawAlertIn.raw; timezone-aware utcnow
  - [CRITICAL] app/main.py: CORS locked down (allow_credentials=False, allow_methods=["GET","POST"], explicit allow_headers); Ollama client init/close in lifespan
  - [CRITICAL] app/services/remediation_service.py: Bash script body validated — dangerous patterns (eval, curl|sh, wget|sh, base64 pipe) rejected; size capped at 32KB
  - [HIGH] app/models/remediation.py: BashScript.target_hosts mutable default fixed (Field(default_factory=list)); datetime.utcnow fixed (2 places)
  - [HIGH] app/core/config.py: api_key setting added (empty = auth disabled)
  - [HIGH] app/api/deps.py: require_api_key() dependency added for optional API key auth
  - [HIGH] app/services/store.py: transition_remediation() atomic method added (lock-protected read-check-update)
  - [HIGH] app/api/remediation.py: approve/reject use atomic transition; api key auth wired; removed TOCTOU race
  - [HIGH] app/services/parsers/json_parser.py: _parse_port() added — try/except + 0-65535 bounds + handles "22/tcp"-style strings
  - [HIGH] app/services/ollama_client.py: health_check bare except narrowed to (httpx.HTTPError, OSError)
  - [HIGH] app/services/ws_broker.py: subscriber cap (20/report); subscribe() returns bool; bare except logged
  - [HIGH] app/api/ws.py: import json moved to top; report existence verified before ws.accept(); ReportStatus enum comparison fixed; subscriber cap enforced
  - [MEDIUM] app/services/prompts.py: f-string without interpolation fixed

## Backend test results
49 tests passing in 0.06s (Session 1 — pre-review)
PENDING: re-run after Session 2 fixes (venv must be activated first)

## Frontend build
Zero TypeScript errors, 241KB JS (gzipped: 77KB), 20KB CSS

## In progress
Session 2 interrupted — test re-run and frontend tests not yet done

## Remaining work for Session 3
1. **[FIRST]** Re-run test suite to verify all fixes pass
   - IMPORTANT: use venv python, not system python
   - Command: cd backend && source .venv/bin/activate && python -m pytest tests/ -v
   - If pytest not found: pip install -r requirements-dev.txt
2. **[REQUIRED]** Add Vitest frontend unit tests (quality bar: 80% coverage)
   - Target: utils (severity color mapper, API error parsing), hooks (useAlerts, useRemediationQueue)
   - Setup: cd frontend && npm install -D vitest @testing-library/react @testing-library/user-event jsdom
   - Add vitest.config.ts
3. **[OPTIONAL]** Live smoke test with Ollama
   - Blocker: Ollama not installed locally
   - Workaround: docker compose up (spins up Ollama + backend + frontend)
4. **[FINAL]** Commit all Session 2 fixes + tests, push to GitHub, mark COMPLETE

## How to activate the venv
```
cd /Users/rayankarimcheca/dev/daily-projects/incident-autopilot/backend
source .venv/bin/activate
```
If .venv doesn't exist:
```
~/.local/bin/python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

## Blockers
- Ollama not installed locally — cannot test full LLM streaming end-to-end without it
  (Docker Compose solves this for end users)
- Python 3.14 incompatible with pydantic-core — must use Python 3.11 venv

## Notes
- Python 3.11 binary: ~/.local/bin/python3.11
- Venv: backend/.venv (activate before running pytest)
- GitHub remote: rayancheca/incident-autopilot (verify username)
- ws_broker.subscribe() now returns bool — ws.py updated to check it

## Files changed in Session 2 (all need to be staged and committed)
- backend/app/models/alerts.py
- backend/app/models/remediation.py
- backend/app/core/config.py
- backend/app/main.py
- backend/app/api/deps.py
- backend/app/api/remediation.py
- backend/app/api/ws.py
- backend/app/services/store.py
- backend/app/services/ollama_client.py
- backend/app/services/ws_broker.py
- backend/app/services/remediation_service.py
- backend/app/services/parsers/json_parser.py
- backend/app/services/prompts.py

## Git log
- 14c1226 feat: backend foundation — models, parsers, enrichment, store, FastAPI app
- 0203120 test: 49 unit and integration tests — parsers, enrichment, store, endpoints
- bdd8aff feat: complete frontend, Docker Compose, CI, sample alerts, and README
