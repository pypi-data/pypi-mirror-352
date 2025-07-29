"""
Types for applications.
"""

from typing import TYPE_CHECKING, Generic, TypedDict, TypeVar

if TYPE_CHECKING:  # pragma: no cover
    from pax25.services.connection.connection import Connection
    from pax25.station import Station


S = TypeVar("S")


class BaseApplication(Generic[S]):
    """
    Raw BaseApplication that implements the minimum contract that Connection and
    the FrameRouter expect. In most cases you will not want to inherit from this, but
    from Application instead.
    """

    name: str
    settings: S
    # If this is set, will be used when constructing the default station ID beacon
    # to advertise its availability on that interface. If blank, will be omitted.
    short_name: str = ""

    def __init__(
        self, *, name: str, station: "Station", settings: S
    ):  # pragma: no cover
        """
        Initialize a copy of this application. Usually you want to store
        the settings and whether this is being invoked as a proxy object.
        """
        raise NotImplementedError

    def on_connect(self, connection: "Connection") -> None:
        """
        Called when a new connection is established. For instance, if we need to store
        any state for the user's session, we'd set it here. You might also send a
        welcome message.
        """

    def on_disconnect(self, connection: "Connection") -> None:
        """
        Called when a connection is being disconnected. Perform any cleanup here.
        """

    def on_killed(self, connection: "Connection") -> None:
        """
        Run when the connection has been killed. None of the other hooks, such as
        on_connect, or on_shutdown are guaranteed to have run before this.
        You are unlikely to need this hook, but you might for some special applications.
        """

    def on_bytes(self, connection: "Connection", bytes_received: bytes) -> None:
        """
        Called when bytes are received from a connection for this application.
        """


class BasicApplicationState(TypedDict):
    """
    State for the Application.
    """

    command: bytes


BasicStateTable = dict["Connection", BasicApplicationState]
