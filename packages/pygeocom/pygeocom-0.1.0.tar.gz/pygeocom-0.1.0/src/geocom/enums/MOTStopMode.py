from enum import Enum

class MOTStopMode(Enum):
    MOT_NORMAL = 0  # Slow down with current acceleration
    MOT_SHUTDOWN = 1  # slow down by switch off power supply
