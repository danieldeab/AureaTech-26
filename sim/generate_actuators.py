from uuid import uuid4
from datetime import datetime, timezone

from app.model.actuator import Actuator
from app.repository.actuator_repository import ActuatorRepository


def generate_actuators() -> None:
    '''
    Generates simulated actuators for the base system.

    Base (mandatory):
    - Streetlight / Lighting actuators (ON/OFF)

    Optional (extension, not required):
    - Fire alarm
    - Garage door

    All actuators are simulated and persisted in JSON.
    '''

    repo = ActuatorRepository()

    now = datetime.now(timezone.utc)

    actuators = [
        # -------------------------
        # BASE SYSTEM (MANDATORY)
        # -------------------------
        Actuator(
            id=uuid4(),
            name="Streetlight 1A",
            type="LED",
            state=False,
            community_id=1,
            lastChangedAt=now,
        ),
        Actuator(
            id=uuid4(),
            name="Streetlight 1B",
            type="LED",
            state=False,
            community_id=1,
            lastChangedAt=now,
        ),
        Actuator(
            id=uuid4(),
            name="Streetlight 2A",
            type="LED",
            state=False,
            community_id=2,
            lastChangedAt=now,
        ),
        Actuator(
            id=uuid4(),
            name="Streetlight 2B",
            type="LED",
            state=False,
            community_id=2,
            lastChangedAt=now,
        ),

        # -------------------------
        # OPTIONAL / EXTENSIONS
        # -------------------------
        Actuator(
            id=uuid4(),
            name="Fire Alarm 1A",
            type="BUZZER",
            state=False,
            community_id=1,
            lastChangedAt=now,
        ),
        Actuator(
            id=uuid4(),
            name="Garage Door 2A",
            type="SERVOMOTOR",
            state=False,
            community_id=2,
            lastChangedAt=now,
        ),
    ]

    for act in actuators:
        repo.add(act)

    print(f"[OK] Generated {len(actuators)} actuators.")


if __name__ == "__main__":
    generate_actuators()
