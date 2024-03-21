from pathlib import Path

import sprawl_runner


def load_data(file: str):
    module_path = Path(sprawl_runner.__file__).parent
    base_path = Path(module_path, "data")
    file_path = Path(base_path, file)
    abs_path = file_path.resolve()

    # Ensure the resolved file path is within the intended base directory.
    if not file_path.is_file() or base_path != abs_path.parent:
        message = "Attempted path traversal detected or file does not exist"
        raise FileNotFoundError(message)

    with open(file_path) as input_file:
        return input_file.read()
