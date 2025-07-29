"""
Serial KISS reader.
"""

import asyncio
import logging
import os
import threading
from asyncio import Queue, QueueShutDown, Task
from collections.abc import Callable, Coroutine
from typing import TYPE_CHECKING

from serial import Serial

from pax25.ax25.frame import Frame
from pax25.interfaces.kiss.constants import (
    KISS_CMD_DATA,
    KISS_CMD_FULLDUP,
    KISS_CMD_PERSIST,
    KISS_CMD_SLOTTIME,
    KISS_CMD_TXDELAY,
    KISS_ENDIAN,
)
from pax25.interfaces.kiss.protocol import ax25_frames_from_kiss, kiss_command
from pax25.interfaces.types import (
    Interface,
    SerialSettings,
    TerminalNodeControllerSettings,
)
from pax25.utils import async_wrap, cancel_all, smart_clone

if TYPE_CHECKING:  # pragma: no cover
    from pax25.station import Station


logger = logging.getLogger(__name__)

aprint = async_wrap(print)


def default_tnc_settings() -> TerminalNodeControllerSettings:
    """
    Default settings to send to the TNC.
    """
    return {
        "port": 0,
        "tx_delay": 12,
        "persist": 63,
        "slot_time": 1,
        "full_duplex": 0,
    }


def build_serial_reader(serial: Serial) -> Callable[[], Coroutine[None, None, bytes]]:
    """
    Creates a thread and makes a reader based on it.
    """
    queue = Queue[bytes]()

    def read_loop() -> None:
        while True:
            try:
                data = serial.read(serial.in_waiting or 1)
            except TypeError:
                # Can happen if the file handle is closed abruptly.
                queue.shutdown()
                return
            if not data:
                queue.shutdown()
                return
            queue.put_nowait(data)

    thread = threading.Thread(target=read_loop)
    thread.start()

    buffer = bytearray()

    async def read_next() -> bytes:
        nonlocal buffer
        if not buffer:
            try:
                buffer.extend(await queue.get())
            except QueueShutDown:
                thread.join()
                return b""
        return buffer.pop(0).to_bytes(1, KISS_ENDIAN)

    return read_next


class SerialInterface(Interface[SerialSettings]):
    """
    Interface for KISS serial interaction.
    """

    type = "Serial"
    serial: Serial

    def __init__(self, name: str, settings: SerialSettings, station: "Station") -> None:
        """
        Initialize a serial interface.
        """
        self.name = name
        self.station = station
        self.send_queue: Queue[Frame] = Queue()
        self._settings = settings
        tnc_settings = default_tnc_settings()
        tnc_settings.update(settings.get("tnc_settings", {}))
        self._tnc_settings = tnc_settings
        self._read_loop: Task[None] | None = None
        self._write_loop: Task[None] | None = None
        self.serial = self.initialize_serial()

    def initialize_serial(self) -> Serial:
        """
        Set up the serial interface.
        """
        return Serial(
            self.path,
            baudrate=self.baud_rate,
            bytesize=8,
            parity="N",
            stopbits=1,
            rtscts=self.rtscts,
            dsrdtr=self.dsrdtr,
            xonxoff=self.xonxoff,
        )

    @property
    def settings(self) -> SerialSettings:
        """
        Return the running settings of the serial interface.
        """
        settings = smart_clone(self._settings)
        settings["tnc_settings"] = smart_clone(self._tnc_settings)
        return settings

    @property
    def sudo(self) -> bool:
        """
        Randos over the air shouldn't be superusers.
        """
        return False

    async def reload_settings(self, settings: SerialSettings) -> None:
        """
        Reload the serial interface.
        """
        await self.shutdown()
        self._settings = settings
        tnc_settings = default_tnc_settings()
        tnc_settings.update(settings.get("tnc_settings", {}))
        self._tnc_settings = tnc_settings
        self.serial = self.initialize_serial()
        self.start()

    @property
    def path(self) -> str:
        default_path = "COM1" if os.name == "nt" else "/dev/ttyUSB0"
        return self.settings.get("path", default_path)

    @property
    def baud_rate(self) -> int:
        return self.settings.get("baud_rate", 9600)

    @property
    def timeout(self) -> int:
        return self.settings.get("timeout", 1)

    @property
    def write_timeout(self) -> int:
        return self.settings.get("write_timeout", 2)

    @property
    def rtscts(self) -> bool:
        return self.settings.get("rtscts", False)

    @property
    def dsrdtr(self) -> bool:
        return self.settings.get("dsrdtr", False)

    @property
    def xonxoff(self) -> bool:
        return self.settings.get("xonxoff", False)

    @property
    def exit_kiss(self) -> bool:
        return self.settings.get("exit_kiss", False)

    @property
    def gateway(self) -> bool:
        return self.settings.get("gateway", True)

    @property
    def tx_delay(self) -> bytes:
        return self._tnc_settings["tx_delay"].to_bytes(1, KISS_ENDIAN)

    @property
    def persist(self) -> bytes:
        return self._tnc_settings["persist"].to_bytes(1, KISS_ENDIAN)

    @property
    def slot_time(self) -> bytes:
        return self._tnc_settings["slot_time"].to_bytes(1, KISS_ENDIAN)

    @property
    def full_duplex(self) -> bytes:
        return self._tnc_settings["full_duplex"].to_bytes(1, KISS_ENDIAN)

    @property
    def port(self) -> int:
        return self._tnc_settings["port"]

    @property
    def listening(self) -> bool:
        """
        Returns a bool indicating whether the interface is listening.
        """
        if not self._read_loop:
            return False
        return not self._read_loop.done()

    def start(self) -> None:
        """
        Starts the serial loops.
        """
        if self.exit_kiss:
            self.exit_kiss_mode()
            logger.info("Exit KISS mode invoked. Shutting down immediately.")
            asyncio.ensure_future(self.station.shutdown())
            return
        self._read_loop = asyncio.ensure_future(self.read_loop())
        self._write_loop = asyncio.ensure_future(self.write_loop())

    def send_settings(self) -> None:
        """
        Send the bytes down serial to configure the TNC.
        """
        # Need to write out the bytes to set up the TNC.
        self.serial.write(
            kiss_command(KISS_CMD_TXDELAY, self.port, self.tx_delay)
            + kiss_command(KISS_CMD_PERSIST, self.port, self.persist)
            + kiss_command(KISS_CMD_SLOTTIME, self.port, self.slot_time)
            + kiss_command(KISS_CMD_FULLDUP, self.port, self.full_duplex)
        )

    def exit_kiss_mode(self) -> None:
        """
        Can be used if we need to exit KISS mode, if your TNC supports it.
        """
        self.serial.write(b"\xc0\xff\xc0")

    async def read_loop(self) -> None:
        """
        Connect to the given serial object and then start reading frames.
        """
        async for frame in ax25_frames_from_kiss(build_serial_reader(self.serial)):
            self.station.frame_router.process_frame(self, frame)

    async def write_loop(self) -> None:
        """
        Write loop for serial interface.
        """
        self.send_settings()
        while frame := await self.send_queue.get():
            self.serial.write(kiss_command(KISS_CMD_DATA, self.port, frame.assemble()))

    def send_frame(self, frame: Frame) -> None:
        """
        Send frames out on KISS to the serial device.
        """
        self.send_queue.put_nowait(frame)

    async def shutdown(self) -> None:
        """
        Close the serial connection and stop listening.
        """
        self._read_loop, self._write_loop = await cancel_all(
            [self._read_loop, self._write_loop]
        )
        if self.serial.is_open:
            self.serial.flush()
            self.serial.close()
