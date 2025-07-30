from enum import Enum

class ATRMode(Enum):
    AUT_POSITION = 0  # Positioning to the hz- and v-angle
    AUT_TARGET = 1  # Positioning to a target in the environment of the hz- and v-angle.
