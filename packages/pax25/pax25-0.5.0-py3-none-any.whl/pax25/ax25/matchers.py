"""
Matching utilities. Used for composing routing rules.
"""

from collections.abc import Callable
from typing import NamedTuple, cast

from pax25.ax25.address import Address
from pax25.ax25.constants import FrameType, SFrameType, UCommand
from pax25.ax25.control import Supervisory, Unnumbered
from pax25.ax25.frame import Frame
from pax25.ax25.utils import should_repeat_for
from pax25.interfaces import Interface

# All matcher functions take a frame and return True for a successful match
# and False if unsuccessful. More complex matching criteria are composed by
# combining simpler matchers.
type Matcher = Callable[[Frame, Interface], bool]
type Notifier = Callable[[Frame, Interface], None]


class MatchCall(NamedTuple):
    """
    A pair of functions-- one for matching, and one for processing a frame.

    Used by the FrameRouter-- if a matcher function matches, calls the notify function.

    Notifiers must be synchronous. If they need to perform an async action, have them
    use an async queue to defer the result. This is to prevent blocking the entire
    station on an async background action.
    """

    matcher: Matcher
    notify: Notifier


def check_all(*checks: Matcher) -> Matcher:
    """
    Returns True if all specified matcher functions return True.

    !!! note

        Passing no matchers will always return True.

    !!! tip

        Put faster-matching functions near the beginning of the list. Matching
        functions which iterate over lists will be used on every frame, potentially
        slowing processing if they are invoked when a faster matcher would otherwise
        decide the matching status.
    """

    def wrapped(frame: Frame, interface: Interface) -> bool:
        """Bound wrapper."""
        return all(check(frame, interface) for check in checks)

    return wrapped


def check_any(*checks: Matcher) -> Matcher:
    """
    Returns True if any of the specified matcher functions return True.

    !!! note

        Passing no matchers will always return True.

    !!! tip

        Put faster-matching functions near the beginning of the list. Matching
        functions which iterate over lists will be used on every frame, potentially
        slowing processing if they are invoked when a faster matcher would otherwise
        decide the matching status.
    """

    def wrapped(frame: Frame, interface: Interface) -> bool:
        """Bound wrapper."""
        return any(check(frame, interface) for check in checks)

    return wrapped


def has_src_address(address: Address) -> Matcher:
    """
    Check if the given frame has the specific destination address.
    """

    def wrapped(frame: Frame, _interface: Interface) -> bool:
        return frame.route.src.address == address

    return wrapped


def has_dest_address(address: Address) -> Matcher:
    """
    Check if the given frame has the specific destination address.
    """

    def wrapped(frame: Frame, _interface: Interface) -> bool:
        """Bound wrapper."""
        return frame.route.dest.address == address

    return wrapped


def needs_repeat_from(address: Address) -> Matcher:
    """
    Checks if the given frame needs repeating by the given address.

    Only does so if it's the next repeater in the set. Otherwise, ignores.
    """

    def wrapped(frame: Frame, _interface: Interface) -> bool:
        """Bound wrapper."""
        return should_repeat_for(address, frame)

    return wrapped


def has_these_digipeaters(digipeaters: tuple[Address, ...]) -> Matcher:
    """
    Checks if a connection has a specific list of intermediate digipeaters.
    """

    def wrapped(frame: Frame, _interface: Interface) -> bool:
        """Bound wrapper."""
        return digipeaters == tuple(
            digipeater.address for digipeater in frame.route.digipeaters
        )

    return wrapped


def is_s_frame(frame: Frame, _interface: Interface) -> bool:
    """
    Checks if the frame is an S frame.
    """
    return frame.control.type == FrameType.SUPERVISORY


def is_u_frame(frame: Frame, _interface: Interface) -> bool:
    """
    Checks if the frame is a U frame.
    """
    return frame.control.type == FrameType.UNNUMBERED


def _u_frame_check(command: UCommand) -> Matcher:
    """
    Creates a matcher based on a specific UCommand.
    """

    def command_check(frame: Frame, interface: Interface) -> bool:
        """
        Checks if the command type on a frame is a specific ucommand.
        """
        if is_u_frame(frame, interface):
            return cast(Unnumbered, frame.control).command == command
        return False

    return command_check


def _s_frame_check(frame_type: SFrameType) -> Matcher:
    """
    Creates a matcher based on a specific UCommand.
    """

    def frame_type_check(frame: Frame, interface: Interface) -> bool:
        """
        Checks if the command type on a frame is a specific ucommand.
        """
        if is_s_frame(frame, interface):
            return cast(Supervisory, frame.control).frame_type == frame_type
        return False

    return frame_type_check


U_FRAME_CHECKS = {command: _u_frame_check(command) for command in UCommand}
S_FRAME_CHECKS = {frame_type: _s_frame_check(frame_type) for frame_type in SFrameType}


def is_i_frame(frame: Frame, _interface: Interface) -> bool:
    """
    Checks if the frame is an I-frame.
    """
    return frame.control.type == FrameType.INFORMATIONAL


def repeats_completed(frame: Frame, _interface: Interface) -> bool:
    """
    Checks that a frame has finished making its way through the repeat chain.
    """
    if not frame.route.digipeaters:
        return True
    return all(digi.command_or_repeated for digi in frame.route.digipeaters)


def is_connection_frame_for(
    src: Address, dest: Address, digipeaters: tuple[Address, ...]
) -> Matcher:
    """
    Checks if a frame belongs to a specific connection defined by the src, dest, and
    digipeater path.
    """
    return check_all(
        has_src_address(src),
        has_dest_address(dest),
        has_these_digipeaters(digipeaters),
        repeats_completed,
        check_any(
            is_s_frame,
            is_i_frame,
        ),
    )


def on_gateway(_frame: Frame, interface: Interface) -> bool:
    """
    Checks if a frame was heard on a gateway interface.
    """
    return interface.gateway
