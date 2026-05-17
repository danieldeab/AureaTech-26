from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from math import sqrt
from typing import Any, Iterable


@dataclass(frozen=True)
class StatisticsResult:
    count: int
    min: float | None
    max: float | None
    avg: float | None
    stddev: float | None
    trend_slope: float | None
    trend_intercept: float | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class StatisticsService:
    def describe_series(self, points: Iterable[dict[str, Any]]) -> StatisticsResult:
        normalized: list[tuple[float, float]] = []
        fallback_index = 0

        for point in points:
            try:
                value = float(point["value"])
            except (KeyError, TypeError, ValueError):
                continue

            x_value = self._x_value(point.get("timestamp"))
            if x_value is None:
                x_value = float(fallback_index)
            fallback_index += 1
            normalized.append((x_value, value))

        if not normalized:
            return StatisticsResult(
                count=0,
                min=None,
                max=None,
                avg=None,
                stddev=None,
                trend_slope=None,
                trend_intercept=None,
            )

        values = [value for _, value in normalized]
        avg = sum(values) / len(values)
        variance = sum((value - avg) ** 2 for value in values) / len(values)
        slope, intercept = self._linear_regression(normalized)

        return StatisticsResult(
            count=len(values),
            min=min(values),
            max=max(values),
            avg=avg,
            stddev=sqrt(variance),
            trend_slope=slope,
            trend_intercept=intercept,
        )

    def _x_value(self, raw_timestamp: Any) -> float | None:
        if raw_timestamp is None:
            return None
        if isinstance(raw_timestamp, datetime):
            return raw_timestamp.timestamp()
        if isinstance(raw_timestamp, (int, float)):
            return float(raw_timestamp)
        if isinstance(raw_timestamp, str):
            try:
                return datetime.fromisoformat(raw_timestamp).timestamp()
            except ValueError:
                return None
        return None

    def _linear_regression(self, points: list[tuple[float, float]]) -> tuple[float | None, float | None]:
        if len(points) < 2:
            return None, None

        first_x = points[0][0]
        xs = [(x - first_x) / 3600.0 for x, _ in points]
        ys = [y for _, y in points]
        mean_x = sum(xs) / len(xs)
        mean_y = sum(ys) / len(ys)
        denominator = sum((x - mean_x) ** 2 for x in xs)
        if denominator == 0:
            return None, None

        slope = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys)) / denominator
        intercept = mean_y - slope * mean_x
        return slope, intercept
