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
    DISTANCE = "DISTANCE"
    CAMERA = "CAMERA"
    SMOKE = "SMOKE"
    WIND = "WIND"

class ActuatorTypeEnum(str, Enum):
    LED = "LED"
    BUZZER = "BUZZER"
    SERVOMOTOR = "SERVOMOTOR"
