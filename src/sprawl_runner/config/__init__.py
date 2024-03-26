import configparser
from pathlib import Path
from typing import TypedDict

from sprawl_runner import data
from sprawl_runner.ai.assistant import create_assistant


class GameSettings(TypedDict):
    has_loaded: bool
    openai_api_key: str
    openai_model: str
    openai_assistant_id: str


def _set_config_path() -> str:
    file_name = ".sprawl-runner"
    full_path = Path.joinpath(Path.home(), file_name)
    return f"{full_path}"


def _load_settings() -> GameSettings:
    config_parser = configparser.ConfigParser()
    has_loaded = config_path in config_parser.read(config_path)
    openai_api_key = config_parser.get("OpenAI", "openai_api_key", fallback="")
    openai_model = config_parser.get("OpenAI", "openai_model", fallback="")
    openai_assistant_id = config_parser.get("OpenAI", "openai_assistant_id", fallback="")

    if has_loaded and not openai_assistant_id:
        instructions = data.load_data("assistant-instructions.txt")
        assistant_id = create_assistant(
            "Text-Based Adventure Assistant",
            openai_api_key,
            openai_model,
            instructions,
            [],
        )
        config_parser.set("OpenAI", "openai_assistant_id", assistant_id)
        with open(config_path, "w") as config_file:
            config_parser.write(config_file)

    return {
        "has_loaded": has_loaded,
        "openai_api_key": openai_api_key,
        "openai_model": openai_model,
        "openai_assistant_id": openai_assistant_id,
    }


config_path = _set_config_path()
settings = _load_settings()
