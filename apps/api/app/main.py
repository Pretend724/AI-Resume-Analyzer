from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.routers.health import router as health_router
from app.routers.resumes import router as resumes_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    yield


def _build_error_payload(code: str, message: str, details: object | None = None) -> dict[str, object]:
    error_payload: dict[str, object] = {
        "code": code,
        "message": message,
    }
    if details is not None:
        error_payload["details"] = details
    return {"error": error_payload}


def create_app() -> FastAPI:
    app = FastAPI(
        title="AI Resume Analyzer API",
        description="Backend API for PDF resume analysis and job matching.",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content=_build_error_payload(
                "VALIDATION_ERROR",
                "Request validation failed.",
                exc.errors(),
            ),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request,
        exc: StarletteHTTPException,
    ) -> JSONResponse:
        detail = exc.detail if isinstance(exc.detail, dict) else {
            "code": "HTTP_ERROR",
            "message": str(exc.detail),
        }
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": detail},
        )

    @app.exception_handler(Exception)
    async def unexpected_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content=_build_error_payload(
                "INTERNAL_SERVER_ERROR",
                "An unexpected error occurred.",
            ),
        )

    app.include_router(health_router)
    app.include_router(resumes_router)

    return app


app = create_app()
