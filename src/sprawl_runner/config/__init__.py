import configparser
from pathlib import Path
from typing import TypedDict


class GameSettings(TypedDict):
    has_loaded: bool
    openai_api_key: str
    openai_model: str


def _set_config_path() -> str:
    file_name = ".sprawl-runner"
    full_path = Path.joinpath(Path.home(), file_name)
    return f"{full_path}"


def _load_settings() -> GameSettings:
    config_parser = configparser.ConfigParser()
    has_loaded = config_path in config_parser.read(config_path)
    return {
        "has_loaded": has_loaded,
        "openai_api_key": config_parser.get("OpenAI", "openai_api_key", fallback=""),
        "openai_model": config_parser.get("OpenAI", "openai_model", fallback=""),
    }


config_path = _set_config_path()
settings = _load_settings()
