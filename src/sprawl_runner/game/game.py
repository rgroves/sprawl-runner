from __future__ import annotations

import sys
from typing import TYPE_CHECKING, TypedDict

from sprawl_runner.ai.constants import TOOL_REGISTER_FACTIONS, TOOL_REGISTER_LOCATIONS

if TYPE_CHECKING:
    from sprawl_runner.ai.assistant_message_bus import AssistantMessageBus
    from sprawl_runner.ai.types import ToolHandlerEntry
    from sprawl_runner.consoles.console import Console
    from sprawl_runner.game.states.game_state import GameState


class Faction(TypedDict):
    name: str
    description: str
    motivation: str


class Location(TypedDict):
    name: str
    type: str
    description: str


class Game:
    MAX_ITERS_WITHOUT_STATE_CHANGE = 15

    def __init__(self, console: Console):
        self._console = console
        self._message_bus: AssistantMessageBus | None = None
        self._state: GameState | None = None
        self.factions: list[Faction] = []
        self.locations: list[Location] = []
        self.iterations_without_state_change = 0

    @property
    def message_bus(self):
        if self._message_bus:
            return self._message_bus

        msg = "Game.message_bus has not been set."
        raise AttributeError(msg)

    @message_bus.setter
    def message_bus(self, value: AssistantMessageBus):
        if not self._message_bus:
            self._message_bus = value
        else:
            msg = "Cannot re-assign message_bus."
            raise AttributeError(msg)

    def get_tool_handlers(self) -> list[ToolHandlerEntry]:
        return [
            (TOOL_REGISTER_FACTIONS, self.register_factions),
            (TOOL_REGISTER_LOCATIONS, self.register_locations),
        ]

    def change_state(self, new_state: GameState):
        if self._state != new_state:
            new_state.game = self
            self._state = new_state
            self.iterations_without_state_change = 0

    def emit(self, data: str) -> None:
        self._console.emit(data)

    def play(self) -> None:
        if not self._state:
            msg = "Invalid game state encountered."
            raise RuntimeError(msg)

        while not self._state.is_terminal_state:
            self._state.transition()
            self.iterations_without_state_change += 1
            if self.iterations_without_state_change > self.MAX_ITERS_WITHOUT_STATE_CHANGE:
                # Safety check in case there is a "stuck in state" issue.
                # This shouldn't happen... <cough!>
                # If the OpenAI Assistant doesn't make the expected tool calls it can happen.
                self.emit("There was a glitch in the Matrix.")
                sys.exit(1)

    def register_factions(self, arguments: dict[str, list]) -> str:
        for entry in arguments["factions"]:
            faction = Faction(
                name=entry.get("name"),
                description=entry.get("description"),
                motivation=entry.get("motivation"),
            )
            self.factions.append(faction)
        return "OK"

    def register_locations(self, arguments: dict[str, list]) -> str:
        for entry in arguments["locations"]:
            location = Location(
                name=entry.get("name"),
                type=entry.get("type"),
                description=entry.get("description"),
            )
            self.locations.append(location)
        return "OK"

    def validate(self) -> None:
        if not self._message_bus:
            msg = "Message Bus has not been set."
            raise ValueError(msg)  # TODO: Error handling
