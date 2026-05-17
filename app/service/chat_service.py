from __future__ import annotations

from typing import Optional

from app.model.enums import RoleEnum
from app.service.audit_log_service import AuditLogService
from app.service.error_service import ErrorService


class ChatService:
    def __init__(
        self,
        chat_repository,
        user_repository,
        faq_repository,
        audit_log_service: AuditLogService | None = None,
        error_service: ErrorService | None = None,
    ):
        self.chat_repository = chat_repository
        self.user_repository = user_repository
        self.faq_repository = faq_repository
        self.audit_log_service = audit_log_service or AuditLogService()
        self.error_service = error_service or ErrorService()

    def assign_technician(self, community_id: int) -> Optional[int]:
        techs = self.user_repository.find_by_community_id_and_role(community_id, RoleEnum.TECHNICIAN.value)
        if not techs:
            return None
        tech = sorted(techs, key=lambda u: int(u.id))[0]
        return int(tech.id)

    def open_from_faq(self, neighbor_id: int, community_id: int, faq_id: int, faq_question: str) -> str:
        try:
            faq = self.faq_repository.find_by_id(faq_id)
            if not faq:
                raise ValueError("FAQ not found.")
            if int(faq["community_id"]) != int(community_id):
                raise ValueError("FAQ does not belong to user's community.")

            technician_id = self.assign_technician(int(community_id))
            chat_id = self.chat_repository.create_chat(
                community_id=community_id,
                faq_id=faq_id,
                title=f"FAQ: {faq_question}",
                neighbor_id=neighbor_id,
                technician_id=technician_id,
            )
            if technician_id is None:
                self.chat_repository.update_chat_assignment_and_status(
                    chat_id,
                    status="OPEN",
                )
            else:
                self.chat_repository.update_chat_assignment_and_status(
                    chat_id,
                    assigned_user_id=technician_id,
                    status="OPEN",
                )

            self.chat_repository.add_message(
                chat_id,
                neighbor_id,
                RoleEnum.NEIGHBOR.value,
                f"Opened from FAQ: {faq_question}",
            )

            self.audit_log_service.log(
                actor_id=int(neighbor_id),
                actor_role=RoleEnum.NEIGHBOR,
                category="CHAT",
                action="chat_created",
                details=f"Chat opened from FAQ {faq_id}",
                community_id=int(community_id),
                target_entity_type="chat_thread",
                target_entity_id=int(chat_id),
            )
            return str(chat_id)
        except Exception as exc:
            self.error_service.capture_exception(
                exc,
                source_layer="SERVICE",
                user_id=int(neighbor_id),
                community_id=int(community_id),
                target_entity_type="chat_thread",
            )
            raise

    def send_message(self, thread_id: int | str, sender_id: int, sender_role: str, text: str) -> None:
        try:
            if not text or not text.strip():
                raise ValueError("Message cannot be empty.")

            thread = self.chat_repository.get_chat_by_id(thread_id)
            if not thread:
                raise ValueError("Chat thread not found.")
            if thread.get("status") == "CLOSED":
                raise ValueError("Cannot send messages to a closed chat.")

            role = self._normalize_role(sender_role)
            self._ensure_sender_can_write(thread, int(sender_id), role)

            assignment_update = {}
            if role == RoleEnum.TECHNICIAN and thread.get("assigned_user_id") is None:
                assignment_update["assigned_user_id"] = int(sender_id)

            self.chat_repository.add_message(thread_id, sender_id, role.value, text.strip())
            if thread.get("status") == "OPEN":
                assignment_update["status"] = "IN_PROGRESS"

            if assignment_update:
                self.chat_repository.update_chat_assignment_and_status(
                    thread_id,
                    **assignment_update,
                )

            self.audit_log_service.log(
                actor_id=int(sender_id),
                actor_role=role,
                category="CHAT",
                action="chat_message_sent",
                details=f"Message sent in chat {thread_id}",
                community_id=thread.get("community_id"),
                target_entity_type="chat_thread",
                target_entity_id=int(thread_id),
            )
        except Exception as exc:
            self.error_service.capture_exception(
                exc,
                source_layer="SERVICE",
                user_id=int(sender_id),
                target_entity_type="chat_thread",
                target_entity_id=int(thread_id),
            )
            raise

    def _normalize_role(self, sender_role: str) -> RoleEnum:
        normalized = str(sender_role or "").upper()
        if normalized in RoleEnum._value2member_map_:
            return RoleEnum(normalized)
        return RoleEnum.NEIGHBOR

    def _ensure_sender_can_write(self, thread: dict, sender_id: int, role: RoleEnum) -> None:
        if role == RoleEnum.NEIGHBOR:
            if int(thread.get("created_by_user_id")) != int(sender_id):
                raise PermissionError("Neighbor can only write to their own chat.")
            return

        if role == RoleEnum.TECHNICIAN:
            assigned_user_id = thread.get("assigned_user_id")
            if assigned_user_id is not None and int(assigned_user_id) != int(sender_id):
                raise PermissionError("Technician is not assigned to this chat.")

            if assigned_user_id is None and not self._technician_belongs_to_thread_community(sender_id, int(thread.get("community_id"))):
                raise PermissionError("Technician cannot claim a chat from another community.")
            return

        if role == RoleEnum.ADMIN:
            return

        raise PermissionError("User cannot write to this chat.")

    def _technician_belongs_to_thread_community(self, technician_id: int, community_id: int) -> bool:
        finder = getattr(self.user_repository, "find_by_id", None)
        if callable(finder):
            tech = finder(str(technician_id))
            if tech is not None:
                return int(getattr(tech, "community_id", -1)) == int(community_id)

        scoped_finder = getattr(self.user_repository, "find_by_community_id_and_role", None)
        if callable(scoped_finder):
            technicians = scoped_finder(int(community_id), RoleEnum.TECHNICIAN.value)
            return any(int(t.id) == int(technician_id) for t in technicians if getattr(t, "id", None) is not None)

        return False

    def resolve_thread(self, thread_id: int | str, technician_id: int) -> None:
        try:
            thread = self.chat_repository.get_chat_by_id(thread_id)
            if not thread:
                raise ValueError("Chat thread not found.")
            self._ensure_sender_can_write(thread, int(technician_id), RoleEnum.TECHNICIAN)
            if thread.get("assigned_user_id") is None:
                self.chat_repository.update_chat_assignment_and_status(
                    thread_id,
                    assigned_user_id=int(technician_id),
                )
            self.chat_repository.resolve_chat(thread_id)
            self.audit_log_service.log(
                actor_id=int(technician_id),
                actor_role=RoleEnum.TECHNICIAN,
                category="CHAT",
                action="chat_closed",
                details=f"Chat {thread_id} closed",
                community_id=thread.get("community_id"),
                target_entity_type="chat_thread",
                target_entity_id=int(thread_id),
            )
        except Exception as exc:
            self.error_service.capture_exception(
                exc,
                source_layer="SERVICE",
                user_id=int(technician_id),
                target_entity_type="chat_thread",
                target_entity_id=int(thread_id),
            )
            raise
