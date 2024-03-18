import pytest

from sprawl_runner.consoles.console import Console
from sprawl_runner.game.game import Game
from sprawl_runner.game.states.game_state import GameState


@pytest.fixture
def mocked_console(mocker):
    return mocker.MagicMock(spec=Console)


@pytest.fixture
def mocked_state(mocker):
    return mocker.MagicMock(spec=GameState)


class TestGame:
    def test_can_instantiate(self, mocked_console):
        game = Game(mocked_console)

        assert game._console == mocked_console  # noqa: SLF001
        assert game._state is None  # noqa: SLF001

    def test_change_state_updates_state(self, mocked_console, mocked_state):
        game = Game(mocked_console)
        assert game._state is None  # noqa: SLF001

        game.change_state(mocked_state)

        assert game._state == mocked_state  # noqa: SLF001

    def test_emit_sends_data_to_console(self, mocked_console):
        game = Game(mocked_console)
        data = "test"

        game.emit(data)

        mocked_console.emit.assert_called_once_with(data)

    def test_play_does_not_transition_state_when_no_state_is_set(self, mocked_console, mocked_state):
        game = Game(mocked_console)
        assert game._state is None  # noqa: SLF001

        game.play()

        mocked_state.transition.assert_not_called()

    def test_play_does_not_transition_state_when_state_is_terminal(self, mocked_console, mocked_state):
        game = Game(mocked_console)
        game._state = mocked_state  # noqa: SLF001

        game.play()

        mocked_state.transition.assert_not_called()

    def test_play_does_transition_state_when_state_is_non_terminal(self, mocker, mocked_console, mocked_state):
        type(mocked_state).is_terminal_state = mocker.PropertyMock(side_effect=[False, True])
        game = Game(mocked_console)
        game._state = mocked_state  # noqa: SLF001

        game.play()

        mocked_state.transition.assert_called_once_with()
