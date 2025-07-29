"""
The Frame Router routes frames to relevant matching functions used to perform any
protocol work.
"""

from datetime import UTC, datetime
from logging import getLogger
from typing import TYPE_CHECKING

from pax25.ax25.frame import Frame
from pax25.ax25.matchers import MatchCall
from pax25.utils import LazyRepr

if TYPE_CHECKING:  # pragma: no cover
    from pax25.interfaces import Interface
    from pax25.station import Station


logger = getLogger(__name__)


class FrameRouter:
    """
    The Frame queue is a sort of router. It takes in frames from the varying interfaces
    and makes sure they go to their proper destination, whether that be an existing
    connection object or re-transcribed and sent out to another interface.
    """

    def __init__(self, *, station: "Station"):
        self.station = station
        self.matchers: dict[str, MatchCall] = {}
        self.last_transmission: None | datetime = None

    def process_frame(self, interface: "Interface", frame: Frame) -> None:
        """
        Interfaces call this function to put a new frame in the queue, to be interpreted
        as a received frame.

        This function must be resilient to avoid bringing down the station from one bug.
        """
        # Could change while iterating, since we might do something like register a
        # connection.
        if interface.type != "File":
            logger.debug(
                "Received from %s: %s",
                interface.name,
                LazyRepr(frame),
            )
        matchers = list(self.matchers.items())
        for key, match_call in matchers:
            try:
                if not match_call.matcher(frame, interface):
                    continue
            except Exception:
                logger.exception(
                    "Got error for matcher with key %s:",
                    repr(key),
                )
                continue
            try:
                match_call.notify(frame, interface)
            except Exception:
                logger.exception(
                    "Got error for notifier with key %s:",
                    repr(key),
                )
                continue

    def send_frame(
        self,
        interface: "Interface",
        frame: Frame,
        update_timestamp: bool = True,
    ) -> None:
        """
        Send a frame out on a specific interface. Also does some bookkeeping in the
        process, like checking if we're sending over a gateway and updating our
        .last_transmission stamp if so.

        In the future, it may be possible to filter outgoing packets, or otherwise
        listen for them.
        """
        if interface.name not in self.station.interfaces:
            # Interface was removed, and thus inert.
            logger.debug(
                "Dropping packet for %s (not in interface table): %s",
                (
                    interface.name,
                    LazyRepr(frame),
                ),
            )
            return
        if interface.gateway and update_timestamp:
            self.last_transmission = datetime.now(UTC)
        if interface.type != "File":
            logger.debug("Sending on %s: %s", interface.name, LazyRepr(frame))
        interface.send_frame(frame)

    def register_matcher(self, key: str, match_call: MatchCall) -> None:
        """
        Registers a matcher.
        """
        if key in self.matchers:
            logger.warning(
                "Existing matcher for key %s, %s, was replaced with new matcher %s. "
                "This may be a collision or a sign of a cleanup issue.",
                repr(key),
                self.matchers[key],
                match_call,
            )
        self.matchers[key] = match_call

    def remove_matcher(self, key: str) -> None:
        """
        Removes a matcher based on its key.
        """
        if key not in self.matchers:
            logger.warning(
                "Non-existent key removed, %s. This may indicate that the key was "
                "never registered, or cleanup has been called multiple times "
                "unnecessarily.",
                repr(key),
            )
            return
        del self.matchers[key]
