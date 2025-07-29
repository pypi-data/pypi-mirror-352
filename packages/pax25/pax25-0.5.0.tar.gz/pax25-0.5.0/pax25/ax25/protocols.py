"""
Protocols for duck typing elements of AX.25 serialization/deserialization.

Do not include any code that should actually run here, as it won't be analyzed for
test coverage.
"""

from typing import Protocol, Self


class Assembler(Protocol):  # pragma: no cover
    """
    Protocol for logical segments of a packet. Allows for assembly/disassembly.

    Also includes __len__ for Sized compatibility because you cannot intersect
    protocols with MyPy (yet.)
    """

    def size(self) -> int:
        """
        The length of the data structure when assembled.
        """
        raise NotImplementedError("Subclasses must implement size.")

    def assemble(self) -> bytes:
        """
        Method for turning a data structure into bytes suitable for transmission.
        """

    @classmethod
    def disassemble(cls, data: bytes) -> Self:
        """
        Method for instantiating this data structure from bytes.
        """
