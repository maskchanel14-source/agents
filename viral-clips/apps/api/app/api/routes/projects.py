from __future__ import annotations

import io
import logging
import shutil
import tempfile
import zipfile
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Query, Request, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, owned
from app.core.config import settings
from app.core.db import get_db
from app.models import Clip, Job, Project, Transcript, User
from app.schemas import (
    AnalyzeRequest,
    ClipOut,
    JobOut,
    ProjectOut,
    RenderRequest,
    TranscriptOut,
    UrlIngestRequest,
)
from app.services import ingest
from app.services.metering import (
    QuotaError,
    check_can_create_project,
    check_minutes,
    clamp_target_clips,
)
from app.services.queue import get_queue
from app.services.ratelimit import limit
from app.services.storage import get_storage

router = APIRouter(prefix="/projects", tags=["projects"])
log = logging.getLogger(__name__)


def _source_url(project: Project) -> str | None:
    if not project.source_key:
        return None
    return get_storage().url_for(project.source_key)


def _poster_url(project: Project) -> str | None:
    return get_storage().url_for(project.poster_key) if project.poster_key else None


async def _to_out(session: AsyncSession, project: Project) -> ProjectOut:
    clip_count = await session.scalar(
        select(func.count(Clip.id)).where(Clip.project_id == project.id)
    )
    data = ProjectOut.model_validate(project)
    return data.model_copy(
        update={
            "poster_url": _poster_url(project),
            "source_url_playable": _source_url(project),
            "clip_count": int(clip_count or 0),
        }
    )


async def _get_project(session: AsyncSession, user: User, project_id: str) -> Project:
    project = await session.get(Project, project_id)
    if project is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Project not found")
    owned(user, project)
    return project


@router.post("/upload", response_model=ProjectOut, status_code=201)
async def upload_project(
    request: Request,
    file: UploadFile = File(...),
    title: str | None = Query(default=None, max_length=200),
    auto_analyze: bool = Query(default=True),
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    limit(request, key="projects:upload", max_calls=20, window_s=3600)
    plan = settings.plan(user.plan)
    try:
        await check_can_create_project(session, user)
    except QuotaError as exc:
        raise HTTPException(status.HTTP_402_PAYMENT_REQUIRED, str(exc)) from exc

    max_bytes = ingest.size_limit_for_plan(plan)
    head = await file.read(64)
    try:
        ext = ingest.validate_upload(file.filename, file.content_type, head)
    except ingest.IngestError as exc:
        raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, str(exc)) from exc

    project = Project(
        user_id=user.id,
        title=(title or Path(file.filename or "Untitled").stem)[:200],
        source_type="upload",
        status="uploading",
        stage="uploading",
        settings_snapshot={"plan": user.plan},
    )
    session.add(project)
    await session.commit()

    storage = get_storage()
    key = f"{user.id}/{project.id}/source{ext}"
    stream = ingest.PrefixedReader(head, file.file)
    try:
        written = storage.save_stream(key, stream, max_bytes=max_bytes)
    except ValueError as exc:
        await session.delete(project)
        await session.commit()
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, str(exc)) from exc
    finally:
        await file.close()

    if written <= 0:
        await session.delete(project)
        await session.commit()
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Empty upload")

    project.source_key = key
    project.status = "uploaded"
    project.stage = "uploaded"
    await session.commit()

    if auto_analyze:
        job = await _enqueue_analysis(session, project, user, AnalyzeRequest())
        project.stage = "queued"
        await session.commit()
        log.info("auto-analysis job %s queued for project %s", job.id, project.id)

    return await _to_out(session, project)


