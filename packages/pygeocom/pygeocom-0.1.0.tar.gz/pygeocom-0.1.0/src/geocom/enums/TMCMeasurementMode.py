from enum import Enum

class TMCMeasurementMode(Enum):
    TMC_STOP = 0  # Stop measurement program
    TMC_DEF_DIST = 1  # Default DIST-measurement program
    TMC_CLEAR = 3  # TMC_STOP and clear data
    TMC_SIGNAL = 4  # Signal measurement (test function)
    TMC_DO_MEASURE = 6  # Restart measurement task
    TMC_RTRK_DIST = 8  # Distance-TRK measurement program
    TMC_RED_TRK_DIST = 10  # Reflectorless tracking
    TMC_FREQUENCY = 11  # Frequency measurement (test)
