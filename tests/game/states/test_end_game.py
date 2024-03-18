from sprawl_runner.game.states.end_game import EndGame


class TestEndGame:
    def test_action_sets_terminal_state(self):
        state = EndGame()
        assert state.is_terminal_state is False

        state.action()

        assert state.is_terminal_state is True
