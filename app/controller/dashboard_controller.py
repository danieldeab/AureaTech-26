from app.model.enums import RoleEnum
from app.view.lists.view_faqs import FaqItem
from app.view.chats.view_chat_messages import ChatMessageItem
from app.view.lists.view_chat_thread_list import ChatThreadItem


class DashboardController:
    """
    Orchestrates dashboard-related operations.
    """

    def __init__(self, alert_service, monitoring_service, session, actuator_service, log_repo, user_repository, faq_repository, chat_repository):
        self.alert_service = alert_service
        self.monitoring_service = monitoring_service
        self.session = session
        self.actuator_service = actuator_service
        self.log_repo = log_repo
        self.user_repository = user_repository
        self.faq_repository = faq_repository
        self.chat_repository = chat_repository

    def get_kpis(self) -> dict:
        actuators = self.actuator_service.get_all_actuators()
        alerts = self.alert_service.get_all_alerts()
        logs = self.log_repo.all()

        streetlights_on = sum(1 for a in actuators if a.type in {"STREETLIGHT", "LED"} and a.state is True)
        streetlights_total = sum(1 for a in actuators if a.type in {"STREETLIGHT", "LED"})

        automation_logs = [
            l for l in logs if (l.get("metadata", {}) or {}).get("category") == "AUTOMATION"
        ]

        last_log_ts = max((l.get("ts", 0) for l in logs), default=None)

        return {
            "streetlights_on": streetlights_on,
            "streetlights_total": streetlights_total,
            "active_alerts": len(alerts),
            "automation_events": len(automation_logs),
            "last_event": last_log_ts,
        }

    def get_alerts(self, user, selected_community_id=None):
        if user.role == RoleEnum.ADMIN:
            if selected_community_id is None:
                return []
            comm = selected_community_id
        else:
            comm = user.community_id

        decision = self.monitoring_service.evaluate_streetlights_for_community(comm)

        if decision is not None:
            changed = self.actuator_service.apply_streetlight_decision(decision)
            if changed and decision.get("streetlights_on"):
                self.alert_service.apply_streetlight_decision(decision)

        return self.alert_service.get_alerts_for_community(comm)

    def get_faqs_for_community(self, community_id: str):
        rows = self.faq_repository.find_by_community_id(community_id)
        return [
            FaqItem(
                id=r["id"],
                question=r["question"],
                answer=r["answer"],
            )
            for r in rows
        ]

    def get_chat_threads_for_technician(self, technician_id: str):
        rows = self.chat_repository.get_threads_for_technician(technician_id)
        return [
            ChatThreadItem(
                chat_id=r["id"],
                title=r["title"],
                neighbor_name=r.get("neighbor_name", "Unknown neighbor"),
                status=r["status"],
                last_message_preview="Open chat to see latest message",
                last_updated=r.get("resolved_at") or r.get("created_at", ""),
            )
            for r in rows
        ]

    def get_chat_by_id(self, chat_id: str):
        return self.chat_repository.get_chat_by_id(chat_id)

    def get_chat_messages(self, chat_id: str):
        rows = self.chat_repository.get_messages(chat_id)
        return [
            ChatMessageItem(
                sender_name=r["sender_role"].capitalize(),
                sender_role=r["sender_role"],
                text=r["text"],
                timestamp=r["timestamp"],
            )
            for r in rows
        ]