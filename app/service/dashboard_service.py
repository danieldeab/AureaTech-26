from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from app.model.user import User
from app.repository.sensor_repository import SensorRepository
from app.repository.log_repository import LogRepository
from app.repository.reading_repository import ReadingRepository
from app.repository.actuator_repository import ActuatorRepository
from app.repository.error_repository import ErrorRepository
from app.infraestructure.db import get_db
from app.service.alert_service import AlertService
from app.service.statistics_service import StatisticsService


# -----------------------------------------------------------------------------
# DATA TRANSFER OBJECT
# -----------------------------------------------------------------------------

@dataclass
class DashboardDTO:
    user_info: Dict[str, Any]
    available_communities: List[int]
    sensors_summary: Dict[str, Any]
    actuators_summary: Dict[str, Any]
    alerts_summary: Dict[str, Any]
    recent_logs: List[Dict[str, Any]]
    statistics: Dict[str, Any]

    def to_dict(self):
        return asdict(self)


# -----------------------------------------------------------------------------
# LOG ENTRY PRESENTATION OBJECT
# -----------------------------------------------------------------------------

@dataclass
class LogEntryDTO:
    id: str
    ts: int
    event_type: str
    user_id: Optional[str]
    description: str
    metadata: Dict[str, Any]

    def __post_init__(self):
        self.timestamp_iso = datetime.fromtimestamp(self.ts).isoformat()

    def to_dict(self):
        return {
            "id": self.id,
            "ts": self.ts,
            "timestamp": self.timestamp_iso,
            "event_type": self.event_type,
            "user_id": self.user_id,
            "description": self.description,
            "metadata": self.metadata,
        }


# -----------------------------------------------------------------------------
# INTERNAL HELPERS
# -----------------------------------------------------------------------------

def _count_recent_readings(
    reading_repo: ReadingRepository,
    sensor_ids: List[int],
    hours: int = 24,
) -> int:
    cutoff = datetime.now() - timedelta(hours=hours)
    sensor_id_set = {str(x) for x in sensor_ids}
    count = 0

    for r in reading_repo.get_all():
        try:
            if str(r.sensor_id) in sensor_id_set and r.timestamp >= cutoff:
                count += 1
        except Exception:
            continue

    return count


# -----------------------------------------------------------------------------
# MAIN SERVICE CLASS
# -----------------------------------------------------------------------------

