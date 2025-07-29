"""
Timer functionality. Used for setting up timeout callbacks which can be cancelled as
needed.
"""

import asyncio
from asyncio import CancelledError, Task
from collections.abc import Callable
from enum import Enum
from logging import getLogger

from pax25.utils import EnumReprMixin, generate_nones

log = getLogger(__name__)


class TimerState(EnumReprMixin, Enum):
    """Enum for timer status."""

    INACTIVE = "inactive"
    RUNNING = "running"


class Timer:
    """
    Timer class. Keeps track of outstanding time, an action to perform, and if it's been
    cancelled.
    """

    def __init__(self, name: str) -> None:
        """
        Set up timer. Does not activate. For that, use the schedule function.
        """
        self.name = name
        self.killed = False
        self._sleep_task: Task[None] | None = None

    def __str__(self) -> str:
        """
        String representation of this timer.
        """
        return f"Timer ({self.name} [{self.state.value}])"

    @property
    def state(self) -> TimerState:
        """
        Return the state of the current timer.
        """
        return TimerState.RUNNING if self._sleep_task else TimerState.INACTIVE

    async def run(self, delay: int) -> bool:
        """
        Start this timer, and wait until the time is complete or the timer is cancelled.

        If the task is cancelled, return True. If the timeout elapsed, return False. The
        reason we return true is so you can write something like:

        ```
        if await timer.run(100):
            return
        # Do something if the timer expired here.
        ```

        See the Station class for examples in the `retry_loop` and `delay_action`
        methods.

        If the timer is already running, cancels the old task to replace with the new
        timer.
        """
        if self.killed:
            # Killed timers act as though their tasks have always been cancelled.
            return True
        if self._sleep_task:
            self.cancel()
        task = asyncio.ensure_future(asyncio.sleep(0.001 * delay))
        try:
            self._sleep_task = task
            await self._sleep_task
        except CancelledError:
            return True
        return False

    def cancel(self) -> None:
        """
        Cancels a timer if it's running. Otherwise, does nothing.
        """
        if self._sleep_task is None:
            return
        self._sleep_task.cancel("Timer cancelled.")
        self._sleep_task = None

    def kill(self) -> None:
        """
        Kills a timer. This means that the timer will no longer accept new tasks.
        """
        self.cancel()
        self.killed = True


def retry_loop(
    *,
    timer: Timer,
    retries: int,
    interval: int,
    immediate: bool = True,
    check: Callable[[], bool] = lambda: False,
    action: Callable[[], None],
    fail_action: Callable[[], None] = lambda: None,
) -> Task[None]:
    """
    Retries an action multiple times at a given interval.
    The action will always be run at least once if immediate is true.
    The number of retries determines how many attempts will be made after this.

    `action` is a callable to perform.
    `check` is a callable that will return True if the action we're calling was
    successful, or `false` if not. If not specified, check is a lambda that always
    returns False.
    `fail_action` will be called if all retries failed. If no function is specified,
    performs a no-op.
    `interval` is the number of milliseconds between attempts.

    This function will exit early if the timer it is using was cancelled by an
    outside action. In this case, the fail_action will not be run.
    """
    # Basic sanity checks to avoid infinite loops.
    if retries is not None:
        assert retries >= 0
    assert interval >= 1

    # Cancel any outstanding items before beginning.
    timer.cancel()

    async def wrapped_retry() -> None:
        if immediate:
            action()
        for _ in generate_nones(retries):
            if await timer.run(interval):
                # Timer was cancelled. We bail.
                return
            if check():
                # Check succeeded. We bail.
                return
            action()
        if await timer.run(interval):
            return
        if check():
            return
        fail_action()

    future = asyncio.ensure_future(wrapped_retry())
    return future


def delay_action(*, timer: Timer, action: Callable[[], None], delay: int) -> Task[None]:
    """
    Performs an action if the timer elapses with the given delay in milliseconds.
    """
    assert delay >= 1
    timer.cancel()

    async def wrapped_delayed_action() -> None:
        if await timer.run(delay):
            return
        action()

    return asyncio.ensure_future(wrapped_delayed_action())
