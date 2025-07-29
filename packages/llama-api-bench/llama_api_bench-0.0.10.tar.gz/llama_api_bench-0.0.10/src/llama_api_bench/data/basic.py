from .tool_call import GET_WEATHER_TOOL
from .types import CriteriaTestCase

BASIC_DATA: dict[str, CriteriaTestCase] = {
    "basic_paris": CriteriaTestCase(
        id="basic_paris",
        request_data={"messages": [{"role": "user", "content": "What is the capital of France?"}]},
        criteria="basic_chat_completion",
        criteria_params={"expected_output": ["paris"]},
    ),
    "basic_saturn": CriteriaTestCase(
        id="basic_saturn",
        request_data={
            "messages": [
                {"role": "user", "content": "Which planet has rings around it with a name starting with letter S?"}
            ]
        },
        criteria="basic_chat_completion",
        criteria_params={"expected_output": ["saturn"]},
    ),
    "basic_dont_call_tool": CriteriaTestCase(
        id="basic_dont_call_tool",
        request_data={
            "messages": [
                {
                    "role": "user",
                    "content": "Which planet has rings around it with a name starting with letter S? Dont use tools. ",
                },
            ],
            "tools": [GET_WEATHER_TOOL],
        },
        criteria="basic_chat_completion",
        criteria_params={"expected_output": ["saturn"]},
    ),
}
