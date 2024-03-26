import pytest

from sprawl_runner.main import main


def test_main_happy_path(mocker):
    mocked_basic_console = mocker.patch("sprawl_runner.main.BasicConsole")
    mocked_console_instance = mocked_basic_console.return_value
    mocked_game = mocker.patch("sprawl_runner.main.Game")
    mocked_game_instance = mocked_game.return_value

    main()

    mocked_basic_console.assert_called_once_with()
    mocked_game.assert_called_once_with(mocked_console_instance)
    mocked_game_instance.play.assert_called_once_with()


def test_main_exits_when_config_fails_to_load(mocker):
    mocked_basic_console = mocker.patch("sprawl_runner.main.BasicConsole")
    mocked_console_instance = mocked_basic_console.return_value
    mocked_game = mocker.patch("sprawl_runner.main.Game")
    exception = FileNotFoundError("test exceptions")
    mocked_conf_load_settings = mocker.patch("sprawl_runner.main.config.load_settings", side_effect=exception)

    with pytest.raises(SystemExit):
        main()

    mocked_basic_console.assert_called_once_with()
    mocked_conf_load_settings.assert_called_once_with()
    mocked_console_instance.emit.assert_called_once_with(str(exception))
    mocked_game.assert_not_called()
