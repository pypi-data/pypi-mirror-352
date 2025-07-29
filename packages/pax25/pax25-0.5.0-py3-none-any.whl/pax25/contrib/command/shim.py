"""
Shim application. Used to shim between two connections, such as is required when
a connecting station wants to connect to a third party using us as the jump box.
"""

from pax25 import Application
from pax25.contrib.command.types import ShimSettings
from pax25.services.connection.connection import Connection


class ShimApplication(Application[ShimSettings]):
    """
    Shim application. Shuttles data over to the source application/connection.

    Unlike other applications which are instantiated station-wide, this one is
    instantiated on-need and per connection.
    """

    hidden = True

    def on_bytes(self, connection: "Connection", bytes_received: bytes) -> None:
        """
        Forward bytes to the proxy application.
        """
        self.settings.upstream_application.on_proxy_bytes(
            self.settings.proxy_connection,
            bytes_received,
        )

    def on_killed(self, connection: "Connection") -> None:
        """
        Inform the upstream application that this connection is closed.
        """
        self.settings.upstream_application.on_proxy_killed(
            self.settings.proxy_connection, connection
        )
