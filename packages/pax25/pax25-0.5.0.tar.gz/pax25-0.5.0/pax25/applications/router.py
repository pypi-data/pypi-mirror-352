"""
CommandRouter module. We use the command router to route commands for the command line
app. Other apps can use it, too, as it's not strictly bound to the command line app.
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from pax25.applications.autocomplete import AutocompleteDict
from pax25.applications.parsers import ParseError, string_parser
from pax25.applications.utils import send_message
from pax25.exceptions import ConfigurationError
from pax25.services.connection.connection import Connection

type CommandFunc[P] = Callable[[Connection, "CommandContext[P]"], None]

type CommandMap = dict[str, CommandFunc[object]]


@dataclass(frozen=True, kw_only=True)
class CommandSpec[P]:
    """
    Used for defining commands that are used by the command line app, or any other app
    that follows its conventions for commands.
    """

    command: str
    aliases: tuple[str, ...] = tuple()
    # A long description of the command and its usage.
    help: str
    # The function for this command, when run.
    function: CommandFunc[P]
    parser: Callable[["ParserSpec"], P]


@dataclass(frozen=True, kw_only=True)
class ParserSpec:
    # The full raw input line from the user.
    raw_input: str
    # The first segment of the raw input line.
    command: str
    # The remainder of the input line after the command.
    args: str
    connection: Connection
    # Sometimes, we may need to know what the settings of the CommandSpec were to parse.
    # For an example of this, check 'requires_full_command'.
    # However, we need to prevent full type reflection here since parser wrappers may
    # modify types along the way. See the 'optional' wrapper in the parsers module for
    # an example of this.
    command_spec: CommandSpec[Any]


@dataclass()
class CommandContext[P]:
    """
    Context handed to a command.
    """

    spec: CommandSpec[P]
    # The actual command as entered by the user, as interpreted by the command router.
    command: str
    args: P
    # The full raw input from the user, as a string.
    raw_input: str


def default_command_func(connection: Connection, context: CommandContext[str]) -> None:
    """
    Default command used by CommandRouter.
    """
    if not context.command:
        # User entered nothing. Do nothing in response. Works best when the
        # post_command_func is set to show a prompt.
        return
    send_message(connection, f"{repr(context.command)} is not a recognized command.")


default_command: CommandSpec[str] = CommandSpec(
    command="",
    help="",
    function=default_command_func,
    parser=string_parser,
)


def default_post_command_func(_connection: Connection) -> None:
    """
    Default 'Post command'. Does nothing. Overwrite this to provide your own command
    prompt, for instance.
    """


class CommandRouter:
    """
    Router object that allows us to quickly route to command functions based on a
    command string sent by a user.
    """

    def __init__(
        self,
        *,
        default: CommandSpec[Any] = default_command,
        post_command_func: Callable[[Connection], None] = default_post_command_func,
    ) -> None:
        """
        Creates an autocompleting command map that handles input and runs any matching
        command.
        """
        self.command_store: AutocompleteDict[CommandSpec[Any]] = AutocompleteDict()
        # Canonical listing of all command names, used for checking conflicts.
        self.command_set: set[str] = set()
        # Canonical listing of all aliases, used for checking conflicts.
        self.alias_set: set[str] = set()
        self.default = default
        # A 'post command' that runs after a command is complete.
        self.post_command = post_command_func

    @property
    def help_available(self) -> bool:
        """
        Returns a boolean indicating if there's a help command installed.
        """
        try:
            results = self.command_store["HELP"]
            # Help command is ambiguous if there's more than 1.
            # This could still be wrong if there is an entry named something like
            # 'helpmeplz' and it's not a help command. But we're going to discount that
            # possibility here. If it ever becomes a real problem we'll refactor this
            # to something more robust.
            return len(results) == 1
        except KeyError:
            return False

    def add(self, *args: CommandSpec[Any]) -> None:
        """
        Add commands to the command router.
        """
        for arg in args:
            command = arg.command.upper()
            aliases = set(alias.upper() for alias in arg.aliases)
            to_check = (command, *aliases)
            for entry in to_check:
                if entry in self.command_set or entry in self.alias_set:
                    existing_spec = self.command_store[entry]
                    raise ConfigurationError(
                        f"Found preexisting entry with conflicting name or "
                        f"aliases when adding spec {repr(arg)}. Conflicting "
                        f"entry was: {repr(existing_spec)}"
                    )
            for entry in to_check:
                self.command_store[entry] = arg
            self.command_set |= {command}
            self.alias_set |= aliases

    def remove(self, *args: CommandSpec[Any]) -> None:
        """
        Remove commands from the command router.
        """
        for arg in args:
            command = arg.command.upper()
            if command not in self.command_store.store:
                raise KeyError(f"Command does not exist, {repr(arg.command)}")
            if self.command_store.store[command] != arg:
                raise KeyError(
                    f"Command {repr(arg.command)} exists, but is for a different spec!"
                )
            del self.command_store[command]
            self.command_set -= {command}
            for alias in arg.aliases:
                del self.command_store[alias.upper()]
                self.alias_set -= {alias.upper()}

    def route(self, connection: Connection, raw_command: str) -> None:
        """
        Routes a user to a command function based on their selection, or gives them
        a hint otherwise.
        """
        segments = raw_command.split(maxsplit=1)
        try:
            first_segment = segments[0]
            command = first_segment.upper()
        except IndexError:
            # No command specified-- it was an empty string. Run the default.
            context = CommandContext(
                command="",
                args="",
                spec=self.default,
                raw_input="",
            )
            self.default.function(connection, context)
            self.post_command(connection)
            return
        args = ""
        if len(segments) == 2:
            args = segments[1]
        try:
            candidates = self.command_store[command]
        except KeyError:
            context = CommandContext(
                command=first_segment,
                args=args,
                spec=self.default,
                raw_input=raw_command,
            )
            self.default.function(connection, context)
            self.post_command(connection)
            return
        if len(candidates) > 1:
            possibilities = sorted(entry[1].command for entry in candidates)
            send_message(
                connection,
                "Ambiguous command. "
                f"Did you mean one of these?: {', '.join(possibilities)}",
            )
            return
        [selection] = candidates
        (_key, spec) = selection
        try:
            parser_spec = ParserSpec(
                raw_input=raw_command,
                command=command,
                args=args,
                connection=connection,
                command_spec=spec,
            )
            parsed_args = spec.parser(parser_spec)
            context = CommandContext(
                command=first_segment,
                args=parsed_args,
                spec=spec,
                raw_input=raw_command,
            )
        except ParseError as err:
            error_string = str(err)
            if self.help_available:
                error_string += f"\rTry: help {spec.command}"
            send_message(connection, error_string)
            self.post_command(connection)
            return
        selection[1].function(connection, context)
        self.post_command(connection)
