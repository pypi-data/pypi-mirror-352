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


def _check_usage_openai_non_streaming(
    response: Any,
    test_case: CriteriaTestCase,
) -> dict[str, Any]:
    if response.usage is None:
        return {
            "pass": False,
            "usage": "No usage found",
        }

    if response.usage.prompt_tokens != test_case.criteria_params["num_prompt_tokens"]:
        return {
            "pass": False,
            "usage": "Prompt tokens mismatch",
        }

    return {
        "pass": True,
    }


def _check_usage_openai_streaming(
    response: Any,
    test_case: CriteriaTestCase,
) -> dict[str, Any]:
    usage = None
    for chunk in response:
        usage = chunk.usage

    if usage is None:
        return {
            "pass": False,
            "usage": "No usage found",
        }

    if usage.prompt_tokens != test_case.criteria_params["num_prompt_tokens"]:
        return {
            "pass": False,
            "usage": "Prompt tokens mismatch",
        }

    return {
        "pass": True,
    }


def _check_usage_llamaapi_non_streaming(
    response: CreateChatCompletionResponse,
    test_case: CriteriaTestCase,
) -> dict[str, Any]:
    if response.metrics is None:
        return {
            "pass": False,
            "usage": "No usage found",
        }

    for m in response.metrics:
        if m.metric == "num_prompt_tokens":
            if m.value == test_case.criteria_params["num_prompt_tokens"]:
                return {
                    "pass": True,
                }

    return {
        "pass": False,
        "usage": "Prompt tokens mismatch",
    }


def _check_usage_llamaapi_streaming(
    response: Stream[CreateChatCompletionResponseStreamChunk],
    test_case: CriteriaTestCase,
) -> dict[str, Any]:
    usage = None
    for chunk in response:
        if chunk.event.event_type == "metrics":
            usage = chunk.event.metrics

    if usage is None:
        return {
            "pass": False,
            "usage": "No usage found",
        }

    for m in usage:
        if m.metric == "num_prompt_tokens":
            if m.value == test_case.criteria_params["num_prompt_tokens"]:
                return {
                    "pass": True,
                }

    return {
        "pass": False,
        "usage": "Prompt tokens mismatch",
    }


def check_usage(
    test_case: CriteriaTestCase, model: str, stream: bool, provider_config: ProviderConfig
) -> CriteriaTestResult:
    """Check the basic chat completion."""
    client = get_provider_client(provider_config)
    if isinstance(client, llama_api_client.LlamaAPIClient):
        check_func = _check_usage_llamaapi_streaming if stream else _check_usage_llamaapi_non_streaming
    elif isinstance(client, openai.OpenAI):
        check_func = _check_usage_openai_streaming if stream else _check_usage_openai_non_streaming
    else:
        raise NotImplementedError(f"Provider {provider_config.provider} not supported")

    return send_request_and_check_result(test_case, model, stream, provider_config, check_func)