class DashboardService:
    """
    Provides aggregated dashboard data for the app.
    Uses AlertService for user-facing alert summaries because alerts are now
    relationally split into Alert + UserAlert.
    """

    def __init__(
        self,
        sensor_repo: SensorRepository,
        actuator_repo: ActuatorRepository,
        alert_service: AlertService,
        log_repo: LogRepository,
        reading_repo: ReadingRepository,
        error_repo: ErrorRepository | None = None,
        db=None,
    ):
        self.sensor_repo = sensor_repo
        self.actuator_repo = actuator_repo
        self.alert_service = alert_service
        self.log_repo = log_repo
        self.reading_repo = reading_repo
        self.error_repo = error_repo or ErrorRepository()
        self.db = db
        self.statistics_service = StatisticsService()

    def _window_start(self, window: str) -> datetime:
        normalized = str(window).lower()
        now = datetime.now()
        if normalized.endswith("h"):
            return now - timedelta(hours=int(normalized[:-1] or 24))
        if normalized.endswith("d"):
            return now - timedelta(days=int(normalized[:-1] or 7))
        return now - timedelta(hours=24)

    def get_sensor_timeseries(self, community_id: int, sensor_type: str, window: str = "24h") -> list[dict[str, Any]]:
        cutoff = self._window_start(window)
        sensors = [
            s for s in self.sensor_repo.get_all()
            if s.from_community_id == int(community_id) and str(s.type).upper() == str(sensor_type).upper()
        ]
        sensor_ids = {s.sensor_id for s in sensors if s.sensor_id is not None}
        if not sensor_ids:
            return []

        points: list[dict[str, Any]] = []
        for r in self.reading_repo.get_all():
            if r.sensor_id in sensor_ids and r.timestamp >= cutoff:
                points.append(
                    {
                        "sensor_id": int(r.sensor_id),
                        "timestamp": r.timestamp.isoformat(),
                        "value": float(r.value),
                        "unit": r.unit,
                    }
                )
        points.sort(key=lambda p: p["timestamp"])
        return points

    def get_sensors_for_community_and_type(self, community_id: int, sensor_type: str) -> list[dict[str, Any]]:
        sensors = [
            s for s in self.sensor_repo.get_all()
            if s.from_community_id == int(community_id) and str(s.type).upper() == str(sensor_type).upper()
        ]
        return [
            {
                "sensor_id": int(s.sensor_id),
                "label": f"{s.type} #{s.sensor_id} - {s.location}",
            }
            for s in sensors
            if s.sensor_id is not None
        ]

    def get_sensor_series_by_id(
        self,
        sensor_id: int,
        *,
        window: str = "7d",
        aggregate: bool = False,
        aggregate_bucket: str = "weekday",
    ) -> list[dict[str, Any]]:
        cutoff = self._window_start(window)
        rows = [r for r in self.reading_repo.get_all() if int(r.sensor_id) == int(sensor_id) and r.timestamp >= cutoff]
        rows.sort(key=lambda r: r.timestamp)
        if not aggregate:
            return [
                {
                    "timestamp": r.timestamp.isoformat(),
                    "value": float(r.value),
                    "unit": r.unit,
                }
                for r in rows
            ]

        buckets: dict[str, dict[str, Any]] = {}
        weekday_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        for r in rows:
            if aggregate_bucket == "date":
                key = r.timestamp.strftime("%Y-%m-%d")
                sort_key = key
            elif aggregate_bucket == "weekday":
                weekday = r.timestamp.weekday()
                key = weekday_names[weekday]
                sort_key = str(weekday)
            elif aggregate_bucket == "hour_2":
                hour = (r.timestamp.hour // 2) * 2
                key = f"{hour:02d}:00"
                sort_key = f"{hour:02d}"
            else:
                key = f"{r.timestamp.weekday()}-{r.timestamp.hour:02d}"
                sort_key = key
            item = buckets.get(key)
            if not item:
                item = {"sum": 0.0, "count": 0, "unit": r.unit, "sort_key": sort_key}
                buckets[key] = item
            item["sum"] += float(r.value)
            item["count"] += 1

        out = []
        for key in sorted(buckets.keys(), key=lambda k: buckets[k]["sort_key"]):
            item = buckets[key]
            out.append(
                {
                    "bucket": key,
                    "value": item["sum"] / item["count"],
                    "count": item["count"],
                    "unit": item["unit"],
                }
            )
        return out

    def get_alert_chart_data(self, community_id: int, window: str = "7d") -> dict[str, Any]:
        alerts = self.alert_service.get_alerts_for_community(int(community_id))
        scoped = list(alerts)

        by_severity: dict[str, int] = {}
        by_day: dict[str, int] = {}
        for a in scoped:
            sev = a.severity.value if hasattr(a.severity, "value") else str(a.severity)
            by_severity[sev] = by_severity.get(sev, 0) + 1
            day_key = a.created_at.strftime("%Y-%m-%d")
            by_day[day_key] = by_day.get(day_key, 0) + 1
        return {
            "by_severity": by_severity,
            "by_day": dict(sorted(by_day.items())),
            "total": len(scoped),
        }

    def get_actuator_state_summary(self, community_id: int) -> dict[str, int]:
        acts = [a for a in self.actuator_repo.findAll() if a.community_id == int(community_id)]
        on_count = sum(1 for a in acts if bool(a.state))
        off_count = sum(1 for a in acts if not bool(a.state))
        return {"on": on_count, "off": off_count, "total": len(acts)}

    def get_error_summary(self, community_id: int, window: str = "7d") -> dict[str, Any]:
        cutoff = self._window_start(window)
        errors = self.error_repo.search({"community_id": int(community_id)})
        scoped = [
            e for e in errors
            if e.get("timestamp") and datetime.fromisoformat(e["timestamp"]) >= cutoff
        ]
        by_severity: dict[str, int] = {}
        by_layer: dict[str, int] = {}
        for e in scoped:
            sev = str(e.get("severity", "UNKNOWN"))
            layer = str(e.get("source_layer", "UNKNOWN"))
            by_severity[sev] = by_severity.get(sev, 0) + 1
            by_layer[layer] = by_layer.get(layer, 0) + 1
        return {"total": len(scoped), "by_severity": by_severity, "by_layer": by_layer}

    def get_basic_statistics(self, community_id: int, sensor_type: str, window: str = "24h") -> dict[str, Any]:
        series = self.get_sensor_timeseries(community_id, sensor_type, window)
        return self.statistics_service.describe_series(series).to_dict()

    def get_sensor_statistics(self, community_id: int, sensor_type: str, window: str = "24h") -> dict[str, Any]:
        return self.get_basic_statistics(community_id, sensor_type, window)

    def get_latest_sensor_reading(self, community_id: int, sensor_type: str) -> dict[str, Any] | None:
        series = self.get_sensor_timeseries(community_id, sensor_type, "24h")
        if not series:
            return None
        last = series[-1]
        return {
            "value": last.get("value"),
            "unit": last.get("unit"),
            "timestamp": last.get("timestamp"),
        }

    def get_unknown_plate_events_summary(self, community_id: int | None = None, window: str = "7d") -> dict[str, Any]:
        db = self.db or get_db()
        cutoff = self._window_start(window)
        params: list[Any] = [cutoff]
        where = "detected_at >= %s AND (is_allowed = 0 OR is_allowed IS NULL)"
        if community_id is not None:
            where += " AND s.community_id = %s"
            params.append(int(community_id))

        sql = f"""
            SELECT
                s.community_id,
                COUNT(*) AS total
            FROM camera_event ce
            INNER JOIN sensor s ON s.sensor_id = ce.sensor_id
            WHERE {where}
            GROUP BY s.community_id
            ORDER BY s.community_id ASC
        """
        rows = db.execute(sql, tuple(params))
        by_community = {int(r["community_id"]): int(r["total"]) for r in rows}
        return {
            "total": sum(by_community.values()),
            "by_community": by_community,
        }

    def get_user_plate_history(self, user_id: int, community_id: int, limit: int = 20) -> list[dict[str, Any]]:
        db = self.db or get_db()
        sql = """
            SELECT
                ce.detected_plate,
                ce.detected_at,
                ce.is_allowed,
                ce.image_path
            FROM camera_event ce
            INNER JOIN sensor s ON s.sensor_id = ce.sensor_id
            INNER JOIN allowed_plate ap ON ap.plate = ce.detected_plate
            WHERE ap.user_id = %s
              AND ap.community_id = %s
              AND s.community_id = %s
            ORDER BY ce.detected_at DESC
            LIMIT %s
        """
        rows = db.execute(sql, (int(user_id), int(community_id), int(community_id), int(limit)))
        return [
            {
                "plate": r["detected_plate"],
                "detected_at": r["detected_at"].isoformat() if r.get("detected_at") else None,
                "is_allowed": r.get("is_allowed"),
                "image_path": r.get("image_path"),
            }
            for r in rows
        ]

    def get_dashboard_summary(
        self,
        user: User,
        effective_community_id: Optional[int],
    ) -> DashboardDTO:
        # ---------------------------------------------------------------------
        # USER INFO
        # ---------------------------------------------------------------------
        user_info = {
            "id": str(user.id),
            "name": user.name,
            "email": user.email,
            "role": user.role.value if hasattr(user.role, "value") else str(user.role),
            "community_id": user.community_id,
        }

        # ---------------------------------------------------------------------
        # SENSOR SUMMARY
        # ---------------------------------------------------------------------
        try:
            all_sensors = self.sensor_repo.get_all()

            if effective_community_id is not None:
                sensors = [s for s in all_sensors if s.from_community_id == effective_community_id]
            else:
                sensors = list(all_sensors)

            active_sensors = [s for s in sensors if getattr(s, "is_enabled", False)]
            sensor_types = sorted({s.type for s in sensors})

            recent_readings = _count_recent_readings(
                self.reading_repo,
                [s.sensor_id for s in sensors if s.sensor_id is not None],
                hours=24,
            )

            sensors_summary = {
                "total_sensors": len(sensors),
                "active_sensors": len(active_sensors),
                "recent_readings_24h": recent_readings,
                "types": sensor_types,
            }

        except Exception as e:
            sensors_summary = {
                "total_sensors": 0,
                "active_sensors": 0,
                "recent_readings_24h": 0,
                "types": [],
                "error": str(e),
            }

        # ---------------------------------------------------------------------
        # ACTUATOR SUMMARY
        # ---------------------------------------------------------------------
        try:
            all_acts = self.actuator_repo.findAll()

            if effective_community_id is not None:
                actuators = [a for a in all_acts if a.community_id == effective_community_id]
            else:
                actuators = list(all_acts)

            active = [a for a in actuators if a.state]
            inactive = [a for a in actuators if not a.state]
            types = sorted({a.type for a in actuators})

            actuators_summary = {
                "total_actuators": len(actuators),
                "active_actuators": len(active),
                "inactive_actuators": len(inactive),
                "types": types,
            }

        except Exception as e:
            actuators_summary = {
                "total_actuators": 0,
                "active_actuators": 0,
                "inactive_actuators": 0,
                "types": [],
                "error": str(e),
            }

        # ---------------------------------------------------------------------
        # ALERT SUMMARY
        # ---------------------------------------------------------------------
        try:
            deliveries = self.alert_service.get_alert_deliveries_for_user(user.id)

            unread = [d for d in deliveries if not d.get("read_status", False)]

            severity_count: Dict[str, int] = {}
            for d in deliveries:
                sev = d["severity"].value if hasattr(d["severity"], "value") else str(d["severity"])
                severity_count[sev] = severity_count.get(sev, 0) + 1

            recent_alerts = []
            for d in deliveries[:5]:
                recent_alerts.append(
                    {
                        "alert_id": d["alert_id"],
                        "user_alert_id": d["user_alert_id"],
                        "alert_type": d["alert_type"],
                        "severity": d["severity"].value if hasattr(d["severity"], "value") else str(d["severity"]),
                        "message": d["message"],
                        "created_at": d["created_at"].isoformat() if d.get("created_at") else None,
                        "read_status": d["read_status"],
                        "read_at": d["read_at"].isoformat() if d.get("read_at") else None,
                    }
                )

            alerts_summary = {
                "total": len(deliveries),
                "unread": len(unread),
                "read": len(deliveries) - len(unread),
                "by_severity": severity_count,
                "recent_alerts": recent_alerts,
            }

        except Exception as e:
            alerts_summary = {
                "total": 0,
                "unread": 0,
                "read": 0,
                "by_severity": {},
                "recent_alerts": [],
                "error": str(e),
            }

        # ---------------------------------------------------------------------
        # RECENT LOGS
        # ---------------------------------------------------------------------
        try:
            raw_logs = self.log_repo.all()
            user_logs = [l for l in raw_logs if l.get("user_id") == str(user.id)]
            user_logs.sort(key=lambda x: x.get("ts", 0), reverse=True)
            recent = user_logs[:10]

            recent_logs = [
                LogEntryDTO(
                    id=str(log.get("id")),
                    ts=int(log.get("ts", 0)),
                    event_type=log.get("event_type", ""),
                    user_id=log.get("user_id"),
                    description=log.get("description", ""),
                    metadata=log.get("metadata", {}) or {},
                ).to_dict()
                for log in recent
            ]

        except Exception as e:
            recent_logs = [{
                "id": "error",
                "ts": 0,
                "timestamp": "",
                "event_type": "error",
                "user_id": None,
                "description": str(e),
                "metadata": {},
            }]

        # ---------------------------------------------------------------------
        # AVAILABLE COMMUNITIES
        # ---------------------------------------------------------------------
        available_communities = sorted({
            s.from_community_id for s in self.sensor_repo.get_all()
            if getattr(s, "from_community_id", None) is not None
        })

        # ---------------------------------------------------------------------
        # STATISTICS
        # ---------------------------------------------------------------------
        statistics = {
            "generated_at": datetime.now().isoformat(),
            "effective_community_id": effective_community_id,
        }

        return DashboardDTO(
            user_info=user_info,
            available_communities=available_communities,
            sensors_summary=sensors_summary,
            actuators_summary=actuators_summary,
            alerts_summary=alerts_summary,
            recent_logs=recent_logs,
            statistics=statistics,
        )