@router.post("/from-url", response_model=ProjectOut, status_code=201)
async def project_from_url(
    body: UrlIngestRequest,
    request: Request,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    limit(request, key="projects:url", max_calls=10, window_s=3600)
    plan = settings.plan(user.plan)
    try:
        await check_can_create_project(session, user)
    except QuotaError as exc:
        raise HTTPException(status.HTTP_402_PAYMENT_REQUIRED, str(exc)) from exc
    try:
        kind = ingest.check_url_policy(body.url, attests_rights=body.attests_rights)
    except ingest.IngestError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc)) from exc

    project = Project(
        user_id=user.id,
        title=(body.title or "Imported video")[:200],
        source_type="url",
        source_url=body.url,
        status="uploading",
        stage="downloading",
        settings_snapshot={"plan": user.plan, "ingest": kind},
    )
    session.add(project)
    await session.commit()

    max_bytes = ingest.size_limit_for_plan(plan)
    tmpdir = Path(tempfile.mkdtemp(prefix="vcingest-"))
    try:
        if kind == "youtube":
            src = ingest.ytdlp_download(body.url, tmpdir, max_bytes=max_bytes)
        else:
            src = await ingest.fetch_direct(body.url, tmpdir / "source.mp4", max_bytes=max_bytes)
        key = f"{user.id}/{project.id}/source{src.suffix or '.mp4'}"
        get_storage().save_file(key, src)
        project.source_key = key
        project.status = "uploaded"
        project.stage = "uploaded"
        await session.commit()
    except ingest.IngestError as exc:
        project.status, project.stage, project.error = "failed", "failed", str(exc)
        await session.commit()
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc)) from exc
    except Exception as exc:
        project.status, project.stage, project.error = "failed", "failed", str(exc)[:500]
        await session.commit()
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, f"Could not fetch the video: {exc}") from exc
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

    job = await _enqueue_analysis(session, project, user, AnalyzeRequest())
    project.stage = "queued"
    await session.commit()
    return await _to_out(session, project)


async def _enqueue_analysis(
    session: AsyncSession, project: Project, user: User, body: AnalyzeRequest
) -> Job:
    plan = settings.plan(user.plan)
    minutes = (project.duration_s or 0) / 60 if project.duration_s else 0.0
    if minutes:
        try:
            await check_minutes(session, user, minutes)
        except QuotaError as exc:
            raise HTTPException(status.HTTP_402_PAYMENT_REQUIRED, str(exc)) from exc

    payload = {
        "target_clips": clamp_target_clips(body.target_clips, plan),
        "min_seconds": body.min_seconds,
        "max_seconds": body.max_seconds,
        "language": body.language,
        "use_deep_model": body.use_deep_model,
        "allow_overlap": body.allow_overlap,
    }
    job = Job(project_id=project.id, user_id=user.id, type="analyze", payload=payload)
    session.add(job)
    await session.commit()
    await session.refresh(job)
    get_queue().enqueue(job.id)
    return job


