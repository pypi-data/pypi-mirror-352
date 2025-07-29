"""
Data structures and functions used for ingesting and exporting KISS frames.
"""

import logging
from collections.abc import AsyncIterator, Awaitable, Callable
from dataclasses import dataclass
from typing import NamedTuple, Self, TypeVar, cast

from pax25.ax25.exceptions import DisassemblyError
from pax25.ax25.frame import Frame
from pax25.ax25.protocols import Assembler
from pax25.interfaces.kiss.constants import (
    KISS_CMD_DATA,
    KISS_CMD_PASSWORD,
    KISS_ENDIAN,
    KISS_ESCAPED_FEND,
    KISS_ESCAPED_FESC,
    KISS_FEND,
    KISS_FESC,
    KISS_SHIFT_PORT,
    KISS_TFEND,
    KISS_TFESC,
)

logger = logging.getLogger(__name__)


@dataclass
class ReaderState:
    """
    Dataclass for keeping track of KISS frame ingestion.
    """

    packet: bytes = b""
    command: bytes = b""
    packet_started: bool = False
    reading: bool = False
    escaped: bool = False
    ready: bool = False


ReaderUpdater = Callable[[bytes, ReaderState], None]


class APRSPasswordFrame(NamedTuple):
    call_sign: str
    password: int

    def size(self) -> int:
        """
        Return length of password frame.
        """
        return len(self.assemble())

    def assemble(self) -> bytes:
        """
        Generate a bytestring for sending over transport.
        """
        return (
            self.call_sign.encode("utf-8") + b"\r" + str(self.password).encode("utf-8")
        )

    @property
    def valid(self) -> bool:
        """
        Returns if this frame contains a valid APRS username/password combo.
        """
        try:
            return aprs_password(self.call_sign) == self.password
        except ValueError:
            return False

    @classmethod
    def disassemble(cls, data: bytes) -> Self:
        """
        Given a bytestring, construct an APRSPasswordFrame.
        """
        segments = data.split(b"\r", maxsplit=1)
        if len(segments) != 2:
            raise DisassemblyError("Password missing.")
        [raw_call_sign, raw_password] = segments
        try:
            # Note: We don't verify a call sign is real, just that it is a valid string.
            call_sign = raw_call_sign.decode("utf-8")
        except ValueError as err:
            raise DisassemblyError("Could not decode call sign.") from err
        try:
            password = int(raw_password.decode("utf-8"))
        except ValueError as err:
            raise DisassemblyError("Password is not an integer.") from err
        return cls(call_sign=call_sign, password=password)


class EmptyFrame(NamedTuple):
    """
    Used for frames that are intended to be "empty" since the command is sufficient.
    Contains one byte of data to avoid making parsing more complicated on the KISS-side.
    """

    def size(self) -> int:
        """
        Returns the length of the frame, which is 0 because it's empty.
        """
        return 0

    def assemble(self) -> bytes:
        """
        Returns a single byte, content doesn't matter.
        """
        return b""

    @classmethod
    def disassemble(cls, data: bytes) -> Self:
        """
        Returns an instance of the frame.
        """
        return cls()


class BadCredentialsFrame(EmptyFrame):
    """
    Used when the credentials received are bogus.
    """


def requires_read(func: ReaderUpdater) -> ReaderUpdater:
    """
    Makes a function inert if the 'reading' state isn't set
    to true.
    """

    def wrapped(byte: bytes, state: ReaderState) -> None:
        if not state.reading:
            return
        func(byte, state)

    return wrapped


def handle_f_end(_byte: bytes, state: ReaderState) -> None:
    """
    Handle an f-end marker.
    """
    if not state.command:
        state.packet_started = True
        return
    state.reading = False
    state.ready = True
    return


@requires_read
def handle_tf_esc(byte: bytes, state: ReaderState) -> None:
    """
    Handle a tf escape.
    """
    if state.escaped:
        state.packet += KISS_FESC
        state.escaped = False
        return
    # Just a normal byte if we're not escaped.
    state.packet += byte


@requires_read
def handle_f_esc(_byte: bytes, state: ReaderState) -> None:
    """
    Handle an f escape.
    """
    if state.escaped:
        # This is an error. Continue.
        state.escaped = False
        return
    state.escaped = True


@requires_read
def handle_tf_end(byte: bytes, state: ReaderState) -> None:
    """
    Handle a tf_end.
    """
    if state.escaped:
        state.packet += KISS_FEND
        state.escaped = False
        return
    # Not in escaped mode, so this is the actual byte.
    state.packet += byte


