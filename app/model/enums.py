from __future__ import annotations
from enum import Enum

class RoleEnum(str, Enum):
    ADMIN = "ADMIN"
    TECHNICIAN = "TECHNICIAN"
    NEIGHBOR = "NEIGHBOR"

class SeverityEnum(str, Enum):
    INFO = "INFO"
    WARN = "WARN"
    CRIT = "CRIT"

class SensorTypeEnum(str, Enum):
    TEMPERATURE = "TEMPERATURE"
    HUMIDITY = "HUMIDITY"
    LIGHT = "LIGHT"
    MOTION = "MOTION"
    CAMERA = "CAMERA"
    SMOKE = "SMOKE"

class ActuatorTypeEnum(str, Enum):
    LED = "LED"
    BUZZER = "BUZZER"
    SERVOMOTOR = "SERVOMOTOR"
