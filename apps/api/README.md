# AI Resume Analyzer API

FastAPI backend for the AI Resume Analyzer MVP.

## Development

```bash
uv run uvicorn app.main:app --reload --port 8001
```

Health check:

```txt
GET http://localhost:8001/health
```

Analyze a resume:

```txt
POST /resumes/analyze
Content-Type: multipart/form-data
```

Match a resume against a job description:

```txt
POST /resumes/match
Content-Type: application/json
```

When LLM configuration is available, matching uses the rule-based keyword and experience analysis as evidence, then asks the configured model for a final score and recruiter-facing summary. The response field `scoring.source` indicates whether the final score came from `llm`, `rule_based`, or `llm_fallback`.

## LLM Configuration

The API can enrich resume extraction through the official OpenAI Python SDK. OpenAI-compatible providers are supported through `LLM_BASE_URL`.

Create `apps/api/.env`:

```txt
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_API_KEY=your-api-key
LLM_MODEL=qwen-plus
```

`LLM_BASE_URL` defaults to `https://api.openai.com/v1` when omitted.
If these variables are not configured, the API still returns a deterministic profile using local regex and heuristic extraction.
The response includes `profile_extraction.source` and `profile_extraction.warnings` so callers can see whether the result came from the LLM or from the local fallback.

Check whether the backend has loaded the configuration without printing the API key:

```bash
uv run python -c "from app.services.llm_client import load_llm_config; c=load_llm_config(); print({'configured': c.is_configured, 'base_url': c.base_url, 'model': c.model, 'api_key_loaded': bool(c.api_key), 'missing_fields': c.missing_fields})"
```

When `POST /resumes/analyze` returns `profile_extraction.source: "llm"`, the AI provider was used. `heuristic` means the local fallback was used because configuration is incomplete, and `llm_fallback` means the provider call or response parsing failed.
