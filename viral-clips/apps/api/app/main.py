"""FastAPI application entry point."""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app import __version__
from app.core.config import settings
from app.core.db import init_db
from app.services.media.ffmpeg import MediaError

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s :: %(message)s",
)
log = logging.getLogger("api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.ensure_dirs()
    await init_db()
    log.info(
        "%s %s starting — storage=%s queue=%s llm=%s asr=%s",
        settings.app_name, __version__, settings.storage_backend,
        settings.queue_backend, settings.llm_provider, settings.asr_provider,
    )
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="AI Viral Clip Generator API",
        version=__version__,
        description=(
            "Turn long-form videos into vertical short clips. Analysis, moment "
            "detection, subtitles and rendering."
        ),
        lifespan=lifespan,
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "Range"],
        expose_headers=["Content-Range", "Content-Length", "Accept-Ranges"],
    )

    @app.exception_handler(MediaError)
    async def media_error_handler(request: Request, exc: MediaError):
        log.warning("media error on %s: %s", request.url.path, exc)
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": str(exc)},
        )

    @app.middleware("http")
    async def security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
        if request.url.path.startswith("/api"):
            response.headers.setdefault("Cache-Control", "no-store")
        return response

    from app.api.routes import auth, clips, jobs, media, projects, system, usage

    api = APIRouter(prefix=settings.api_prefix)
    api.include_router(auth.router)
    api.include_router(projects.router)
    api.include_router(clips.router)
    api.include_router(jobs.router)
    api.include_router(usage.router)
    api.include_router(system.router)
    app.include_router(api)
    app.include_router(media.router)  # /media/{key} (root, not /api)

    return app


app = create_app()
