from typing import Any, Dict

from pydantic import BaseModel, Field


class CriteriaTestCase(BaseModel):
    id: str
    request_data: Dict[str, Any] = Field(default_factory=dict)
    criteria: str
    criteria_params: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CriteriaTestResult(BaseModel):
    id: str
    model: str
    stream: bool
    provider: str
    request_json: Dict[str, Any] = Field(default_factory=dict)
    response_json: Dict[str, Any] = Field(default_factory=dict)
    result: Dict[str, Any] = Field(default_factory=dict)
    criteria: str
    criteria_params: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
