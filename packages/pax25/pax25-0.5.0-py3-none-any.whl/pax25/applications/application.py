"""
Module for the Application class, used for creating all applications.
"""

import sys
from typing import TYPE_CHECKING

from .types import BaseApplication, BasicStateTable, S

if TYPE_CHECKING:  # pragma: no cover
    from pax25.services.connection.connection import Connection
    from pax25.station import Station


class Application(BaseApplication[S]):
    """
    The Application class. You should inherit from this class to create your own custom
    pax25 apps.
    """

    def __init__(self, *, name: str, station: "Station", settings: S):
        self.name = name
        self.settings = settings
        self.connection_state_table: BasicStateTable = {}
        self.station = station
        self.setup()

    def setup(self) -> None:
        """
        Perform any initial state configuration for your application in this
        function.
        """

    def is_admin(self, connection: "Connection") -> bool:
        """
        Check if the current user is an admin.
        """
        return connection.sudo and connection.first_party.name == self.station.name

    def on_connect(self, connection: "Connection") -> None:
        """
        Called when a new connection is established.
        """
        self.connection_state_table[connection] = {"command": b""}
        self.on_startup(connection)

    def on_startup(self, connection: "Connection") -> None:
        """
        Run right after a new connection is established. You can use this function to
        do any initial state configuration and/or send a welcome message.
        """

    def on_disconnect(self, connection: "Connection") -> None:
        """
        Run when a connection is being dropped.
        """
        self.on_shutdown(connection)
        del self.connection_state_table[connection]

    def on_shutdown(self, connection: "Connection") -> None:
        """
        Called when a connection is being disconnected. Perform any cleanup here.
        """

    def on_message(self, connection: "Connection", message: str) -> None:
        """
        Called when a message is received. By default, this is called by
        on_bytes when it detects a carriage return has been sent.
        """

    def on_bytes(
        self,
        connection: "Connection",
        bytes_received: bytes,
    ) -> None:
        """
        Called when bytes are received from a connection for this application. You
        usually don't want to call this directly, but you might need to if you need
        to control how bytes sent from the client are handled.
        """
        # Not sure how often we'll receive packets with carriage returns in the
        # middle of them, but for most applications that should indicate the
        # end of one command and the start of another, so we break them up here.
        for raw_int in bytes_received:
            # Iterating over bytes produces ints.
            byte = raw_int.to_bytes(1, sys.byteorder)
            try:
                self.connection_state_table[connection]["command"]
            except KeyError:
                # Disconnected between our previous processed byte and our current one.
                return
            match byte:
                case b"\r":
                    current_message = (
                        self.connection_state_table[connection]["command"] + byte
                    ).decode("utf-8")
                    # Clear the command before sending the message in case there's an
                    # exception.
                    self.connection_state_table[connection]["command"] = b""
                    self.on_message(
                        connection,
                        # Remove trailing newline.
                        current_message[:-1],
                    )
                # Backspace
                case b"\x7f":
                    current_string = self.connection_state_table[connection][
                        "command"
                    ].decode("utf-8", errors="backslashreplace")
                    self.connection_state_table[connection]["command"] = current_string[
                        :-1
                    ].encode("utf-8")
                case _:
                    self.connection_state_table[connection]["command"] += byte
