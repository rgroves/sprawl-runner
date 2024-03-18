from sprawl_runner.consoles.console import Console


class BasicConsole(Console):
    def emit(self, data: str) -> None:
        print(data)  # noqa: T201

    def get_player_input(self) -> str:
        return input()
