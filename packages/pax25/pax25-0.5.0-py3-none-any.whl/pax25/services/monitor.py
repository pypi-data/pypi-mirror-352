"""
Monitoring service module.

The monitoring service allows the station to keep track of traffic it has heard, and
keep reference tables that can be used. Comes with a couple of commands that you can
add to other applications.
"""

import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Literal

from pax25.applications.parsers import autocompleted_enum
from pax25.applications.router import CommandContext, CommandSpec
from pax25.applications.utils import build_table, send_message
from pax25.ax25.address import Address
from pax25.ax25.constants import UCommand
from pax25.ax25.control import Unnumbered
from pax25.ax25.frame import Frame
from pax25.ax25.matchers import MatchCall, on_gateway
from pax25.interfaces import Interface
from pax25.services.connection.connection import Connection, connection_key
from pax25.types import MonitorSettings
from pax25.utils import GatewayDict, PortSpec, gateways_for, smart_clone

if TYPE_CHECKING:  # pragma: no cover
    from pax25.station import Station


logger = logging.getLogger(__name__)


@dataclass(kw_only=True)
class HeardEntry:
    """
    Log entry for heard stations.
    """

    last_frame: Frame
    last_heard: datetime = field(default_factory=datetime.now)
    interface: str = ""
    last_ui: bytes = b""


@dataclass(kw_only=True, frozen=True)
class LoggedFrame:
    """
    Logged frame heard over the air, with context information.
    """

    frame: Frame
    port: PortSpec


def default_monitoring_settings() -> MonitorSettings:
    """
    Default monitoring settings.
    """
    return {"max_frame_log_size": 256, "max_stations_tracked": 30}


type LogListener = Callable[[Frame, Interface], bool]

type HeardOptions = Literal["short", "long", "normal"]


