from enum import Enum

class StopMode(Enum):
    COM_TPS_STOP_SHUT_DOWN = 0  # power down Instrument
    COM_TPS_STOP_SLEEP = 1  # Sleep Mode
    COM_TPS_STOP_GUI_ONLY = 4  # close onboard gui (Viva)
