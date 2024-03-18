from unittest.mock import Mock

import pytest

from sprawl_runner.consoles.basic_console import BasicConsole


@pytest.fixture
def mock_input(mocker) -> Mock:
    mock = Mock()
    mocker.patch("builtins.input", return_value=mock)
    return mock


class TestBasicConsole:
    def test_emit_outputs_expected_data(self, capsys):
        console = BasicConsole()
        msg = "Test"
        console.emit(msg)
        captured = capsys.readouterr()
        assert captured.out == f"{msg}\n"

    def test_player_input(self, mock_input):
        console = BasicConsole()
        data = console.get_player_input()
        assert data == mock_input
