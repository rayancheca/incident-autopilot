import asyncio
from collections import defaultdict

from fastapi import WebSocket


class WSBroker:
    """Fan-out WebSocket broker: publish tokens to all subscribers of a report."""

    def __init__(self) -> None:
        self._subscribers: dict[str, list[WebSocket]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def subscribe(self, report_id: str, ws: WebSocket) -> None:
        async with self._lock:
            self._subscribers[report_id].append(ws)

    async def unsubscribe(self, report_id: str, ws: WebSocket) -> None:
        async with self._lock:
            subs = self._subscribers.get(report_id, [])
            if ws in subs:
                subs.remove(ws)

    async def publish(self, report_id: str, message: str) -> None:
        async with self._lock:
            targets = list(self._subscribers.get(report_id, []))

        dead: list[WebSocket] = []
        for ws in targets:
            try:
                await ws.send_text(message)
            except Exception:
                dead.append(ws)

        if dead:
            async with self._lock:
                subs = self._subscribers.get(report_id, [])
                for d in dead:
                    if d in subs:
                        subs.remove(d)

    def subscriber_count(self, report_id: str) -> int:
        return len(self._subscribers.get(report_id, []))


broker = WSBroker()
