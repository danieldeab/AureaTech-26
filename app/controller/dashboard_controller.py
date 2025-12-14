# app/controller/dashboard_controller.py
from app.model.enums import RoleEnum

class DashboardController:
    """
    Orchestrates dashboard-related operations.
    """

    def __init__(self, alert_service, monitoring_service, session, actuator_service, log_repo):
        self.alert_service = alert_service
        self.monitoring_service = monitoring_service
        self.session = session
        self.actuator_service = actuator_service
        self.log_repo = log_repo


    # --------------------------------------
    # HELPER METHODS
    # --------------------------------------

    def get_kpis(self) -> dict:
        actuators = self.actuator_service.get_all_actuators()
        alerts = self.alert_service.get_all_alerts()
        logs = self.log_repo.all()

        streetlights_on = sum(1 for a in actuators if a.type == "STREETLIGHT" and a.state == True)
        streetlights_total = sum(1 for a in actuators if a.type == "STREETLIGHT")

        automation_logs = [
            l for l in logs if l.get("category") == "AUTOMATION"
        ]

        last_log_ts = max(
            (l.get("timestamp") for l in logs),
            default=None
        )


        return {
            "streetlights_on": streetlights_on,
            "streetlights_total": streetlights_total,
            "active_alerts": len(alerts),
            "automation_events": len(automation_logs),
            "last_event": last_log_ts,
        }

    def get_alerts(self, user, selected_community_id=None):
        '''
        Decide which community's alerts to return.
        - Admin: uses selected_community_id (from session)
        - Technician / Neighbor: always their own community_id
        '''
        
        # First, evaluate automations for the current community
        decision = self.monitoring_service.evaluate_streetlights_for_community(
            self.session.current_community_id
        )

        if decision is not None:
            self.alert_service.apply_streetlight_decision(decision)

        
        '''
        In the first-term implementation, automation is evaluated when 
        the dashboard is accessed, simulating periodic system checks 
        without introducing real-time infrastructure.
        '''

        if user.role == RoleEnum.ADMIN:
            if selected_community_id is None:
                return []
            comm = selected_community_id
        else:
            comm = user.community_id
        
        return self.alert_service.get_alerts_for_community(comm)

