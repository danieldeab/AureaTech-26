# app/controller/dashboard_controller.py
from app.model.enums import RoleEnum

class DashboardController:
    """
    Orchestrates dashboard-related operations.
    """

    def __init__(self, alert_service):
        self.alert_service = alert_service

    def get_alerts(self, user, selected_community_id=None):
        '''
        Decide which community's alerts to return.
        - Admin: uses selected_community_id (from session)
        - Technician / Neighbor: always their own community_id
        '''
        if user.role == RoleEnum.ADMIN:
            if selected_community_id is None:
                return []
            comm = selected_community_id
        else:
            comm = user.community_id
        
        return self.alert_service.get_alerts_for_community(comm)

