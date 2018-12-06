# Python's color conversion library: https://docs.python.org/3/library/colorsys.html

# ============================================================================
#  Setup logging
# ============================================================================

import logging
logging.basicConfig(level=logging.CRITICAL,
                    format='%(levelname)-9s: %(name)s : %(funcName)s() : %(message)s')
log = logging.getLogger('color_converter')
log.setLevel(logging.DEBUG)


# ============================================================================
#  ColorType enum
# ============================================================================

from enum import Enum

class ColorType(Enum):
    UINT24 = 0
    UINT32 = 1
    RGB = 2
    ARGB = 3


# ============================================================================
#  Color conversion functions
# ============================================================================

def convert_uint24(uint24, result_type=ColorType.RGB):

    result = 0

    if result_type == ColorType.RGB:
        log.info('RGB')
        result = _uint24_to_rgb(uint24)
    elif result_type == ColorType.ARGB:
        log.info('ARGB')

    return result


def _uint24_to_rgb(i):
    R = (i & 0x000000FF)
    G = (i & 0x0000FF00) >> 8
    B = (i & 0x00FF0000) >> 16

    return (R,G,B) # tuple


def _rgb_to_uint24(RGB):
    return (RGB[0]) + (RGB[1]<<8) + (RGB[2]<<16)