@requires_read
def handle_new_char(byte: bytes, state: ReaderState) -> None:
    """
    Handle any other byte character that's part of the KISS frame.
    """
    state.packet += byte


COMMAND_FUNCS: dict[bytes, ReaderUpdater] = {
    KISS_FEND: handle_f_end,
    KISS_FESC: handle_f_esc,
    KISS_TFEND: handle_tf_end,
    KISS_TFESC: handle_tf_esc,
}


def kiss_command(command: int, port: int, value: bytes) -> bytes:
    """
    Format a kiss command for transmission.
    """
    cmd_byte = port
    cmd_byte <<= KISS_SHIFT_PORT
    cmd_byte |= command
    value = value.replace(KISS_FESC, KISS_ESCAPED_FESC)
    value = value.replace(KISS_FEND, KISS_ESCAPED_FEND)
    return KISS_FEND + cmd_byte.to_bytes(1, KISS_ENDIAN) + value + KISS_FEND


type CommandToDisassembler = dict[bytes, Callable[[bytes], Assembler]]


# If we ever need new frame command types for some reason, we can register them here.
def default_frame_disassemblers() -> CommandToDisassembler:
    """
    Returns a default set of frame disassemblers for use with reading in KISS commands.
    """
    return {KISS_CMD_DATA.to_bytes(1, KISS_ENDIAN): Frame.disassemble}


FT = TypeVar("FT", bound=Assembler)


async def filter_kiss_frames(
    read_byte: Callable[[], Awaitable[bytes]],
    frame_types: set[type[FT]],
    get_disassemblers: Callable[
        [], CommandToDisassembler
    ] = default_frame_disassemblers,
) -> AsyncIterator[FT]:
    """
    Pulls specific frame types from KISS
    """
    async for _, frame in read_from_kiss(
        read_byte, get_disassemblers=get_disassemblers
    ):
        if frame.__class__ in frame_types:
            yield cast(FT, frame)


async def ax25_frames_from_kiss(
    read_byte: Callable[[], Awaitable[bytes]],
) -> AsyncIterator[Frame]:
    """
    Generator loop for reading KISS from a source. Drops all frames except for AX.25
    frames.
    """
    async for frame in filter_kiss_frames(read_byte, frame_types={Frame}):
        yield frame


async def pull_password_frame(
    read_byte: Callable[[], Awaitable[bytes]],
) -> APRSPasswordFrame | None:
    """
    Returns the first frame received if it is a password frame, otherwise return None.
    """
    password_disassemblers = {
        KISS_CMD_PASSWORD.to_bytes(1, KISS_ENDIAN): APRSPasswordFrame.disassemble,
    }
    async for _, frame in read_from_kiss(
        read_byte,
        get_disassemblers=lambda: {
            **default_frame_disassemblers(),
            **password_disassemblers,
        },
    ):
        match frame:
            case APRSPasswordFrame():
                return frame
            case _:
                return None
    return None


async def read_from_kiss(
    read_byte: Callable[[], Awaitable[bytes]],
    get_disassemblers: Callable[
        [], CommandToDisassembler
    ] = default_frame_disassemblers,
) -> AsyncIterator[tuple[int, Assembler]]:
    """
    Generator loop for reading KISS frames from a source.
    """
    disassemblers = get_disassemblers()
    state = ReaderState()
    while byte := await read_byte():
        if state.packet_started and not state.reading and byte != KISS_FEND:
            # This is the command byte.
            state.command = byte
            state.reading = True
            continue
        modifier: ReaderUpdater = COMMAND_FUNCS.get(byte, handle_new_char)
        modifier(byte, state)
        if state.ready:
            try:
                disassembler = disassemblers.get(state.command, None)
                if disassembler is None:
                    raise DisassemblyError(
                        "No existing frame disassembler for this command."
                    )
                frame = disassembler(state.packet)
                yield int.from_bytes(state.command, KISS_ENDIAN), frame
            except Exception as err:
                logger.debug("Packet decoding error: %s", (err,))
            state = ReaderState()


def aprs_password(call_sign: str) -> int:
    """
    Generates an APRS "password" from a call sign.
    """
    call_sign = call_sign.split("-", maxsplit=1)[0].upper()[:10]
    if not call_sign:
        raise ValueError("Call sign empty.")
    call_sign_bytes = call_sign.encode("utf-8")
    base_code = 0x73E2
    index = 0
    length = len(call_sign_bytes)
    # This is trickier than it appears. Yes, we have to do it this way.
    while index < length:
        base_code ^= int(call_sign_bytes[index]) << 8
        if (index + 1) < length:
            base_code ^= call_sign_bytes[index + 1]
        index += 2
    return base_code & 0x7FFF
