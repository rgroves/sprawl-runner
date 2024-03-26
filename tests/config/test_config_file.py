from configparser import ConfigParser
from pathlib import Path

import pytest

from sprawl_runner.config.config_file import ConfigFile
from sprawl_runner.config.constants import SETTINGS_FILE_NAME
from sprawl_runner.config.types import GameSettings

FAKE_MODULE_PATH_PARENT = "/fake/path/to/sprawl_runner"
FAKE_MODULE_PATH = f"{FAKE_MODULE_PATH_PARENT}/__init__.py"


class TestConfigFile:
    def test_config_file_default_path_initialization(self):
        config_file = ConfigFile()
        expected_path = Path.home().joinpath(SETTINGS_FILE_NAME).__str__()
        assert config_file.path == expected_path, "ConfigFile path does not match expected default path."

    def test_config_file_custom_path_initialization(self):
        custom_file_name = ".sprawl_runner_custom_settings"
        config_file = ConfigFile(file_name=custom_file_name)
        expected_path = Path.home().joinpath(custom_file_name).__str__()
        assert config_file.path == expected_path, "ConfigFile path does not match expected custom path."

    def test_load_method_success_with_mock(self, mocker):
        file_contents = "[DEFAULT]\nkey=value"
        mocked_open = mocker.mock_open(read_data=file_contents)
        mocker.patch("builtins.open", mocked_open)

        config_file = ConfigFile(file_name=".sprawl_runner_dummy_config")
        result = config_file.load()

        assert isinstance(result, ConfigParser), "Did not return a ConfigParser object."
        assert result.get("DEFAULT", "key") == "value", "ConfigParser object did not contain expected values."

    def test_load_method_file_not_found_with_mock(self, mocker):
        mocked_open = mocker.mock_open()
        mocked_open.side_effect = FileNotFoundError
        mocker.patch("builtins.open", mocked_open)
        file_name = ".sprawl_runner_nonexistent_config"

        config_file = ConfigFile(file_name=file_name)
        with pytest.raises(FileNotFoundError) as excinfo:
            config_file.load()

        assert file_name in str(excinfo.value), "Error message does not contain the non-existent file name."

    def test_write_new_settings(self, mocker):
        file_contents = ""
        mocked_open = mocker.mock_open(read_data=file_contents)

        expected_settings = [
            ("OpenAI", "openai_api_key", ""),
            ("OpenAI", "openai_model", ""),
            ("OpenAI", "openai_assistant_id", ""),
        ]

        updated_settings = GameSettings(openai_api_key="value1", openai_model="value2", openai_assistant_id="value3")

        mocker.patch("builtins.open", mocked_open)

        config_file = ConfigFile(file_name=".sprawl_runner_dummy_config")
        config_file.write(expected_settings, updated_settings)

        # Check that the file was opened in write mode and that the expected calls to write were made
        handle = mocked_open()
        handle.write.assert_has_calls(
            [
                mocker.call("[OpenAI]\n"),
                mocker.call("openai_api_key = value1\n"),
                mocker.call("openai_model = value2\n"),
                mocker.call("openai_assistant_id = value3\n"),
            ],
            any_order=True,
        )

    def test_update_existing_settings(self, mocker):
        file_contents = "[OpenAI]\nopenai_api_key=default1\nopenai_model=default2\nopenai_assistant_id=default3\n"
        mocked_open = mocker.mock_open(read_data=file_contents)

        expected_settings = [
            ("OpenAI", "openai_api_key", ""),
            ("OpenAI", "openai_model", ""),
            ("OpenAI", "openai_assistant_id", ""),
        ]

        updated_settings = GameSettings(openai_api_key="value1", openai_model="value2", openai_assistant_id="value3")

        mocker.patch("builtins.open", mocked_open)

        config_file = ConfigFile(file_name=".sprawl_runner_dummy_config")
        config_file.write(expected_settings, updated_settings)

        # Verify that the file was opened for writing and the new values were written
        handle = mocked_open()
        handle.write.assert_has_calls(
            [
                mocker.call("[OpenAI]\n"),
                mocker.call("openai_api_key = value1\n"),
                mocker.call("openai_model = value2\n"),
                mocker.call("openai_assistant_id = value3\n"),
            ],
            any_order=True,
        )
