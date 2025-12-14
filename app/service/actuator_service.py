# app/service/actuator_service.py

from __future__ import annotations
from typing import List, Optional
from uuid import UUID, uuid4
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
    """

    def __init__(self, actuator_repo: ActuatorRepository):
        self.repo = actuator_repo
        self.log_repo = LogRepository()

    # ---------------------------------------------------------
    # Query API
    # ---------------------------------------------------------

    def get_actuators_in_community(self, community_id: int) -> List[Actuator]:
        """Return all actuators belonging to a community."""
        all_acts = self.repo.findAll()
        return [a for a in all_acts if a.community_id == community_id]

    def get_actuator(self, actuator_id: str | UUID) -> Optional[Actuator]:
        """Return a single actuator by ID."""
        return self.repo.findById(str(actuator_id))

    # ---------------------------------------------------------
    # Mutation API
    # ---------------------------------------------------------

    def toggle_actuator(self, actuator_id: str | UUID, *, user_id: UUID, user_community: int, user_role: RoleEnum, ) -> Optional[Actuator]:
        """
        Toggle actuator state if the user has access.

        Rules:
        - Admin can toggle any actuator
        - Technician can toggle only actuators in their own community
        - Neighbors cannot toggle actuators
        """
        act = self.repo.findById(str(actuator_id))
        if not act:
            return None

        # Permission logic
        # admin can toggle any actuator
        if user_role == RoleEnum.ADMIN:
            pass
        elif user_role == RoleEnum.TECHNICIAN:
            if act.community_id != user_community:
                return None # no permission
        else:
            return None # no permission
        
        # Perform toggle
        act.toggle()

        log = LogEntry.new(
            actor_id=user_id,
            actor_role=user_role,
            category="ACTUATOR",
            action="TOGGLE",
            details=f"Actuator {act.id} set to {'ON' if act.state else 'OFF'} (community {act.community_id})",
        )

        self.log_repo.add(log)
        self.log_repo.save()

        # Persist change
        self.repo.save(act)
        return act
