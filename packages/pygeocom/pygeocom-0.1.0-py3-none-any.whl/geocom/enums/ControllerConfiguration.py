from enum import Enum

class ControllerConfiguration(Enum):
    MOT_POSIT = 0  # configured for relative postioning
    MOT_OCONST = 1  # configured for constant speed
    MOT_MANUPOS = 2  # configured for manual positioning default setting
    MOT_LOCK = 3  # configured as "Lock-In"-controller
    MOT_BREAK = 4  # configured as "Brake"-controller do not use 5 and 6
    MOT_TERM = 7  # terminates the controller task
