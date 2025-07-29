from ..interface import TestCriteria
from .basic import check_basic_chat_completion
from .long_context import check_long_context_chat_completion
from .structured import check_structured_output
from .tool_call import check_tool_call
from .tool_response import check_tool_response
from .usage import check_usage
from .vision import check_vision

CRITERIAS: dict[str, TestCriteria] = {
    "basic_chat_completion": check_basic_chat_completion,
    "structured_output": check_structured_output,
    "vision": check_vision,
    "tool_call": check_tool_call,
    "tool_response": check_tool_response,
    "long_context": check_long_context_chat_completion,
    "usage": check_usage,
}


def get_criteria(criteria: str) -> TestCriteria:
    """Get the criteria function."""
    return CRITERIAS[criteria]
