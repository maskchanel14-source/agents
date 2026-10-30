from __future__ import annotations

from fastapi import APIRouter

from app import __version__
from app.core.config import PLANS, settings
from app.schemas import HealthOut, PlanInfo, ProviderStatus
from app.services.media.ffmpeg import ffmpeg_path, ffmpeg_version
from app.services.media.presets import PRESETS

router = APIRouter(tags=["system"])


@router.get("/health", response_model=HealthOut)
async def health():
    return HealthOut(
        status="ok",
        version=__version__,
        env=settings.env,
        database="sqlite" if settings.is_sqlite else "postgres",
        ffmpeg=bool(ffmpeg_path()),
    )


@router.get("/providers", response_model=ProviderStatus)
async def providers():
    warnings: list[str] = []
    if not settings.asr_configured():
        warnings.append(
            "No transcription provider configured (ASR_API_KEY missing). "
            "Analysis will use acoustic + visual signals only, without captions."
        )
    if not settings.llm_configured():
        warnings.append(
            "No LLM provider configured (LLM_API_KEY missing). Viral scoring uses the "
            "deterministic local heuristic model, not an LLM."
        )
    if settings.storage_backend == "local":
        warnings.append("Local disk storage is for development; configure R2 for production.")
    if settings.queue_backend == "inline":
        warnings.append("Inline queue is single-node only; use QUEUE_BACKEND=rq in production.")
    if not settings.cookie_secure and settings.env == "production":
        warnings.append("COOKIE_SECURE is false in production.")
    return ProviderStatus(
        llm_provider=settings.llm_provider,
        llm_configured=settings.llm_configured(),
        llm_model_fast=settings.llm_model_fast,
        llm_model_deep=settings.llm_model_deep,
        asr_provider=settings.asr_provider,
        asr_configured=settings.asr_configured(),
        asr_model=settings.asr_model,
        storage_backend=settings.storage_backend,
        queue_backend=settings.queue_backend,
        vision_enabled=settings.vision_enabled,
        ffmpeg_version=ffmpeg_version(),
        ffmpeg_path=ffmpeg_path(),
        youtube_ingest=settings.enable_youtube_ingest,
        supabase_auth=bool(settings.supabase_jwt_secret),
        warnings=warnings,
    )


@router.get("/presets")
async def presets():
    return {
        "default": "bold_viral",
        "presets": [
            {
                "id": key,
                "label": value["label"],
                "tier": value.get("tier", "free"),
                "font": value["font"],
                "size": value["size"],
                "primary": value["primary"],
                "highlight": value["highlight"],
                "karaoke": value["karaoke"],
                "max_words": value["max_words"],
            }
            for key, value in PRESETS.items()
        ],
    }


@router.get("/plans")
async def plans():
    return [
        PlanInfo(
            name=key,
            label=value.get("label", key.title()),
            minutes_per_month=value["minutes_per_month"],
            max_clips_per_video=value["max_clips_per_video"],
            max_projects=value["max_projects"],
            max_upload_mb=value["max_upload_mb"],
            max_video_minutes=value["max_video_minutes"],
            features=value.get("features", []),
        )
        for key, value in PLANS.items()
    ]
