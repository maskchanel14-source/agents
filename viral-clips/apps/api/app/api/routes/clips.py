from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, owned
from app.core.config import settings
from app.core.db import get_db
from app.models import Clip, Job, Project, Transcript, User
from app.schemas import ClipOut, ClipPatch, JobOut
from app.services.media.ass import (
    build_ass,
    extract_keywords,
    group_cues,
    sentences_to_words,
    words_in_range,
)
from app.services.media.presets import PRESETS, preset_allowed_for_plan
from app.services.queue import get_queue
from app.services.storage import get_storage

router = APIRouter(prefix="/clips", tags=["clips"])


async def _get_clip(session: AsyncSession, user: User, clip_id: str) -> Clip:
    clip = await session.get(Clip, clip_id)
    if clip is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Clip not found")
    owned(user, clip)
    return clip


def _to_out(clip: Clip) -> ClipOut:
    storage = get_storage()
    data = ClipOut.model_validate(clip)
    return data.model_copy(
        update={
            "video_url": storage.url_for(clip.render_key) if clip.render_key else None,
            "thumb_url": storage.url_for(clip.thumb_key) if clip.thumb_key else None,
        }
    )


@router.get("/{clip_id}", response_model=ClipOut)
async def get_clip(
    clip_id: str,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return _to_out(await _get_clip(session, user, clip_id))


@router.patch("/{clip_id}", response_model=ClipOut)
async def patch_clip(
    clip_id: str,
    body: ClipPatch,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    clip = await _get_clip(session, user, clip_id)
    project = await session.get(Project, clip.project_id)
    max_duration = project.duration_s if project and project.duration_s else 3600

    if body.title is not None:
        clip.title = body.title[:200]
    if body.hook is not None:
        clip.hook = body.hook[:300]
    if body.start_s is not None:
        if body.start_s >= max_duration:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "start_s is past the video end")
        clip.start_s = round(body.start_s, 3)
    if body.end_s is not None:
        if body.end_s <= clip.start_s:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "end_s must be after start_s")
        clip.end_s = round(min(body.end_s, max_duration), 3)
    if body.start_s is not None or body.end_s is not None:
        clip.duration_s = round(clip.end_s - clip.start_s, 3)
        if clip.duration_s < 3:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Clips must be at least 3s")
    if body.crop_x is not None:
        clip.crop_x = body.crop_x
    if body.fit_mode is not None:
        clip.fit_mode = body.fit_mode
    if body.preset is not None:
        if body.preset not in PRESETS:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Unknown subtitle preset")
        if not preset_allowed_for_plan(body.preset, user.plan):
            raise HTTPException(
                status.HTTP_402_PAYMENT_REQUIRED,
                f"Preset '{body.preset}' requires a higher plan",
            )
        clip.preset = body.preset
    if body.subtitle_json is not None:
        data = dict(clip.subtitle_json or {})
        data.update(body.subtitle_json)
        data["edited"] = True
        clip.subtitle_json = data
        clip.status = "suggested"  # needs re-render
    await session.commit()
    return _to_out(clip)


@router.post("/{clip_id}/render", response_model=JobOut, status_code=202)
async def render_clip_endpoint(
    clip_id: str,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    clip = await _get_clip(session, user, clip_id)
    job = Job(
        project_id=clip.project_id,
        user_id=user.id,
        type="render",
        payload={"clip_ids": [clip.id], "preset": clip.preset, "fit_mode": clip.fit_mode},
    )
    session.add(job)
    await session.commit()
    await session.refresh(job)
    get_queue().enqueue(job.id)
    return JobOut.model_validate(job)


@router.get("/{clip_id}/subtitle-preview")
async def subtitle_preview(
    clip_id: str,
    preset: str | None = None,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Return the generated ASS (useful for debugging caption styling)."""
    clip = await _get_clip(session, user, clip_id)
    transcript = await session.scalar(
        select(Transcript).where(Transcript.project_id == clip.project_id)
    )
    words = words_in_range(
        (transcript.words if transcript else []) or [], clip.start_s, clip.end_s
    )
    if words:
        from app.services.media.presets import get_preset

        cues = group_cues(words, max_words=int(get_preset(preset or clip.preset)["max_words"]))
        ass = build_ass(cues, preset=preset or clip.preset, keywords=extract_keywords(words))
    else:
        payload = (clip.subtitle_json or {}).get("cues") or []
        cues = [
            type("C", (), {"start": float(c["start"]), "end": float(c["end"]),
                           "words": sentences_to_words(str(c["text"]), float(c["start"]), float(c["end"]))})()
            for c in payload
        ]
        ass = build_ass(cues, preset=preset or clip.preset)
    return {"ass": ass}


@router.delete("/{clip_id}", status_code=204)
async def delete_clip(
    clip_id: str,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    clip = await _get_clip(session, user, clip_id)
    storage = get_storage()
    if clip.render_key:
        storage.delete_prefix(clip.render_key)
    if clip.thumb_key:
        storage.delete_prefix(clip.thumb_key)
    await session.delete(clip)
    await session.commit()
    return None
