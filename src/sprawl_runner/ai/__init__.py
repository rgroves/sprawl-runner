from __future__ import annotations

import json
from typing import TYPE_CHECKING

from openai import OpenAI

from sprawl_runner import data

if TYPE_CHECKING:
    from openai.types.beta.assistant import Assistant
    from openai.types.beta.assistant_tool_param import AssistantToolParam
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
    tool_metadata_list = data.load_all_tool_metadata()
    tools: list[AssistantToolParam] = []

    for tool_metadata in tool_metadata_list:
        function_definition: FunctionDefinition = json.loads(tool_metadata)
        tool_param: AssistantToolParam = {
            "type": "function",
            "function": function_definition,
        }
        tools.append(tool_param)

    assistant = client.beta.assistants.update(assistant.id, tools=tools)
