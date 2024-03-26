from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import sprawl_runner

_DATA_DIR = "data"
_TOOL_METADATA_DIR = "tool-metadata"


def load_data(file: str, sub_dir: str = "") -> str:
    module_path = Path(sprawl_runner.__file__).parent
    base_path = Path(module_path, _DATA_DIR, sub_dir)
    file_path = Path(base_path, file)
    abs_path = file_path.resolve()

    # Ensure the resolved file path is within the intended base directory.
    if not file_path.is_file() or base_path != abs_path.parent:
        message = "Attempted path traversal detected or file does not exist"
        raise FileNotFoundError(message)

    with open(file_path) as input_file:
        return input_file.read()


def load_tool_metadata(tool_file_name: str) -> str:
    if not tool_file_name.endswith(".json"):
        tool_file_name += ".json"

    return load_data(tool_file_name, _TOOL_METADATA_DIR)


def load_all_tool_metadata() -> list[Any]:
    module_path = Path(sprawl_runner.__file__).parent
    base_path = Path(module_path, _DATA_DIR, _TOOL_METADATA_DIR)

    tool_file_names = [
        entry.name for entry in os.scandir(base_path) if entry.is_file() and entry.name.endswith(".json")
    ]

    tool_metadata = []
    for tool_file_name in tool_file_names:
        metadata = load_data(tool_file_name, _TOOL_METADATA_DIR)
        tool_metadata.append(json.loads(metadata))

    return tool_metadata
