import json
from collections import deque

import pytest

from sprawl_runner.ai.assistant_message_bus import AssistantMessageBus


@pytest.fixture
def message_bus() -> AssistantMessageBus:
    openai_api_key = "test-key"
    openai_assistant_id = "test-id"
    return AssistantMessageBus(openai_api_key, openai_assistant_id)


class TestAssistantMessageBus:
    def test_can_instantiate(self, mocker):
        openai_api_key = "test-key"
        openai_assistant_id = "test-id"
        mock_deque = mocker.MagicMock()
        mocker.patch("sprawl_runner.ai.assistant_message_bus.deque", return_value=mock_deque)

        message_bus = AssistantMessageBus(openai_api_key, openai_assistant_id)

        assert message_bus._openai_api_key == openai_api_key  # noqa: SLF001
        assert message_bus._assistant_id == openai_assistant_id  # noqa: SLF001
        assert message_bus._active_runs == mock_deque  # noqa: SLF001
        assert message_bus._tool_handlers == {}  # noqa: SLF001

    def test__get_tool_handler_returns_handler_when_tool_is_registered(self, mocker, monkeypatch, message_bus):
        tool_name = "test-tool"
        mock_tool_handler = mocker.MagicMock()
        mock_tool_handlers = {tool_name: mock_tool_handler}

        monkeypatch.setattr(message_bus, "_tool_handlers", mock_tool_handlers)

        tool_handler = message_bus._get_tool_handler(tool_name)  # noqa: SLF001

        assert tool_handler == mock_tool_handler

    def test__get_tool_handler_returns_none_when_tool_is_not_registered(self, monkeypatch, message_bus):
        tool_name = "test-tool"
        mock_tool_handlers = {}
        monkeypatch.setattr(message_bus, "_tool_handlers", mock_tool_handlers)

        tool_handler = message_bus._get_tool_handler(tool_name)  # noqa: SLF001

        assert tool_handler is None

    def test__process_tool_calls_returns_successful_tool_output_when_handler_exists(
        self, mocker, monkeypatch, message_bus
    ):
        mock_tool_call = mocker.MagicMock()
        mock_tool_calls = [mock_tool_call]
        mock__get_tool_handler = mocker.MagicMock()
        mock_handler = mock__get_tool_handler.return_value
        monkeypatch.setattr(message_bus, "_get_tool_handler", mock__get_tool_handler)
        mock_json_loads = mocker.MagicMock()
        monkeypatch.setattr(json, "loads", mock_json_loads)

        tool_outputs = message_bus._process_tool_calls(mock_tool_calls)  # noqa: SLF001

        message_bus._get_tool_handler.assert_called_once_with(  # noqa: SLF001
            mock_tool_call.function.name
        )
        mock_json_loads.assert_called_once_with(mock_tool_call.function.arguments)
        mock_handler.assert_called_once_with(mock_json_loads.return_value)
        assert tool_outputs == [
            {
                "tool_call_id": mock_tool_call.id,
                "output": mock_handler.return_value,
            }
        ]

    def test__process_tool_calls_returns_successful_tool_output_when_handler_does_not_exists(
        self, mocker, monkeypatch, message_bus
    ):
        mock_tool_call = mocker.MagicMock()
        mock_tool_calls = [mock_tool_call]
        mock__get_tool_handler = mocker.MagicMock(return_value=None)
        monkeypatch.setattr(message_bus, "_get_tool_handler", mock__get_tool_handler)
        mock_json_loads = mocker.MagicMock()
        monkeypatch.setattr(json, "loads", mock_json_loads)

        tool_outputs = message_bus._process_tool_calls(mock_tool_calls)  # noqa: SLF001

        message_bus._get_tool_handler.assert_called_once_with(  # noqa: SLF001
            mock_tool_call.function.name
        )
        mock_json_loads.assert_not_called()
        assert tool_outputs == [{"tool_call_id": mock_tool_call.id, "output": "ERROR"}]

    def test__requeue_run_if_pending_does_requeue_for_queued_status(self, mocker, monkeypatch, message_bus):
        monkeypatch.setattr(message_bus, "_active_runs", mocker.MagicMock())
        mock_run = mocker.MagicMock(status="queued")

        is_requeued = message_bus._requeue_run_if_pending(mock_run)  # noqa: SLF001

        assert is_requeued is True

    def test__requeue_run_if_pending_does_requeue_for_cancelling_status(self, mocker, monkeypatch, message_bus):
        monkeypatch.setattr(message_bus, "_active_runs", mocker.MagicMock())
        mock_run = mocker.MagicMock(status="cancelling")

        is_requeued = message_bus._requeue_run_if_pending(mock_run)  # noqa: SLF001

        assert is_requeued is True

    def test__requeue_run_if_pending_does_requeue_for_in_progress_status(self, mocker, monkeypatch, message_bus):
        monkeypatch.setattr(message_bus, "_active_runs", mocker.MagicMock())
        mock_run = mocker.MagicMock(status="in_progress")

        is_requeued = message_bus._requeue_run_if_pending(mock_run)  # noqa: SLF001

        assert is_requeued is True

    def test__requeue_run_if_pending_does_not_requeue_for_non_pending_status(self, mocker, monkeypatch, message_bus):
        monkeypatch.setattr(message_bus, "_active_runs", mocker.MagicMock())
        mock_run = mocker.MagicMock(status="completed")

        is_requeued = message_bus._requeue_run_if_pending(mock_run)  # noqa: SLF001

        assert is_requeued is False

    def test__send_tool_outputs_does_submit_outputs_when_not_empty(self, mocker, message_bus):
        mock_client = mocker.MagicMock()
        mock_updated_run = mock_client.beta.threads.runs.submit_tool_outputs.return_value
        mock_updated_run.status = "queued"
        mock_run = mocker.MagicMock(status="queued")
        mock_tool_outputs = [mocker.MagicMock()]

        message_bus._send_tool_outputs(mock_client, mock_run, mock_tool_outputs)  # noqa: SLF001

        mock_client.beta.threads.runs.submit_tool_outputs.assert_called_once_with(
            thread_id=mock_run.thread_id,
            run_id=mock_run.id,
            tool_outputs=mock_tool_outputs,
        )

    def test__send_tool_outputs_does_not_submit_outputs_when_empty(self, mocker, message_bus):
        mock_client = mocker.MagicMock()
        mock_updated_run = mock_client.beta.threads.runs.submit_tool_outputs.return_value
        mock_updated_run.status = "queued"
        mock_run = mocker.MagicMock(status="queued")
        mock_tool_outputs = []

        message_bus._send_tool_outputs(mock_client, mock_run, mock_tool_outputs)  # noqa: SLF001

        mock_client.beta.threads.runs.submit_tool_outputs.assert_not_called()

    def test_process_tool_message_async_successfully_queues_new_run(self, mocker, message_bus):
        content = "test message content"
        mock_thread = mocker.MagicMock(id="mock_thread_id")
        mock_run = mocker.MagicMock(id="mock_run_id", thread_id="mock_thread_id")
        mock_openai_client = mocker.MagicMock()
        mock_openai_client.beta.threads.create.return_value = mock_thread
        mock_openai_client.beta.threads.messages.create.return_value = None
        mock_openai_client.beta.threads.runs.create.return_value = mock_run
        mock_openai = mocker.patch("sprawl_runner.ai.assistant_message_bus.OpenAI")
        mock_openai.return_value = mock_openai_client

        message_bus.process_tool_message_async(content)

        mock_openai_client.beta.threads.create.assert_called_once_with()
        mock_openai_client.beta.threads.messages.create.assert_called_once_with(
            thread_id=mock_thread.id,
            role="user",
            content=content,
        )
        mock_openai_client.beta.threads.runs.create.assert_called_once_with(
            thread_id=mock_thread.id,
            assistant_id=message_bus._assistant_id,  # noqa: SLF001
        )
        assert message_bus._active_runs[-1] == mock_run  # noqa: SLF001

    def test_resolve_async_tool_messages_does_nothing_when_no_active_runs(self, mocker, message_bus):
        mock_openai = mocker.patch("sprawl_runner.ai.assistant_message_bus.OpenAI")

        message_bus.resolve_async_tool_messages()

        mock_openai.assert_not_called()

    def test_resolve_async_tool_messages_does_process_tool_calls_when_run_requires_action(self, mocker, message_bus):
        # Mock run that requires action
        mock_run = mocker.MagicMock()
        mock_run.status = "requires_action"
        mock_run.required_action.submit_tool_outputs.tool_calls = [mocker.MagicMock()]
        message_bus._active_runs = deque([mock_run])  # noqa: SLF001
        mock_openai = mocker.patch("sprawl_runner.ai.assistant_message_bus.OpenAI")
        mock_openai_client = mocker.MagicMock()
        mock_openai.return_value = mock_openai_client
        mock_updated_run = mocker.MagicMock(status="requires_action")
        mock_openai_client.beta.threads.runs.retrieve.return_value = mock_updated_run

        mock_process_tool_calls = mocker.patch.object(message_bus, "_process_tool_calls")
        mock_send_tool_outputs = mocker.patch.object(message_bus, "_send_tool_outputs")
        mock_requeue_run_if_pending = mocker.patch.object(message_bus, "_requeue_run_if_pending")

        message_bus.resolve_async_tool_messages()

        mock_openai_client.beta.threads.runs.retrieve.assert_called_once_with(
            thread_id=mock_run.thread_id, run_id=mock_run.id
        )
        mock_process_tool_calls.assert_called_once_with(mock_updated_run.required_action.submit_tool_outputs.tool_calls)
        mock_send_tool_outputs.assert_called_once_with(
            mock_openai_client, mock_updated_run, mock_process_tool_calls.return_value
        )
        mock_requeue_run_if_pending.assert_called_once_with(mock_send_tool_outputs.return_value)

    def test_resolve_async_tool_messages_does_not_process_tool_calls_when_run_does_not_require_action(
        self, mocker, message_bus
    ):
        # Mock run that requires action
        mock_run = mocker.MagicMock()
        mock_run.status = "in_progress"
        mock_run.required_action = None
        message_bus._active_runs = deque([mock_run])  # noqa: SLF001
        mock_openai = mocker.patch("sprawl_runner.ai.assistant_message_bus.OpenAI")
        mock_openai_client = mocker.MagicMock()
        mock_openai.return_value = mock_openai_client
        mock_updated_run = mocker.MagicMock(status="completed")
        mock_openai_client.beta.threads.runs.retrieve.return_value = mock_updated_run

        mock_process_tool_calls = mocker.patch.object(message_bus, "_process_tool_calls")
        mock_send_tool_outputs = mocker.patch.object(message_bus, "_send_tool_outputs")
        mock_requeue_run_if_pending = mocker.patch.object(message_bus, "_requeue_run_if_pending")

        message_bus.resolve_async_tool_messages()

        mock_openai_client.beta.threads.runs.retrieve.assert_called_once_with(
            thread_id=mock_run.thread_id, run_id=mock_run.id
        )
        mock_process_tool_calls.assert_not_called()
        mock_send_tool_outputs.assert_not_called()
        mock_requeue_run_if_pending.assert_called_once_with(mock_updated_run)

    def test_register_tool_handler_success(self, mocker, message_bus):
        tool_name = "test_tool"
        handler = mocker.MagicMock()

        message_bus.register_tool_handler(tool_name, handler)

        assert message_bus._tool_handlers[tool_name] == handler  # noqa: SLF001

    def test_register_tool_handlers_success(self, mocker, message_bus):
        tool1_name = "tool1"
        tool1_handler = mocker.MagicMock()
        tool2_name = "tool2"
        tool2_handler = mocker.MagicMock()
        tool_handlers = [
            (tool1_name, tool1_handler),
            (tool2_name, tool2_handler),
        ]
        mock_register_tool_handler = mocker.patch.object(message_bus, "register_tool_handler")

        message_bus.register_tool_handlers(tool_handlers)

        mock_register_tool_handler.assert_has_calls(
            [
                mocker.call(tool1_name, tool1_handler),
                mocker.call(tool2_name, tool2_handler),
            ]
        )
