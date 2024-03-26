from configparser import ConfigParser
from pathlib import Path

from sprawl_runner.config.constants import SETTINGS_FILE_NAME
from sprawl_runner.config.types import ExpectedSettings, GameSettings


class ConfigFile:
    def __init__(self, file_name: str = SETTINGS_FILE_NAME) -> None:
        home_path = Path.home()
        self.path = Path.joinpath(home_path, file_name).__str__()

    def load(self) -> ConfigParser:
        config_parser = ConfigParser()

        if self.path not in config_parser.read(self.path):
            msg = f"No config file found at: {self.path}"
            raise FileNotFoundError(msg)

        return config_parser

    def write(self, expected_settings: ExpectedSettings, updated_settings: GameSettings) -> None:
        sections = set()
        config_parser = ConfigParser()

        for section, key, default in expected_settings:
            if section not in sections:
                config_parser.add_section(section)
                sections.add(section)

            value = updated_settings[key] or default
            config_parser.set(section, key, value)

        with open(self.path, "w") as config_file:
            config_parser.write(config_file)
