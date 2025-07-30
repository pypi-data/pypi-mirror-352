from enum import Enum

class StartMode(Enum):
    COM_TPS_STARTUP_LOCAL = 0  # not supported
    COM_TPS_STARTUP_REMOTE = 1  # RPC´s enabled online mode
    COM_TPS_STARTUP_GUI = 2  # start onboard gui (Viva)
