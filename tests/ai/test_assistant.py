from openai.types.shared_params import FunctionDefinition

from sprawl_runner.ai.assistant import create_assistant


def test_create_assistant_returns_assistant_id(mocker):
    mock_openai = mocker.patch("sprawl_runner.ai.assistant.OpenAI")
    mock_openai_client = mock_openai.return_value
    mock_tool_function_definition = mocker.MagicMock(spec=FunctionDefinition)
    mock_tool_functions = [mock_tool_function_definition]
    mock_assitant_tool_param = {
        "type": "function",
        "function": mock_tool_function_definition,
    }
    name = "test-assistant"
    openai_api_key = "test-key"
    openai_model = "test-model"
    instructions = "test-instructions"

    assistant_id = create_assistant(name, openai_api_key, openai_model, instructions, mock_tool_functions)

    mock_openai.assert_called_once_with(api_key=openai_api_key)
    mock_openai_client.beta.assistants.create.assert_called_once_with(
        name=name,
        instructions=instructions,
        model=openai_model,
        tools=[mock_assitant_tool_param],
    )
    assert assistant_id == mock_openai_client.beta.assistants.create.return_value.id
