from sprawl_runner.config.config_file import ConfigFile
from sprawl_runner.config.constants import (
    DEFAULT_AI_MODEL,
    EMPTY_SETTINGS,
    EXPECTED_SETTINGS,
)
from sprawl_runner.config.types import GameSettings


class GameConfiguration:
    @staticmethod
    def _unimplemented_handler(openai_api_key: str, openai_model: str) -> str:
        raise NotImplementedError

    def __init__(self, config_file: ConfigFile):
        self.default_ai_model: str = DEFAULT_AI_MODEL
        self.assistant_creation_handler = self._unimplemented_handler
        self._config_file = config_file
        self._settings: GameSettings = EMPTY_SETTINGS
        self._has_dirty_settings = False

    @property
    def settings(self) -> GameSettings:
        return self._settings

    def _check_openai_api_key_setting(self) -> None:
        key = self._settings.get("openai_api_key")

        if not key or not isinstance(key, str):
            msg = "OpenAI API Key was not found in settings."
            raise AttributeError(msg)

    def _check_default_ai_model_setting(self) -> None:
        if not self.settings.get("openai_model"):
            self.settings["openai_model"] = self.default_ai_model
            self._has_dirty_settings = True

    def _check_assistant_id_setting(self) -> None:
        if not self.settings.get("openai_assistant_id"):
            self.settings["openai_assistant_id"] = self.assistant_creation_handler(
                self.settings["openai_api_key"],
                self.settings["openai_model"],
            )
            self._has_dirty_settings = True

    def load_settings(self) -> GameSettings:
        config_parser = self._config_file.load()
        settings = EMPTY_SETTINGS

        for section, key, default in EXPECTED_SETTINGS:
            value = config_parser.get(section, key, fallback=default)
            settings[key] = value

        return settings

    def refresh_settings(self, updated_settings: GameSettings):
        self._config_file.write(EXPECTED_SETTINGS, updated_settings)
        self._settings = updated_settings

    def validate(self) -> None:
        self._check_openai_api_key_setting()
        self._check_default_ai_model_setting()
        self._check_assistant_id_setting()

        if self._has_dirty_settings:
            self.refresh_settings(self.settings)
