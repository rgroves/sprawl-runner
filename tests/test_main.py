import pytest

from sprawl_runner.main import main


def test_main_happy_path(mocker):
    mocked_basic_console = mocker.patch("sprawl_runner.main.BasicConsole")
    mocked_conf = mocker.patch("sprawl_runner.main.config")
    mocked_console_instance = mocked_basic_console.return_value
    mocked_game = mocker.patch("sprawl_runner.main.Game")
    mocked_game_instance = mocked_game.return_value
    mocked_message_bus = mocker.patch("sprawl_runner.main.AssistantMessageBus")
    mocked_message_bus_instance = mocked_message_bus.return_value
    mocked_start_game = mocker.patch("sprawl_runner.main.StartGame")

    main()

    mocked_basic_console.assert_called_once_with()
    mocked_conf.load_settings.assert_called_once_with()
    mocked_conf.validate.assert_called_once_with()
    mocked_game.assert_called_once_with(mocked_console_instance)
    mocked_game_instance.get_tool_handlers.assert_called_once_with()
    mocked_message_bus.assert_called_once()
    mocked_message_bus_instance.register_tool_handlers.assert_called_once_with(
        mocked_game_instance.get_tool_handlers.return_value
    )
    mocked_game_instance.change_state.assert_called_once_with(mocked_start_game.return_value)
    mocked_game_instance.play.assert_called_once_with()


def test_main_exits_when_config_fails_to_load(mocker):
    mocked_basic_console = mocker.patch("sprawl_runner.main.BasicConsole")
    mocked_console_instance = mocked_basic_console.return_value
    mocked_game = mocker.patch("sprawl_runner.main.Game")

    mocked_message_bus = mocker.patch("sprawl_runner.main.AssistantMessageBus")
    exception = FileNotFoundError("test exceptions")
    mocked_conf_load_settings = mocker.patch("sprawl_runner.main.config.load_settings", side_effect=exception)
    mocked_conf_validate = mocker.patch("sprawl_runner.main.config.validate")

    with pytest.raises(SystemExit):
        main()

    mocked_basic_console.assert_called_once_with()
    mocked_conf_load_settings.assert_called_once_with()
    mocked_console_instance.emit.assert_called_once_with(str(exception))
    mocked_game.assert_not_called()
    mocked_conf_validate.assert_not_called()
    mocked_message_bus.assert_not_called()
