"""
TCP Interface for AX25 frames/connections
"""

import asyncio
import logging
from asyncio import (
    Queue,
    QueueShutDown,
    Server,
    StreamReader,
    StreamWriter,
    Task,
    wait_for,
)
from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING

from pax25.ax25.frame import Frame
from pax25.ax25.protocols import Assembler
from pax25.exceptions import ConfigurationError
from pax25.interfaces.kiss.constants import (
    KISS_CMD_DATA,
    KISS_CMD_PASSWORD,
    KISS_CMD_PASSWORD_REJECT,
    KISS_ENDIAN,
)
from pax25.interfaces.kiss.protocol import (
    APRSPasswordFrame,
    BadCredentialsFrame,
    CommandToDisassembler,
    default_frame_disassemblers,
    filter_kiss_frames,
    kiss_command,
    pull_password_frame,
)
from pax25.interfaces.types import Interface, ResolvedConnectionSpec, TCPSettings
from pax25.timer import Timer
from pax25.utils import cancel_all

if TYPE_CHECKING:  # pragma: no cover
    from pax25.station import Station

logger = logging.getLogger(__name__)

DEFAULT_PORT = 7773
DEFAULT_ADDRESS = "0.0.0.0"


@dataclass(kw_only=True, frozen=True)
class SocketHandles:
    """
    Struct for keeping track of data handles for a TCP stream.
    """

    reader: StreamReader
    writer: StreamWriter


class TCPInterface(Interface[TCPSettings]):
    """
    Interface for linking pax25 stations over TCP.
    """

    type = "TCP"

    def __init__(self, name: str, settings: TCPSettings, station: "Station") -> None:
        """
        Initialize the TCP Interface.
        """
        self.name = name
        self._settings = settings
        self.station = station
        self.connections: set[TCPConnection] = set()
        self.shutting_down = False
        self.server_task: Task[None] | None = None
        self.server: None | Server = None

    @property
    def listening(self) -> bool:
        """
        Returns true if we have any connections still operating.
        """
        return bool(
            any(
                connection
                for connection in self.connections
                if (connection.writer and not connection.writer.is_closing())
            )
            or self.server
        )

    @property
    def gateway(self) -> bool:
        """
        Returns True if this interface can be used to make outbound connections.
        """
        return self._settings.get("gateway", True)

    @property
    def sudo(self) -> bool:
        """
        Returns True if connections on this interface should be considered privileged.
        """
        return self._settings.get("sudo", False)

    async def reload_settings(self, settings: TCPSettings) -> None:
        """
        Reload TCP interface settings.
        """
        await self.shutdown()
        self._settings = settings
        self.shutting_down = False
        self.start()

    def connection_closed(self, connection: "TCPConnection") -> None:
        """
        Callback for closing a TCP connection.
        """
        if self.shutting_down:
            # Do nothing, this will be cleaned up elsewhere.
            return
        if connection.inbound or connection.force_close:
            self.connections.remove(connection)
            return
        # Need to retry.
        connection.initialize_connection(delay=5)

    def handle_client(self, reader: StreamReader, writer: StreamWriter) -> None:
        """
        Set up a connection for an inbound client.
        """
        result = writer.transport.get_extra_info("peername")
        if result is None:  # pragma: no cover
            # Something went wrong. Underlying C library should have provided this
            # metadata.
            writer.close()
        address, port = result
        self.connections.add(
            TCPConnection(
                remote_station=ResolvedConnectionSpec(
                    host=address,
                    port=port,
                ),
                reader=reader,
                writer=writer,
                close_callback=self.connection_closed,
                interface=self,
                inbound=True,
            ),
        )

    async def start_server(self) -> None:
        """
        Start listening for inbound connections.
        """
        if not self._settings.get("allow_inbound"):
            return
        try:
            self.server = await asyncio.start_server(
                self.handle_client,
                self._settings.get("listening_address", DEFAULT_ADDRESS),
                self._settings.get("listening_port", DEFAULT_PORT),
            )
            async with self.server:
                await self.server.serve_forever()
        finally:
            self.server = None

    def build_connections(self) -> None:
        """
        Create all the connections for the TCP Interface.
        """
        connections = self._settings.get("connections", [])
        if not connections:
            return
        call_sign = self._settings.get("call_sign", "")
        password = self._settings.get("password", 0)
        if not (call_sign and password):
            raise ConfigurationError(
                "TCP settings must include both call_sign and password.",
            )
        for value in self._settings.get("connections", []):
            self.connections.add(
                TCPConnection(
                    remote_station=ResolvedConnectionSpec(
                        host=value["host"], port=value["port"]
                    ),
                    close_callback=self.connection_closed,
                    credentials=APRSPasswordFrame(
                        call_sign=call_sign,
                        password=password,
                    ),
                    interface=self,
                    inbound=False,
                )
            )

    def send_frame(self, frame: Frame) -> None:
        """
        Send a frame out to all the connections which are listening.
        """
        for connection in self.connections:
            connection.send_frame(frame)

    def start(self) -> None:
        """
        Set up the loops.
        """
        self.shutting_down = False
        self.build_connections()
        self.server_task = asyncio.ensure_future(self.start_server())

    async def shutdown(self) -> None:
        """
        Close out all connections.
        """
        self.shutting_down = True
        if self.server:
            # Must explicitly close clients so read/write file handles raise exceptions.
            # Otherwise, serve_forever could get deadlocked when cancelling if we're
            # mid-read. See https://github.com/python/cpython/issues/123720
            self.server.close_clients()
            self.server.close()
        await cancel_all([self.server_task])
        for connection in self.connections:
            await connection.close()
        self.server = None


