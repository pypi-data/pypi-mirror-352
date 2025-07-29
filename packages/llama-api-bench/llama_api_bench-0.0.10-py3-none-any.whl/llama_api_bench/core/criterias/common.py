from typing import Any, Callable

from ...data.types import CriteriaTestCase, CriteriaTestResult
from ..interface import ProviderConfig, ProviderEnum
from ..providers import get_provider_client


def get_request_json(
    test_case: CriteriaTestCase, model: str, stream: bool, provider_config: ProviderConfig
) -> dict[str, Any]:
    """Get the request JSON."""
    if provider_config.provider == ProviderEnum.LLAMAAPI:
        return {
            "model": model,
            "stream": stream,
            **test_case.request_data,
        }
    elif provider_config.provider in {
        ProviderEnum.OPENAI,
        ProviderEnum.LLAMAAPI_OPENAI_COMPAT,
        ProviderEnum.OPENROUTER,
    }:
        return {
            "model": model,
            "stream": stream,
            **test_case.request_data,
            **provider_config.extra_params,
        }
    else:
        raise ValueError(f"Provider {provider_config.provider} not supported")


def extract_assistant_message_from_response(response: Any) -> dict[str, Any]:
    if not isinstance(response, dict):
        raise ValueError(f"Unexpected response type: {type(response)}")

    if "choices" in response:
        return response["choices"][0]["message"]
    if "completion_message" in response:
        return response["completion_message"]
    if "data" in response:
        # this is a streaming response, we need to aggregate the assistant message from all chunks
        tool_calls: list[dict[str, Any]] = []
        assistant_msg = {"role": "assistant", "content": "", "tool_calls": tool_calls}
        curr_tool_call_id = None
        aggregated_tool_calls = {}
        for chunk in response["data"]:
            if "choices" in chunk:
                delta = chunk["choices"][0]["delta"]
                if "content" in delta:
                    assistant_msg["content"] += delta["content"] or ""  # type: ignore
                if "tool_calls" in delta:
                    for tool_call in delta["tool_calls"]:
                        if "id" in tool_call:
                            curr_tool_call_id = tool_call["id"]
                        if curr_tool_call_id is None:
                            continue
                        if curr_tool_call_id not in aggregated_tool_calls:
                            aggregated_tool_calls[curr_tool_call_id] = {
                                "function": {
                                    "name": "",
                                    "arguments": "",
                                },
                                "type": "function",
                                "id": curr_tool_call_id,
                            }
                        if "name" in tool_call["function"]:
                            aggregated_tool_calls[curr_tool_call_id]["function"]["name"] = tool_call["function"]["name"]
                        if "arguments" in tool_call["function"]:
                            aggregated_tool_calls[curr_tool_call_id]["function"]["arguments"] += tool_call["function"][
                                "arguments"
                            ]
                assistant_msg["tool_calls"] = [x for _, x in aggregated_tool_calls.items()]
            if "event" in chunk:
                if chunk["event"]["delta"]["type"] == "text":
                    assistant_msg["content"] += chunk["event"]["delta"]["text"]
                elif chunk["event"]["delta"]["type"] == "tool_call":
                    tool_call = chunk["event"]["delta"]
                    if "id" in tool_call:
                        curr_tool_call_id = tool_call["id"]
                    if curr_tool_call_id is None:
                        continue
                    if curr_tool_call_id not in aggregated_tool_calls:
                        aggregated_tool_calls[curr_tool_call_id] = {
                            "function": {
                                "name": "",
                                "arguments": "",
                            },
                            "type": "function",
                            "id": curr_tool_call_id,
                        }
                    if "name" in tool_call["function"]:
                        aggregated_tool_calls[curr_tool_call_id]["function"]["name"] = tool_call["function"]["name"]
                    if "arguments" in tool_call["function"]:
                        aggregated_tool_calls[curr_tool_call_id]["function"]["arguments"] += tool_call["function"][
                            "arguments"
                        ]
                assistant_msg["tool_calls"] = [x for _, x in aggregated_tool_calls.items()]

        return assistant_msg

    raise ValueError(f"Unexpected response type: {type(response)}")


def send_request_and_check_result(
    test_case: CriteriaTestCase,
    model: str,
    stream: bool,
    provider_config: ProviderConfig,
    check_func: Callable[[Any, CriteriaTestCase], dict[str, Any]],
):
    """Run a criteria check with common error handling and response processing."""
    client = get_provider_client(provider_config)
    request_json = get_request_json(test_case, model, stream, provider_config)

    try:
        response = client.chat.completions.create(
            **request_json,
        )
    except Exception as e:
        return CriteriaTestResult(
            id=test_case.id,
            model=model,
            stream=stream,
            provider=provider_config.provider.value,
            request_json=request_json,
            response_json={},
            result={"pass": False, "reason": str(e)},
            criteria=test_case.criteria,
            criteria_params=test_case.criteria_params,
            metadata=test_case.metadata,
        )

    if stream:
        response = list(response)

    result = check_func(response, test_case)

    for m in request_json["messages"]:
        if len(m["content"]) > 4096:
            m["content"] = m["content"][:4096] + "..."

    return CriteriaTestResult(
        id=test_case.id,
        model=model,
        stream=stream,
        provider=provider_config.provider.value,
        request_json=request_json,
        response_json=response.to_dict() if not stream else {"data": [chunk.to_dict() for chunk in response]},
        result=result,
        criteria=test_case.criteria,
        criteria_params=test_case.criteria_params,
        metadata=test_case.metadata,
    )
