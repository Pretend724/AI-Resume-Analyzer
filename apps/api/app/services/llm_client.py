from dataclasses import dataclass
import json
import os
from pathlib import Path
import re

from dotenv import load_dotenv
from openai import AsyncOpenAI, OpenAIError


DEFAULT_OPENAI_BASE_URL = "https://api.openai.com/v1"
ENV_FILE_PATH = Path(__file__).resolve().parents[2] / ".env"


class LLMClientError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class LLMConfig:
    base_url: str
    api_key: str
    model: str
    timeout_seconds: float = 60.0

    @property
    def is_configured(self) -> bool:
        return not self.missing_fields

    @property
    def missing_fields(self) -> list[str]:
        fields = []
        if not self.api_key.strip():
            fields.append("LLM_API_KEY")
        if not self.model.strip():
            fields.append("LLM_MODEL")
        return fields


def load_llm_config() -> LLMConfig:
    load_dotenv(ENV_FILE_PATH, override=False)

    return LLMConfig(
        base_url=os.getenv("LLM_BASE_URL", DEFAULT_OPENAI_BASE_URL).strip(),
        api_key=os.getenv("LLM_API_KEY", "").strip(),
        model=os.getenv("LLM_MODEL", "").strip(),
    )


async def call_chat_completion(
    messages: list[dict[str, str]],
    *,
    config: LLMConfig | None = None,
) -> str:
    resolved_config = config or load_llm_config()
    if not resolved_config.is_configured:
        missing_fields = ", ".join(resolved_config.missing_fields)
        raise LLMClientError(f"LLM client is not configured. Missing: {missing_fields}.")

    client = AsyncOpenAI(
        api_key=resolved_config.api_key,
        base_url=_normalize_openai_base_url(resolved_config.base_url),
        timeout=resolved_config.timeout_seconds,
    )

    try:
        response = await client.chat.completions.create(
            model=resolved_config.model,
            messages=messages,  # type: ignore[arg-type]
            temperature=0.2,
        )
    except OpenAIError as exc:
        raise LLMClientError("Failed to call LLM provider.") from exc

    choices = response.choices
    if not choices:
        raise LLMClientError("LLM provider returned no choices.")

    content = choices[0].message.content
    if not isinstance(content, str) or not content.strip():
        raise LLMClientError("LLM provider returned an empty message.")

    return content


def extract_json_payload(raw_text: str) -> dict[str, object]:
    cleaned_text = raw_text.strip()
    if cleaned_text.startswith("```"):
        cleaned_text = re.sub(r"^```(?:json)?\s*", "", cleaned_text)
        cleaned_text = re.sub(r"\s*```$", "", cleaned_text)

    try:
        parsed = json.loads(cleaned_text)
    except json.JSONDecodeError:
        json_block_match = re.search(r"\{.*\}", cleaned_text, re.DOTALL)
        if not json_block_match:
            raise LLMClientError("LLM response is not valid JSON.")
        try:
            parsed = json.loads(json_block_match.group(0))
        except json.JSONDecodeError as exc:
            raise LLMClientError("LLM response is not valid JSON.") from exc

    if not isinstance(parsed, dict):
        raise LLMClientError("LLM response must be a JSON object.")

    return parsed


def _normalize_openai_base_url(base_url: str) -> str:
    normalized_base_url = base_url.rstrip("/")
    if normalized_base_url.endswith("/chat/completions"):
        return normalized_base_url[: -len("/chat/completions")]
    return normalized_base_url
