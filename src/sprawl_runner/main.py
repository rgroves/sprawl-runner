import sys

from sprawl_runner.config import config
from sprawl_runner.consoles.basic_console import BasicConsole
from sprawl_runner.game.game import Game
from sprawl_runner.game.states.start_game import StartGame


def main() -> None:
    console = BasicConsole()

    try:
        config.load_settings()
    except FileNotFoundError as error:
        console.emit(str(error))
        sys.exit(1)

    game = Game(console)
    game.change_state(StartGame())
    game.play()


if __name__ == "__main__":
    main()
