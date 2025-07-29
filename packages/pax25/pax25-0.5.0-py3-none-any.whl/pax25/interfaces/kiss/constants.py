"""
Constants for the KISS protocol.
"""

import sys

KISS_FEND = b"\xc0"
KISS_FESC = b"\xdb"
KISS_TFEND = b"\xdc"
KISS_TFESC = b"\xdd"
KISS_ESCAPED_FEND = b"\xdb\xdc"
KISS_ESCAPED_FESC = b"\xdb\xdd"

KISS_MIN_FRAME_LEN = 15

KISS_CMD_DATA = 0x0  # For sending frames.
KISS_CMD_TXDELAY = 0x1  # 1 - TXDELAY (next byte is value in 10ms units (def 50))
KISS_CMD_PERSIST = 0x2  # 2 - PERSIST (next byte is p value in equation (def 63))
KISS_CMD_SLOTTIME = (
    0x3  # 3 - SLOTTIME (next byte is slot interval in 10ms units (def 10))
)
KISS_CMD_CUSTOM4 = 0x4  # 4 - UNUSED - was TXTAIL
KISS_CMD_FULLDUP = 0x5  # 5 - FULLDUPLEX (next byte > 0  FD, 0 HD (def 0))
KISS_CMD_SET_HARDWARE = 0x6  # 6 - SET-HARDWARE - user definable
KISS_CMD_PASSWORD = 0x7  # 7 - We use this for APRS password exchange over TCP, but for
# Some hardware devices over serial, it may have other uses.
KISS_CMD_PASSWORD_REJECT = 0x8  # 8 - Another user-definable value. We use this for the
# password rejected command, but it may have other uses.

KISS_MASK_PORT = 0b11110000
KISS_SHIFT_PORT = 4
KISS_MASK_CMD = 0b00001111

KISS_ENDIAN = sys.byteorder
