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


def _check_vision_openai_non_streaming(
    response: Any,
    test_case: CriteriaTestCase,
) -> dict[str, Any]:
    prediction = response.choices[0].message.content.lower()
    expected_output = test_case.criteria_params["expected_output"]
    return {
        "pass": any(expected_item.lower() in prediction for expected_item in expected_output),
    }


def _check_vision_openai_streaming(
    response: Any,
    test_case: CriteriaTestCase,
) -> dict[str, Any]:
    prediction = ""
    for chunk in response:
        prediction += chunk.choices[0].delta.content

    prediction = prediction.lower()
    expected_output = test_case.criteria_params["expected_output"]
    return {
        "pass": any(expected_item.lower() in prediction for expected_item in expected_output),
    }


def _check_vision_llamaapi_non_streaming(
    response: CreateChatCompletionResponse,
    test_case: CriteriaTestCase,
) -> dict[str, Any]:
    out_msg_content = response.completion_message.content
    if isinstance(out_msg_content, str):
        prediction = out_msg_content.lower()
    elif out_msg_content.type == "text":
        prediction = out_msg_content.text.lower()
    else:
        return {"pass": False, "reason": "Incorrect content type", "prediction": out_msg_content}

    expected_output = test_case.criteria_params["expected_output"]
    return {
        "pass": any(expected_item.lower() in prediction for expected_item in expected_output),
    }


def _check_vision_llamaapi_streaming(
    response: Stream[CreateChatCompletionResponseStreamChunk],
    test_case: CriteriaTestCase,
) -> dict[str, Any]:
    prediction = ""
    for chunk in response:
        if chunk.event.delta.type == "text":
            prediction += chunk.event.delta.text

    prediction = prediction.lower()
    expected_output = test_case.criteria_params["expected_output"]
    return {
        "pass": any(expected_item.lower() in prediction for expected_item in expected_output),
    }


def check_vision(
    test_case: CriteriaTestCase, model: str, stream: bool, provider_config: ProviderConfig
) -> CriteriaTestResult:
    """Check the vision chat completion."""
    client = get_provider_client(provider_config)

    if isinstance(client, llama_api_client.LlamaAPIClient):
        check_func = _check_vision_llamaapi_streaming if stream else _check_vision_llamaapi_non_streaming
    elif isinstance(client, openai.OpenAI):
        check_func = _check_vision_openai_streaming if stream else _check_vision_openai_non_streaming
    else:
        raise NotImplementedError(f"Provider {provider_config.provider} not supported")

    return send_request_and_check_result(test_case, model, stream, provider_config, check_func)
