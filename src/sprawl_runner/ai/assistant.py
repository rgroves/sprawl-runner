from __future__ import annotations

from typing import TYPE_CHECKING

from openai import OpenAI

if TYPE_CHECKING:
    from openai.types.beta.assistant_tool_param import AssistantToolParam
    from openai.types.shared_params import FunctionDefinition


def create_assistant(
    name: str,
    openai_api_key: str,
    openai_model: str,
    instructions: str,
    tool_functions: list[FunctionDefinition],
) -> str:
    tools: list[AssistantToolParam] = []

    for function_definition in tool_functions:
        tool_param: AssistantToolParam = {
            "type": "function",
            "function": function_definition,
        }
        tools.append(tool_param)

    openai_client = OpenAI(api_key=openai_api_key)
    assistant = openai_client.beta.assistants.create(
        name=name, instructions=instructions, model=openai_model, tools=tools
    )
    return assistant.id
