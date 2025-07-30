from enum import Enum

class EDMMeasurementType(Enum):
    EDM_SIGNAL_MEASUREMENT = 1
    EDM_FREQ_MEASUREMENT = 2
    EDM_DIST_MEASUREMENT = 4
    EDM_ANY_MEASUREMENT = 8
