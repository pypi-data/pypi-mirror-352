"""
Connection service. Keeps track of the connection table, instantiates connections,
performs other housekeeping around them.
"""

from collections import defaultdict
from typing import TYPE_CHECKING, Any

from pax25.applications import BaseApplication
from pax25.applications.types import S
from pax25.ax25.address import Address, AddressHeader, Route
from pax25.ax25.constants import UCommand
from pax25.ax25.control import Unnumbered
from pax25.ax25.frame import Frame
from pax25.ax25.matchers import (
    U_FRAME_CHECKS,
    MatchCall,
    check_all,
    repeats_completed,
)
from pax25.ax25.utils import reply_digipeaters
from pax25.exceptions import ConfigurationError
from pax25.interfaces import Interface
from pax25.services.connection.connection import (
    Connection,
    ConnectionKey,
    connection_key,
)
from pax25.types import ConnectionSettings
from pax25.utils import smart_clone

if TYPE_CHECKING:  # pragma: no cover
    from pax25.station import Station


type ApplicationMap = defaultdict[str, dict[Address, BaseApplication[Any]]]


def default_connection_settings() -> "ConnectionSettings":
    """
    Default parameters for parameter settings.
    """
    return {
        "retries": 10,
        "retry_interval": 10000,
        "reception_status_delay": 2000,
        "connection_check_interval": 30_000,
    }


