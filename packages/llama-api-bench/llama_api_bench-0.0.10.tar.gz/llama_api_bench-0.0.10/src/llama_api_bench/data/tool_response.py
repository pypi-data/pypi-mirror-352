from .tool_call import GET_WEATHER_TOOL
from .types import CriteriaTestCase

TOOL_RESPONSE_DATA: dict[str, CriteriaTestCase] = {
    "tool_response_get_weather": CriteriaTestCase(
        id="tool_response_get_weather",
        request_data={
            "messages": [
                {
                    "role": "user",
                    "content": "What is the weather in San Francisco?",
                },
            ],
            "tools": [GET_WEATHER_TOOL],
        },
        criteria="tool_response",
        criteria_params={
            "tool_calls": [
                {
                    "function": {
                        "name": "get_weather",
                        "arguments": '{"location":"San Francisco"}',
                    },
                },
            ],
            # NOTE: change this to sunny and fails the test
            "get_weather": '{"response":"sunny"}',
            "expected_output": ["sunny"],
        },
    ),
}