@router.get("", response_model=list[ProjectOut])
async def list_projects(
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    limit_: int = Query(default=50, alias="limit", ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    status_filter: str | None = Query(default=None, alias="status"),
):
    stmt = select(Project).where(Project.user_id == user.id)
    if status_filter:
        stmt = stmt.where(Project.status == status_filter)
    stmt = stmt.order_by(Project.created_at.desc()).limit(limit_).offset(offset)
    projects = (await session.scalars(stmt)).all()
    return [await _to_out(session, p) for p in projects]


@router.get("/{project_id}", response_model=ProjectOut)
async def get_project(
    project_id: str,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await _to_out(session, await _get_project(session, user, project_id))


@router.delete("/{project_id}", status_code=204)
async def delete_project(
    project_id: str,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    project = await _get_project(session, user, project_id)
    from app.services.pipeline import delete_project_assets

    await delete_project_assets(project)
    await session.delete(project)
    await session.commit()
    return None


@router.post("/{project_id}/analyze", response_model=JobOut, status_code=202)
async def analyze(
    project_id: str,
    body: AnalyzeRequest,
    request: Request,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    limit(request, key="projects:analyze", max_calls=30, window_s=3600)
    project = await _get_project(session, user, project_id)
    if project.status in {"analyzing", "uploading"}:
        raise HTTPException(status.HTTP_409_CONFLICT, "This project is already being processed")
    job = await _enqueue_analysis(session, project, user, body)
    project.status = "queued"
    project.stage = "queued"
    project.progress = 0
    project.error = None
    await session.commit()
    return JobOut.model_validate(job)


@router.get("/{project_id}/analysis")
async def get_analysis(
    project_id: str,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Full analysis report: media, audio, transcript, visuals, scoring metadata."""
    project = await _get_project(session, user, project_id)
    return {
        "project_id": project.id,
        "status": project.status,
        "analysis": project.analysis or {},
        "warnings": (project.analysis or {}).get("warnings", []),
    }


@router.get("/{project_id}/clips", response_model=list[ClipOut])
async def list_clips(
    project_id: str,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    project = await _get_project(session, user, project_id)
    clips = (
        await session.scalars(
            select(Clip).where(Clip.project_id == project.id).order_by(Clip.score.desc())
        )
    ).all()
    storage = get_storage()
    out = []
    for c in clips:
        data = ClipOut.model_validate(c)
        out.append(
            data.model_copy(
                update={
                    "video_url": storage.url_for(c.render_key) if c.render_key else None,
                    "thumb_url": storage.url_for(c.thumb_key) if c.thumb_key else None,
                }
            )
        )
    return out


@router.get("/{project_id}/transcript", response_model=TranscriptOut)
async def get_transcript(
    project_id: str,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    project = await _get_project(session, user, project_id)
    row = await session.scalar(select(Transcript).where(Transcript.project_id == project.id))
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Transcript not available for this project")
    return TranscriptOut(
        project_id=project.id,
        language=row.language,
        provider=row.provider,
        model=row.model,
        full_text=row.full_text,
        segments=row.segments or [],
        words=row.words or [],
        speakers=row.speakers,
    )


@router.post("/{project_id}/render", response_model=JobOut, status_code=202)
async def render(
    project_id: str,
    body: RenderRequest,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    project = await _get_project(session, user, project_id)
    if project.status in {"rendering", "analyzing"}:
        raise HTTPException(status.HTTP_409_CONFLICT, "Rendering is already in progress")
    if body.clip_ids:
        rows = (
            await session.scalars(
                select(Clip).where(Clip.project_id == project.id, Clip.id.in_(body.clip_ids))
            )
        ).all()
        if len(rows) != len(set(body.clip_ids)):
            raise HTTPException(status.HTTP_404_NOT_FOUND, "One or more clips were not found")
    job = Job(
        project_id=project.id,
        user_id=user.id,
        type="render",
        payload={"clip_ids": body.clip_ids, "preset": body.preset, "fit_mode": body.fit_mode},
    )
    session.add(job)
    project.status = "queued"
    project.stage = "queued_render"
    await session.commit()
    await session.refresh(job)
    get_queue().enqueue(job.id)
    return JobOut.model_validate(job)


@router.get("/{project_id}/export")
async def export_bundle(
    project_id: str,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """ZIP of every rendered clip (ready for upload to Shorts/TikTok/Reels)."""
    project = await _get_project(session, user, project_id)
    clips = [
        c
        for c in (
            await session.scalars(select(Clip).where(Clip.project_id == project.id).order_by(Clip.score.desc()))
        ).all()
        if c.status == "ready" and c.render_key
    ]
    if not clips:
        raise HTTPException(status.HTTP_409_CONFLICT, "No rendered clips yet — render first")

    storage = get_storage()
    tmpdir = Path(tempfile.mkdtemp(prefix="vcexport-"))
    zip_path = tmpdir / "clips.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_STORED, allowZip64=True) as zf:
        for idx, clip in enumerate(clips, start=1):
            local = storage.local_path(clip.render_key) if clip.render_key else None
            if local is None and clip.render_key:
                local = storage.download_to(clip.render_key, tmpdir / f"c{idx}.mp4")
            if local and local.exists():
                name = ingest.safe_filename(f"{idx:02d}-{clip.title}", "clip")
                zf.write(local, arcname=f"{name}.mp4")
        zf.writestr(
            "manifest.json",
            __import__("json").dumps(
                [
                    {
                        "id": c.id,
                        "title": c.title,
                        "start_s": c.start_s,
                        "end_s": c.end_s,
                        "duration_s": c.duration_s,
                        "score": c.score,
                        "preset": c.preset,
                    }
                    for c in clips
                ],
                indent=2,
            ),
        )
    filename = ingest.safe_filename(project.title, "clips")
    return FileResponse(
        zip_path,
        media_type="application/zip",
        filename=f"{filename}-clips.zip",
        background=None,
    )
