from __future__ import annotations

import json
import time
from collections import deque
from typing import TYPE_CHECKING

from openai import OpenAI

if TYPE_CHECKING:
    from openai.types.beta.thread import Thread
    from openai.types.beta.threads.message_content import MessageContent
    from openai.types.beta.threads.required_action_function_tool_call import (
        RequiredActionFunctionToolCall,
    )
    from openai.types.beta.threads.run import Run
    from openai.types.beta.threads.run_submit_tool_outputs_params import ToolOutput

    from sprawl_runner.ai.types import ToolHandler, ToolHandlerEntry, ToolName


class AssistantMessageBus:
    def __init__(self, openai_api_key: str, openai_assistant_id: str) -> None:
        self._openai_api_key = openai_api_key
        self._assistant_id = openai_assistant_id
        self._active_runs: deque[Run] = deque()
        self._tool_handlers: dict[ToolName, ToolHandler] = {}
        self._narrative_thread: Thread | None = None

    def _get_tool_handler(self, function_name) -> ToolHandler | None:
        return self._tool_handlers.get(function_name)

    def _process_tool_calls(self, tool_calls: list[RequiredActionFunctionToolCall]) -> list[ToolOutput]:
        tool_outputs: list[ToolOutput] = []

        for tool_call in tool_calls:
            handler = self._get_tool_handler(tool_call.function.name)

            if handler:
                arguments = json.loads(tool_call.function.arguments)
                status = handler(arguments)
            else:
                status = "ERROR"

            tool_outputs.append({"tool_call_id": tool_call.id, "output": status})

        return tool_outputs

    def _requeue_run_if_pending(self, run: Run) -> bool:
        requeued = False

        if run.status in ("queued", "in_progress", "cancelling"):
            self._active_runs.append(run)
            requeued = True

        return requeued

    def _send_tool_outputs(self, client: OpenAI, run: Run, tool_outputs: list[ToolOutput]) -> Run:
        if not tool_outputs:
            return run

        return client.beta.threads.runs.submit_tool_outputs(
            thread_id=run.thread_id,
            run_id=run.id,
            tool_outputs=tool_outputs,
        )

    def process_tool_message_async(self, content: str) -> None:
        openai_client = OpenAI(api_key=self._openai_api_key)
        thread = openai_client.beta.threads.create()
        openai_client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=content,
        )
        run = openai_client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=self._assistant_id,
        )
        self._active_runs.append(run)

    def resolve_async_tool_messages(self) -> None:
        if not self._active_runs:
            return

        openai_client = OpenAI(api_key=self._openai_api_key)
        initial_active_run_count = len(self._active_runs)

        for _ in range(initial_active_run_count):
            cur_run = self._active_runs.popleft()

            # Get the current state of the active run.
            run = openai_client.beta.threads.runs.retrieve(
                thread_id=cur_run.thread_id,
                run_id=cur_run.id,
            )

            if run.status == "requires_action" and run.required_action:
                tool_outputs = self._process_tool_calls(run.required_action.submit_tool_outputs.tool_calls)
                run = self._send_tool_outputs(openai_client, run, tool_outputs)

            self._requeue_run_if_pending(run)

    def register_tool_handler(self, tool_name: ToolName, handler: ToolHandler):
        self._tool_handlers[tool_name] = handler

    def register_tool_handlers(self, tool_handlers: list[ToolHandlerEntry]):
        for tool_name, handler in tool_handlers:
            self.register_tool_handler(tool_name, handler)

    def process_narrative_message(self, content: str) -> str:
        openai_client = OpenAI(api_key=self._openai_api_key)

        # TODO: probably should move this so it is only done once
        if not self._narrative_thread:
            self._narrative_thread = openai_client.beta.threads.create()

        openai_client.beta.threads.messages.create(
            thread_id=self._narrative_thread.id,
            role="user",
            content=content,
        )
        run = openai_client.beta.threads.runs.create(
            thread_id=self._narrative_thread.id,
            assistant_id=self._assistant_id,
        )

        # wait on run
        while run.status in ("queued", "in_progress"):
            run = openai_client.beta.threads.runs.retrieve(
                thread_id=run.thread_id,
                run_id=run.id,
            )
            print("...[thinking]...")  # noqa T201
            time.sleep(1)

        messages = openai_client.beta.threads.messages.list(thread_id=run.thread_id)
        narrative_content: MessageContent = messages.data[0].content[0]
        show_json(messages)
        if narrative_content.type == "text":
            output = narrative_content.text.value
        return output


def show_json(obj) -> None:
    import pprint

    print("\n\n>>>")  # noqa T201
    pprint.pprint(json.loads(obj.model_dump_json()), indent=2, width=140, compact=True)  # noqa T201
    print("<<<\n")  # noqa T201
