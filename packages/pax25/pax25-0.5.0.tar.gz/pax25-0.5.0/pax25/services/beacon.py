"""
Beacon service.
"""

import asyncio
import logging
from asyncio import Task
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from pax25.ax25.address import Address, AddressHeader, Route
from pax25.ax25.constants import AX25_PID_TEXT, UCommand
from pax25.ax25.control import Unnumbered
from pax25.ax25.frame import Frame
from pax25.types import BeaconServiceSettings
from pax25.utils import cancel_all, smart_clone

if TYPE_CHECKING:  # pragma: no cover
    from pax25.station import Station


logger = logging.getLogger(__name__)


type PerInterfaceBytes = dict[str, bytes]

type BeaconContents = bytes | PerInterfaceBytes | None

type BeaconCoroutine = Callable[["BeaconContext"], Awaitable[BeaconContents]]

type DigipeaterDict = dict[str, tuple[Address, ...]]


@dataclass(kw_only=True)
class BeaconSettings:
    """
    Data structure for defining a beacon. This structure is mutable and updating it will
    update the beacon's settings.
    """

    # Interval in seconds. Can be subsecond if needed via float.
    interval: int | float
    # Destination of resulting UI frame.
    dest: Address
    protocol: int = AX25_PID_TEXT
    max_length: int = 256
    update_station_timestamp: bool = False
    digipeaters: DigipeaterDict = field(default_factory=dict)
    coroutine: BeaconCoroutine


@dataclass(kw_only=True, frozen=True)
class BeaconContext:
    """
    Context for a beacon.
    """

    # The last time the station remembers running this beacon, or None if never.
    last_run: None | datetime = None
    # When the station first set up the beacon. The beacon may not have run at this
    # time.
    started: datetime
    # The registered name of this beacon.
    label: str
    # The settings for the beacon.
    spec: BeaconSettings
    station: "Station"


@dataclass(kw_only=True)
class BeaconTracker:
    """
    Tracking object for beacons-- notes when their last run was, and holds their spec.
    """

    spec: BeaconSettings
    started: datetime = field(default_factory=lambda: datetime.now(UTC))
    last_run: None | datetime = None


STATION_ID_LABEL = "station_id"
STATION_ID_CHECK_INTERVAL = 60


def delta_to_microseconds(delta: timedelta) -> int:
    """
    Converts a timedelta to microseconds.
    """
    return (
        ((delta.days * 24 * 60 * 60) + delta.seconds) * 1_000_000
    ) + delta.microseconds


async def next_interval(last_timestamp: datetime, interval: int | float) -> datetime:
    """
    Return the value of the next minute, after waiting for it to arrive.
    """
    next_interval_timestamp = last_timestamp + timedelta(seconds=interval)
    delta = next_interval_timestamp - last_timestamp
    delta_microseconds = delta_to_microseconds(delta)
    if delta_microseconds < 0:  # pragma: no cover
        # Must be right on the border between minutes. Unlikely, but possible.
        return next_interval_timestamp
    await asyncio.sleep(delta_microseconds / 1_000_000)
    return next_interval_timestamp


def generate_beacon_map(context: BeaconContext) -> PerInterfaceBytes:
    """
    Generate the default beacon text.
    """
    results: dict[str, bytes] = {}
    for interface in context.station.interfaces.values():
        text = context.station.name
        if not interface.gateway:
            continue
        apps = context.station.connection.application_map.get(interface.name, {})
        for key, value in apps.items():
            if not value.short_name:
                continue
            text += f" {key}/{value.short_name}"
        results[interface.name] = text.encode("utf-8")
    return results


async def station_id_beacon(context: BeaconContext) -> BeaconContents:
    """
    Example beacon which sends its text if we've been transmitting for a while
    and haven't sent a station ID.
    """
    interval = context.station.beacon._settings["id_beacon_interval"]
    if not context.station.frame_router.last_transmission:
        return None
    last_transmission = context.station.frame_router.last_transmission
    now = datetime.now(UTC)
    last_run = context.last_run or context.started
    if last_transmission > last_run and (last_run + timedelta(seconds=interval) < now):
        if context.station.beacon._settings["id_beacon_content"] is None:
            return generate_beacon_map(context)
        return context.station.beacon._settings["id_beacon_content"].encode("utf-8")
    return None


