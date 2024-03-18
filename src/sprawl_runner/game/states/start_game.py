from __future__ import annotations

from sprawl_runner.game.states.end_game import EndGame
from sprawl_runner.game.states.game_state import GameState


class StartGame(GameState):
    def action(self) -> GameState | None:
        player_input = input("Hit Enter to exit: ")
        return EndGame() if player_input.lower() == "" else None
