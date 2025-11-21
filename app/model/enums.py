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
