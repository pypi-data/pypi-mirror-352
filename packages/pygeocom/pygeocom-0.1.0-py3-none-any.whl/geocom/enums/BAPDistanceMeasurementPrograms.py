from enum import Enum

class BAPDistanceMeasurementPrograms(Enum):
    BAP_SINGLE_REF_STANDARD = 0  # IR Standard
    BAP_SINGLE_REF_FAST = 1  # IR Fast
    BAP_SINGLE_REF_VISIBLE = 2  # LO Standard
    BAP_SINGLE_RLESS_VISIBLE = 3  # RL Standard
    BAP_CONT_REF_STANDARD = 4  # IR Tracking
    BAP_CONT_REF_FAST = 5  # not supported by TPS1200
    BAP_CONT_RLESS_VISIBLE = 6  # RL Fast Tracking
    BAP_AVG_REF_STANDARD = 7  # IR Average
    BAP_AVG_REF_VISIBLE = 8  # LO Average
    BAP_AVG_RLESS_VISIBLE = 9  # RL Average
    BAP_CONT_REF_SYNCRO = 10  # IR Synchro Tracking
    BAP_SINGLE_REF_PRECISE = 11  # IR Precise (TS30, TM30)
