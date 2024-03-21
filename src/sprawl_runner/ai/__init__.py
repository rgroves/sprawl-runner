from __future__ import annotations

from typing import TYPE_CHECKING

from openai import OpenAI

if TYPE_CHECKING:
    from openai.types.beta.assistant import Assistant
    from openai.types.beta.assistant_tool_param import AssistantToolParam
    from openai.types.beta.function_tool_param import FunctionToolParam
    from openai.types.shared_params import FunctionDefinition


DEFAULT_MODEL = "gpt-3.5-turbo"


def get_openai_client(openai_api_key: str) -> OpenAI:
    return OpenAI(api_key=openai_api_key)


def create_assistant(name: str, openai_api_key: str, openai_model: str, instructions: str) -> str:
    client = get_openai_client(openai_api_key)
    assistant = client.beta.assistants.create(
        name=name,
        instructions=instructions,
        model=openai_model,
    )
    register_tools(client, assistant)
    return assistant.id


def register_tools(client: OpenAI, assistant: Assistant):
    register_factions_definition: FunctionDefinition = {
        "name": "register_factions",
        "description": "Provides details of the factions that exist in the game world.",
        "parameters": {
            "type": "object",
            "properties": {
                "factions": {
                    "type": "array",
                    "description": "An array of factions, each with a name, description, and motivation.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "description": {"type": "string"},
                            "motivation": {"type": "string"},
                        },
                        "required": ["name", "description", "motiviation"],
                    },
                }
            },
        },
    }

    function_def: FunctionToolParam = {
        "type": "function",
        "function": register_factions_definition,
    }
    tools: list[AssistantToolParam] = [function_def]
    assistant = client.beta.assistants.update(assistant.id, tools=tools)
