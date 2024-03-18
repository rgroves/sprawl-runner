import pytest

from sprawl_runner.consoles.console import Console


class FakeConsole(Console):
    def emit(self, data):
        super().emit(data)  # type: ignore

    def get_player_input(self) -> str:
        return super().get_player_input()  # type: ignore


class TestConsole:
    def test_emit_raises(self):
        console = FakeConsole()
        with pytest.raises(NotImplementedError):
            console.emit("")

    def test_get_player_input_raises(self):
        console = FakeConsole()
        with pytest.raises(NotImplementedError):
            console.get_player_input()
