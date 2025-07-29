"""
Main application module of the contributed bulletin board system.
"""

import json
import os
import random
import string
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from threading import Lock
from typing import Literal, cast

from pax25 import Application
from pax25.applications.help import Help
from pax25.applications.parsers import (
    ParseError,
    address_parser,
    integer_parser,
    no_arguments,
    pull_segment,
    raw_string_parser,
    string_parser,
)
from pax25.applications.router import (
    CommandContext,
    CommandRouter,
    CommandSpec,
    ParserSpec,
)
from pax25.applications.utils import send_message
from pax25.ax25.address import Address
from pax25.contrib.bulletin_board.types import (
    BoardConnections,
    BoardSettings,
    BoardState,
    Message,
    ReaderState,
)
from pax25.services.connection.connection import Connection
from pax25.types import Version
from pax25.utils import version_string

DEFAULT_MAX_LENGTH = 5000
DEFAULT_SLOTS = 100


def message_headers(message: Message) -> str:
    """
    Format the main headers of a message.
    """
    created_on = (
        str(datetime.fromisoformat(message["created_on"]).strftime("%d/%m/%Y %H:%M:%S"))
        + " "
    )
    to_callsign = f"{message['to_callsign']}".ljust(7, " ")
    from_callsign = f"{message['from_callsign']}".ljust(7, " ")
    return f"{created_on}{to_callsign}{from_callsign}"


def is_party(name: str, message: Message) -> bool:
    """
    Checks if a name (callsign) is party to a message.
    """
    return any(
        (
            message["from_callsign"] == name,
            message["to_callsign"] == name,
        )
    )


def message_preview(message: Message) -> str:
    """
    Create a message preview string, like what would be used in message listings.
    """
    id_text = f"{message['id']}".ljust(4, " ")
    status_text = "R" if message["read"] else "U"
    status_text += "!" if message["private"] else ""
    status_text = status_text.ljust(6, " ")
    message_size = len(message["body"].encode("utf-8")) + len(
        message["subject"].encode("utf-8")
    )
    size = str(f"{message_size}").ljust(5, " ")
    headers = message_headers(message)
    subject_snippet = message["subject"][:30]
    return f"{id_text}{status_text}{size}{headers}{subject_snippet}"


@dataclass
class ListOpts:
    """
    Arguments for the list command.
    """

    direction: Literal[">", "<"] | None
    callsign: Address | None


def listing_parser(spec: ParserSpec) -> ListOpts:
    """
    Parser for the list command.
    """
    args = spec.args.strip()
    if not args:
        return ListOpts(direction=None, callsign=None)
    direction: Literal[">", "<"] | None = None
    direction_segment, remainder = pull_segment(spec.args)
    if direction_segment and direction_segment not in [">", "<"]:
        raise ParseError(
            f"Unrecognized direction: {repr(direction_segment)}. Options are > or <."
        )
    elif direction_segment:
        direction = cast(Literal[">", "<"], direction_segment)
    address = remainder.strip()
    try:
        callsign = Address.from_string(address)
    except ValueError as err:
        raise ParseError(f"{repr(address)} is not a valid callsign.") from err
    return ListOpts(
        direction=direction,
        callsign=callsign,
    )


PROMPT_TEXT = "B,L,K,R,S, H(elp) or I(nfo) >"


