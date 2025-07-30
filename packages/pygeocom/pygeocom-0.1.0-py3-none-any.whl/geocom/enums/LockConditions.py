from enum import Enum

class LockConditions(Enum):
    MOT_LOCKED_OUT = 0  # locked out
    MOT_LOCKED_IN = 1  # locked in
    MOT_PREDICTION = 2  # prediction mode
