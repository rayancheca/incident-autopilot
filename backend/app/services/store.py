import threading
from collections import deque
from typing import Iterator

from app.models.alerts import NormalizedEvent
from app.models.remediation import RemediationItem
from app.models.reports import IRReport


class InMemoryStore:
    """Thread-safe in-memory store for alerts, reports, and remediation queue."""

    def __init__(self, alert_cap: int = 10_000) -> None:
        self._lock = threading.Lock()
        self._alert_cap = alert_cap
        self._alerts: deque[NormalizedEvent] = deque(maxlen=alert_cap)
        self._alert_index: dict[str, NormalizedEvent] = {}
        self._reports: dict[str, IRReport] = {}
        self._remediation: dict[str, RemediationItem] = {}

    # ── Alerts ────────────────────────────────────────────────────────────────

    def add_alert(self, event: NormalizedEvent) -> None:
        with self._lock:
            if len(self._alerts) == self._alert_cap:
                evicted = self._alerts[0]
                self._alert_index.pop(evicted.id, None)
            self._alerts.append(event)
            self._alert_index[event.id] = event

    def get_alert(self, alert_id: str) -> NormalizedEvent | None:
        with self._lock:
            return self._alert_index.get(alert_id)

    def list_alerts(self, limit: int = 100, offset: int = 0) -> list[NormalizedEvent]:
        with self._lock:
            items = list(reversed(self._alerts))
            return items[offset : offset + limit]

    def alert_count(self) -> int:
        with self._lock:
            return len(self._alerts)

    # ── Reports ───────────────────────────────────────────────────────────────

    def upsert_report(self, report: IRReport) -> None:
        with self._lock:
            self._reports[report.id] = report

    def get_report(self, report_id: str) -> IRReport | None:
        with self._lock:
            return self._reports.get(report_id)

    def list_reports(self) -> list[IRReport]:
        with self._lock:
            return list(self._reports.values())

    # ── Remediation queue ─────────────────────────────────────────────────────

    def add_remediation(self, item: RemediationItem) -> None:
        with self._lock:
            self._remediation[item.id] = item

    def get_remediation(self, item_id: str) -> RemediationItem | None:
        with self._lock:
            return self._remediation.get(item_id)

    def update_remediation(self, item: RemediationItem) -> None:
        with self._lock:
            self._remediation[item.id] = item

    def transition_remediation(
        self,
        item_id: str,
        from_statuses: set,
        updates: dict,
    ) -> RemediationItem | None:
        """Atomically check status and apply updates. Returns updated item or None on conflict."""
        with self._lock:
            item = self._remediation.get(item_id)
            if item is None:
                return None
            if item.approval_status not in from_statuses:
                return None
            updated = item.model_copy(update=updates)
            self._remediation[item_id] = updated
            return updated

    def list_remediation_queue(self) -> list[RemediationItem]:
        with self._lock:
            return list(self._remediation.values())

    def iter_alerts(self) -> Iterator[NormalizedEvent]:
        with self._lock:
            yield from list(self._alerts)
