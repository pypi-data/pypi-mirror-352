"""
Included generic parser functions which can be used by client developer commands.
"""

from collections.abc import Callable
from typing import TYPE_CHECKING, TypeVar

from pax25.applications.autocomplete import AutocompleteDict
from pax25.ax25.address import Address

if TYPE_CHECKING:
    from pax25.applications.router import ParserSpec


def string_parser(spec: "ParserSpec") -> str:
    """
    Returns the stripped argument string without further modification.
    """
    return spec.args.strip()


def raw_string_parser(spec: "ParserSpec") -> str:
    """
    Does absolutely no processing to the arguments after the command name.

    NOTE: If you need the full input from the user, including the command, use
    the `raw_input` property on the CommandContext.
    """
    return spec.raw_input[len(spec.command) :]


def address_parser(spec: "ParserSpec") -> Address:
    """
    Parses an address from a string.
    """
    value = spec.args.strip().upper()
    if not value:
        raise ParseError("You must specify a callsign/address.")
    try:
        return Address.from_string(value)
    except ValueError as err:
        raise ParseError(f"{repr(value)} is not a valid callsign or address.") from err


def integer_parser(spec: "ParserSpec") -> int:
    """
    Parses an integer.
    """
    value = spec.args.strip()
    if not value:
        raise ParseError("You must specify an integer.")
    try:
        return int(spec.args.strip())
    except ValueError as err:
        raise ParseError(f"{repr(value)} is not a valid integer.") from err


def no_arguments(spec: "ParserSpec") -> None:
    """
    Use when a command accepts no arguments.
    """
    if spec.args.strip():
        raise ParseError("This command takes no arguments.")
    return None


def pull_segment(args: str) -> tuple[str, str]:
    """
    Splits a string once and returns the first segment as well as the remainder.
    """
    result = args.split(maxsplit=1)
    segment = result.pop(0)
    remainder = result[0] if result else ""
    return segment, remainder


def optional[T](
    func: Callable[["ParserSpec"], T],
) -> Callable[["ParserSpec"], None | T]:
    """
    Makes the expected arguments optional. If the args are empty, returns None.
    """

    def wrapped(spec: "ParserSpec") -> None | T:
        if not spec.args.strip():
            return None
        return func(spec)

    return wrapped


def requires_full_name[T](
    func: Callable[["ParserSpec"], T],
) -> Callable[["ParserSpec"], T]:
    """
    Wraps a command parser to first check that the full name of the command was used.
    """

    def wrapped(spec: "ParserSpec") -> T:
        if not spec.command_spec.command.lower() == spec.command.lower():
            raise ParseError(
                f"{repr(spec.command_spec.command)} must be typed in full."
            )
        return func(spec)

    return wrapped


class ParseError(Exception):
    """
    Throw when there is a parsing error.
    """


E = TypeVar("E", bound=str)


def autocompleted_enum(
    options: tuple[E, ...], *, default: E | None = None
) -> Callable[["ParserSpec"], E]:
    """
    A parser which will return a normalized entry.
    """
    lookup: AutocompleteDict[E] = AutocompleteDict()
    for entry in options:
        lookup[entry.lower()] = entry

    def parse_enum(spec: "ParserSpec") -> E:
        """
        Return which entry in the options was used, if any.
        """
        value = spec.args.strip().lower()
        if not value:
            if default is not None:
                return default
            raise ParseError(f"Argument must be one of: {options}")
        try:
            results = lookup[value]
            possibilities = list(sorted(result[1] for result in results))
            if len(results) > 1:
                raise ParseError(
                    f"Ambiguous argument. Could be: {', '.join(possibilities)}"
                )
            result = possibilities[0]
            return result
        except KeyError as err:
            raise ParseError(f"Argument must be one of: {', '.join(options)}") from err

    return parse_enum
