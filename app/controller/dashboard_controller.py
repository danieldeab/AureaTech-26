# app/controller/dashboard_controller.py
from app.model.enums import RoleEnum

class DashboardController:
    """
    Orchestrates dashboard-related operations.
    """

    def __init__(self, alert_service):
        self.alert_service = alert_service

    def get_alerts(self, user):
        if user.role == RoleEnum.ADMIN:
            comm = user.selected_community_id
            return self.alert_service.get_alerts_for_community(comm)
        elif user.role == RoleEnum.TECHNICIAN:
            return self.alert_service.get_alerts_for_technician(user.community_id)
        else:
            return self.alert_service.get_alerts_for_community(user.community_id)

