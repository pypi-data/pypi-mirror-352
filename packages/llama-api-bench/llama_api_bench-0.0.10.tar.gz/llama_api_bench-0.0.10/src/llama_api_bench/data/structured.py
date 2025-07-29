from pydantic import BaseModel

from .types import CriteriaTestCase


class CalendarEvent(BaseModel):
    name: str
    day_of_week: str
    participants: list[str]


class ExtractName(BaseModel):
    name: str


STRUCTURED_DATA: dict[str, CriteriaTestCase] = {
    "structured_calendar_event": CriteriaTestCase(
        id="structured_calendar_event",
        request_data={
            "messages": [
                {
                    "role": "system",
                    "content": "Extract the event information.",
                },
                {
                    "role": "user",
                    "content": "Alice and Bob are going to a Science Fair on Friday.",
                },
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "CalendarEvent",
                    "schema": CalendarEvent.model_json_schema(),
                },
            },
        },
        criteria="structured_output",
        criteria_params={
            "expected_output": [
                CalendarEvent(
                    name="science fair",
                    day_of_week="friday",
                    participants=["alice", "bob"],
                ).model_dump(),
                CalendarEvent(
                    name="science fair",
                    day_of_week="friday",
                    participants=["bob", "alice"],
                ).model_dump(),
            ],
        },
    ),
    "structured_extract_name": CriteriaTestCase(
        id="structured_extract_name",
        request_data={
            "messages": [
                {
                    "role": "system",
                    "content": "Your task is to extract the name of the person from the following text.",
                },
                {
                    "role": "user",
                    "content": "I'm John Doe",
                },
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "ExtractName",
                    "schema": ExtractName.model_json_schema(),
                },
            },
        },
        criteria="structured_output",
        criteria_params={
            "expected_output": [
                ExtractName(
                    name="john doe",
                ).model_dump(),
            ],
        },
    ),
}
