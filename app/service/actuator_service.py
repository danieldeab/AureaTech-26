from __future__ import annotations

from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone

from app.model.actuator import Actuator
from app.model.log_entry import LogEntry
from app.model.enums import RoleEnum
from app.repository.actuator_repository import ActuatorRepository
from app.repository.log_repository import LogRepository


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

    def __init__(self, actuator_repo: ActuatorRepository):
        self.repo = actuator_repo
        self.log_repo = LogRepository()

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

        act.state = not bool(act.state)
        self._persist_state_change(act)

        log = LogEntry.new(
            actor_id=self._normalize_actor_id(user_id),
            actor_role=user_role,
            category="ACTUATOR",
            action="TOGGLE",
            details=f"Actuator {act.id} set to {'ON' if act.state else 'OFF'} (community {act.community_id})",
        )
        self.log_repo.add(log)

        return act

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

                    log = LogEntry.new(
                        actor_id=1,
                        actor_role=RoleEnum.ADMIN,
                        category="AUTOMATION",
                        action="AUTO_TOGGLE",
                        details=(
                            f"Streetlight {'ON' if desired else 'OFF'} due to sensors "
                            f"(community {community_id}, actuator {act.id})"
                        ),
                    )
                    self.log_repo.add(log)
                    changed.append(act)

        return changed