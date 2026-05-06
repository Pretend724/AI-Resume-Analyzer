from dataclasses import dataclass
import json
import os
import re

import httpx


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
        return bool(self.base_url.strip() and self.api_key.strip() and self.model.strip())


def load_llm_config() -> LLMConfig:
    return LLMConfig(
        base_url=os.getenv("LLM_BASE_URL", "").strip(),
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
        raise LLMClientError("LLM client is not configured.")

    payload = {
        "model": resolved_config.model,
        "messages": messages,
        "temperature": 0.2,
    }
    headers = {
        "Authorization": f"Bearer {resolved_config.api_key}",
        "Content-Type": "application/json",
    }
    url = _build_chat_completions_url(resolved_config.base_url)

    try:
        async with httpx.AsyncClient(timeout=resolved_config.timeout_seconds) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
    except httpx.HTTPError as exc:
        raise LLMClientError("Failed to call LLM provider.") from exc

    try:
        data = response.json()
    except ValueError as exc:
        raise LLMClientError("LLM provider returned invalid JSON.") from exc

    choices = data.get("choices") or []
    if not choices:
        raise LLMClientError("LLM provider returned no choices.")

    message = choices[0].get("message") or {}
    content = message.get("content")
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


def _build_chat_completions_url(base_url: str) -> str:
    normalized_base_url = base_url.rstrip("/")
    if normalized_base_url.endswith("/chat/completions"):
        return normalized_base_url
    return f"{normalized_base_url}/chat/completions"
