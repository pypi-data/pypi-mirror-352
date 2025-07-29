from ...data.types import CriteriaTestCase, CriteriaTestResult
from ..interface import ProviderConfig
from .basic import check_basic_chat_completion


def check_long_context_chat_completion(
    test_case: CriteriaTestCase, model: str, stream: bool, provider_config: ProviderConfig
) -> CriteriaTestResult:
    return check_basic_chat_completion(test_case, model, stream, provider_config)
