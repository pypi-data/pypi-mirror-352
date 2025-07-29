"""
Utility functions/coroutines for the pax25 project.
"""

import asyncio
import os
import random
import string
from asyncio import CancelledError, Future, Task
from collections import defaultdict
from collections.abc import Callable, Coroutine, Generator, Iterable
from contextlib import suppress
from dataclasses import dataclass
from functools import partial, singledispatch
from typing import (
    TYPE_CHECKING,
    Any,
    ParamSpec,
    TypeVar,
    cast,
)

if TYPE_CHECKING:  # pragma: no cover
    from pax25.interfaces.types import Interface
    from pax25.station import Station
    from pax25.types import Updatable, Version

P = ParamSpec("P")
R = TypeVar("R")


def async_wrap(func: Callable[P, R]) -> Callable[P, Coroutine[None, None, R]]:
    """
    Wraps a function that requires syncronous operation so it can be awaited instead
    of blocking the thread.

    Shamelessly stolen and modified from:
    https://dev.to/0xbf/turn-sync-function-to-async-python-tips-58nn
    """

    async def run(*args: P.args, **kwargs: P.kwargs) -> R:
        loop = asyncio.get_event_loop()
        part = partial(func, *args, **kwargs)
        return await loop.run_in_executor(None, part)

    return run


class EnumReprMixin:
    """
    Mixin for enums that allows their export to remain copy-pastable for instantiation.
    """

    def __repr__(self) -> str:
        """
        Repr for an Enum that allows for copy-pastable instantiation.
        """
        return f"{self.__class__.__name__}.{self._name_}"  # type: ignore [attr-defined]


def digipeater_factor(*, interval: int, hops: int, constant: int = 1000) -> int:
    """
    Returns a modified length of time based on the number of digipeaters used.

    Each digipeater increases the amount of time required between retries.
    """
    # For now, assuming this is a straight multiplication factor, though maybe we should
    # add some additional padding for processing time.
    constant = constant if hops else 0
    return (hops + 1) * interval + constant


async def cancel(task: Task[Any]) -> None:
    """
    Cancels a task, and then waits for it to be cleaned up.
    """
    task.cancel()
    with suppress(CancelledError):
        await task


async def cancel_all(tasks: Iterable[Task[Any] | None]) -> list[None]:
    """
    Cancel a series of tasks. Returns a None for each task as they are cancelled,
    useful for closing out optionally running tasks.
    """
    results: list[None] = []
    for task in tasks:
        if task is not None:
            await cancel(task)
        results.append(None)
    return results


@singledispatch
def normalize_line_endings(data: bytes) -> bytes:
    """
    Normalize line endings in a bytestring to be sensible on the target sytem.
    """
    return (
        data.replace(b"\r\n", b"\r")
        .replace(b"\n", b"\r")
        .replace(b"\r", os.linesep.encode("utf-8"))
    )


def generate_nones(times: int | None) -> Generator[None]:
    """
    Generator that yields however many Nones as you specify, or an infinite number
    of Nones if times is None.

    This is primarily to normalize loops that could be either a certain amount of
    iterations or forever.
    """
    if times is None:
        while True:
            yield
    else:
        for _ in range(times):
            yield


@dataclass(kw_only=True, frozen=True)
class PortSpec:
    """
    Named tuple for Interface identities as enumerated by the gateways_for function.
    """

    number: int
    name: str
    type: str


type GatewayDict = dict["Interface", PortSpec]


def gateways_for(station: "Station") -> GatewayDict:
    """
    Retrieve all gateways from a station in numerical order.
    """
    gateways: dict[Interface, PortSpec] = {}
    number = 0
    for key, value in station.interfaces.items():
        if value.gateway:
            number += 1
            gateways[value] = PortSpec(number=number, name=key, type=value.type)
    return gateways


def smart_clone[T](
    item: T,
) -> T:
    """
    This makes a copy of item, with a few caveats:

    1. The copy will copy all references to primitive immutable items (str, int, float).
    2. The copy will create independent copies of all containers it understands.
    3. If the object is not recognized and mutable, copies reference.
    4. It can't handle self-referential structures. So don't hand it any, or you'll get
       an infinite loop.

    The standard clone function is a shallow clone that doesn't clone recursively.
    The deep cloning function is TRULY deep in a way that could cause problems in the
    case that we're cloning something like the settings of the file interface, and it's
    been handed a buffer.

    This is a middle ground-- the primary data structures are all rebuilt so their
    contents aren't affected when you modify the result you get. However, for objects
    which are more complicated than primitives and the basic data structures, we copy
    existing references rather than cloning deeply.
    """
    result: Any

    match item:
        case tuple():
            # Could be a NamedTuple, so clone with class.
            result = item.__class__(*(smart_clone(entry) for entry in item))
        case list():
            result = [smart_clone(entry) for entry in item]
        case defaultdict():
            result = defaultdict(item.default_factory)
            for key, value in item.items():
                result[smart_clone(key)] = smart_clone(value)
        case dict():
            result = {
                smart_clone(key): smart_clone(value) for key, value in item.items()
            }
        case set():
            result = {smart_clone(item) for item in item}
        case _:
            result = item
    return cast(T, result)


D = TypeVar("D", bound="Updatable")


def maybe_update(to_update: D, new_values: None | D) -> D:
    """
    Updates a dictionary if new_values is not None. Useful for config structs which
    may not have a value, to avoid needlessly verbose if chains.

    Returns the updated dict for convenience, but it is indeed mutated in place.
    """
    if new_values is None:
        return to_update
    to_update.update(new_values)
    return to_update


def random_ascii_data() -> bytes:
    """
    Generates a significant amount of ASCII bytes data for transfer-- enough to exhaust
    the frame window.
    """
    data = bytearray()
    letters = string.ascii_lowercase
    for _ in range(10):
        # 256 is the default MTU, and we want our lines to be longer than that so they
        # have to be broken up. We also don't want the commands to be exactly the size
        # of the MTU so we know they're sent/received correctly.
        data.extend(
            int.from_bytes(random.choice(letters).encode("ascii")) for __ in range(300)
        )
        data.append(int.from_bytes(b"\r"))
    return bytes(data)


async def first(*args: Task[None] | Future[None]) -> None:
    """
    Waits until the first in a set of futures returns.
    """
    await asyncio.wait(
        tuple(task for task in args if task),
        return_when=asyncio.FIRST_COMPLETED,
    )


def version_string(version: "Version") -> str:
    """
    Constructs a version string from a version dictionary.
    """
    return f"{version['major']}.{version['minor']}.{version['patch']}"


class LazyRepr:
    """
    Utility class that stringifies to the repr of the object handed to it. Useful to
    make sure the logs show the full details of a packet without going through the
    translation even when we're not debugging.
    """

    def __init__(self, target: Any):
        self.target = target

    def __str__(self) -> str:
        return repr(self.target)

    def __eq__(self, other: Any) -> bool:
        """
        Should allow us to test for this kind of argument in tests.
        """
        if not isinstance(other, LazyRepr):
            return False
        return bool(other.target == self.target)
