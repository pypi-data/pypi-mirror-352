from enum import Enum

class ShutDownMechanismen(Enum):
    AUTO_POWER_DISABLED = 0  # instrument remains on
    AUTO_POWER_OFF = 2  # turns off mechanism
