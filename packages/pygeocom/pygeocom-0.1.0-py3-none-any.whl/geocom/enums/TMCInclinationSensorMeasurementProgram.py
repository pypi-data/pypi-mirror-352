from enum import Enum

class TMCInclinationSensorMeasurementProgram(Enum):
    TMC_MEA_INC = 0  # Use sensor (apriori sigma)
    TMC_AUTO_INC = 1  # Automatic mode (sensor/plane)
    TMC_PLANE_INC = 2  # Use plane (apriori sigma)
