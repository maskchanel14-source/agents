"""Pydantic request/response models (the public API contract)."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, EmailStr, Field, field_validator


# ── Auth ────────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    display_name: str | None = Field(default=None, max_length=120)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class UserOut(BaseModel):
    id: str
    email: str
    display_name: str | None = None
    plan: str
    is_admin: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Projects ────────────────────────────────────────────────
class UrlIngestRequest(BaseModel):
    url: str = Field(min_length=8, max_length=2048)
    title: str | None = Field(default=None, max_length=200)
    attests_rights: bool = False


class ProjectOut(BaseModel):
    id: str
    title: str
    source_type: str
    source_url: str | None = None
    status: str
    stage: str
    progress: int
    duration_s: float | None = None
    width: int | None = None
    height: int | None = None
    fps: float | None = None
    language: str | None = None
    error: str | None = None
    poster_url: str | None = None
    source_url_playable: str | None = None
    clip_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AnalyzeRequest(BaseModel):
    target_clips: int = Field(default=5, ge=1, le=20)
    min_seconds: float = Field(default=15, ge=8, le=180)
    max_seconds: float = Field(default=60, ge=10, le=240)
    language: str | None = Field(default=None, max_length=12)
    use_deep_model: bool = True
    allow_overlap: bool = False

    @field_validator("max_seconds")
    @classmethod
    def _check_range(cls, v: float, info):
        mn = info.data.get("min_seconds", 15)
        if v <= mn:
            raise ValueError("max_seconds must be greater than min_seconds")
        return v


class ClipOut(BaseModel):
    id: str
    project_id: str
    start_s: float
    end_s: float
    duration_s: float
    title: str
    hook: str | None = None
    text: str
    score: float
    score_breakdown: dict[str, Any] | None = None
    explanation: str | None = None
    tags: list[str] | None = None
    status: str
    preset: str
    crop_x: float | None = None
    fit_mode: str = "crop"
    subtitle_json: dict[str, Any] | None = None
    video_url: str | None = None
    thumb_url: str | None = None
    render_error: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ClipPatch(BaseModel):
    title: str | None = Field(default=None, max_length=200)
    hook: str | None = Field(default=None, max_length=300)
    start_s: float | None = Field(default=None, ge=0)
    end_s: float | None = Field(default=None, gt=0)
    crop_x: float | None = Field(default=None, ge=0, le=1)
    fit_mode: Literal["crop", "blur"] | None = None
    preset: str | None = None
    subtitle_json: dict[str, Any] | None = None


class JobOut(BaseModel):
    id: str
    project_id: str | None = None
    type: str
    status: str
    stage: str
    progress: int
    error: str | None = None
    result: dict[str, Any] | None = None
    created_at: datetime
    started_at: datetime | None = None
    finished_at: datetime | None = None

    model_config = {"from_attributes": True}


class TranscriptOut(BaseModel):
    project_id: str
    language: str | None = None
    provider: str
    model: str | None = None
    full_text: str
    segments: list[dict[str, Any]]
    words: list[dict[str, Any]]
    speakers: list[dict[str, Any]] | None = None


class RenderRequest(BaseModel):
    clip_ids: list[str] | None = None
    preset: str | None = None
    fit_mode: Literal["crop", "blur"] | None = None


# ── Usage / plans ───────────────────────────────────────────
class PlanInfo(BaseModel):
    name: str
    label: str
    minutes_per_month: int
    max_clips_per_video: int
    max_projects: int
    max_upload_mb: int
    max_video_minutes: int
    features: list[str]


class UsageOut(BaseModel):
    plan: PlanInfo
    minutes_used: float
    minutes_remaining: float
    projects: int
    clips: int
    clips_rendered: int
    ai_cost_usd: float
    ai_calls: int


class ProviderStatus(BaseModel):
    llm_provider: str
    llm_configured: bool
    llm_model_fast: str
    llm_model_deep: str
    asr_provider: str
    asr_configured: bool
    asr_model: str
    storage_backend: str
    queue_backend: str
    vision_enabled: bool
    ffmpeg_version: str
    ffmpeg_path: str
    youtube_ingest: bool
    supabase_auth: bool
    warnings: list[str] = []


class HealthOut(BaseModel):
    status: str
    version: str
    env: str
    database: str
    ffmpeg: bool
