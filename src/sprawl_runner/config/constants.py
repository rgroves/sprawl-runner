# Config Section Constants
from sprawl_runner.config.types import (
    ExpectedSettings,
    GameSettings,
    SettingsKey,
    SettingsSection,
)

SETTINGS_FILE_NAME = ".sprawl-runner"
DEFAULT_AI_MODEL = "gpt-3.5-turbo-0125"


OPENAI: SettingsSection = "OpenAI"

# Setting Name Constants
OPENAI_API_KEY: SettingsKey = "openai_api_key"
OPENAI_MODEL: SettingsKey = "openai_model"
OPENAI_ASSISTANT_ID: SettingsKey = "openai_assistant_id"


EMPTY_SETTINGS = GameSettings(openai_api_key="", openai_assistant_id="", openai_model="")

EXPECTED_SETTINGS: ExpectedSettings = [
    (OPENAI, OPENAI_API_KEY, ""),
    (OPENAI, OPENAI_MODEL, ""),
    (OPENAI, OPENAI_ASSISTANT_ID, ""),
]
