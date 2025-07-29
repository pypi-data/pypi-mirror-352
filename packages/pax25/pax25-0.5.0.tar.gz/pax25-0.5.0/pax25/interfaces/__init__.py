"""
This module contains the different interfaces which are included with pax25.
"""

from .dummy import DummyInterface
from .file import FileInterface
from .serial import SerialInterface
from .tcp import TCPInterface
from .types import Interface

INTERFACE_TYPES = {
    "file": FileInterface,
    "dummy": DummyInterface,
    "serial": SerialInterface,
    "tcp": TCPInterface,
}

__all__ = [
    "FileInterface",
    "Interface",
    "SerialInterface",
    "DummyInterface",
    "TCPInterface",
    "INTERFACE_TYPES",
]
