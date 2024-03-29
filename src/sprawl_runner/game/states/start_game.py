from __future__ import annotations

from sprawl_runner.game.states.end_game import EndGame
from sprawl_runner.game.states.game_state import GameState
from sprawl_runner.game.states.initialize_game_world import InitializeGameWorld


class StartGame(GameState):
    def action(self) -> GameState:
        player_input = input("Hit Enter to start or q to exit: ")
        return EndGame() if player_input == "q" else InitializeGameWorld()