class Monitor:
    """
    Service that monitors incoming packets and keeps track of information like what
    stations have been heard and what they've said about themselves.
    """

    def __init__(
        self,
        *,
        station: "Station",
        settings: MonitorSettings | None,
    ):
        """
        Initializes the monitoring service.
        """
        self.station = station
        self._frame_log: list[LoggedFrame] = []
        self._heard_table: dict[Address, HeardEntry] = {}
        self._listeners: dict[str, LogListener] = {}
        self._ports_cache = gateways_for(self.station)
        self._settings = default_monitoring_settings()
        if settings:
            self._settings.update(settings)
        self.station.frame_router.register_matcher(
            "monitor", MatchCall(matcher=on_gateway, notify=self.update_entry)
        )

    def refresh_ports_cache(self) -> None:
        """
        Refreshes the ports cache.
        """
        self._ports_cache = gateways_for(self.station)

    @property
    def settings(self) -> MonitorSettings:
        """
        Return the monitor's current settings.
        """
        return smart_clone(self._settings)

    async def reload_settings(self, settings: MonitorSettings) -> None:
        """
        Reload monitoring settings.
        """
        # The settings for monitoring currently don't require any specific action
        # to change.
        self._settings = settings

    def update_entry(self, frame: Frame, interface: Interface) -> None:
        """
        Updates the entry in the heard table.
        """
        source = frame.route.src.address
        entry = self._heard_table.get(source) or HeardEntry(
            last_frame=frame,
        )
        entry.last_heard = datetime.now(UTC)
        entry.interface = interface.name
        if isinstance(frame.control, Unnumbered) and (
            frame.control.command == UCommand.UNNUMBERED_INFORMATION
        ):
            entry.last_ui = frame.info
        self._heard_table[source] = entry
        self.log_frame(frame, interface)
        max_tracked = self._settings["max_stations_tracked"]
        if (max_tracked is not None) and (len(self._heard_table) > max_tracked):
            new_table: dict[Address, HeardEntry] = {}
            revised_set = list(
                sorted(self._heard_table.items(), key=lambda x: x[1].last_heard)
            )[-max_tracked:]
            for address, entry in revised_set:
                new_table[address] = entry
            self._heard_table = new_table

    def log_frame(self, frame: Frame, interface: Interface) -> None:
        """
        Log a frame heard on a gateway.
        """
        route_key = connection_key(
            frame.route.src.address, frame.route.dest.address, interface
        )
        if route_key in self.station.connection.table:
            # We don't log frames we're active party to. This may change in the future,
            # delegating filtering downstream.
            return
        # If any of our frame listeners return True, we don't log. We consider the frame
        # 'consumed' from the log in that case.
        if any([listener(frame, interface) for listener in self._listeners.values()]):
            return
        self._frame_log.append(
            LoggedFrame(frame=frame, port=self._ports_cache[interface])
        )
        if self._settings["max_frame_log_size"] is None:
            return
        if self._settings["max_frame_log_size"] < len(self._frame_log):
            del self._frame_log[: -self._settings["max_frame_log_size"]]

    def _build_std_table(
        self,
        heard_stations: dict[Address, HeardEntry],
        gateways: GatewayDict,
        include_dest: bool = False,
    ) -> list[str]:
        lines = []
        for address, entry in heard_stations.items():
            try:
                port = gateways[self.station.interfaces[entry.interface]].number
            except KeyError:
                # No longer a gateway, or the interface is down.
                continue
            marker = ""
            if entry.last_frame.route.digipeaters:
                marker = "*"
            line = [f"{port}:{address}{marker}"]
            if include_dest:
                line.append(f"> {entry.last_frame.route.dest}")
            last_heard = entry.last_heard.astimezone()
            line.append(str(last_heard.date()))
            line.append(str(last_heard.time()).split(".")[0])
            lines.append(line)
        return build_table(lines)

    def _std_table(self, connection: Connection, gateways: GatewayDict) -> None:
        """
        Print a standard heard table.
        """
        heard_stations = self.heard_stations
        table = self._build_std_table(heard_stations, gateways)
        send_message(connection, "\r".join(table))

    def _short_table(self, connection: Connection, gateways: GatewayDict) -> None:
        """
        Print a short heard table.
        """
        lines = []
        for address, entry in self.heard_stations.items():
            try:
                port = gateways[self.station.interfaces[entry.interface]].number
            except KeyError:
                # No longer a gateway, or the interface is down.
                continue
            marker = ""
            if entry.last_frame.route.digipeaters:
                marker = "*"
            line = f"{port}:{address}{marker}"
            lines.append(line)
        send_message(connection, "\r".join(lines))

    def _long_table(self, connection: Connection, gateways: GatewayDict) -> None:
        """
        Print a long heard table.
        """
        heard_stations = self.heard_stations
        table = self._build_std_table(heard_stations, gateways, include_dest=True)
        final_lines = []
        for summary_line, entry in zip(table, heard_stations.values(), strict=False):
            final_lines.append(summary_line)
            if entry.last_frame.route.digipeaters:
                final_lines.append(
                    " VIA "
                    + ",".join(
                        str(digipeater)
                        for digipeater in entry.last_frame.route.digipeaters
                    )
                )
            last_ui = entry.last_ui.decode("utf-8", errors="ignore").strip()
            if last_ui:
                final_lines.append(" UI: " + last_ui)
        send_message(connection, "\r".join(final_lines))

    def heard(
        self, connection: Connection, context: CommandContext[HeardOptions]
    ) -> None:
        """
        Heard command. Can be included using the 'command' property on the monitoring
        service, which defines a CommandSpec for inclusion in other apps.
        """
        gateways = gateways_for(self.station)
        match context.args:
            case "short":
                self._short_table(connection, gateways)
            case "long":
                self._long_table(connection, gateways)
            case "normal":
                self._std_table(connection, gateways)

    def add_listener(self, label: str, listener: LogListener) -> None:
        """
        Registers a frame listener.
        """
        if label in self._listeners:
            logger.warning(
                f"Duplicate label {repr(label)} registered as monitoring listener. "
                f"This is likely a bug or configuration issue.",
            )
        self._listeners[label] = listener

    def remove_listener(self, label: str) -> None:
        """
        Removes a frame listener.
        """
        if label not in self._listeners:
            logger.warning(
                f"Removing non-existent monitoring listener, {repr(label)}. This is "
                f"likely a bug or configuration issue.",
            )
            return
        del self._listeners[label]

    def consume_logs(self) -> list[LoggedFrame]:
        """
        Returns the current frame log, emptying it.
        """
        log = self._frame_log
        self._frame_log = []
        return log

    @property
    def heard_stations(self) -> dict[Address, HeardEntry]:
        """
        Return a tuple of heard stations.
        """
        return {
            key: value
            for key, value in sorted(
                self._heard_table.items(), key=lambda x: x[1].last_heard
            )
        }

    @property
    def command(self) -> CommandSpec[HeardOptions]:
        """
        Builds a command spec for the heard command.
        """
        return CommandSpec(
            command="heard",
            aliases=("j",),
            help="List all stations heard by this station. Use 'heard long' for "
            "extended info, or 'heard short' for abbreviated info.",
            function=self.heard,
            parser=autocompleted_enum(
                ("short", "long", "normal"),
                default="normal",
            ),
        )
