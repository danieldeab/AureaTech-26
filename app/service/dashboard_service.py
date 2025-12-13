# app/service/dashboard_service.py

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from uuid import UUID

from app.model.user import User
from app.repository.sensor_repository import SensorRepository
from app.repository.alert_repository import AlertRepository
from app.repository.log_repository import LogRepository
from app.repository.reading_repository import ReadingRepository
from app.repository.actuator_repository import ActuatorRepository


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

def _count_recent_readings(reading_repo: ReadingRepository, sensor_ids: List[UUID], hours: int = 24) -> int:
    """Counts readings in the last N hours for a list of sensors."""
    cutoff = datetime.now() - timedelta(hours=hours)
    count = 0

    sensor_id_set = {str(x) for x in sensor_ids}

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
    Fully community-aware and compatible with the new architecture.
    """

    def __init__(
        self,
        sensor_repo: SensorRepository,
        actuator_repo: ActuatorRepository,
        alert_repo: AlertRepository,
        log_repo: LogRepository,
        reading_repo: ReadingRepository
    ):
        self.sensor_repo = sensor_repo
        self.actuator_repo = actuator_repo
        self.alert_repo = alert_repo
        self.log_repo = log_repo
        self.reading_repo = reading_repo

    # -------------------------------------------------------------------------
    # PUBLIC API
    # -------------------------------------------------------------------------

    def get_dashboard_summary(self, user: User, effective_community_id: Optional[int]) -> DashboardDTO:
        """
        The controller will pass:
            - user                  (User dataclass)
            - effective_community_id (from Session.get_effective_community())

        Admins may switch communities.
        Neighbors/Technicians always use their own.
        """

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
                sensors = [s for s in all_sensors if s.community_id == effective_community_id]
            else:
                sensors = list(all_sensors)

            active_sensors = [s for s in sensors if getattr(s, "is_active", True)]

            sensor_types = sorted({s.type for s in sensors})

            recent_readings = _count_recent_readings(
                self.reading_repo,
                [s.id for s in sensors],
                hours=24
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
                "error": str(e)
            }

        # ---------------------------------------------------------------------
        # ACTUATOR SUMMARY
        # ---------------------------------------------------------------------
        try:
            all_acts = self.actuator_repo.findAll()

            # Community filtering applies if actuators have community_id
            if all(hasattr(a, "community_id") for a in all_acts):
                if effective_community_id is not None:
                    actuators = [a for a in all_acts if a.community_id == effective_community_id]
                else:
                    actuators = all_acts
            else:
                # Older dataset fallback
                actuators = all_acts

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
            all_alerts = self.alert_repo.get_all()
            uid = str(user.id)

            user_alerts = [a for a in all_alerts if str(a.target_user_id) == uid]
            unread = [a for a in user_alerts if not a.read_status]

            severity_count: Dict[str, int] = {}
            for a in user_alerts:
                sev = a.severity.value if hasattr(a.severity, "value") else str(a.severity)
                severity_count[sev] = severity_count.get(sev, 0) + 1

            alerts_summary = {
                "total": len(user_alerts),
                "unread": len(unread),
                "read": len(user_alerts) - len(unread),
                "by_severity": severity_count,
                "recent_alerts": [a.to_dict() for a in user_alerts[:5]],
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
                    id=str(l.get("id")),
                    ts=int(l.get("ts")),
                    event_type=l.get("event_type", "unknown"),
                    user_id=l.get("user_id"),
                    description=l.get("description", ""),
                    metadata=l.get("metadata", {}),
                ).to_dict()
                for l in recent
            ]

        except Exception:
            recent_logs = []

        # ---------------------------------------------------------------------
        # SYSTEM STATISTICS
        # ---------------------------------------------------------------------
        statistics = {
            "total_events": len(recent_logs),
            "last_update": datetime.now().isoformat(),
            "system_status": "operational",
        }
        
        available_communities = sorted(
            {s.community_id for s in self.sensor_repo.get_all()}
        )

        return DashboardDTO(
            user_info=user_info,
            available_communities=available_communities,
            sensors_summary=sensors_summary,
            actuators_summary=actuators_summary,
            alerts_summary=alerts_summary,
            recent_logs=recent_logs,
            statistics=statistics
        )


    # -------------------------------------------------------------------------
    # LOG FILTERING API (Equivalent to getLogs())
    # -------------------------------------------------------------------------

    def get_logs(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        General-purpose log query interface, matching the ExportService filtering logic.
        """
        logs = self.log_repo.all()
        if not filters:
            filters = {}

        def _parse(ts):
            if ts is None:
                return None
            if isinstance(ts, int):
                return ts
            try:
                return int(datetime.fromisoformat(ts).timestamp())
            except Exception:
                try:
                    return int(ts)
                except Exception:
                    return None

        start_ts = _parse(filters.get("start_date"))
        end_ts = _parse(filters.get("end_date"))
        user_id = filters.get("user_id")
        event_type = filters.get("event_type")
        limit = filters.get("limit", 100)

        result = []

        for l in logs:
            ts = l.get("ts", 0)

            if start_ts is not None and ts < start_ts:
                continue
            if end_ts is not None and ts > end_ts:
                continue
            if user_id and str(l.get("user_id")) != str(user_id):
                continue
            if event_type and l.get("event_type") != event_type:
                continue

            dto = LogEntryDTO(
                id=str(l.get("id")),
                ts=int(ts),
                event_type=l.get("event_type", "unknown"),
                user_id=l.get("user_id"),
                description=l.get("description", ""),
                metadata=l.get("metadata", {}),
            )

            result.append(dto.to_dict())

        result.sort(key=lambda x: x["ts"], reverse=True)
        return result[:limit]
