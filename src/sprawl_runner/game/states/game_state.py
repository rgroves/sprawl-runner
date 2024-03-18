from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from sprawl_runner.game.game import Game


class GameState(Protocol):
    _game: Game
    _is_terminal_state: bool = False

    @property
    def game(self) -> Game:
        return self._game

    @game.setter
    def game(self, game: Game):
        self._game = game

    @property
    def is_terminal_state(self) -> bool:
        return self._is_terminal_state

    def action(self) -> GameState | None:
        raise NotImplementedError

    def transition(self) -> None:
        new_state = self.action()
        if new_state:
            self._game.change_state(new_state)

    def emit(self, data) -> None:
        self._game.emit(data)
