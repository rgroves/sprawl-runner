from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sprawl_runner.consoles.console import Console
    from sprawl_runner.game.states.game_state import GameState


class Game:
    def __init__(self, console: Console):
        self._console = console
        self._state: GameState | None = None

    def change_state(self, new_state: GameState):
        new_state.game = self
        self._state = new_state

    def emit(self, data: str) -> None:
        self._console.emit(data)

    def play(self) -> None:
        if not self._state:
            return  # TODO: this should raise a custom exception instead of returning.

        while not self._state.is_terminal_state:
            self._state.transition()
