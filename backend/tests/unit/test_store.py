import pytest

from app.models.alerts import AlertFormat, AlertSeverity, NormalizedEvent
from app.services.store import InMemoryStore
from app.utils.ids import new_id
from datetime import datetime, timezone


def _make_event(event_id: str | None = None) -> NormalizedEvent:
    return NormalizedEvent(
        id=event_id or new_id(),
        timestamp=datetime.now(tz=timezone.utc),
        source_format=AlertFormat.JSON,
        severity=AlertSeverity.HIGH,
        event_type="test",
        message="test event",
    )


def test_add_and_retrieve(store: InMemoryStore) -> None:
    event = _make_event()
    store.add_alert(event)
    retrieved = store.get_alert(event.id)
    assert retrieved is not None
    assert retrieved.id == event.id


def test_list_newest_first(store: InMemoryStore) -> None:
    ids = [new_id() for _ in range(3)]
    for i, eid in enumerate(ids):
        store.add_alert(_make_event(eid))
    listed = store.list_alerts(limit=3)
    # newest first
    assert listed[0].id == ids[-1]


def test_ring_buffer_cap() -> None:
    small_store = InMemoryStore(alert_cap=3)
    events = [_make_event() for _ in range(5)]
    for e in events:
        small_store.add_alert(e)
    assert small_store.alert_count() == 3
    # oldest two should be gone
    assert small_store.get_alert(events[0].id) is None
    assert small_store.get_alert(events[1].id) is None
    # newest three should be present
    assert small_store.get_alert(events[2].id) is not None
    assert small_store.get_alert(events[4].id) is not None


def test_pagination(store: InMemoryStore) -> None:
    for _ in range(10):
        store.add_alert(_make_event())
    page1 = store.list_alerts(limit=3, offset=0)
    page2 = store.list_alerts(limit=3, offset=3)
    assert len(page1) == 3
    assert len(page2) == 3
    assert {e.id for e in page1}.isdisjoint({e.id for e in page2})
