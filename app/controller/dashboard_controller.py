# app/controller/dashboard_controller.py

class DashboardController:
    """
    Orchestrates dashboard-related operations.
    """

    def __init__(self, alert_service):
        self.alert_service = alert_service

    def get_alerts(self):
        """Return all alerts (no filtering yet)."""
        return self.alert_service.get_all_alerts()
