from typing import Literal

from pydantic import BaseModel, Field


LLMConfigSource = Literal["env", "runtime"]


class LLMConfigResponse(BaseModel):
    base_url: str
    model: str
    is_configured: bool
    api_key_configured: bool
    missing_fields: list[str] = Field(default_factory=list)
    source: LLMConfigSource


class LLMConfigUpdateRequest(BaseModel):
    base_url: str = Field(default="", max_length=500)
    api_key: str = Field(min_length=1, max_length=500)
    model: str = Field(min_length=1, max_length=200)


class LLMConfigTestResponse(BaseModel):
    success: bool
    message: str
