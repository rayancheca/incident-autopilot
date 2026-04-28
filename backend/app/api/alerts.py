from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_store
from app.models.alerts import NormalizedEvent, RawAlertIn
from app.services.enrichment import enrich
from app.services.parsers import parse
from app.services.store import InMemoryStore

router = APIRouter()


@router.post("/alerts/ingest", response_model=NormalizedEvent, status_code=201)
def ingest_alert(
    payload: RawAlertIn,
    store: InMemoryStore = Depends(get_store),
) -> NormalizedEvent:
    try:
        event = parse(payload)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    enriched = enrich(event)
    store.add_alert(enriched)
    return enriched


@router.get("/alerts", response_model=list[NormalizedEvent])
def list_alerts(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    store: InMemoryStore = Depends(get_store),
) -> list[NormalizedEvent]:
    return store.list_alerts(limit=limit, offset=offset)


@router.get("/alerts/{alert_id}", response_model=NormalizedEvent)
def get_alert(
    alert_id: str,
    store: InMemoryStore = Depends(get_store),
) -> NormalizedEvent:
    event = store.get_alert(alert_id)
    if not event:
        raise HTTPException(status_code=404, detail="Alert not found")
    return event
