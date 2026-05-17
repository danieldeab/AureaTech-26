from __future__ import annotations

from typing import Optional, Protocol, TypedDict, Any


class SensorPayload(TypedDict, total=False):
    sensor_id: int
    value: float | int | str
    unit: str
    recorded_at: str
    raw_payload: dict[str, Any]
    recipient_user_ids: list[int]
    user_id: int


class SensorPayloadProvider(Protocol):
    def __call__(self) -> Optional[SensorPayload]:
        ...
