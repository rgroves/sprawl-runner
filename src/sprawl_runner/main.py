import sprawl_runner.config as conf
from sprawl_runner.consoles.basic_console import BasicConsole
from sprawl_runner.game.game import Game
from sprawl_runner.game.states.start_game import StartGame


def main() -> None:
    console = BasicConsole()

    if not conf.settings["has_loaded"]:
        console.emit(
            f"No config file found at: {conf.config_path}\n" "See Sprawl Runner documentation for more details."
        )
        return

    game = Game(console)
    game.change_state(StartGame())
    game.play()


if __name__ == "__main__":
    main()
