import json
from typing import Any

import llama_api_client
import openai
from llama_api_client.resources.chat.completions import (
    CreateChatCompletionResponse,
    CreateChatCompletionResponseStreamChunk,
    Stream,
)

from ...data.types import CriteriaTestCase, CriteriaTestResult
from ..interface import ProviderConfig
from ..providers import get_provider_client
from .common import send_request_and_check_result


def _check_tools_match(actual_tools: list[dict[str, Any]], expected_tools: list[dict[str, Any]]) -> dict[str, Any]:
    result_pass = False
    result_reason = f"Tool call does not match {actual_tools=}, {expected_tools=}"
    if len(actual_tools) != len(expected_tools):
        return {"pass": result_pass, "reason": result_reason}

    # check tool function names match
    expected_tool_names = [t["function"]["name"] for t in expected_tools]
    actual_tool_names = [t["function"]["name"] for t in actual_tools]

    if set(expected_tool_names) != set(actual_tool_names):
        return {
            "pass": result_pass,
            "reason": f"Tool function names do not match {expected_tool_names=}, {actual_tool_names=}",
        }

    # check tool function argument's key match
    for t in actual_tools:
        try:
            actual_args = json.loads(t["function"]["arguments"])
        except Exception as e:
            return {
                "pass": False,
                "reason": f"Tool function arguments {t['function']['arguments']} are not valid JSON: {e}",
            }

        # check if the actual args match expected args
        match_args = False
        for exp_t in expected_tools:
            if exp_t["function"]["name"] == t["function"]["name"]:
                exp_args = json.loads(exp_t["function"]["arguments"])
                if set(exp_args.keys()) == set(actual_args.keys()):
                    match_args = True

        if not match_args:
            return {
                "pass": result_pass,
                "reason": f"Tool function argument's key do not match {exp_args.keys()=}, {actual_args.keys()=}",
            }

    result_pass = True
    result_reason = f"Tool call matches {actual_tools=}, {expected_tools=}"

    return {"pass": result_pass, "reason": result_reason}


def _check_tool_call_openai_non_streaming(
    response: Any,
    test_case: CriteriaTestCase,
) -> dict[str, Any]:
    actual_tool_calls = response.choices[0].message.tool_calls
    if actual_tool_calls is None:
        return {"pass": False, "reason": "No tool calls found"}

    expected_tool_calls = test_case.criteria_params["tool_calls"]
    return _check_tools_match([x.to_dict() for x in actual_tool_calls], expected_tool_calls)


def _check_tool_call_openai_streaming(
    response: Any,
    test_case: CriteriaTestCase,
) -> dict[str, Any]:
    expected_tool_calls = test_case.criteria_params["tool_calls"]
    actual_tools = {}
    curr_tool_call_id = None

    for chunk in response:
        if chunk.choices[0].delta.tool_calls:
            for tool_call in chunk.choices[0].delta.tool_calls:
                if tool_call.id:
                    curr_tool_call_id = tool_call.id
                if curr_tool_call_id not in actual_tools:
                    actual_tools[curr_tool_call_id] = {
                        "function": {
                            "name": "",
                            "arguments": "",
                        }
                    }

                if tool_call.function.name:
                    actual_tools[curr_tool_call_id]["function"]["name"] = tool_call.function.name
                if tool_call.function.arguments:
                    actual_tools[curr_tool_call_id]["function"]["arguments"] += tool_call.function.arguments

    actual_tool_calls = [{"id": x, **actual_tools[x]} for x in actual_tools]
    return _check_tools_match(actual_tool_calls, expected_tool_calls)


def _check_tool_call_llamaapi_non_streaming(
    response: CreateChatCompletionResponse,
    test_case: CriteriaTestCase,
) -> dict[str, Any]:
    actual_tool_calls = response.completion_message.tool_calls
    if actual_tool_calls is None:
        return {"pass": False, "reason": "No tool calls found"}

    expected_tool_calls = test_case.criteria_params["tool_calls"]
    return _check_tools_match([x.to_dict() for x in actual_tool_calls], expected_tool_calls)


def _check_tool_call_llamaapi_streaming(
    response: Stream[CreateChatCompletionResponseStreamChunk],
    test_case: CriteriaTestCase,
) -> dict[str, Any]:
    expected_tool_calls = test_case.criteria_params["tool_calls"]
    actual_tools = {}
    curr_tool_call_id = None

    for chunk in response:
        if chunk.event.delta.type == "tool_call":
            if chunk.event.delta.id:
                curr_tool_call_id = chunk.event.delta.id
            if curr_tool_call_id not in actual_tools:
                actual_tools[curr_tool_call_id] = {
                    "function": {
                        "name": "",
                        "arguments": "",
                    }
                }

            if chunk.event.delta.function is not None:
                if chunk.event.delta.function.name is not None:
                    actual_tools[curr_tool_call_id]["function"]["name"] = chunk.event.delta.function.name
                if chunk.event.delta.function.arguments is not None:
                    actual_tools[curr_tool_call_id]["function"]["arguments"] += chunk.event.delta.function.arguments

    actual_tool_calls = [{"id": x, **actual_tools[x]} for x in actual_tools]
    return _check_tools_match(actual_tool_calls, expected_tool_calls)


def check_tool_call(
    test_case: CriteriaTestCase, model: str, stream: bool, provider_config: ProviderConfig
) -> CriteriaTestResult:
    """Check the tool_call chat completion."""
    client = get_provider_client(provider_config)

    if isinstance(client, llama_api_client.LlamaAPIClient):
        check_func = _check_tool_call_llamaapi_streaming if stream else _check_tool_call_llamaapi_non_streaming
    elif isinstance(client, openai.OpenAI):
        check_func = _check_tool_call_openai_streaming if stream else _check_tool_call_openai_non_streaming
    else:
        raise NotImplementedError(f"Provider {provider_config.provider} not supported")

    return send_request_and_check_result(test_case, model, stream, provider_config, check_func)
