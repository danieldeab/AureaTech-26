# app/service/alert_service.py

from typing import List, Optional

from app.model.alert import Alert
from app.repository.interfaces.alert_repository_interface import IAlertRepository


class AlertService:
    """
    Thin service layer over the alert repository.

    For now we just:
      - expose read-only access to alerts
      - leave room for future 'mark as read' / creation logic
    """

    def __init__(self, repo: IAlertRepository):
        self._repo = repo

    # ------------ READ ------------

    def get_all_alerts(self) -> List[Alert]:
        """Return all alerts stored in the repository."""
        return self._repo.get_all()

    def get_alert_by_id(self, alert_id: str) -> Optional[Alert]:
        """Return a single alert by its id, or None if not found."""
        return self._repo.find_by_id(alert_id)

    # ------------ WRITE (optional, for later) ------------

    def add_alert(self, alert: Alert) -> Alert:
        """
        Add a new alert and persist changes.
        Repository is responsible for assigning id/timestamp if missing.
        """
        self._repo.add_alert(alert)
        self._repo.save()
        return alert

    def save(self) -> None:
        """Force persisting repository state (mostly for future updates)."""
        self._repo.save()
