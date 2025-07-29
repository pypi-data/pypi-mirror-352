"""
Contains classes for managing state variables used in AX.25 connections.
"""

from collections.abc import Iterator
from dataclasses import dataclass, field

from pax25.ax25.constants import AX25_SEQ_MAX
from pax25.ax25.frame import Frame


class RolloverCounter:
    """
    Rollover value counter. Allows us to count up or down while rolling over a specific
    range of values.
    """

    def __init__(
        self,
        *,
        name: str,
        initial: int = 0,
        minimum: int = 0,
        maximum: int = AX25_SEQ_MAX,
    ):
        """
        Initializes the rollover counter.
        """
        self.name = name
        self.value = initial
        self.minimum = minimum
        self.maximum = maximum
        assert self.minimum <= self.value <= maximum, (
            f"Value {self.value} is not between {self.minimum} and {self.maximum}."
        )

    def __str__(self) -> str:
        """
        Represents the RolloverCounter as a string.
        """
        return f"Rollover Counter ({self.name}), value: {self.value}"

    def retrace_from(self, start_value: int) -> Iterator[int]:
        """
        Returns an iterable that returns all integers from a starting position to the
        current value, inclusive.
        """
        assert self.minimum <= start_value <= self.maximum
        current_value = self.value
        counting_value = start_value
        yield counting_value
        if counting_value == current_value:
            return
        while counting_value != current_value:
            counting_value = self.after(counting_value)
            if counting_value == current_value:
                # We'll send the final included value after the loop.
                break
            yield counting_value
        yield current_value

    def iterate_up_to(self, end_value: int) -> Iterator[int]:
        """
        Iterably advance this counter up to the target number. There are some tricky
        parts to this.

        Since we're using this to keep track of all unacknowledged frames, we could have
        eight valid values, but only 7 alternative values from the current one. So,
        if we get the current value, we haven't actually changed, and should return no
        items in iteration. If we end up with a value one previous to the current value,
        we would loop all the way around, minus actually including the current value.

        As we loop, we also set the current value as the new value.
        """
        assert self.minimum <= end_value <= self.maximum
        while self.value != end_value:
            self.increment()
            yield self.value

    def next(self) -> int:
        """
        Gets the next value that would be set if incrementing.
        """
        return self.after(self.value)

    def previous(self) -> int:
        """
        Gets the previous value that would be set if decrementing.
        """
        return self.before(self.value)

    def after(self, value: int) -> int:
        """
        Get the value that would come after the given one.
        """
        assert self.minimum <= value <= self.maximum
        value += 1
        if value > self.maximum:
            return self.minimum
        return value

    def before(self, value: int) -> int:
        """
        Get the value that would come before the given one.
        """
        assert self.minimum <= value <= self.maximum
        value -= 1
        if value < self.minimum:
            return self.maximum
        return value

    def increment(self) -> None:
        """
        Increment the value.
        """
        self.value = self.next()

    def decrement(self) -> None:
        """
        Decrement the value.
        """
        self.value = self.previous()


@dataclass
class FrameStateTracker:
    """
    Tracks the frame variables and sequence numbers as defined in the AX.25
    Specification.
    """

    vs: RolloverCounter = field(
        default_factory=lambda: RolloverCounter(name="Send State Variable")
    )
    vr: RolloverCounter = field(
        default_factory=lambda: RolloverCounter(name="Receive State Variable")
    )
    # Acknowledgement has to start at the maximum so the initial zeroth frame will be
    # forward.
    va: RolloverCounter = field(
        default_factory=lambda: RolloverCounter(
            name="Acknowledge State Variable", initial=AX25_SEQ_MAX
        )
    )
    # Not a rollover counter like the others. This is keeping track of how many frames
    # we've received without sending an acknowledgement of some kind. If this hits
    # a high enough amount, we need to send an RR manually to avoid having the
    # connection hang too long.
    received_without_acknowledgement: int = 0
    # Whether we've made a request to retransmit a frame. There can only be one
    # outstanding retransmission request at a time.
    request_retransmit: bool = False
    # We set this true when the other station has indicated that it is busy and unable
    # to accept more frames.
    other_station_busy: bool = False
    outstanding_frames: dict[int, Frame | None] = field(default_factory=dict)
    # Maximum length of a frame in bytes. The primary constraint is the length of the
    # info field, which must shrink based on the length of the header.
    maximum_transmission_unit: int = 256
