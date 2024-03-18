from __future__ import annotations

import pytest

from sprawl_runner.game.states.game_state import GameState


class FakeGameState(GameState):
    def action(self) -> GameState | None:
        return super().action()  # type: ignore


class TestGameState:
    def test_game_property_sets_and_returns_game(self, mocker):
        game_state = FakeGameState()
        game = mocker.MagicMock()
        game_state.game = game
        assert game_state.game == game

    def test_is_terminal_state_property_default_returns_false(self):
        game_state = FakeGameState()
        assert game_state.is_terminal_state is False

    def test_action_raises_not_implemented(self):
        game_state = FakeGameState()
        with pytest.raises(NotImplementedError):
            game_state.action()

    def test_transition_changes_state_when_action_returns_a_game_state(self, mocker):
        new_state = FakeGameState()
        mocker.patch(
            "tests.game.states.test_game_state.FakeGameState.action",
            return_value=new_state,
        )
        mocked_game = mocker.MagicMock()
        game_state = FakeGameState()
        game_state.game = mocked_game

        game_state.transition()

        mocked_game.change_state.assert_called_once_with(new_state)

    def test_transition_does_not_change_state_when_action_returns_none(self, mocker):
        mocker.patch(
            "tests.game.states.test_game_state.FakeGameState.action",
            return_value=None,
        )
        mocked_game = mocker.MagicMock()
        game_state = FakeGameState()
        game_state.game = mocked_game

        game_state.transition()

        mocked_game.change_state.assert_not_called()

    def test_emit_calls_game_emit(self, mocker):
        mocked_game = mocker.MagicMock()
        game_state = FakeGameState()
        game_state.game = mocked_game
        data = "test"

        game_state.emit(data)

        mocked_game.emit.assert_called_once_with(data)
