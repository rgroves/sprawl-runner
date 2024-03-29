import json
import os
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

import sprawl_runner
from sprawl_runner.data import (
    _TOOL_METADATA_DIR,
    load_all_tool_metadata,
    load_data,
    load_tool_metadata,
)

FAKE_MODULE_PATH_PARENT = "/fake/path/to/sprawl_runner"
FAKE_MODULE_PATH = f"{FAKE_MODULE_PATH_PARENT}/__init__.py"


@pytest.fixture
def mock_sprawl_runner_path(monkeypatch):
    # Mock the __file__ attribute of the sprawl_runner module to a fixed path.
    monkeypatch.setattr(sprawl_runner, "__file__", FAKE_MODULE_PATH)


@pytest.mark.usefixtures("mock_sprawl_runner_path")
def test_load_data_success(monkeypatch):
    # Ensure Path.resolve returns appropriate value for each call.
    monkeypatch.setattr(
        Path,
        "resolve",
        MagicMock(
            side_effect=[
                Path(f"{FAKE_MODULE_PATH_PARENT}/data/test_file.txt"),
            ],
        ),
    )
    # Mock Path.is_file to return True for mock file paths.
    monkeypatch.setattr(Path, "is_file", MagicMock(return_value=True))
    # Patch the open function to mock reading from a file.
    with patch("builtins.open", mock_open(read_data="test data")) as mock_file_open:
        result = load_data("test_file.txt")
        # Verify file contents are read correctly.
        assert result == "test data"
        # Ensure the file was opened once.
        mock_file_open.assert_called_once()


@pytest.mark.usefixtures("mock_sprawl_runner_path")
def test_load_data_raises_when_file_does_not_exist(monkeypatch):
    # Make Path.is_file return False to simulate a non-existent file.
    monkeypatch.setattr(Path, "is_file", MagicMock(return_value=False))
    with pytest.raises(FileNotFoundError) as excinfo:
        load_data("nonexistent.txt")
    assert "Attempted path traversal detected or file does not exist" in str(excinfo.value)


@pytest.mark.usefixtures("mock_sprawl_runner_path")
def test_load_data_raises_when_path_traversal_attack_attempted(monkeypatch):
    monkeypatch.setattr(Path, "parent", FAKE_MODULE_PATH_PARENT)

    # Adjust Path.resolve to simulate a path traversal attempt.
    monkeypatch.setattr(Path, "resolve", MagicMock(side_effect=lambda: Path("/etc/passwd")))
    with pytest.raises(FileNotFoundError) as excinfo:
        load_data("../../etc/passwd")
    assert "Attempted path traversal detected or file does not exist" in str(excinfo.value)


@pytest.mark.usefixtures("mock_sprawl_runner_path")
def test_load_data_raises_when_file_outside_intended_directory(monkeypatch):
    # Mock resolve to return a path outside the intended 'data' directory.
    monkeypatch.setattr(
        Path,
        "resolve",
        MagicMock(side_effect=lambda: Path("/fake/path/to/other_dir/test_file.txt")),
    )
    with pytest.raises(FileNotFoundError) as excinfo:
        load_data("test_file.txt")
    assert "Attempted path traversal detected or file does not exist" in str(excinfo.value)


def test_load_tool_metadata_adds_json_extension_if_missing(mocker):
    mocked_load_data = mocker.patch("sprawl_runner.data.load_data")
    tool_file_name = "tool-name"
    tool_file_name_json = f"{tool_file_name}.json"

    load_tool_metadata(tool_file_name)

    mocked_load_data.assert_called_once_with(tool_file_name_json, _TOOL_METADATA_DIR)


def test_load_tool_metadata2(mocker):
    mocked_load_data = mocker.patch("sprawl_runner.data.load_data")
    tool_file_name = "tool-name.json"

    load_tool_metadata(tool_file_name)

    mocked_load_data.assert_called_once_with(tool_file_name, _TOOL_METADATA_DIR)


@pytest.mark.usefixtures("mock_sprawl_runner_path")
def test_load_all_tool_metadata_loads_successfully(monkeypatch):
    mock_files = ["tool1.json", "tool2.json"]
    mock_metadata = ["metadata1", "metadata2"]

    mock_scandir = MagicMock(
        side_effect=lambda _: [
            MagicMock(is_file=MagicMock(return_value=name.endswith(".json")), name=name) for name in mock_files
        ]
    )
    monkeypatch.setattr(os, "scandir", mock_scandir)
    mock_json_loads = MagicMock(side_effect=[mock_metadata[0], mock_metadata[1]])
    monkeypatch.setattr(json, "loads", mock_json_loads)

    with patch("sprawl_runner.data.load_data", side_effect=mock_metadata) as mock_load_data:
        metadata = load_all_tool_metadata()
        assert metadata == mock_metadata
        assert mock_load_data.call_count == len(mock_files)
        assert mock_json_loads.call_count == len(mock_files)


@pytest.mark.usefixtures("mock_sprawl_runner_path")
def test_load_all_tool_metadata_ignores_non_json_files(monkeypatch):
    mock_json_files = ["tool1.json", "tool2.json"]
    mock_files = [*mock_json_files, "non-tool1", "non-tool2"]
    mock_metadata = ["metadata1", "metadata2"]
    mock_json_loads = MagicMock(side_effect=[mock_metadata[0], mock_metadata[1]])
    monkeypatch.setattr(json, "loads", mock_json_loads)

    mock_scandir = MagicMock(
        side_effect=lambda _: [
            MagicMock(is_file=MagicMock(return_value=name.endswith(".json")), name=name) for name in mock_files
        ]
    )
    monkeypatch.setattr(os, "scandir", mock_scandir)

    with patch("sprawl_runner.data.load_data", side_effect=mock_metadata) as mock_load_data:
        metadata = load_all_tool_metadata()
        assert metadata == mock_metadata
        assert mock_load_data.call_count == len(mock_json_files)
