from typing_extensions import Protocol


class Console(Protocol):
    def emit(self, data: str) -> None:
        raise NotImplementedError

    def get_player_input(self) -> str:
        raise NotImplementedError
