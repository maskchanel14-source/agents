"""Typed application configuration.

Every integration (storage, queue, ASR, LLM) is selected here so the rest of the
code only depends on interfaces, never on a single vendor.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PlanName = Literal["free", "pro", "business"]


class PlanLimits(BaseSettings):
    """Per-plan quotas. Override with env vars e.g. PLAN_PRO_MINUTES=600."""

    minutes_per_month: int
    max_clips_per_video: int
    max_projects: int
    max_upload_mb: int
    max_video_minutes: int
    priority: bool = False


PLANS: dict[str, dict] = {
    "free": {
        "label": "Free",
        "minutes_per_month": 30,
        "max_clips_per_video": 3,
        "max_projects": 5,
        "max_upload_mb": 256,
        "max_video_minutes": 30,
        "priority": False,
        "features": ["basic_presets", "720p_export"],
    },
    "pro": {
        "label": "Pro",
        "minutes_per_month": 300,
        "max_clips_per_video": 10,
        "max_projects": 50,
        "max_upload_mb": 1024,
        "max_video_minutes": 90,
        "priority": False,
        "features": ["all_presets", "1080p_export", "deep_llm", "vision_analysis"],
    },
    "business": {
        "label": "Business",
        "minutes_per_month": 1500,
        "max_clips_per_video": 20,
        "max_projects": 500,
        "max_upload_mb": 4096,
        "max_video_minutes": 240,
        "priority": True,
        "features": [
            "all_presets",
            "1080p_export",
            "deep_llm",
            "vision_analysis",
            "batch_processing",
            "priority_queue",
        ],
    },
}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../../.env"), env_file_encoding="utf-8", extra="ignore"
    )

    # App
    app_name: str = "AI Viral Clip Generator"
    env: str = "development"
    log_level: str = "INFO"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_prefix: str = "/api"
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    # Storage / data
    data_dir: Path = Path("./data")
    database_url: str = "sqlite+aiosqlite:///./data/viralclips.db"

    # Auth
    auth_login_per_min: int = 10
    auth_register_per_min: int = 5
    jwt_secret: str = "dev-insecure-secret-change-me"
    jwt_ttl_hours: int = 168
    cookie_name: str = "vc_token"
    cookie_secure: bool = False
    supabase_url: str | None = None
    supabase_jwt_secret: str | None = None
    supabase_anon_key: str | None = None
    supabase_service_role_key: str | None = None

    # Object storage
    storage_backend: Literal["local", "r2"] = "local"
    r2_account_id: str | None = None
    r2_access_key_id: str | None = None
    r2_secret_access_key: str | None = None
    r2_bucket: str | None = None
    r2_public_base_url: str | None = None
    signed_url_ttl_seconds: int = 3600

    # Queue
    queue_backend: Literal["inline", "rq"] = "inline"
    redis_url: str = "redis://127.0.0.1:6379/0"
    job_max_workers: int = 1

    # ASR
    asr_provider: Literal["auto", "openai", "groq", "faster_whisper", "fixture", "none"] = "auto"
    asr_base_url: str = "https://api.openai.com/v1"
    asr_api_key: str | None = None
    asr_model: str = "whisper-1"
    asr_language: str | None = None
    faster_whisper_model: str = "small"
    faster_whisper_device: str = "cpu"

    # LLM
    llm_provider: Literal[
        "auto", "openai", "anthropic", "groq", "gemini", "ollama", "heuristic"
    ] = "auto"
    llm_api_key: str | None = None
    llm_base_url: str | None = None
    llm_model_fast: str = "gpt-4o-mini"
    llm_model_deep: str = "gpt-4o"
    llm_timeout_seconds: int = 90
    llm_max_retries: int = 3
    llm_max_output_tokens: int = 2000
    vision_enabled: bool = False
    vision_max_frames: int = 12

    # Media
    ffmpeg_bin: str | None = None
    ffmpeg_threads: int = 2
    max_upload_mb: int = 512
    max_video_minutes: int = 90
    temp_ttl_hours: int = 24
    enable_youtube_ingest: bool = False

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _parse_origins(cls, v):
        if isinstance(v, str):
            v = v.strip()
            if v.startswith("["):
                return json.loads(v)
            return [o.strip() for o in v.split(",") if o.strip()]
        return v

    # ── Derived ─────────────────────────────────────────────
    @property
    def media_root(self) -> Path:
        return self.data_dir / "media"

    @property
    def work_root(self) -> Path:
        return self.data_dir / "work"

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")

    def plan(self, name: str) -> dict:
        return PLANS.get(name, PLANS["free"])

    def llm_configured(self) -> bool:
        if self.llm_provider == "heuristic":
            return False
        if self.llm_provider == "ollama":
            return bool(self.llm_base_url)
        return bool(self.llm_api_key)

    def asr_configured(self) -> bool:
        if self.asr_provider in {"fixture", "none"}:
            return self.asr_provider == "fixture"
        if self.asr_provider == "faster_whisper":
            return True
        return bool(self.asr_api_key)

    def ensure_dirs(self) -> None:
        for p in (self.data_dir, self.media_root, self.work_root):
            p.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    s = Settings()
    s.ensure_dirs()
    return s


settings = get_settings()
