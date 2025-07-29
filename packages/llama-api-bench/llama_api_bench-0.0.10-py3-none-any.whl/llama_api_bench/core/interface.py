from enum import Enum
from typing import Any, Protocol

from pydantic import BaseModel

from ..data.types import CriteriaTestCase, CriteriaTestResult


class ProviderEnum(Enum):
    OPENAI = "openai"
    LLAMAAPI = "llamaapi"
    LLAMAAPI_OPENAI_COMPAT = "llamaapi-openai-compat"
    OPENROUTER = "openrouter"


class ModelConfig(BaseModel):
    """
    :model: The model name for the provider
    :unsupported_test_cases: The test cases that the model does not support.
    """

    model: str
    unsupported_test_cases: list[str]


class ProviderConfig(BaseModel):
    """
    :provider: The provider to use. One of ProviderEnum.values()
    :api_key: The API key to use.
    """

    provider: ProviderEnum
    provider_params: dict[str, Any]
    available_models: list[ModelConfig]
    extra_params: dict[str, Any] = {}


class TestCriteria(Protocol):
    """
    :param test_case: The test case to run.
    :param model: The model to use.
    :param stream: Whether to stream the response.
    :param provider_config: The provider configuration.
    :return: The test result.
    """

    def __call__(
        self, test_case: CriteriaTestCase, model: str, stream: bool, provider_config: ProviderConfig
    ) -> CriteriaTestResult: ...
