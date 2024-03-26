import pytest

from sprawl_runner.ai.assistant_message_bus import AssistantMessageBus
from sprawl_runner.ai.constants import TOOL_REGISTER_FACTIONS, TOOL_REGISTER_LOCATIONS
from sprawl_runner.consoles.console import Console
from sprawl_runner.game.game import Game
from sprawl_runner.game.states.game_state import GameState


class TestGame:
    @pytest.fixture
    def mock_console(self, mocker):
        return mocker.create_autospec(Console, instance=True)

    @pytest.fixture
    def mock_message_bus(self, mocker):
        return mocker.create_autospec(AssistantMessageBus, instance=True)

    @pytest.fixture
    def mock_state(self, mocker):
        return mocker.create_autospec(GameState, instance=True)

    def test_can_instantiate(self, mock_console):
        game = Game(mock_console)

        assert game._console == mock_console  # noqa: SLF001
        assert game._state is None  # noqa: SLF001

    def test_change_state_updates_state(self, mock_console, mock_state):
        game = Game(mock_console)
        assert game._state is None  # noqa: SLF001

        game.change_state(mock_state)

        assert game._state == mock_state  # noqa: SLF001

    def test_emit_sends_data_to_console(self, mock_console):
        game = Game(mock_console)
        data = "test"

        game.emit(data)

        mock_console.emit.assert_called_once_with(data)

    def test_get_tool_handlers_returns_correct_handlers(self, mock_console):
        game = Game(mock_console)

        # Retrieve the tool handlers list from the game instance
        tool_handlers = game.get_tool_handlers()

        # Define the expected list of tool handlers
        expected_handlers = [
            (TOOL_REGISTER_FACTIONS, game.register_factions),
            (TOOL_REGISTER_LOCATIONS, game.register_locations),
        ]

        # Verify that the returned list matches the expected list
        assert tool_handlers == expected_handlers, "get_tool_handlers did not return the expected tool handlers."

        # Additionally, verify that the list contains the correct methods associated with each tool name
        for tool_name, handler in tool_handlers:
            assert callable(handler), f"The handler for {tool_name} should be a callable method."

    def test_message_bus_getter_raises_when_none(self, mock_console):
        game = Game(mock_console)

        with pytest.raises(AttributeError, match="Game.message_bus has not been set."):
            assert game.message_bus is None

    def test_message_bus_setter_prevents_reassignment(self, mocker, mock_console, mock_message_bus):
        game = Game(mock_console)
        game.message_bus = mock_message_bus

        with pytest.raises(AttributeError, match="Cannot re-assign message_bus."):
            game.message_bus = mocker.create_autospec(AssistantMessageBus, instance=True)

    def test_message_bus_setter_successful_assignment(self, mock_console, mock_message_bus):
        game = Game(mock_console)

        game.message_bus = mock_message_bus
        assert game.message_bus is mock_message_bus, "message_bus was not set correctly"

    def test_play_does_not_transition_state_when_state_is_terminal(self, mock_console, mock_state):
        game = Game(mock_console)
        game._state = mock_state  # noqa: SLF001

        game.play()

        mock_state.transition.assert_not_called()

    def test_play_does_transition_state_when_state_is_non_terminal(self, mocker, mock_console, mock_state):
        type(mock_state).is_terminal_state = mocker.PropertyMock(side_effect=[False, True])
        game = Game(mock_console)
        game._state = mock_state  # noqa: SLF001

        game.play()

        mock_state.transition.assert_called_once_with()

    def test_play_raises_runtime_error_when_no_state_is_set(self, mock_console):
        game = Game(mock_console)
        assert game._state is None  # noqa: SLF001
        msg = "Invalid game state encountered."

        with pytest.raises(RuntimeError, match=msg):
            game.play()

    def test_register_factions_correctly(self, mock_console):
        faction_data = {
            "factions": [
                {
                    "name": "Faction1",
                    "description": "Desc1",
                    "motivation": "Motivation1",
                },
                {
                    "name": "Faction2",
                    "description": "Desc2",
                    "motivation": "Motivation2",
                },
            ]
        }
        expected_result = "OK"
        game = Game(mock_console)

        result = game.register_factions(faction_data)

        assert result == expected_result, "register_factions should return 'OK'"
        assert len(game.factions) == 2, "Two factions should have been registered."
        assert game.factions[0]["name"] == "Faction1", "First faction's name should be 'Faction1'"
        assert game.factions[1]["name"] == "Faction2", "Second faction's name should be 'Faction2'"

    def test_register_factions_with_empty_arguments(self, mock_console):
        faction_data = {"factions": []}
        expected_result = "OK"
        game = Game(mock_console)

        result = game.register_factions(faction_data)

        assert result == expected_result, "register_factions should return 'OK' even with empty factions list"
        assert len(game.factions) == 0, "No factions should have been registered."

    def test_register_locations_correctly(self, mock_console):
        location_data = {
            "locations": [
                {"name": "Location1", "type": "Type1", "description": "Desc1"},
                {"name": "Location2", "type": "Type2", "description": "Desc2"},
            ]
        }
        expected_result = "OK"
        game = Game(mock_console)

        result = game.register_locations(location_data)

        assert result == expected_result, "register_locations should return 'OK'"
        assert len(game.locations) == 2, "Two locations should have been registered."
        assert game.locations[0]["name"] == "Location1", "First location's name should be 'Location1'"
        assert game.locations[1]["name"] == "Location2", "Second location's name should be 'Location2'"

    def test_register_locations_with_empty_arguments(self, mock_console):
        location_data = {"locations": []}
        expected_result = "OK"
        game = Game(mock_console)

        result = game.register_locations(location_data)

        assert result == expected_result, "register_locations should return 'OK' even with empty locations list"
        assert len(game.locations) == 0, "No locations should have been registered."

    def test_validate_does_not_raise_when_game_instance_is_valid(self, mock_console, mock_message_bus):
        game = Game(mock_console)
        game.message_bus = mock_message_bus

        assert game.validate() is None

    def test_validate_raises_value_error_when_message_bus_not_set(self, mock_console):
        game = Game(mock_console)

        with pytest.raises(ValueError, match="Message Bus has not been set."):
            game.validate()
