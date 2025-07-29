"""
Loopback interface. Used internally for allowing internal connections without any
gateways being involved.
"""

import asyncio
from asyncio import Queue, Task
from collections.abc import Callable
from typing import TYPE_CHECKING, Self

from pax25.ax25.frame import Frame
from pax25.interfaces import Interface
from pax25.interfaces.types import LoopbackSettings
from pax25.services.connection.connection import Connection
from pax25.utils import cancel_all

if TYPE_CHECKING:  # pragma: no cover
    from pax25.services.connection.connection import Connection
    from pax25.station import Station


async def read_loop(queue: Queue[Frame], handler: Callable[[Frame], None]) -> None:
    """
    Starts a read loop for a connection and its associated queue.
    """
    while frame := await queue.get():
        handler(frame)


class LoopbackInterface(Interface[LoopbackSettings]):
    type = "Loopback"

    def __init__(self, name: str, settings: LoopbackSettings, station: "Station"):
        """
        Just stash the args but don't do anything with them.
        """
        self.name = name
        self._settings = settings
        self.station = station
        self.first_party_queue: Queue[Frame] = Queue()
        self.second_party_queue: Queue[Frame] = Queue()
        self._first_party_loop: Task[None] | None = None
        self._second_party_loop: Task[None] | None = None
        self._internal_connections: tuple[Connection, Connection] | None = None

    @property
    def listening(self) -> bool:
        """
        Returns a bool indicating whether the interface is listening.
        """
        tests = [
            self._first_party_loop and not self._first_party_loop.done(),
            self._second_party_loop and not self._second_party_loop.done(),
        ]
        return any(tests)

    @property
    def sudo(self) -> bool:
        """
        Returns if this connection should be privileged.
        """
        return self._settings["connection"].sudo

    @property
    def connection(self) -> Connection:
        """
        Returns the initiating connection for this loopback.
        """
        return self._settings["connection"]

    @classmethod
    def install(
        cls, station: "Station", *, name: str, settings: LoopbackSettings
    ) -> Self:
        """
        Install and copy over references to the existing apps for the user's current
        connection.
        """
        instance = super().install(station, name=name, settings=settings)
        station.connection.application_map[instance.name] = (
            # Note: We're sharing a reference here. Theoretically, we should be updated
            # when the other interface updates.
            station.connection.application_map.get(
                settings["connection"].interface.name,
                {},
            )
        )
        return instance

    async def reload_settings(self, settings: LoopbackSettings) -> None:
        """
        Reloads the interface with revised settings.
        """
        raise NotImplementedError("Changing loopback settings is insane.")

    def register_connections(
        self, connection1: Connection, connection2: Connection
    ) -> None:
        """
        Gives the interface a reference to the internal connections so that it can
        sanely close them out on shutdown.
        """
        self._internal_connections = (connection1, connection2)

    @property
    def gateway(self) -> bool:
        """
        Loopbacks are never gateways.
        """
        return False

    def send_frame(self, frame: Frame) -> None:
        """
        Dummy send frame function. Does nothing.
        """

    def initialize_first_party(
        self,
        handle_frame: Callable[[Frame], None],
    ) -> Callable[[Frame], None]:
        """
        Builds the first party sender function, and starts its loop.
        """
        self._first_party_loop = asyncio.ensure_future(
            read_loop(self.first_party_queue, handle_frame)
        )

        def send_frame(frame: Frame) -> None:
            """
            Puts a frame from the first party on the second party's queue.
            """
            self.second_party_queue.put_nowait(frame)
            # We are bypassing the matchers when adding to the queue, but we still want
            # frames to be matchable for any novel use cases.
            self.station.frame_router.process_frame(self, frame)

        return send_frame

    def initialize_second_party(
        self,
        handle_frame: Callable[[Frame], None],
    ) -> Callable[[Frame], None]:
        """
        Builds the second party sender function, and starts its loop.
        """
        self._second_party_loop = asyncio.ensure_future(
            read_loop(self.second_party_queue, handle_frame)
        )

        def send_frame(frame: Frame) -> None:
            """
            Puts a frame from the first party on the second party's queue.
            """
            self.first_party_queue.put_nowait(frame)

        return send_frame

    def start(self) -> None:
        """
        Starts the read loop.
        """
        self.first_party_queue = Queue()
        self.second_party_queue = Queue()

    async def shutdown(self) -> None:
        """
        Dummy shut down function.
        """
        if self._internal_connections:
            for connection in self._internal_connections:
                connection.shutdown()
        await cancel_all([self._first_party_loop, self._second_party_loop])
        self.first_party_queue.shutdown()
        self.second_party_queue.shutdown()
