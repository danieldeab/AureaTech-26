from __future__ import annotations

from queue import Empty, Queue
from typing import Any


class DashboardEventBus:
    def __init__(self, maxsize: int = 0):
        self._queue: Queue[dict[str, Any]] = Queue(maxsize=maxsize)

    def publish(self, event: dict[str, Any]) -> None:
        self._queue.put(event)

    def drain(self, limit: int | None = None) -> list[dict[str, Any]]:
        drained: list[dict[str, Any]] = []
        while limit is None or len(drained) < limit:
            try:
                drained.append(self._queue.get_nowait())
            except Empty:
                break
        return drained