class ConnectionService:
    """
    Connection handling service.
    """

    def __init__(
        self,
        station: "Station",
        settings: ConnectionSettings | None,
    ) -> None:
        """
        Initialize the connection service.
        """
        self.station = station
        self._settings = default_connection_settings()
        if settings:
            self._settings.update(settings)
        # We keep track of the addresses we are internally watching for here, such
        # as contacts to our internally registered applications.
        self._internal_addresses: dict[Address, set[Interface[Any]]] = {}
        self.table: dict[ConnectionKey, Connection] = {}
        self._application_map: ApplicationMap = defaultdict(dict)
        self.station.frame_router.register_matcher(
            "connection",
            MatchCall(matcher=self.connection_matcher, notify=self.inbound_connect),
        )
        self.station.frame_router.register_matcher(
            "disconnect_mode",
            MatchCall(
                matcher=self.disconnect_mode_matcher,
                notify=self.disconnect_mode_sender,
            ),
        )

    @property
    def settings(self) -> ConnectionSettings:
        """
        Get the default tunable parameters for connected sessions.
        """
        return smart_clone(self._settings)

    async def reload_settings(self, settings: ConnectionSettings) -> None:
        """
        Reload the settings for connections.
        """
        old_settings = self._settings
        # Makes a clone.
        result = self.settings
        result.update(settings)
        if result == self._settings:
            return
        self._settings = settings
        # OK, looks like we need to reload all the connections, too.
        for value in self.table.values():
            # We don't want to change any connections that had anything special applied.
            if value.settings == old_settings:
                await value.reload_settings(settings)

    @property
    def application_map(self) -> ApplicationMap:
        """
        Return a copy of the application map.
        """
        return smart_clone(self._application_map)

    def connection_matcher(self, frame: Frame, interface: Interface) -> bool:
        """
        Matches incoming connection frames.
        """
        if interface.type == "Loopback":
            # Ignore all loopback connection frames.
            return False
        if not check_all(
            repeats_completed, U_FRAME_CHECKS[UCommand.SET_ASYNC_BALANCED_MODE]
        )(frame, interface):
            return False
        return frame.route.dest.address in self._application_map.get(interface.name, [])

    def disconnect_mode_matcher(self, frame: Frame, interface: Interface) -> bool:
        """
        Checks if we have a frame that's addressed to us like we have a connection open,
        but no such connection exists.
        """
        if interface.type == "Loopback":
            return False
        if not repeats_completed(frame, interface):
            return False
        if frame.route.dest.address not in self._application_map.get(
            interface.name,
            [],
        ):
            return False
        if U_FRAME_CHECKS[UCommand.SET_ASYNC_BALANCED_MODE](frame, interface):
            return False
        if U_FRAME_CHECKS[UCommand.UNNUMBERED_INFORMATION](frame, interface):
            return False
        first_party = frame.route.src.address
        second_party = frame.route.dest.address
        return connection_key(first_party, second_party, interface) not in self.table

    def disconnect_mode_sender(self, frame: Frame, interface: Interface) -> None:
        """
        Send a disconnect mode frame in response to a frame.
        """
        response_frame = Frame(
            route=Route(
                src=AddressHeader(address=frame.route.dest.address),
                dest=AddressHeader(address=frame.route.src.address),
                digipeaters=reply_digipeaters(frame.route.digipeaters),
            ),
            control=Unnumbered(command=UCommand.DISCONNECT_MODE, poll_or_final=True),
            pid=None,
        )
        self.station.frame_router.send_frame(interface, response_frame)

    def add_app(
        self,
        app: type[BaseApplication[S]],
        *,
        interfaces: list[str],
        application_name: str | None = None,
        station_name: str | None = None,
        ssid: int | None = None,
        settings: S,
    ) -> BaseApplication[S]:
        """
        Registers a new application to the specified interfaces.
        """
        station_name = (station_name if station_name else self.station.name).upper()
        application_name = (
            application_name if application_name is not None else app.__name__
        )
        application_instance = app(
            name=application_name,
            settings=settings,
            station=self.station,
        )
        for interface in interfaces:
            if interface not in self.station.interfaces:
                raise ConfigurationError(
                    "Attempted to register application to non-existent "
                    f"interface, {repr(interface)}.",
                )
            new_address = Address(
                name=station_name,
                ssid=self.next_ssid(
                    interface=self.station.interfaces[interface],
                    name=station_name,
                    ssid=ssid,
                ),
            )
            self._application_map[interface][new_address] = application_instance
            self.register_station(
                interface=self.station.interfaces[interface], address=new_address
            )
        return application_instance

    def register_station(
        self, *, interface: "Interface[Any]", address: Address
    ) -> None:
        """
        Registers an address as existing on a particular interface. It can then be
        looked up later for making connections.
        """
        self._internal_addresses[address] = self._internal_addresses.get(
            address, set()
        ) | {interface}

    def inbound_connect(self, frame: Frame, interface: Interface) -> None:
        """
        Add a connection to the connection table based on an incoming frame.
        """
        first_party = frame.route.src.address
        second_party = frame.route.dest.address
        digipeaters = tuple(
            digipeater.address for digipeater in frame.route.digipeaters
        )
        key = connection_key(first_party, second_party, interface)
        if key in self.table:
            # Existing connection will handle this.
            return
        connection = self.add_connection(
            first_party=frame.route.src.address,
            second_party=frame.route.dest.address,
            interface=interface,
            digipeaters=digipeaters,
            inbound=True,
        )
        connection.negotiate()

    def app_for(
        self,
        interface: Interface,
        destination: Address,
    ) -> BaseApplication[Any]:
        """
        Get an app for a particular address on a specific interface.

        Raises KeyError if no such app exists.
        """
        return self._application_map[interface.name][destination]

    def add_connection(
        self,
        *,
        first_party: Address,
        second_party: Address,
        digipeaters: tuple[Address, ...] = tuple(),
        interface: Interface,
        inbound: bool,
        application: BaseApplication[Any] | None = None,
    ) -> Connection:
        """
        Add a connection to the connection table. Returns a connection if one already
        exists. Note that an existing connection may be outbound rather than inbound,
        or vice versa.
        """
        key = connection_key(first_party, second_party, interface)
        if key in self.table:
            raise ConnectionError(f"Connection already exists! {self.table[key]}")
        if not application and inbound:
            application = self._application_map[interface.name][second_party]
        connection = Connection(
            first_party=first_party,
            second_party=second_party,
            digipeaters=digipeaters,
            interface=interface,
            application=application,
            station=self.station,
            service=self,
            inbound=inbound,
            sudo=interface.sudo,
            close_callback=self.connection_closed_callback,
        )
        self.table[key] = connection
        match_call = MatchCall(
            matcher=connection.frame_matcher(),
            notify=connection.inbound_frame,
        )
        self.station.frame_router.register_matcher(
            connection.match_key,
            match_call,
        )
        return connection

    def connection_closed_callback(self, connection: Connection) -> None:
        """
        Callback function to be used when connections are closed out.
        """
        self.station.frame_router.remove_matcher(connection.match_key)
        self.remove_connection(connection)

    def remove_connection(self, connection: Connection) -> None:
        """
        Removes a connection from the connection table.
        """
        key = connection_key(
            connection.first_party, connection.second_party, connection.interface
        )
        del self.table[key]

    def next_ssid(
        self,
        *,
        name: str,
        interface: "Interface[Any]",
        ssid: int | None = None,
    ) -> int:
        """
        Given a station name and an interface, produces the next SSID.

        You can give an ssid you would prefer by specifying the ssid argument. If the
        ssid already exists or is invalid, throws an exception. This function is
        used primarily by the station in order to assign default SSIDs to applications.
        """
        name = name.upper()
        ssids: set[int] = set()
        for address, interfaces in self._internal_addresses.items():
            if address.name != name:
                continue
            if interface in interfaces:
                ssids |= {address.ssid}
        if ssid is None:
            for candidate in range(16):
                if candidate not in ssids:
                    ssid = candidate
                    break
            else:
                raise ConfigurationError(
                    f"All valid SSIDs on {name}, interface {interface} are taken! "
                    "You may have at most 16 SSIDs, numbered 0-15."
                )
        if not 0 <= ssid <= 15:
            raise ConfigurationError("SSID must be between 0 and 15.")
        if ssid in ssids:
            raise ConfigurationError(
                f"SSID {repr(ssid)} already registered on {interface}!"
            )
        return ssid

    async def shutdown(self) -> None:
        """
        Shutdown the connection service, closing out all connections.
        """
        for connection in list(self.table.values()):
            connection.shutdown()
