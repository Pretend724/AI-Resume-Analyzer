# AI Resume Analyzer API

FastAPI backend for the AI Resume Analyzer MVP.

## Development

```bash
uv run uvicorn app.main:app --reload --port 8000
```

Health check:

```txt
GET http://localhost:8000/health
```

Analyze a resume:

```txt
POST /resumes/analyze
Content-Type: multipart/form-data
```
