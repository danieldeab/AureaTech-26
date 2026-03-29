# app/repository/alert_repository.py
import json
import os
import uuid
from typing import List, Optional
from datetime import datetime, timezone

from app.model.alert import Alert
from app.repository.interfaces.alert_repository_interface import IAlertRepository

# Resolve data path relative to the package root (project-level data dir)
_PACKAGE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_DIR = os.path.join(_PACKAGE_ROOT, "data")
ALERTS_PATH = os.path.join(DATA_DIR, "alerts.json")

from app.model.reading import Reading
from app.repository.interfaces.reading_repository_interface import IReadingRepository
class AlertRepository(IAlertRepository):

    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        self.alerts: List[Alert] = self._load()

    """"
    def _load(self) -> List[Alert]:
        if not os.path.exists(ALERTS_PATH):
            return []

        try:
            with open(ALERTS_PATH, "r", encoding="utf-8") as f:
                raw = json.load(f)
        except json.JSONDecodeError:
            raw = []

        alerts: List[Alert] = []
        for a in raw:
            try:
                alerts.append(Alert.from_dict(a))
            except Exception as e:
                print(f"[AlertRepository] Error loading alert: {e}\nAlert data: {a}")

        return alerts
    """""
    """""
    def _write_file(self):
        json_data = [a.to_dict() for a in self.alerts]
        with open(ALERTS_PATH, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
    """""
def add_alert(self, alert: Alert) -> None:
    # if not getattr(alert, "id", None):
    #     alert.id = str(uuid.uuid4())
    # if not getattr(alert, "timestamp", None):
    #     alert.timestamp = datetime.now(timezone.utc)
    # elif isinstance(alert.timestamp, str):
    #     alert.timestamp = datetime.fromisoformat(alert.timestamp)
    # self.alerts.append(alert)
    # self._write_file()

    """
    En la tabla alerts el orden sería:
    [
        community_id,
        rule_alert_action_id,
        alert_type,
        severity,
        message
    ]
    alert_id y created_at se generan solos en la BD
    """

    data = [
        alert.community_id,
        alert.rule_alert_action_id,
        alert.alert_type,
        alert.severity,
        alert.message
    ]

    self.db.add("alerts", data)

def find_by_id(self, alert_id: str) -> Optional[Alert]:
    # for a in self.alerts:
    #     if str(a.id) == str(alert_id):
    #         return a
    # return None

    response = self.db.select("alerts", "alert_id", alert_id)

    if not response:
        return None

    row = response[0]
    return Alert(
        row[0],  # alert_id
        row[1],  # community_id
        row[2],  # rule_alert_action_id
        row[3],  # alert_type
        row[4],  # severity
        row[5],  # message
        row[6]   # created_at
    )

def get_all(self) -> List[Alert]:
    # return list(self.alerts)

    response = self.db.select_all("alerts")

    alerts = []
    for row in response:
        alert = Alert(
            row[0],  # alert_id
            row[1],  # community_id
            row[2],  # rule_alert_action_id
            row[3],  # alert_type
            row[4],  # severity
            row[5],  # message
            row[6]   # created_at
        )
        alerts.append(alert)

    return alerts

def save(self) -> None:
    # self._write_file()
    pass
        
