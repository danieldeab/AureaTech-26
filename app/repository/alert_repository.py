# app/repository/alert_repository.py
import json
import os
import uuid
from datetime import datetime

from app.model.alert import Alert
from app.repository.interfaces.alert_repository_interface import IAlertRepository

# Resolve data path relative to the package root (project-level data dir)
_PACKAGE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_DIR = os.path.join(_PACKAGE_ROOT, "data")
ALERTS_PATH = os.path.join(DATA_DIR, "alerts.json")


class AlertRepository(IAlertRepository):

    def __init__(self, path=ALERTS_PATH):
        self.path = path
        self.alerts = self._load()

    def _load(self):
        if not os.path.exists(self.path):
            return []

        with open(self.path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Accepts: { "alertas": [...] } or [ ... ]
        if isinstance(data, dict) and "alertas" in data:
            data = data["alertas"]

        cleaned = []
        for a in data:
            cleaned.append(Alert(**a))

        return cleaned

    def add_alert(self, alert: Alert) -> None:
        if not getattr(alert, "id", None):
            alert.id = str(uuid.uuid4())

        alert.timestamp = datetime.now().isoformat()
        self.alerts.append(alert)

    def find_by_id(self, alert_id: str):
        for a in self.alerts:
            if a.id == alert_id:
                return a
        return None

    def get_all(self):
        return self.alerts

    def save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)

        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(
                [a.__dict__ for a in self.alerts],
                f,
                ensure_ascii=False,
                indent=4,
            )
