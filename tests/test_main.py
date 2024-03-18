from sprawl_runner.main import main


def test_main(mocker):
    mocked_basic_console = mocker.patch("sprawl_runner.main.BasicConsole")
    mocked_game = mocker.patch("sprawl_runner.main.Game")
    mocked_console_instance = mocked_basic_console.return_value
    mocked_game_instance = mocked_game.return_value

    main()

    mocked_basic_console.assert_called_once_with()
    mocked_game.assert_called_once_with(mocked_console_instance)
    mocked_game_instance.play.assert_called_once_with()
