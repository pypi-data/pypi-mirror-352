from enum import Enum

class BAPMeasurementModes(Enum):
    BAP_NO_MEAS = 0  # no measurements, take last one
    BAP_NO_DIST = 1  # no dist. measurement, angles only
    BAP_DEF_DIST = 2  # default distance measurements, pre-defined using
    BAP_CLEAR_DIST = 5  # clear distances
    BAP_STOP_TRK = 6  # stop tracking
