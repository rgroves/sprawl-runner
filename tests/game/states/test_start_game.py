from sprawl_runner.game.states.end_game import EndGame
from sprawl_runner.game.states.start_game import StartGame


class TestStartGame:
    def test_action_returns_different_state_if_input_is_not_q(self, mocker):
        mocker.patch("builtins.input", return_value="")
        state = StartGame()

        new_state = state.action()

        assert type(new_state) != type(state)

    def test_action_returns_end_game_state_if_input_is_q(self, mocker):
        mocker.patch("builtins.input", return_value="q")
        state = StartGame()

        new_state = state.action()

        assert type(new_state) is EndGame
