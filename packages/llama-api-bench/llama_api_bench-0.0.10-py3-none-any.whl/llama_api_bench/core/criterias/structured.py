import json
from typing import Any

import llama_api_client
import openai
from llama_api_client.resources.chat.completions import (
    CreateChatCompletionResponse,
    CreateChatCompletionResponseStreamChunk,
    Stream,
)
from pydantic import BaseModel

from ...data.types import CriteriaTestCase, CriteriaTestResult
from ..interface import ProviderConfig
from ..providers import get_provider_client
from .common import send_request_and_check_result


def _check_valid_json(prediction: str, expected_output: list[BaseModel]) -> dict[str, Any]:
    try:
        actual_json = json.loads(prediction)
        # just check if keys are equal
        expected_keys = set(expected_output[0].keys())
        is_pass = set(actual_json.keys()) == expected_keys
        return {
            "pass": is_pass,
            "reason": "Keys are not equal" if not is_pass else None,
        }
    except json.JSONDecodeError:
        return {"pass": False, "reason": "Invalid JSON", "prediction": prediction}


def _check_structured_output_openai_non_streaming(
    response: Any,
    test_case: CriteriaTestCase,
) -> dict[str, Any]:
    prediction = response.choices[0].message.content.lower()
    expected_output = test_case.criteria_params["expected_output"]
    return _check_valid_json(prediction, expected_output)


def _check_structured_output_openai_streaming(
    response: Any,
    test_case: CriteriaTestCase,
) -> dict[str, Any]:
    prediction = ""
    for chunk in response:
        prediction += chunk.choices[0].delta.content or ""

    prediction = prediction.lower()
    expected_output = test_case.criteria_params["expected_output"]
    return _check_valid_json(prediction, expected_output)


def _check_structured_output_llamaapi_non_streaming(
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
    return _check_valid_json(prediction, expected_output)


def _check_structured_output_llamaapi_streaming(
    response: Stream[CreateChatCompletionResponseStreamChunk],
    test_case: CriteriaTestCase,
) -> dict[str, Any]:
    prediction = ""
    for chunk in response:
        if chunk.event.delta.type == "text":
            prediction += chunk.event.delta.text

    prediction = prediction.lower()
    expected_output = test_case.criteria_params["expected_output"]
    return _check_valid_json(prediction, expected_output)


def check_structured_output(
    test_case: CriteriaTestCase, model: str, stream: bool, provider_config: ProviderConfig
) -> CriteriaTestResult:
    """Check the structured output."""
    client = get_provider_client(provider_config)
    if isinstance(client, llama_api_client.LlamaAPIClient):
        check_func = (
            _check_structured_output_llamaapi_streaming if stream else _check_structured_output_llamaapi_non_streaming
        )
    elif isinstance(client, openai.OpenAI):
        check_func = (
            _check_structured_output_openai_streaming if stream else _check_structured_output_openai_non_streaming
        )
    else:
        raise NotImplementedError(f"Provider {provider_config.provider} not supported")

    return send_request_and_check_result(test_case, model, stream, provider_config, check_func)
