from sprawl_runner.game.states.game_state import GameState


class EndGame(GameState):
    def action(self) -> None:
        self._is_terminal_state = True
