"""
tool_response criteria
- 2 turn chat completion: (1) check tool call is correct (2) pass back tool response and check summarization
"""

import llama_api_client
import openai

from ...data.types import CriteriaTestCase, CriteriaTestResult
from ..interface import ProviderConfig
from ..providers import get_provider_client
from .basic import (
    _check_basic_chat_completion_llamaapi_non_streaming,
    _check_basic_chat_completion_llamaapi_streaming,
    _check_basic_chat_completion_openai_non_streaming,
    _check_basic_chat_completion_openai_streaming,
)
from .common import extract_assistant_message_from_response, send_request_and_check_result
from .tool_call import (
    _check_tool_call_llamaapi_non_streaming,
    _check_tool_call_llamaapi_streaming,
    _check_tool_call_openai_non_streaming,
    _check_tool_call_openai_streaming,
)


def check_tool_response(
    test_case: CriteriaTestCase, model: str, stream: bool, provider_config: ProviderConfig
) -> CriteriaTestResult:
    """Check the tool_call chat completion."""
    client = get_provider_client(provider_config)

    # first turn, check correct tool call returned
    if isinstance(client, llama_api_client.LlamaAPIClient):
        check_func = _check_tool_call_llamaapi_streaming if stream else _check_tool_call_llamaapi_non_streaming
    elif isinstance(client, openai.OpenAI):
        check_func = _check_tool_call_openai_streaming if stream else _check_tool_call_openai_non_streaming
    else:
        raise NotImplementedError(f"Provider {provider_config.provider} not supported")

    first_turn_result = send_request_and_check_result(test_case, model, stream, provider_config, check_func)
    if not first_turn_result.result["pass"]:
        return first_turn_result

    # second turn, pass back tool response and check summarization
    tool_response = test_case.criteria_params["get_weather"]
    second_turn_request_messages = []
    for message in first_turn_result.request_json["messages"]:
        second_turn_request_messages.append(message)

    # add assistant message response
    assistant_msg = extract_assistant_message_from_response(first_turn_result.response_json)
    second_turn_request_messages.append(assistant_msg)

    if len(assistant_msg["tool_calls"]) == 0:
        first_turn_result.result["pass"] = False
        first_turn_result.result["reason"] = "No tool calls found"
        return first_turn_result

    # add tool response
    second_turn_request_messages.append(
        {"role": "tool", "content": tool_response, "tool_call_id": assistant_msg["tool_calls"][0]["id"]}
    )

    # check second turn
    second_turn_request_json = {
        **first_turn_result.request_json,
        "messages": second_turn_request_messages,
    }

    try:
        response = client.chat.completions.create(
            **second_turn_request_json,
        )
    except Exception as e:
        return CriteriaTestResult(
            id=test_case.id,
            model=model,
            stream=stream,
            provider=provider_config.provider.value,
            request_json=second_turn_request_json,
            response_json={},
            result={"pass": False, "reason": str(e)},
            criteria=test_case.criteria,
            criteria_params=test_case.criteria_params,
            metadata=test_case.metadata,
        )

    if stream:
        response = list(response)

    if isinstance(client, llama_api_client.LlamaAPIClient):
        check_func = (
            _check_basic_chat_completion_llamaapi_streaming
            if stream
            else _check_basic_chat_completion_llamaapi_non_streaming
        )
    elif isinstance(client, openai.OpenAI):
        check_func = (
            _check_basic_chat_completion_openai_streaming
            if stream
            else _check_basic_chat_completion_openai_non_streaming
        )
    else:
        raise NotImplementedError(f"Provider {provider_config.provider} not supported")

    result = check_func(response, test_case)

    return CriteriaTestResult(
        id=test_case.id,
        model=model,
        stream=stream,
        provider=provider_config.provider.value,
        request_json=second_turn_request_json,
        response_json=response.to_dict() if not stream else {"data": [chunk.to_dict() for chunk in response]},
        result=result,
        criteria=test_case.criteria,
        criteria_params=test_case.criteria_params,
        metadata=test_case.metadata,
    )
