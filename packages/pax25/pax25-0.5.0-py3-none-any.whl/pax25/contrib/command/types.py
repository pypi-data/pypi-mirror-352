"""
Types for the command line app.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING, TypedDict

from pax25.interfaces.loopback import LoopbackInterface
from pax25.services.connection.connection import Connection

if TYPE_CHECKING:  # pragma: no cover
    from pax25.contrib.command.command import CommandLine


class CommandSettings(TypedDict, total=False):
    """
    Settings for the command line application.
    """

    # Whether to automatically drop a user after they've disconnected from a remote.
    # Used mostly for testing, but may also work when acting as a node in the future.
    auto_quit: bool


@dataclass()
class CommandLineState:
    """
    Keeps track of the current state for connected sessions.
    """

    # Frames to be stringified and spat out at the connected user
    # when they are no longer remotely connected.
    connection: Connection | None = None
    # Used in loopbacks.
    dest_connection: Connection | None = None
    loopback_interface: LoopbackInterface | None = None


@dataclass()
class ShimSettings:
    """
    Settings for the shim application.
    """

    proxy_connection: Connection
    upstream_application: "CommandLine"
