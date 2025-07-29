"""
Data classes and helpful for assembling/disassembling an AX.25 frame at large.
"""

import os
from dataclasses import dataclass
from datetime import datetime
from typing import NamedTuple, Self, cast

from pax25.ax25.address import Route
from pax25.ax25.constants import AX25_ENDIAN
from pax25.ax25.control import Info, Supervisory, Unnumbered, derive_control_class
from pax25.ax25.exceptions import DisassemblyError
from pax25.ax25.protocols import Assembler
from pax25.ax25.utils import is_command, is_response, size
from pax25.utils import normalize_line_endings


class Frame(NamedTuple):
    """
    Represents an AX.25 frame for transmission or reception
    """

    pid: int | None
    route: Route
    control: Unnumbered | Supervisory | Info
    info: bytes = b""

    def size(self) -> int:
        return sum(
            size(item or "")
            for item in (
                self.route,
                self.control,
                (self.pid is not None) and self.pid.to_bytes(1, AX25_ENDIAN),
                self.info,
            )
        )

    def __str__(self) -> str:
        """
        String representation of an AX25 frame. Emulates (mostly) how a TNC displays a
        frame, with the main exception being that we display binary data as its hex
        representation rather than sending it literally.
        """
        segments = [
            str(self.route),
            ": ",
        ]
        control_segment = str(self.control)
        if is_command(self):
            control_segment = f"<{control_segment}>"
        elif is_response(self):
            control_segment = f"<{control_segment}>".lower()
        segments.append(control_segment)
        if self.info:
            segments.extend(
                [
                    ":",
                    os.linesep,
                    normalize_line_endings(self.info).decode(
                        encoding="utf-8", errors="backslashreplace"
                    ),
                ]
            )
        return "".join(segments)

    def assemble(self) -> bytes:
        """
        Assemble this frame into a bytearray suitable for transmission.
        """
        data = bytearray()
        data.extend(self.route.assemble())
        data.extend(self.control.assemble())
        # PID could only be set if the control byte is set, per disassembly.
        if self.pid is not None:
            data.extend(bytearray(self.pid.to_bytes(1, AX25_ENDIAN)))
        data.extend(self.info)
        return bytes(data)

    @classmethod
    def disassemble(cls, data: bytes) -> Self:
        """
        Given a bytestream frame pulled from the wire, create an Frame instance.
        """
        data, route = consume_assembler(data, Route)
        control_class = derive_control_class(data)
        data, control = consume_assembler(data, control_class)
        try:
            pid = data[0]
        except IndexError as err:
            if not isinstance(control, Supervisory | Unnumbered):
                raise DisassemblyError("Protocol ID is missing.") from err
            pid = None
        data = data[1:]
        info = bytes(data)
        return cls(
            route=route,
            control=cast(Unnumbered | Info | Supervisory, control),
            pid=pid,
            info=info,
        )


@dataclass
class AxFrameTracker:
    """
    Metadata about a frame, unrelated to its protocol contents.
    """

    frame: Frame | None = None
    tx_time: datetime | None = None
    tx_count: int = 0
    # phy: PhysicalInterface, or similar, when ready.
    fault: bool = False


def consume_assembler[T: Assembler](data: bytes, cls: type[T]) -> tuple[bytes, T]:
    """
    Given a bytearray, pull what's necessary from the array to form a given disassembled
    dataclass, and return it with the remainder.
    """
    instance = cls.disassemble(data)
    return data[instance.size() :], instance
