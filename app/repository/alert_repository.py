from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Dict, Any

from app.infraestructure.db import get_db
from app.model.alert import Alert
from app.model.user_alert import UserAlert
from app.model.enums import SeverityEnum
from app.repository.interfaces.alert_repository_interface import IAlertRepository


class AlertRepository(IAlertRepository):
    """
    MariaDB-backed repository for the relational alert model.

    Source of truth:
    - alert
    - user_alert
    """

    def __init__(self):
        self.db = get_db()

    # --------------------------------------------------
    # Mapping helpers: ALERT
    # --------------------------------------------------
    def _row_to_alert(self, row: dict) -> Alert:
        raw_severity = row["severity"]
        severity = raw_severity if isinstance(raw_severity, SeverityEnum) else SeverityEnum(str(raw_severity))

        return Alert(
            id=row["alert_id"],
            community_id=row["community_id"],
            rule_alert_action_id=row["rule_alert_action_id"],
            alert_type=row["alert_type"],
            severity=severity,
            message=row["message"],
            created_at=row["created_at"],
        )

    def _alert_to_db_data(self, alert: Alert) -> dict:
        return {
            "community_id": alert.community_id,
            "rule_alert_action_id": alert.rule_alert_action_id,
            "alert_type": alert.alert_type,
            "severity": alert.severity.value if isinstance(alert.severity, SeverityEnum) else str(alert.severity),
            "message": alert.message,
        }

    # --------------------------------------------------
    # Mapping helpers: USER_ALERT
    # --------------------------------------------------
    def _row_to_user_alert(self, row: dict) -> UserAlert:
        return UserAlert(
            id=row["user_alert_id"],
            user_id=row["user_id"],
            alert_id=row["alert_id"],
            read_status=bool(row["read_status"]),
            read_at=row["read_at"],
        )

    def _user_alert_to_db_data(self, user_alert: UserAlert) -> dict:
        return {
            "user_id": user_alert.user_id,
            "alert_id": user_alert.alert_id,
            "read_status": int(bool(user_alert.read_status)),
            "read_at": user_alert.read_at,
        }

    # --------------------------------------------------
    # ALERT API
    # --------------------------------------------------
    def add_alert(self, alert: Alert) -> Alert:
        new_id = self.db.insert(
            table="alert",
            data=self._alert_to_db_data(alert),
        )
        alert.id = new_id
        return alert

    def find_alert_by_id(self, alert_id: int) -> Optional[Alert]:
        row = self.db.fetch_one(
            table="alert",
            where={"alert_id": alert_id},
        )
        return self._row_to_alert(row) if row else None

    def get_all_alerts(self) -> List[Alert]:
        rows = self.db.fetch_all(
            table="alert",
            order_by="created_at DESC",
        )
        return [self._row_to_alert(row) for row in rows]

    def get_alerts_for_community(self, community_id: int) -> List[Alert]:
        rows = self.db.fetch_all(
            table="alert",
            where={"community_id": community_id},
            order_by="created_at DESC",
        )
        return [self._row_to_alert(row) for row in rows]

    # --------------------------------------------------
    # USER_ALERT API
    # --------------------------------------------------
    def add_user_alert(self, user_alert: UserAlert) -> UserAlert:
        new_id = self.db.insert(
            table="user_alert",
            data=self._user_alert_to_db_data(user_alert),
        )
        user_alert.id = new_id
        return user_alert

    def find_user_alert_by_id(self, user_alert_id: int) -> Optional[UserAlert]:
        row = self.db.fetch_one(
            table="user_alert",
            where={"user_alert_id": user_alert_id},
        )
        return self._row_to_user_alert(row) if row else None

    def find_user_alert(self, user_id: int, alert_id: int) -> Optional[UserAlert]:
        row = self.db.fetch_one(
            table="user_alert",
            where={
                "user_id": user_id,
                "alert_id": alert_id,
            },
        )
        return self._row_to_user_alert(row) if row else None

    def mark_user_alert_read(self, user_id: int, alert_id: int) -> bool:
        existing = self.find_user_alert(user_id, alert_id)
        if not existing:
            return False

        self.db.update(
            table="user_alert",
            data={
                "read_status": 1,
                "read_at": datetime.now(),
            },
            where={
                "user_id": user_id,
                "alert_id": alert_id,
            },
        )
        return True

    def get_user_alerts(self, user_id: int) -> List[UserAlert]:
        rows = self.db.fetch_all(
            table="user_alert",
            where={"user_id": user_id},
            order_by="user_alert_id DESC",
        )
        return [self._row_to_user_alert(row) for row in rows]

    # --------------------------------------------------
    # JOINED / READ-MODEL QUERIES
    # --------------------------------------------------
    def get_alert_deliveries_for_user(self, user_id: int) -> List[Dict[str, Any]]:
        sql = """
            SELECT
                ua.user_alert_id,
                ua.user_id,
                ua.alert_id,
                ua.read_status,
                ua.read_at,
                a.community_id,
                a.rule_alert_action_id,
                a.alert_type,
                a.severity,
                a.message,
                a.created_at
            FROM user_alert ua
            INNER JOIN alert a
                ON a.alert_id = ua.alert_id
            WHERE ua.user_id = %s
            ORDER BY a.created_at DESC, ua.user_alert_id DESC
        """

        rows = self.db.execute(sql, (user_id,))

        results: List[Dict[str, Any]] = []
        for row in rows:
            raw_severity = row["severity"]
            severity = raw_severity if isinstance(raw_severity, SeverityEnum) else SeverityEnum(str(raw_severity))

            results.append(
                {
                    "user_alert_id": row["user_alert_id"],
                    "user_id": row["user_id"],
                    "alert_id": row["alert_id"],
                    "community_id": row["community_id"],
                    "rule_alert_action_id": row["rule_alert_action_id"],
                    "alert_type": row["alert_type"],
                    "severity": severity,
                    "message": row["message"],
                    "created_at": row["created_at"],
                    "read_status": bool(row["read_status"]),
                    "read_at": row["read_at"],
                }
            )

        return results

    # --------------------------------------------------
    # LEGACY COMPATIBILITY
    # --------------------------------------------------
    def find_by_id(self, alert_id: int) -> Optional[Alert]:
        return self.find_alert_by_id(alert_id)

    def get_all(self) -> List[Alert]:
        return self.get_all_alerts()

    def save(self) -> None:
        # Legacy JSON-era holdover.
        # DB-backed repositories persist immediately.
        pass