from enum import Enum

class BAPPrismenType(Enum):
    BAP_PRISM_ROUND = 0  # Leica Circular Prism
    BAP_PRISM_MINI = 1  # Leica Mini Prism
    BAP_PRISM_TAPE = 2  # Leica Reflector Tape
    BAP_PRISM_360 = 3  # Leica 360º Prism
    BAP_PRISM_USER1 = 4  # not supported by TPS1200
    BAP_PRISM_USER2 = 5  # not supported by TPS1200
    BAP_PRISM_USER3 = 6  # not supported by TPS1200
    BAP_PRISM_360_MINI = 7  # Leica Mini 360º Prism
    BAP_PRISM_MINI_ZERO = 8  # Leica Mini Zero Prism
    BAP_PRISM_USER = 9  # User Defined Prism
    BAP_PRISM_NDS_TAPE = 10  # Leica HDS Target
    BAP_PRISM_GRZ121_ROUND = 11  # GRZ121 360° prism for Machine Guidance
    BAP_PRISM_MA_MPR122 = 12  # MPR122 360° prism for Machine Guidance
