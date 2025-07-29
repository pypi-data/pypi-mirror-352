"""
Types used for type checking the library. Client developers can use these if they like,
but they're mostly for our own sanity checks during development/testing.
"""

from typing import TYPE_CHECKING, NotRequired, Protocol, Self, TypedDict

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any

    from pax25.applications import BaseApplication


class EmptyDict(TypedDict):
    """
    Empty dictionary.
    """


class ConnectionSettings(TypedDict):
    """
    Tunable connection parameters. You can probably leave these alone.
    """

    retries: int
    retry_interval: int
    connection_check_interval: int
    reception_status_delay: int


class DigipeaterSettings(TypedDict):
    """
    Settings for the digipeater.
    """

    enabled: NotRequired[bool]


class MonitorSettings(TypedDict):
    """
    Settings for monitoring.
    """

    max_frame_log_size: int | None
    max_stations_tracked: int | None


class BeaconServiceSettings(TypedDict):
    """
    Settings for the beacon service.
    """

    id_beacon_enabled: bool
    # For most jurisdictions, this should be 600 (10 mins) or lower.
    id_beacon_interval: int | float
    id_beacon_destination: str
    id_beacon_digipeaters: dict[str, list[str]]
    id_beacon_content: str | None


# The StationConfig object should always be JSON-serializable. This way we'll eventually
# be able to use JSON for configuration files.


# This means that all interface configs will ALSO need to be JSON-serializable.
class StationConfig(TypedDict):
    """
    Configuration for a station.
    """

    name: str
    digipeater: NotRequired[DigipeaterSettings]
    monitor: NotRequired[MonitorSettings]
    connection: NotRequired[ConnectionSettings]
    beacon: NotRequired[BeaconServiceSettings]


# Map for the station's application registry
ApplicationMap = dict[str, dict[str, "BaseApplication[Any]"]]


class Version(TypedDict):
    """
    Version namedtuple structure. Use this to mark your application versions.
    """

    major: int
    minor: int
    patch: int


class Updatable(Protocol):
    """
    Protocol for objects that can update their values with a copy of themselves,
    I.E., dicts and TypedDicts.
    """

    def update(self, new_values: Self) -> None: ...