class TCPConnection:
    """
    Represents a TCP Connection to another station.
    """

    remote_station: ResolvedConnectionSpec
    send_queue: Queue[tuple[Assembler, int]]
    inbound: bool

    def __init__(
        self,
        *,
        remote_station: ResolvedConnectionSpec,
        inbound: bool,
        interface: TCPInterface,
        close_callback: Callable[["TCPConnection"], None],
        reader: StreamReader | None = None,
        writer: StreamWriter | None = None,
        credentials: APRSPasswordFrame | None = None,
    ):
        """
        Set up the TCP connection tracker.
        """
        self._connect_future: Task[None] | None = None
        self._read_loop: Task[None] | None = None
        self._write_loop: Task[None] | None = None
        self.interface = interface
        # Used to indicate that we should not retry this connection.
        self.force_close = False
        self.remote_station = remote_station
        self.close_callback = close_callback
        self.send_queue: Queue[tuple[Assembler, int]] = Queue()
        self.inbound = inbound
        self.reader = reader
        self.writer = writer
        self.credentials = credentials
        self.retry_timer = Timer(name="retry_connection")
        if inbound:
            if not (reader and writer):
                raise ValueError(
                    "Inbound connections should be initialized with read and "
                    "write streams."
                )
            self.start_loops()
        else:
            if not self.credentials:
                raise ValueError(
                    "Outbound connections should be initialized with APRS credentials."
                )
            self.initialize_connection()

    def send_frame(self, frame: Assembler, command: int = KISS_CMD_DATA) -> None:
        """
        Sends a frame to this TCP connection.
        """
        self.send_queue.put_nowait((frame, command))

    async def read_loop(self) -> None:
        """
        Read loop for serial interface.
        """
        reader = self.reader
        assert reader
        if self.inbound:
            try:
                frame = await wait_for(
                    pull_password_frame(lambda: reader.read(1)), timeout=3
                )
            except (ConnectionResetError, TimeoutError) as err:
                logger.info(
                    f"({self.interface.name}) Dropped remote "
                    f"({self.remote_station.host}, {self.remote_station.port}): "
                    f"{err.__class__.__name__}"
                )
                asyncio.ensure_future(self.close())
                return
            if not frame or not frame.valid:
                # Awaiting will kill Cancel this task before it finishes.
                self.send_frame(BadCredentialsFrame(), KISS_CMD_PASSWORD_REJECT)
                # This will close the connection as well, see the write loop.
                logger.info(
                    f"({self.interface.name}) Dropped remote "
                    f"({self.remote_station.host}, {self.remote_station.port}) "
                    f"connection: Incorrect APRS Authentication details."
                )
                self.send_queue.shutdown()
                return

        def get_disassemblers() -> CommandToDisassembler:
            return {
                **default_frame_disassemblers(),
                KISS_CMD_PASSWORD_REJECT.to_bytes(
                    1, KISS_ENDIAN
                ): BadCredentialsFrame.disassemble,
            }

        try:
            async for frame in filter_kiss_frames(
                lambda: reader.read(1),
                {Frame, BadCredentialsFrame},
                get_disassemblers=get_disassemblers,
            ):
                match frame:
                    case BadCredentialsFrame():
                        self.force_close = True
                        logger.error(
                            f"({self.interface.name}) Remote station "
                            f"{self.remote_station.host}:"
                            f"{self.remote_station.port} "
                            f"rejected credentials.",
                        )
                        asyncio.ensure_future(self.close())
                        return
                    case Frame():
                        self.interface.station.frame_router.process_frame(
                            self.interface, frame
                        )
        except ConnectionResetError:
            asyncio.ensure_future(self.close())

    async def write_loop(self) -> None:
        """
        Write loop for TCP connection.
        """
        try:
            while item := await self.send_queue.get():
                [frame, command] = item
                writer = self.writer
                assert writer
                try:
                    writer.write(kiss_command(command, 0, frame.assemble()))
                    await writer.drain()
                except OSError:
                    # Awaiting will kill Cancel this task before it finishes.
                    asyncio.ensure_future(self.close())
                    return
        except QueueShutDown:
            # Awaiting will kill Cancel this task before it finishes.
            asyncio.ensure_future(self.close())

    async def close(self) -> None:
        """
        Close the connection.
        """
        await cancel_all((self._connect_future, self._read_loop, self._write_loop))
        self.send_queue.shutdown(immediate=True)
        if self.writer:
            self.writer.close()
        self.writer, self.reader = None, None
        self.close_callback(self)

    @property
    def connecting(self) -> bool:
        """
        Return if this connection is still in progress. Returns False if connected
        or disconnected.
        """
        if self.inbound:
            # Not connecting, as this is inbound.
            return False
        return bool(self._connect_future and not self._connect_future.done())

    def initialize_connection(self, delay: int = 0) -> None:
        """
        Sets up a connection to the outbound system.
        """
        self._connect_future = asyncio.ensure_future(self._initialize_connection(delay))

    def start_loops(self) -> None:
        """
        Start up the loops for communicating back and forth.
        """
        self._read_loop = asyncio.ensure_future(self.read_loop())
        self._write_loop = asyncio.ensure_future(self.write_loop())

    async def _initialize_connection(self, delay: int = 0) -> None:
        """
        Internal process used by initialize_connection to perform its work.
        """
        assert self.credentials
        self.send_queue = Queue()
        ip = self.remote_station.host
        port = self.remote_station.port
        await asyncio.sleep(delay)
        future = asyncio.open_connection(ip, port)
        try:
            self.reader, self.writer = await asyncio.wait_for(future, timeout=5)
            logger.debug(f"({self.interface.name}) Connected to {ip}:{port}")
        except (TimeoutError, ConnectionRefusedError) as err:
            logger.error(
                f"({self.interface.name}) Failed connecting to {ip}:{port}. "
                f"{err.__class__.__name__}: {err}"
            )
            await self.close()
            return
        self.send_frame(self.credentials, KISS_CMD_PASSWORD)
        self.start_loops()
