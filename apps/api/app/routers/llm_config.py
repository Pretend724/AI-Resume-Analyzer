from fastapi import APIRouter

from app.schemas.llm_config import (
    LLMConfigResponse,
    LLMConfigTestResponse,
    LLMConfigUpdateRequest,
)
from app.services.llm_client import (
    DEFAULT_OPENAI_BASE_URL,
    LLMConfig,
    LLMClientError,
    call_chat_completion,
    clear_runtime_llm_config,
    has_runtime_llm_config,
    load_llm_config,
    set_runtime_llm_config,
)

router = APIRouter(prefix="/llm", tags=["llm"])


@router.get("/config", response_model=LLMConfigResponse)
async def get_llm_config() -> LLMConfigResponse:
    return build_llm_config_response(load_llm_config())


@router.put("/config", response_model=LLMConfigResponse)
async def update_llm_config(request: LLMConfigUpdateRequest) -> LLMConfigResponse:
    config = set_runtime_llm_config(
        LLMConfig(
            base_url=(request.base_url or DEFAULT_OPENAI_BASE_URL).strip(),
            api_key=request.api_key.strip(),
            model=request.model.strip(),
        )
    )
    return build_llm_config_response(config)


@router.post("/config/test", response_model=LLMConfigTestResponse)
async def test_llm_config(request: LLMConfigUpdateRequest) -> LLMConfigTestResponse:
    config = LLMConfig(
        base_url=(request.base_url or DEFAULT_OPENAI_BASE_URL).strip(),
        api_key=request.api_key.strip(),
        model=request.model.strip(),
        timeout_seconds=20.0,
    )

    try:
        content = await call_chat_completion(
            [
                {
                    "role": "system",
                    "content": "You are a connection test endpoint. Reply with a short OK.",
                },
                {
                    "role": "user",
                    "content": "Reply with OK.",
                },
            ],
            config=config,
        )
    except LLMClientError as exc:
        return LLMConfigTestResponse(
            success=False,
            message=str(exc),
        )

    return LLMConfigTestResponse(
        success=True,
        message=content[:120],
    )


@router.delete("/config", response_model=LLMConfigResponse)
async def reset_llm_config() -> LLMConfigResponse:
    clear_runtime_llm_config()
    return build_llm_config_response(load_llm_config())


def build_llm_config_response(config: LLMConfig) -> LLMConfigResponse:
    return LLMConfigResponse(
        base_url=config.base_url,
        model=config.model,
        is_configured=config.is_configured,
        api_key_configured=bool(config.api_key.strip()),
        missing_fields=config.missing_fields,
        source="runtime" if has_runtime_llm_config() else "env",
    )
