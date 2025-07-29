"""
Digipeater system. Will determine whether a digipeating frame is one we need to relay,
and if so, will queue up the digipeated frame with the correct flags marked.
"""

from typing import TYPE_CHECKING

from pax25.ax25.address import Address
from pax25.ax25.frame import Frame
from pax25.ax25.matchers import MatchCall, needs_repeat_from
from pax25.ax25.utils import repeated_for
from pax25.interfaces import Interface
from pax25.types import DigipeaterSettings
from pax25.utils import smart_clone

if TYPE_CHECKING:  # pragma: no cover
    from pax25.station import Station


class Digipeater:
    """
    Digipeater class. Manages digipeating functions. Only ever digipeats on the
    interface it hears from.

    This may need to be expanded later to allow for multiple digipeater conditions,
    but for now we assume a single digipeater per station, which responds on the main
    station name with SSID 0.
    """

    def __init__(
        self,
        station: "Station",
        settings: DigipeaterSettings | None,
    ) -> None:
        """Initializes the digipeater."""
        self.station = station
        self._settings = settings or DigipeaterSettings(enabled=True)
        matcher = needs_repeat_from(self.address)
        self.station.frame_router.register_matcher(
            "digipeater", MatchCall(matcher=matcher, notify=self.repeat)
        )

    @property
    def address(self) -> Address:
        """
        Gets the repeater address of the station.
        """
        return Address(name=self.station.name, ssid=0)

    async def reload_settings(self, settings: DigipeaterSettings) -> None:
        """
        Reloads the service with new settings.
        """
        # We don't have to restart anything, since this is used on-demand.
        self._settings = settings

    @property
    def enabled(self) -> bool:
        """
        Whether the Digipeater is enabled.
        """
        return self._settings.get("enabled", True)

    @property
    def settings(self) -> DigipeaterSettings:
        """
        Returns the current digipeater settings.
        """
        return smart_clone(self._settings)

    def repeat(self, frame: Frame, interface: Interface) -> None:
        """
        Performs digipeating for a matched frame.
        """
        if not self.enabled:
            return
        self.station.frame_router.send_frame(
            interface, repeated_for(self.address, frame)
        )

    def unregister(self) -> None:
        """
        Remove the digipeater from the matchers, effectively disabling it.
        """
        self.station.frame_router.remove_matcher("digipeater")
