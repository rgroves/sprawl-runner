from configparser import ConfigParser
from unittest.mock import create_autospec

import pytest

from sprawl_runner.config.config_file import ConfigFile
from sprawl_runner.config.constants import (
    DEFAULT_AI_MODEL,
    EMPTY_SETTINGS,
    EXPECTED_SETTINGS,
)
from sprawl_runner.config.game_configuration import GameConfiguration


class TestGameConfiguration:
    @pytest.fixture
    def config_file_mock(self):
        return create_autospec(ConfigFile)

    @pytest.fixture
    def game_configuration(self, config_file_mock):
        return GameConfiguration(config_file=config_file_mock)

    def test_init_method(self, game_configuration, config_file_mock):
        assert game_configuration.default_ai_model == DEFAULT_AI_MODEL
        assert (
            game_configuration.assistant_creation_handler == GameConfiguration._unimplemented_handler  # noqa: SLF001
        )
        assert game_configuration._config_file is config_file_mock  # noqa: SLF001
        assert game_configuration._settings == EMPTY_SETTINGS  # noqa: SLF001
        assert not game_configuration._has_dirty_settings  # noqa: SLF001

    def test_load_settings(self, mocker, config_file_mock, game_configuration):
        mock_config_parser = mocker.MagicMock()
        mock_config_parser.get.return_value = "test_value"
        config_file_mock.load.return_value = mock_config_parser
        expected_settings = [("TestSection", "test_key", "default")]
        mocker.patch(
            "sprawl_runner.config.game_configuration.EXPECTED_SETTINGS",
            expected_settings,
        )

        settings = game_configuration.load_settings()

        config_file_mock.load.assert_called_once()
        mock_config_parser.get.assert_called_with("TestSection", "test_key", fallback="default")
        assert settings["test_key"] == "test_value", "The setting was not loaded correctly."

    def test_load_settings_with_defaults(
        self,
        mocker,
        game_configuration,
        config_file_mock,
    ):
        mock_config_parser = ConfigParser()
        config_file_mock.load.return_value = mock_config_parser
        expected_settings = [("TestSection", "test_key", "default")]
        mocker.patch(
            "sprawl_runner.config.game_configuration.EXPECTED_SETTINGS",
            expected_settings,
        )

        settings = game_configuration.load_settings()

        assert settings["test_key"] == "default", "The setting test_key should fallback to its default value"

    def test_validate_success(self, mocker, game_configuration):
        mocker.patch.object(game_configuration, "_check_openai_api_key_setting")
        mocker.patch.object(game_configuration, "_check_default_ai_model_setting")
        mocker.patch.object(game_configuration, "_check_assistant_id_setting")
        game_configuration._has_dirty_settings = False  # noqa: SLF001

        game_configuration.validate()

        game_configuration._check_openai_api_key_setting.assert_called_once()  # noqa: SLF001
        game_configuration._check_default_ai_model_setting.assert_called_once()  # noqa: SLF001
        game_configuration._check_assistant_id_setting.assert_called_once()  # noqa: SLF001

    def test_validate_triggers_update(self, mocker, game_configuration):
        mocker.patch.object(game_configuration, "_check_openai_api_key_setting")
        mocker.patch.object(game_configuration, "_check_default_ai_model_setting")
        mocker.patch.object(game_configuration, "_check_assistant_id_setting")
        mock_refresh_settings = mocker.patch.object(game_configuration, "refresh_settings")

        game_configuration._has_dirty_settings = True  # noqa: SLF001

        game_configuration.validate()
        mock_refresh_settings.assert_called_once_with(game_configuration.settings)

    def test_refresh_settings(self, mocker, game_configuration):
        mock_write = mocker.patch.object(game_configuration._config_file, "write")  # noqa: SLF001
        updated_settings = {"openai_api_key": "new_key", "openai_model": "new_model"}

        game_configuration.refresh_settings(updated_settings)

        mock_write.assert_called_once_with(EXPECTED_SETTINGS, updated_settings)
        assert (
            game_configuration._settings == updated_settings  # noqa: SLF001
        ), "Internal settings cache was not updated."

    def test_check_openai_api_key_setting_valid(self, game_configuration):
        game_configuration._settings["openai_api_key"] = "valid_key"  # noqa: SLF001

        assert game_configuration._check_openai_api_key_setting() is None  # noqa: SLF001

    def test_check_openai_api_key_setting_raises_error_when_empty(self, game_configuration):
        game_configuration._settings["openai_api_key"] = ""  # noqa: SLF001

        with pytest.raises(AttributeError, match="OpenAI API Key was not found in settings."):
            game_configuration._check_openai_api_key_setting()  # noqa: SLF001

    def test_check_openai_api_key_setting_raises_error_when_missing(self, game_configuration):
        game_configuration._settings.pop("openai_api_key", None)  # noqa: SLF001

        with pytest.raises(AttributeError, match="OpenAI API Key was not found in settings."):
            game_configuration._check_openai_api_key_setting()  # noqa: SLF001

    def test_check_default_ai_model_setting_missing(self, game_configuration):
        game_configuration._settings.pop("openai_model", None)  # noqa: SLF001

        game_configuration._check_default_ai_model_setting()  # noqa: SLF001

        assert (
            game_configuration._settings["openai_model"]  # noqa: SLF001
            == game_configuration.default_ai_model
        ), "Default AI model not set correctly."
        assert (
            game_configuration._has_dirty_settings  # noqa: SLF001
        ), "Settings should be marked as dirty."

    def test_check_default_ai_model_setting_present(self, game_configuration):
        # Setup a specific model
        custom_model = "custom_model"
        game_configuration._settings["openai_model"] = custom_model  # noqa: SLF001

        game_configuration._check_default_ai_model_setting()  # noqa: SLF001

        assert (
            game_configuration._settings["openai_model"] == custom_model  # noqa: SLF001
        ), "AI model should not be modified."
        assert (
            not game_configuration._has_dirty_settings  # noqa: SLF001
        ), "Settings should not be marked as dirty."

    def test_check_assistant_id_setting_creates_assistant_when_missing(self, mocker, game_configuration):
        mocked_handler = mocker.MagicMock(return_value="generated_id")
        game_configuration.assistant_creation_handler = mocked_handler
        game_configuration._settings.pop("openai_assistant_id", None)  # noqa: SLF001
        game_configuration._settings["openai_api_key"] = "valid_key"  # noqa: SLF001
        game_configuration._settings["openai_model"] = "valid_model"  # noqa: SLF001

        game_configuration._check_assistant_id_setting()  # noqa: SLF001

        mocked_handler.assert_called_once_with("valid_key", "valid_model")
        assert (
            game_configuration._settings["openai_assistant_id"] == "generated_id"  # noqa: SLF001
        ), "Assistant ID not set correctly."
        assert (
            game_configuration._has_dirty_settings  # noqa: SLF001
        ), "Settings should be marked as dirty."

    def test_check_assistant_id_setting_does_not_create_assistant_when_present(self, mocker, game_configuration):
        mocked_handler = mocker.MagicMock()
        game_configuration.assistant_creation_handler = mocked_handler
        game_configuration._settings["openai_assistant_id"] = "valid_assistant_id"  # noqa: SLF001
        game_configuration._settings["openai_api_key"] = "valid_key"  # noqa: SLF001
        game_configuration._settings["openai_model"] = "valid_model"  # noqa: SLF001

        game_configuration._check_assistant_id_setting()  # noqa: SLF001

        mocked_handler.assert_not_called()
        assert (
            game_configuration._settings["openai_assistant_id"] == "valid_assistant_id"  # noqa: SLF001
        ), "Assistant ID was regenerated."
        assert (
            game_configuration._has_dirty_settings is False  # noqa: SLF001
        ), "Settings should not be marked as dirty."

    def test_unimplemented_handler(self, game_configuration):
        with pytest.raises(NotImplementedError):
            game_configuration._unimplemented_handler("", "")  # noqa: SLF001
