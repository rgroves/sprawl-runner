from sprawl_runner.consoles.basic_console import BasicConsole
from sprawl_runner.game.game import Game
from sprawl_runner.game.states.start_game import StartGame


def main() -> None:
    console = BasicConsole()
    game = Game(console)
    game.change_state(StartGame())
    game.play()


if __name__ == "__main__":
    main()
