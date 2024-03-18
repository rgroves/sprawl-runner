from sprawl_runner.game.states.end_game import EndGame
from sprawl_runner.game.states.start_game import StartGame


class TestStartGame:
    def test_action_returns_end_game_state_if_enter_is_hit(self, mocker):
        mocker.patch("builtins.input", return_value="")
        state = StartGame()

        new_state = state.action()

        assert type(new_state) == EndGame

    def test_action_returns_none_if_enter_is_not_hit(self, mocker):
        mocker.patch("builtins.input", return_value=mocker.MagicMock())
        state = StartGame()

        new_state = state.action()

        assert new_state is None
