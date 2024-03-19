from sprawl_runner.main import main


def test_main_happy_path(mocker):
    mocked_basic_console = mocker.patch("sprawl_runner.main.BasicConsole")
    mocked_console_instance = mocked_basic_console.return_value
    mocked_game = mocker.patch("sprawl_runner.main.Game")
    mocked_game_instance = mocked_game.return_value
    mocked_conf = mocker.patch("sprawl_runner.main.conf")
    mocked_conf.settings = {"has_loaded": True}

    main()

    mocked_basic_console.assert_called_once_with()
    mocked_game.assert_called_once_with(mocked_console_instance)
    mocked_game_instance.play.assert_called_once_with()


def test_main_exits_when_config_fails_to_load(mocker):
    mocked_basic_console = mocker.patch("sprawl_runner.main.BasicConsole")
    mocked_console_instance = mocked_basic_console.return_value
    mocked_game = mocker.patch("sprawl_runner.main.Game")
    mocked_conf = mocker.patch("sprawl_runner.main.conf")
    mocked_conf.settings = {"has_loaded": False}

    main()

    mocked_basic_console.assert_called_once_with()
    msg = f"No config file found at: {mocked_conf.config_path}\nSee Sprawl Runner documentation for more details."
    mocked_console_instance.emit.assert_called_once_with(msg)
    mocked_game.assert_not_called()