class BeaconService:
    """
    Beacon service. Used for sending out beacons on regular intervals.

    Beacons are sent out over all gateway interfaces.
    """

    def __init__(
        self,
        *,
        station: "Station",
        settings: BeaconServiceSettings | None = None,
    ):
        """
        Initialize the beacon service.
        """
        self._beacons: dict[str, BeaconTracker] = {}
        self.station = station
        self._settings: BeaconServiceSettings = BeaconServiceSettings(
            id_beacon_enabled=True,
            id_beacon_interval=600,
            id_beacon_destination="ID",
            id_beacon_digipeaters={},
            id_beacon_content=None,
        )
        if settings:
            self._settings.update(settings)
        self._id_beacon_tracker: None | BeaconTracker = None
        self._loop_tasks: dict[str, Task[None]] = {}
        self._tasks: set[Task[None]] = set()
        if self._settings["id_beacon_enabled"]:
            self._add_station_beacon()

    @property
    def settings(self) -> BeaconServiceSettings:
        """
        Return the beacon service's settings.
        """
        return smart_clone(self._settings)

    async def reload_settings(self, settings: BeaconServiceSettings) -> None:
        """
        Reload the beacon settings.
        """
        self._settings.update(settings)
        if self._settings["id_beacon_enabled"]:
            self._add_station_beacon()
        else:
            self._remove_station_beacon()
            return
        assert self._id_beacon_tracker
        self._id_beacon_tracker.spec = self._station_id_settings

    @property
    def _station_id_settings(self) -> BeaconSettings:
        return BeaconSettings(
            interval=STATION_ID_CHECK_INTERVAL,
            dest=Address.from_string(self._settings["id_beacon_destination"]),
            digipeaters={
                key: tuple(
                    Address.from_string(digipeater) for digipeater in digipeater_strings
                )
                for key, digipeater_strings in self._settings[
                    "id_beacon_digipeaters"
                ].items()
            },
            coroutine=station_id_beacon,
        )

    def _add_station_beacon(self) -> None:
        """
        Add the default station ID beacon.
        """
        if self._id_beacon_tracker:
            return
        self._id_beacon_tracker = self.add_beacon(
            STATION_ID_LABEL,
            self._station_id_settings,
        )

    def _remove_station_beacon(self) -> None:
        """
        Remove the default station ID beacon.
        """
        if not self._id_beacon_tracker:
            return
        self.remove_beacon(STATION_ID_LABEL)

    def run(self) -> None:
        """
        Initialization function. Starts the beacon service with the included station ID
        beacon.
        """
        for label, tracker in self._beacons.items():
            self._loop_tasks[label] = asyncio.ensure_future(
                self.beacon_loop(label, tracker)
            )

    def add_beacon(self, label: str, beacon_spec: BeaconSettings) -> BeaconTracker:
        """
        Adds a beacon for the service to track.
        """
        if label in self._beacons:
            logger.warning(
                f"Duplicate beacon {repr(label)} added. Overriding existing entry. "
                f"This is likely a bug."
            )
        tracker = BeaconTracker(
            spec=beacon_spec,
            last_run=None,
        )
        self._beacons[label] = tracker
        if self.station.running:
            self._loop_tasks[label] = asyncio.ensure_future(
                self.beacon_loop(label, tracker)
            )
        return tracker

    def remove_beacon(self, label: str) -> None:
        """
        Removes a beacon from the service.
        """
        if label not in self._beacons:
            logger.warning(
                f"Attempted to remove non-existent beacon {repr(label)}. "
                f"This is likely a bug."
            )
            return
        del self._beacons[label]
        if label in self._loop_tasks:
            # Might happen if called before the station has started.
            self._loop_tasks[label].cancel()
            del self._loop_tasks[label]

    async def resolve_beacon(
        self,
        label: str,
        future: Awaitable[BeaconContents],
    ) -> None:
        """
        Performs a run of the given beacon.
        """
        try:
            info = await future
        except Exception as err:
            logger.error(err, exc_info=True)
            return
        if info is None:
            return
        context = self._beacons[label]
        base_frame = Frame(
            route=Route(
                src=AddressHeader(address=Address(name=self.station.name)),
                dest=AddressHeader(address=context.spec.dest),
                digipeaters=tuple(),
            ),
            control=Unnumbered(command=UCommand.UNNUMBERED_INFORMATION),
            pid=context.spec.protocol,
        )
        length = context.spec.max_length - base_frame.size()
        if length < 0:
            length = 0
        to_send: PerInterfaceBytes = {}
        if isinstance(info, bytes):
            for interface in self.station.interfaces.values():
                if not interface.gateway:
                    continue
                to_send[interface.name] = info
        else:
            to_send = info
        for key, value in to_send.items():
            frame = base_frame._replace(
                info=value[:length],
                route=base_frame.route._replace(
                    digipeaters=tuple(
                        AddressHeader(address=digipeater)
                        for digipeater in context.spec.digipeaters.get(key, tuple())
                    ),
                ),
            )
            self.station.frame_router.send_frame(
                self.station.interfaces[key],
                frame,
                update_timestamp=context.spec.update_station_timestamp,
            )
        context.last_run = datetime.now(UTC)

    def clean_tasks(self) -> None:
        """
        Clear out any beacon promises that have already been fulfilled.
        """
        self._tasks = set(task for task in self._tasks if not task.done())

    async def beacon_loop(self, label: str, beacon: BeaconTracker) -> None:
        """
        Creates a loop for a beacon.

        This loop is configured to autocorrect for drift over time. Python won't give
        us true microsecond precision, but we can get close enough for any needs
        packet radio has. It might fail to correct if the interval is higher than we
        can reliably schedule recurring events, in which case this will just go as
        fast as it can.
        """
        # This loop is configured to autocorrect for drift over time. Python won't give
        # us true microsecond precision, but we can get close enough for any needs
        # packet radio has. It might fail to correct if the interval is higher than we
        # can reliably schedule recurring events, in which case this will just go as
        # fast as it can.
        next_timestamp = datetime.now(UTC)
        while True:
            next_timestamp = await next_interval(next_timestamp, beacon.spec.interval)
            self.clean_tasks()
            await self.resolve_beacon(
                label,
                beacon.spec.coroutine(
                    BeaconContext(
                        spec=beacon.spec,
                        station=self.station,
                        last_run=beacon.last_run,
                        started=beacon.started,
                        label=label,
                    )
                ),
            )

    async def shutdown(self) -> None:
        """
        Shutdown the beacons.
        """
        await cancel_all(self._loop_tasks.values())
        self._loop_tasks = {}
        self._beacons = {}