class BulletinBoard(Application[BoardSettings]):
    """
    A Personal Bulletin Board System (PBBS) application.

    The bulletin board has the ability to persist its data to disk. By default,
    it will store its data in the current working directory, but the storage file can
    be customized.
    """

    version = Version(major=0, minor=2, patch=0)
    version_string = f"[PAX25-PBBS-{version_string(version)}]"
    short_name = "B"
    board_state: BoardState
    connections: BoardConnections
    _next_id = 1
    _save_lock: Lock
    routers: dict[Literal["home", "subject", "body"], CommandRouter]

    def setup(self) -> None:
        """
        Set up the basic state of the bulletin board system.
        """
        self.connections = {}
        self._save_lock = Lock()
        self.board_state = self.load_board_state()
        self.routers = {
            "home": CommandRouter(
                post_command_func=self.send_prompt,
                default=CommandSpec(
                    command="",
                    help="",
                    parser=string_parser,
                    function=lambda x, _y: self.send_prompt(x),
                ),
            ),
            "subject": CommandRouter(
                default=CommandSpec(
                    command="",
                    help="",
                    parser=string_parser,
                    function=self.set_subject,
                )
            ),
            "body": CommandRouter(
                post_command_func=self.send_prompt,
                default=CommandSpec(
                    command="",
                    help="",
                    parser=raw_string_parser,
                    function=self.handle_body_line,
                ),
            ),
        }
        help_command = Help(self.routers["home"])
        self.routers["home"].add(
            CommandSpec(
                command="list",
                help="\r".join(
                    [
                        "L(ist)       List messages you can read",
                        "L <|> call   List messages to or from a callsign",
                    ]
                ),
                aliases=("l",),
                parser=listing_parser,
                function=self.list_messages,
            ),
            CommandSpec(
                command="lmine",
                help="LM(ine)\rList unread messages addressed to you",
                parser=no_arguments,
                function=self.list_mine,
            ),
            CommandSpec(
                command="read",
                help="R(ead) n\rDisplay message ID n",
                aliases=("r",),
                parser=integer_parser,
                function=self.read_message,
            ),
            CommandSpec(
                command="rmine",
                help="RM(ine)\rRead all unread messages addressed to you",
                parser=no_arguments,
                function=self.read_mine,
            ),
            CommandSpec(
                command="send",
                help="S(end) call\rSend message to callsign",
                parser=address_parser,
                aliases=("s",),
                function=self.compose_message,
            ),
            CommandSpec(
                command="sprivate",
                help="SP(rivate) call\rSend a private message to a callsign.",
                parser=address_parser,
                function=self.send_private,
            ),
            CommandSpec(
                command="kill",
                help="Deletes a message.",
                aliases=("k",),
                parser=integer_parser,
                function=self.kill_message,
            ),
            CommandSpec(
                command="kmine",
                help="Deletes all messages from and to you.",
                parser=no_arguments,
                function=self.kill_mine,
            ),
            CommandSpec(
                command="bye",
                help="B(ye)\rBBS will disconnect",
                function=self.bye,
                parser=no_arguments,
                aliases=("quit",),
            ),
            CommandSpec(
                command="info",
                help="I(nfo)\rLearn about his PBBS software",
                function=self.send_info,
                parser=no_arguments,
            ),
            help_command.spec,
        )

    @property
    def save_file_path(self) -> Path:
        """Get the path to the board's save file."""
        return Path(self.settings.get("save_file_path", "board.json"))

    @property
    def welcome_message(self) -> str:
        """Get the welcome message for the board."""
        welcome_message = self.settings.get("welcome_message") or ""
        if welcome_message:
            welcome_message += "\r"
        return welcome_message

    def load_board_state(self) -> BoardState:
        """
        Load the board's state from the file path specified in the settings.
        """
        if not self.save_file_path.is_file():
            return BoardState(messages={}, version=self.version)
        with open(self.save_file_path, encoding="utf-8") as save_file:
            struct = json.load(save_file)
            loaded_state = cast(BoardState, struct)
            return loaded_state

    def send_prompt(self, connection: Connection) -> None:
        """
        Send the command prompt.
        """
        if connection not in self.connections:
            return
        state = self.connections[connection]
        if state.mode == "home":
            send_message(connection, "B,L,K,R,S, H(elp) or I(nfo) >")

    @property
    def next_id(self) -> int:
        """
        Get the next available board message ID. We recycle board IDs since
        we could be running for a very long time, and we have space to burn.
        """
        if str(self._next_id) not in self.board_state["messages"]:
            return self._next_id
        while str(self._next_id) in self.board_state["messages"]:
            self._next_id += 1
        return self._next_id

    def _save_board_state(self) -> None:
        """
        Persist the board's state to disk. First write to a temporary file, then
        overwrite the original. This way we can revert to backup if we fail mid-dump.

        Don't call this directly. .save() instead.
        """
        cookie = "".join(random.choice(string.ascii_lowercase) for _ in range(10))
        tmp_path = self.save_file_path.with_suffix(f".{cookie}.tmp")
        with open(tmp_path, "w", encoding="utf-8") as tmp_file:
            json.dump(
                self.board_state,
                tmp_file,
                indent=2 if self.settings.get("debug", False) else None,
            )
        os.replace(tmp_path, self.save_file_path)

    def save(self) -> None:
        """
        Locks the db for save and saves it in an awaitable manner.
        """
        with self._save_lock:
            self._save_board_state()

    def reset_state(self, connection: Connection) -> None:
        """
        Set the user's state to a blank default-- puts them to the home mode.
        """
        self.connections[connection] = ReaderState(
            mode="home",
            body="",
            subject="",
            to_callsign="",
            private=False,
        )

    def on_startup(self, connection: Connection) -> None:
        """Set up the user's connection state and greet them."""
        self.reset_state(connection)
        callsign = connection.first_party.name
        unread_count = len(
            [
                message
                for message in self.board_state["messages"].values()
                if message["to_callsign"] == callsign and not message["read"]
            ]
        )
        unread_segment = ""
        if unread_count:
            plural = "s" if unread_count != 1 else ""
            unread_segment = f"\rYou have {unread_count} unread message{plural}."
        slots_status = ""
        slots = self.settings.get("slots", DEFAULT_SLOTS)
        if slots is not None:
            remaining = max(0, slots - len(self.board_state["messages"]))
            plural = "s" if slots != 1 else ""
            slots_status = f"\r{remaining} of {slots} message slot{plural} available."
        greeting = (
            f"{self.version_string}{self.welcome_message}{unread_segment}{slots_status}"
        )
        greeting += f"\r{PROMPT_TEXT}"
        send_message(connection, greeting)

    def on_shutdown(self, connection: Connection) -> None:
        """Clear the user's connection state."""
        del self.connections[connection]

    def handle_body_line(
        self,
        connection: Connection,
        context: CommandContext[str],
    ) -> None:
        """Handle input when composing a message body."""
        # Default maximum message length is 5000 characters.
        state = self.connections[connection]
        size_limit = self.settings.get("max_message_length", DEFAULT_MAX_LENGTH)
        message = context.raw_input
        if message.rstrip() != "/EX":
            state.body += message + "\r"
            if size_limit is not None:
                state.body = state.body[:size_limit]
                if len(state.body) >= size_limit:
                    send_message(
                        connection,
                        "Message body size limit reached. Type /EX to exit.",
                    )
                    return
            return
        self.board_state["messages"][str(self.next_id)] = Message(
            id=self.next_id,
            to_callsign=state.to_callsign,
            from_callsign=connection.first_party.name,
            subject=state.subject,
            body=state.body,
            created_on=datetime.now(UTC).astimezone().isoformat(),
            read=False,
            private=state.private,
        )
        self.save()
        self.reset_state(connection)
        send_message(connection, "Message saved.")

    def send_listing(self, connection: Connection, messages: Iterable[Message]) -> None:
        """
        Given a list of messages, send all of them to the client.
        """
        # May be a generator. Resolve, in that case, so we can check for emptiness.
        messages = list(messages)
        if not messages:
            send_message(connection, "No messages available.")
            return
        send_message(
            connection,
            "ID# Flags Size Date        Time     To     From   Subject",
        )
        send_message(
            connection,
            "\r".join([message_preview(message) for message in messages]),
        )

    def list_mine(self, connection: Connection, _context: CommandContext[None]) -> None:
        """
        List all messages addressed to the current user.
        """
        self.send_listing(
            connection,
            [
                message
                for message in reversed(self.board_state["messages"].values())
                if message["to_callsign"] == connection.first_party.name
            ],
        )

    def can_read(self, connection: Connection, message: Message) -> bool:
        """
        Determines if a connected user has the right to read this message.
        """
        if self.is_admin(connection):
            return True
        if not message["private"]:
            return True
        return is_party(connection.first_party.name, message)

    def readable(self, connection: Connection) -> Iterable[Message]:
        """
        Yields all messages which can be read by a connected user.
        """
        for message in reversed(self.board_state["messages"].values()):
            if self.can_read(connection, message):
                yield message

    def list_messages(
        self,
        connection: Connection,
        context: CommandContext[ListOpts],
    ) -> None:
        """
        List messages.
        """
        if not (context.args.callsign and context.args.direction):
            self.send_listing(
                connection,
                self.readable(connection),
            )
            return

        attr: Literal["from_callsign", "to_callsign"]
        attr = "from_callsign" if context.args.direction == "<" else "to_callsign"
        self.send_listing(
            connection,
            [
                message
                for message in self.readable(connection)
                if message[attr] == str(context.args.callsign.name)
            ],
        )

    def read_mine(self, connection: Connection, _context: CommandContext[None]) -> None:
        """
        Read all messages addressed to the current user.
        """
        messages = [
            message
            for message in reversed(self.board_state["messages"].values())
            if message["to_callsign"] == connection.first_party.name
            and not message["read"]
        ]
        for message in messages:
            self.perform_read(connection, message, save=False)
        self.save()

    def perform_read(
        self, connection: Connection, message: Message, save: bool = True
    ) -> None:
        """
        Send a message to a user, and mark it read.
        """
        private_prefix = "!!PRIVATE!! " if message["private"] else ""
        body = message["body"]
        # Should always have a newline at the end.
        if body and body[-1] != "\r":
            body += "\r"
        send_message(
            connection,
            f"ID#{message['id']} {message_headers(message)}\r{private_prefix}SUBJECT: "
            f"{message['subject']}\r{body}",
            append_newline=False,
        )
        if message["to_callsign"] == connection.first_party.name:
            message["read"] = True
            if save:
                self.save()

    def read_message(
        self,
        connection: Connection,
        context: CommandContext[int],
    ) -> None:
        """
        Read a given message ID
        """
        number = str(context.args)
        if (number not in self.board_state["messages"]) or not (
            self.can_read(connection, self.board_state["messages"][number])
        ):
            send_message(connection, f"Could not find message with ID {number}")
        message = self.board_state["messages"][number]
        self.perform_read(connection, message)

    def bye(self, connection: Connection, _context: CommandContext[None]) -> None:
        """
        Command for closing the connection.
        """
        send_message(connection, "Goodbye!")
        connection.disconnect()

    def compose_message(
        self,
        connection: Connection,
        context: CommandContext[Address],
        private: bool = False,
    ) -> None:
        """
        Compose a message. We'd call this function 'send' or 'send_message', but those
        are reserved by the parent class.

        More specifically, this starts the composition by changing the mode. The rest
        of the composition work is handled in on_message.
        """
        slots = self.settings.get("slots", DEFAULT_SLOTS)
        if slots is not None and slots <= len(self.board_state["messages"]):
            send_message(
                connection,
                "The message board is full. You cannot send any more messages.",
            )
            return
        state = self.connections[connection]
        state.to_callsign = context.args.name
        state.mode = "subject"
        state.private = private
        send_message(connection, "SUBJECT: ", append_newline=False)

    def send_private(
        self, connection: Connection, context: CommandContext[Address]
    ) -> None:
        """
        Send a private message.
        """
        self.compose_message(connection, context, private=True)

    def kill_mine(self, connection: Connection, _context: CommandContext[None]) -> None:
        """
        Kills all read messages addressed to the current user.
        """
        count = 0
        lowest = self._next_id
        name = connection.first_party.name
        # Iterating over a coerced list here so that we're not modifying the dictionary
        # as the key, value pairs are being generated.
        for key, message in list(self.board_state["messages"].items()):
            if message["read"] and message["to_callsign"] == name:
                lowest = min(lowest, message["id"])
                del self.board_state["messages"][key]
                count += 1
        if count:
            self.save()
        self._next_id = lowest
        plural = "" if count == 1 else "s"
        send_message(connection, f"\r{count} message{plural} deleted.")

    def kill_message(
        self,
        connection: Connection,
        context: CommandContext[int],
    ) -> None:
        """
        Delete a message from the database.
        """
        number = str(context.args)
        if number not in self.board_state["messages"]:
            send_message(
                connection,
                f"Could not find message with ID {number}.",
            )
        message = self.board_state["messages"][number]
        if self.is_admin(connection) or is_party(connection.first_party.name, message):
            del self.board_state["messages"][number]
            self.save()
            self._next_id = min([self._next_id, int(number)])
            send_message(connection, f"Message {number} deleted.")
            return
        # Do not reveal this message exists.
        if message["private"]:
            send_message(connection, f"Could not find message with ID {number}.")
        send_message(
            connection,
            f"You do not have permission to kill message {number}.",
        )
        return

    def send_info(self, connection: Connection, _context: CommandContext[None]) -> None:
        """
        Send an informational message about this board system.
        """
        info_lines = [
            "## Pax25 PBBS",
            "Welcome to the Pax25 reference bulletin board implementation. Pax25 is a "
            "python library for creating packet radio applications. You are invited to "
            "join in on the fun by visiting us at: ",
            "",
            "https://foxyfoxie.gitlab.io/pax25/",
            "",
            "Pax25 was developed by KW6FOX, K1LEO, and KF0KAA. Additional contribution "
            "credit can be found on the GitLab repository homepage.",
        ]
        send_message(connection, "\r".join(info_lines))

    def set_subject(self, connection: Connection, spec: CommandContext[str]) -> None:
        """
        Sets the subject of the mail.
        """
        state = self.connections[connection]
        state.subject = spec.raw_input[:150]
        state.mode = "body"
        response = "ENTER MESSAGE--END WITH /EX ON A SINGLE LINE"
        max_length = self.settings.get("max_message_length", DEFAULT_MAX_LENGTH)
        if max_length is not None:
            response += f" (MAX {max_length} CHARS)"
        send_message(connection, response)

    def on_message(self, connection: Connection, message: str) -> None:
        """
        Perform the command routing.
        """
        state = self.connections[connection]
        self.routers[state.mode].route(connection, message)
