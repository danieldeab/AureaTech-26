from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from app.model.user import User
from app.repository.sensor_repository import SensorRepository
from app.repository.log_repository import LogRepository
from app.repository.reading_repository import ReadingRepository
from app.repository.actuator_repository import ActuatorRepository
from app.service.alert_service import AlertService


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
    ):
        self.sensor_repo = sensor_repo
        self.actuator_repo = actuator_repo
        self.alert_service = alert_service
        self.log_repo = log_repo
        self.reading_repo = reading_repo

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