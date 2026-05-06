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

## LLM Configuration

The API can enrich resume extraction through an OpenAI-compatible chat completions API.

```txt
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_API_KEY=your-api-key
LLM_MODEL=qwen-plus
```

If these variables are not configured, the API still returns a deterministic profile using local regex and heuristic extraction.
The response includes `profile_extraction.source` and `profile_extraction.warnings` so callers can see whether the result came from the LLM or from the local fallback.
