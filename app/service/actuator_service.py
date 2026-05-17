from __future__ import annotations

from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone

from app.model.actuator import Actuator
from app.model.enums import RoleEnum
from app.repository.actuator_repository import ActuatorRepository
from app.service.audit_log_service import AuditLogService
from app.service.error_service import ErrorService


class ActuatorService:
    """
    Application-level service for actuators.

    Responsibilities:
        - Retrieve actuators (optionally filtered by community)
        - Toggle actuator state
        - Enforce community-based visibility rules
        - Persist updated actuator state
        - Log actuator mutations
    """

    def __init__(
        self,
        actuator_repo: ActuatorRepository,
        audit_log_service: AuditLogService | None = None,
        error_service: ErrorService | None = None,
    ):
        self.repo = actuator_repo
        self.audit_log_service = audit_log_service or AuditLogService()
        self.error_service = error_service or ErrorService()

    # ---------------------------------------------------------
    # Query API
    # ---------------------------------------------------------

    def get_actuators_in_community(self, community_id: int) -> List[Actuator]:
        all_acts = self.repo.findAll()
        return [a for a in all_acts if a.community_id == community_id]

    def get_all_actuators(self) -> List[Actuator]:
        return self.repo.findAll()

    def get_actuator(self, actuator_id: str | int | UUID) -> Optional[Actuator]:
        return self.repo.findById(actuator_id)

    # ---------------------------------------------------------
    # Internal helpers
    # ---------------------------------------------------------

    def _normalize_actor_id(self, value) -> int:
        try:
            return int(value)
        except Exception as exc:
            raise ValueError(f"Actuator log actor_id must be int-compatible, got {value!r}") from exc

    def _persist_state_change(self, actuator: Actuator) -> None:
        actuator.lastChangedAt = datetime.now(timezone.utc)
        self.repo.save(actuator)

    def _target_state_to_bool(self, target_state) -> bool:
        normalized = str(target_state or "").strip().upper()
        if normalized in {"1", "TRUE", "ON", "OPEN", "ACTIVE", "ENABLED"}:
            return True
        if normalized in {"0", "FALSE", "OFF", "CLOSED", "INACTIVE", "DISABLED"}:
            return False
        raise ValueError(f"Unsupported actuator target_state: {target_state!r}")

    def _state_for_rule_command(self, *, command_type: str, target_state, current_state: bool) -> str:
        command = str(command_type or "SET").strip().upper()
        target = str(target_state or "").strip().upper()
        if command in {"SET", "SET_STATE"}:
            if target in {"OPEN", "CLOSED"}:
                return target
            return "ON" if self._target_state_to_bool(target) else "OFF"
        if command == "TOGGLE":
            return "OFF" if bool(current_state) else "ON"
        if command == "BLINK":
            return "BLINKING"
        if command == "BEEP":
            return "BEEPING"
        raise ValueError(f"Unsupported actuator command_type: {command_type!r}")

    # ---------------------------------------------------------
    # Mutation API
    # ---------------------------------------------------------

    def toggle_actuator(
        self,
        actuator_id: str | int | UUID,
        *,
        user_id,
        user_community: int,
        user_role: RoleEnum,
    ) -> Optional[Actuator]:
        """
        Toggle actuator state if the user has access.

        Rules:
        - Admin can toggle any actuator
        - Technician can toggle only actuators in their own community
        - Neighbors cannot toggle actuators
        """
        act = self.repo.findById(actuator_id)
        if not act:
            return None

        if user_role == RoleEnum.ADMIN:
            pass
        elif user_role == RoleEnum.TECHNICIAN:
            if act.community_id != user_community:
                return None
        else:
            return None

        target_state = "ON" if not bool(act.state) else "OFF"
        if str(act.type).upper() == "SERVOMOTOR":
            state_reader = getattr(self.repo, "get_state", None)
            current_state = state_reader(actuator_id) if callable(state_reader) else ("OPEN" if bool(act.state) else "CLOSED")
            target_state = "CLOSED" if current_state == "OPEN" else "OPEN"
            act.state = target_state == "OPEN"
            updater = getattr(self.repo, "update_state", None)
            if callable(updater):
                updater(actuator_id, target_state)
            else:
                self._persist_state_change(act)
        else:
            act.state = target_state == "ON"
            self._persist_state_change(act)

        self.audit_log_service.log(
            actor_id=self._normalize_actor_id(user_id),
            actor_role=user_role,
            category="ACTUATOR",
            action="actuator_command",
            details=f"Actuator {act.id} set to {target_state} (community {act.community_id})",
            community_id=act.community_id,
            target_entity_type="actuator",
            target_entity_id=int(act.id),
        )

        return act

    def apply_rule_action(
        self,
        *,
        actuator_id: str | int | UUID,
        target_state,
        command_type: str = "SET_STATE",
        rule_id: int | None = None,
        community_id: int | None = None,
        actor_id: int = 1,
    ) -> Optional[Actuator]:
        act = self.repo.findById(actuator_id)
        if not act:
            return None

        desired_state = self._state_for_rule_command(
            command_type=command_type,
            target_state=target_state,
            current_state=bool(act.state),
        )
        state_reader = getattr(self.repo, "get_state", None)
        current_state = (
            state_reader(actuator_id)
            if callable(state_reader)
            else ("ON" if bool(act.state) else "OFF")
        )
        if current_state == desired_state:
            return act

        act.state = desired_state in {"ON", "OPEN", "BLINKING", "BEEPING"}
        updater = getattr(self.repo, "update_state", None)
        if callable(updater):
            updater(actuator_id, desired_state)
        else:
            self._persist_state_change(act)

        self.audit_log_service.log(
            actor_id=self._normalize_actor_id(actor_id),
            actor_role=RoleEnum.ADMIN,
            category="AUTOMATION",
            action="rule_actuator_action",
            details=(
                f"Rule {rule_id or '-'} command {command_type or 'SET'} "
                f"set actuator {act.id} to {desired_state}"
            ),
            community_id=community_id if community_id is not None else act.community_id,
            target_entity_type="actuator",
            target_entity_id=int(act.id),
        )

        return act

    def open_garage_for_plate(
        self,
        *,
        community_id: int,
        camera_event_id: int | None = None,
        actor_id: int = 1,
    ) -> Optional[Actuator]:
        finder = getattr(self.repo, "find_garage_door_by_community", None)
        if not callable(finder):
            return None

        garage = finder(int(community_id))
        if not garage:
            return None

        return self.apply_rule_action(
            actuator_id=garage.id,
            command_type="SET",
            target_state="OPEN",
            rule_id=None,
            community_id=int(community_id),
            actor_id=actor_id,
        )

    def apply_streetlight_decision(self, decision: dict) -> list[Actuator]:
        """
        Apply a streetlight automation decision to all matching actuators
        in the target community.

        Returns the list of actuators whose state actually changed.
        """
        community_id = int(decision["community_id"])
        desired = bool(decision["streetlights_on"])

        changed: list[Actuator] = []
        actuators = self.repo.findAll()

        for act in actuators:
            if act.type in {"STREETLIGHT", "LED"} and act.community_id == community_id:
                if bool(act.state) != desired:
                    act.state = desired
                    self._persist_state_change(act)

                    self.audit_log_service.log(
                        actor_id=1,
                        actor_role=RoleEnum.ADMIN,
                        category="AUTOMATION",
                        action="actuator_command",
                        details=(
                            f"Streetlight {'ON' if desired else 'OFF'} due to sensors "
                            f"(community {community_id}, actuator {act.id})"
                        ),
                        community_id=community_id,
                        target_entity_type="actuator",
                        target_entity_id=int(act.id),
                    )
                    changed.append(act)

        return changed
