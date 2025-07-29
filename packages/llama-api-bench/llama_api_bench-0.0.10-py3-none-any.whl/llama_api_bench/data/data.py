from .basic import BASIC_DATA
from .long_context import LONG_CONTEXT_DATA
from .structured import STRUCTURED_DATA
from .tool_call import TOOL_CALL_DATA
from .tool_response import TOOL_RESPONSE_DATA
from .types import CriteriaTestCase
from .usage import USAGE_DATA
from .vision import VISION_DATA

ALL_TEST_CASES: dict[str, CriteriaTestCase] = {
    **BASIC_DATA,
    **STRUCTURED_DATA,
    **TOOL_CALL_DATA,
    **VISION_DATA,
    **TOOL_RESPONSE_DATA,
    **LONG_CONTEXT_DATA,
    **USAGE_DATA,
}
