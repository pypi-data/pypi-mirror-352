"""Station class. Defines the station parameters."""

import asyncio
import logging
from asyncio import Future, Task
from typing import Any, Literal

from pax25.ax25.address import Address
from pax25.exceptions import ConfigurationError
from pax25.frame_router import FrameRouter
from pax25.interfaces import Interface
from pax25.services.beacon import BeaconService
from pax25.services.connection.service import ConnectionService
from pax25.services.digipeater import Digipeater
from pax25.services.monitor import Monitor
from pax25.types import StationConfig
from pax25.utils import cancel, cancel_all, first, maybe_update, smart_clone

logger = logging.getLogger(__name__)


class Station:
    """
    The main station class for Pax25. This class is intended to manage a physical
    station's digital affairs.
    """

    def __init__(self, *, config: StationConfig):
        # Timers may get cancelled and the station may shut down before they would
        # be cleaned up normally. We track these tasks so if we shut down while any
        # are still active, we can reap them manually.
        self._active_future: Future[None] | None = None
        address = Address.from_string(config["name"])
        assert str(address) == config["name"], (
            "Station names must be all caps and have no SSID suffix."
        )
        self._settings = config
        self.interfaces: dict[str, Interface[Any]] = {}
        self.frame_router = FrameRouter(station=self)
        self.digipeater = Digipeater(station=self, settings=config.get("digipeater"))
        self.connection = ConnectionService(
            station=self,
            settings=config.get("connection"),
        )
        self.monitor = Monitor(station=self, settings=config.get("monitor"))
        self.beacon = BeaconService(station=self, settings=config.get("beacon"))
        self.clear_subsettings()
        self._cleanup_lock: Future[None] | None = None
        self._cleanup_task: Future[None] | None = None
        self._to_clean: list[Task[None]] = []
        self.closing = False

    @property
    def running(self) -> bool:
        """
        Returns if the station is currently running.
        """
        if self._active_future is None:
            return False
        return not self._active_future.done()

    @property
    def settings(self) -> StationConfig:
        """
        Returns the current configuration of the station.
        """
        settings = smart_clone(self._settings)
        # These are all smart cloned.
        settings["monitor"] = self.monitor.settings
        settings["beacon"] = self.beacon.settings
        settings["digipeater"] = self.digipeater.settings
        settings["connection"] = self.connection.settings
        return settings

    @property
    def name(self) -> str:
        return self._settings["name"].upper()

    def clear_subsettings(self) -> None:
        """
        Settings are set on the station object, but the authoritative location of the
        settings for each service are on that service. Remove these keys so that if we
        erroneously rely on the internal representation of the settings for a service,
        we raise instead of using data which may be out of date, which could cause a
        very subtle bug.
        """
        keys: tuple[Literal["monitor", "beacon", "digipeater", "connection"], ...] = (
            "monitor",
            "beacon",
            "digipeater",
            "connection",
        )
        for key in keys:
            if key in self._settings:
                del self._settings[key]

    def collect_task(self, task: Task[None]) -> None:
        """
        Tasks which are 'fire and forget' can be sent here to be cleaned up later
        as needed. This prevents the garbage collector from freaking out and sending
        tracebacks as tasks from functions like those in the timer module get reaped.
        """
        self._to_clean.append(task)

    async def reload_settings(self, settings: StationConfig) -> None:
        """
        Reloads station configuration, and all components involved.
        """
        address = Address.from_string(settings["name"])
        assert str(address) == settings["name"], (
            "Station names must be all caps and have no SSID suffix."
        )
        self._settings = settings
        digipeater_settings = maybe_update(
            self.digipeater.settings,
            settings.get("digipeater"),
        )
        monitor_settings = maybe_update(
            self.monitor.settings,
            settings.get("monitor"),
        )
        beacon_settings = maybe_update(
            self.beacon.settings,
            settings.get("beacon"),
        )
        connection_settings = maybe_update(
            self.connection.settings,
            settings.get("connection"),
        )
        self.clear_subsettings()
        await asyncio.gather(
            self.digipeater.reload_settings(digipeater_settings),
            self.monitor.reload_settings(monitor_settings),
            self.beacon.reload_settings(beacon_settings),
            self.connection.reload_settings(connection_settings),
        )

    async def finished(self) -> None:
        """
        Await this to wait until the server is closed down programmatically.
        """
        if self._active_future is None:
            raise RuntimeError(
                "Station has not run. We cannot wait for it to finish if "
                "it never began!"
            )
        await self._active_future

    async def _cleanup_loop(self) -> None:
        """
        Cleanup loop.
        """
        sleep = Task(asyncio.sleep(0.500))
        while self._cleanup_lock:
            await first(sleep, self._cleanup_lock)
            self._to_clean = [task for task in self._to_clean if not task.done()]
        await cancel_all(self._to_clean)
        await cancel(sleep)
        self._cleanup_task = None

    def run(self) -> Future[None]:
        """
        Starts the station. Tasks will not begin unless/until the asyncio loop is
        running.
        """
        if self._active_future and not self._active_future.done():
            raise RuntimeError("Station is already running!")
        self.bring_up_interfaces()
        self.beacon.run()
        self._cleanup_lock = Future()
        self._cleanup_task = asyncio.ensure_future(self._cleanup_loop())
        self._active_future = Future()
        return self._active_future

    async def start(self) -> None:
        """
        Starts the station and awaits its completion. Useful for projects that just
        have one station and want to use it as the event loop entry point, which is
        most projects, or anything which might need to wait on an entire station's
        lifecycle.
        """
        await self.run()

    def bring_up_interfaces(self) -> None:
        """
        Attempts to bring up all interfaces and queue them into the event loop.
        """
        for interface in self.interfaces.values():
            interface.start()

    def add_interface(self, name: str, interface: Interface) -> None:
        """
        Adds an interface to the station.
        """
        if interface.station != self:
            raise ConfigurationError(
                "You cannot assign an interface to an irrelevant station."
            )
        if not name:
            raise ConfigurationError("Interface name may not be blank.")
        if name.split() != [name]:
            raise ConfigurationError(
                f"Interface names may not have spaces. Got: {repr(name)}",
            )
        try:
            name.encode("ascii")
        except ValueError as err:
            raise ConfigurationError(
                f"Interface names MUST be ASCII. Got: {repr(name)}",
            ) from err
        if name in self.interfaces:
            raise ConfigurationError(f"Interface {repr(name)} already exists!")
        self.interfaces[name] = interface
        self.monitor.refresh_ports_cache()
        if self.running and not self.closing:
            interface.start()

    async def remove_interface(self, name: str) -> None:
        """
        Removes an interface from the station.
        """
        if name not in self.interfaces:
            raise KeyError(f"Interface {repr(name)} does not exist.")
        interface = self.interfaces[name]
        del self.interfaces[name]
        self.monitor.refresh_ports_cache()
        await asyncio.ensure_future(interface.shutdown())

    def get_nth_gateway(self, index: int) -> "Interface":
        """
        Get the nth gateway or raise an IndexError if not present.
        """
        if index <= 0:
            raise IndexError("Port numbers start at 1.")
        current = 0
        for interface in self.interfaces.values():
            if interface.gateway:
                current += 1
                if current == index:
                    return interface
        if not current:
            raise IndexError("No gateways available.")
        raise IndexError(f"Port {index} not found.")

    async def shutdown(self) -> None:
        """
        Shut down all interfaces, cutting off the station.
        """
        if not self.running:
            # Already shut down.
            return
        if self.closing and self._active_future:
            await self._active_future
            logger.warning(
                "Shutdown called while shutdown already called."
                "This may cause a deadlock.",
            )
            return
        self.closing = True
        await self.connection.shutdown()
        await self.beacon.shutdown()
        for interface in self.interfaces.values():
            await interface.shutdown()
        if self._active_future:
            self._active_future.set_result(None)
        if self._cleanup_task and self._cleanup_lock:
            self._cleanup_lock.cancel()
            self._cleanup_lock = None
            await self._cleanup_task
        self.closing = False
