from app.model.enums import RoleEnum
from app.view.lists.view_faqs import FaqItem
from app.view.chats.view_chat_messages import ChatMessageItem
from app.view.lists.view_chat_thread_list import ChatThreadItem


class DashboardController:
    """
    Orchestrates dashboard-related operations.
    """

    def __init__(self, alert_service, monitoring_service, session, actuator_service, log_repo, user_repository, faq_repository, chat_repository, chat_service=None):
        self.alert_service = alert_service
        self.monitoring_service = monitoring_service
        self.session = session
        self.actuator_service = actuator_service
        self.log_repo = log_repo
        self.user_repository = user_repository
        self.faq_repository = faq_repository
        self.chat_repository = chat_repository
        self.chat_service = chat_service

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

        return self.alert_service.get_alerts_for_community(comm)

    def get_faqs_for_community(self, community_id: str):
        rows = self.faq_repository.find_by_community_id(community_id)
        return [
            FaqItem(
                id=r["id"],
                question=r["question"],
                answer=r["answer"],
                tags=r.get("tags") or "",
            )
            for r in rows
        ]

    def get_chat_threads_for_technician(self, technician_id: str):
        rows = self.chat_repository.get_threads_for_technician(technician_id)
        return self._thread_items(rows)

    def get_chat_threads_for_neighbor(self, neighbor_id: str):
        rows = self.chat_repository.get_threads_for_neighbor(neighbor_id)
        return self._thread_items(rows)

    def _thread_items(self, rows):
        return [
            ChatThreadItem(
                chat_id=r["id"],
                title=r["title"],
                neighbor_name=r.get("neighbor_name", "Unknown neighbor"),
                status=r["status"],
                last_message_preview=r.get("last_message_preview") or "No messages yet",
                last_updated=r.get("last_message_at") or r.get("resolved_at") or r.get("created_at", ""),
            )
            for r in rows
        ]

    def get_chat_by_id(self, chat_id: str):
        return self.chat_repository.get_chat_by_id(chat_id)

    def get_chat_messages(self, chat_id: str):
        rows = self.chat_repository.get_messages(chat_id)
        return [
            ChatMessageItem(
                sender_name=r.get("sender_name") or r["sender_role"].capitalize(),
                sender_role=r["sender_role"],
                text=r["text"],
                timestamp=str(r["timestamp"]).replace("T", " ")[:19],
            )
            for r in rows
        ]

    def open_chat_from_faq(self, neighbor_id: int, community_id: int, faq_id: int, faq_question: str) -> str:
        if not self.chat_service:
            raise ValueError("Chat service is not configured.")
        return self.chat_service.open_from_faq(
            neighbor_id=neighbor_id,
            community_id=community_id,
            faq_id=faq_id,
            faq_question=faq_question,
        )

    def send_chat_message(self, chat_id: str, sender_id: int, sender_role: str, text: str) -> None:
        if not self.chat_service:
            raise ValueError("Chat service is not configured.")
        self.chat_service.send_message(
            thread_id=chat_id,
            sender_id=sender_id,
            sender_role=sender_role,
            text=text,
        )

    def resolve_chat(self, chat_id: str, technician_id: int) -> None:
        if not self.chat_service:
            raise ValueError("Chat service is not configured.")
        self.chat_service.resolve_thread(
            thread_id=chat_id,
            technician_id=technician_id,
        )
