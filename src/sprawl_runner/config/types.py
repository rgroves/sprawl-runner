from typing import Callable, Literal, TypedDict

SettingsSection = Literal["OpenAI"]
SettingsKey = Literal["openai_api_key", "openai_model", "openai_assistant_id"]
SettingDefault = str
SettingsEntry = tuple[SettingsSection, SettingsKey, SettingDefault]
ExpectedSettings = list[SettingsEntry]

AssistantCreationHandler = Callable[[str, str], str]


class GameSettings(TypedDict):
    openai_api_key: str
    openai_model: str
    openai_assistant_id: str
