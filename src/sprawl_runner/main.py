from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from sprawl_runner import data
from sprawl_runner.ai.assistant import create_assistant
from sprawl_runner.ai.assistant_message_bus import AssistantMessageBus
from sprawl_runner.config import config
from sprawl_runner.consoles.basic_console import BasicConsole
from sprawl_runner.game.game import Game
from sprawl_runner.game.states.start_game import StartGame

if TYPE_CHECKING:
    from openai.types.shared_params import FunctionDefinition


def create_assistant_handler(openai_api_key: str, openai_model: str) -> str:
    instructions = data.load_data("assistant-instructions.txt")
    tool_functions: list[FunctionDefinition] = data.load_all_tool_metadata()

    return create_assistant(
        "Sprawl Runner Assist - A Consensual Hallucination Text-Based Adventure Game Assistant",
        openai_api_key,
        openai_model,
        instructions,
        tool_functions,
    )


def main() -> None:
    console = BasicConsole()

    config.assistant_creation_handler = create_assistant_handler
    try:
        config.load_settings()
    except FileNotFoundError as error:
        console.emit(str(error))
        sys.exit(1)

    config.validate()

    game = Game(console)

    ai_tool_handlers = game.get_tool_handlers()
    message_bus = AssistantMessageBus(config.settings["openai_api_key"], config.settings["openai_assistant_id"])
    message_bus.register_tool_handlers(ai_tool_handlers)
    game.message_bus = message_bus

    game.change_state(StartGame())
    game.validate()
    game.play()


if __name__ == "__main__":
    main()
