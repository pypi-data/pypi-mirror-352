"""
Echo application. Echoes back whatever you send to it.
"""

from pax25.applications import Application
from pax25.applications.utils import send_message
from pax25.services.connection.connection import Connection
from pax25.types import EmptyDict


class Echo(Application[EmptyDict]):
    """
    Echo application.
    """

    def on_message(self, connection: "Connection", message: str) -> None:
        """
        Immediately redirect a received message back to the user.
        """
        send_message(connection, message)
