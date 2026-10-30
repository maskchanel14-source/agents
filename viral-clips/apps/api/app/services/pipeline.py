"""Analysis + rendering pipelines.

`analyze_project` walks the whole video: probe → audio → ASR → acoustics →
scene cuts → visual subject tracking → candidate windows → scoring → clips.
`render_project_clips` turns clips into 1080x1920 MP4s with burned-in captions.

Both are provider-agnostic: missing LLM/ASR credentials degrade gracefully to
deterministic local analysis instead of failing the job.
"""
from __future__ import annotations

import json
import logging
import shutil
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models import AiUsage, Clip, Project, Transcript, User
from app.services.ai.cost import estimate_asr_cost_usd
from app.services.asr import get_asr
from app.services.media import audio as audio_mod
from app.services.media.ass import (
    Cue,
    build_ass,
    extract_keywords,
    group_cues,
    sentences_to_words,
    words_in_range,
)
from app.services.media.crop import plan_clip_crop
from app.services.media.faces import analyze_visuals
from app.services.media.ffmpeg import MediaError
from app.services.media.presets import DEFAULT_PRESET, get_preset
from app.services.media.probe import probe
from app.services.media.render import make_thumb, render_clip
from app.services.media.scenes import detect_scenes
from app.services.metering import clamp_target_clips
from app.services.moments import build_candidates, candidate_features, score_candidates
from app.services.storage import get_storage

log = logging.getLogger(__name__)

ProgressFn = Callable[[int, str], Awaitable[None]]


async def _noop(progress: int, stage: str) -> None:  # pragma: no cover - default
    return None


async def _record_usage(
    session: AsyncSession,
    *,
    user_id: str | None,
    project_id: str | None,
    payload: dict[str, Any],
) -> None:
    session.add(
        AiUsage(
            user_id=user_id,
            project_id=project_id,
            provider=payload.get("provider", "unknown"),
            model=payload.get("model") or "unknown",
            task=payload.get("task", "unknown"),
            prompt_tokens=int(payload.get("prompt_tokens", 0)),
            completion_tokens=int(payload.get("completion_tokens", 0)),
            audio_seconds=float(payload.get("audio_seconds", 0.0)),
            cost_usd=float(payload.get("cost_usd", 0.0)),
            latency_ms=int(payload.get("latency_ms", 0)),
            ok=bool(payload.get("ok", True)),
            error=payload.get("error"),
        )
    )
    await session.commit()


def _workdir(project_id: str) -> Path:
    d = settings.work_root / project_id
    d.mkdir(parents=True, exist_ok=True)
    return d


def _materialize(project: Project) -> Path:
    """Return a local path to the source video (downloading from R2 if needed)."""
    if not project.source_key:
        raise MediaError("This project has no source video attached.")
    storage = get_storage()
    work = _workdir(project.id)
    dest = work / f"source{Path(project.source_key).suffix or '.mp4'}"
    if dest.exists() and dest.stat().st_size > 0:
        return dest
    local = storage.local_path(project.source_key)
    if local is not None:
        return local
    return storage.download_to(project.source_key, dest)


async def analyze_project(
    session: AsyncSession,
    project: Project,
    user: User,
    *,
    options: dict,
    progress: ProgressFn = _noop,
) -> dict:
    plan = settings.plan(user.plan)
    target_clips = clamp_target_clips(int(options.get("target_clips", 5)), plan)
    min_s = float(options.get("min_seconds", 15))
    max_s = float(options.get("max_seconds", 60))
    language = options.get("language") or settings.asr_language
    use_deep = bool(options.get("use_deep_model", True))
    allow_overlap = bool(options.get("allow_overlap", False))

    warnings: list[str] = []
    work = _workdir(project.id)

    await progress(3, "probing_media")
    src = _materialize(project)
    info = probe(str(src))
    if info.duration_s <= 0:
        raise MediaError("Could not read the duration of this video.")
    if info.duration_s / 60 > plan["max_video_minutes"]:
        raise MediaError(
            f"Video is {info.duration_s/60:.1f} min; the {user.plan} plan allows "
            f"{plan['max_video_minutes']} min per video."
        )
    if not info.has_audio:
        warnings.append("No audio track found — analysis used visuals only.")

    project.duration_s = info.duration_s
    project.width, project.height, project.fps = info.width, info.height, info.fps
    project.status = "analyzing"
    project.stage = "extracting_audio"
    project.progress = 8
    await session.commit()

    # ── 1. Audio ────────────────────────────────────────────
    wav = audio_mod.extract_wav(str(src), work / "audio.wav")
    pcm = audio_mod.load_pcm(wav)
    profile = audio_mod.energy_profile(pcm)
    regions = audio_mod.speech_regions(profile)
    await progress(14, "transcribing")

    # ── 2. Transcription ────────────────────────────────────
    asr = get_asr()
    asr_result = None
    asr_error = None
    try:
        asr_result = asr.transcribe(wav, duration_s=info.duration_s, language=language)
    except Exception as exc:  # provider down / no credentials / bad fixture
        asr_error = str(exc)[:400]
        warnings.append(f"Transcription unavailable ({asr.name}): {asr_error}")
        log.warning("ASR failed for project %s: %s", project.id, exc)

    transcript_row = await session.scalar(
        select(Transcript).where(Transcript.project_id == project.id)
    )
    if asr_result and asr_result.segments:
        if transcript_row is None:
            transcript_row = Transcript(project_id=project.id)
            session.add(transcript_row)
        transcript_row.language = asr_result.language
        transcript_row.provider = asr_result.provider
        transcript_row.model = asr_result.model
        transcript_row.full_text = asr_result.text
        transcript_row.segments = asr_result.segments
        transcript_row.words = asr_result.words
    project.language = (asr_result.language if asr_result else None) or language
    await session.commit()
    await progress(45, "analyzing_visuals")

    if asr_result and asr_result.provider not in {"none", "fixture"}:
        await _record_usage(
            session,
            user_id=user.id,
            project_id=project.id,
            payload={
                "provider": asr_result.provider,
                "model": asr_result.model or "whisper",
                "task": "transcribe",
                "audio_seconds": info.duration_s,
                "cost_usd": estimate_asr_cost_usd(asr_result.model or "whisper-1", info.duration_s),
            },
        )

    # ── 3. Scene cuts ───────────────────────────────────────
    scenes: list[dict] = []
    try:
        scenes = detect_scenes(str(src))
    except Exception as exc:
        warnings.append(f"Scene detection skipped: {str(exc)[:120]}")
    await progress(58, "tracking_subjects")

    # ── 4. Visual intelligence ──────────────────────────────
    visuals = {"available": False, "samples": []}
    try:
        visuals = analyze_visuals(str(src))
        if not visuals.get("available"):
            warnings.append(f"Visual analysis unavailable: {visuals.get('reason', 'unknown')}")
    except Exception as exc:
        warnings.append(f"Visual analysis failed: {str(exc)[:120]}")
    await progress(72, "generating_candidates")

    # ── 5. Candidates ───────────────────────────────────────
    segments = (transcript_row.segments if transcript_row else []) or []
    words = (transcript_row.words if transcript_row else []) or []
    candidates = build_candidates(
        duration_s=info.duration_s,
        segments=segments,
        words=words,
        speech_regions=regions,
        min_s=min_s,
        max_s=max_s,
        target_windows=max(12, target_clips * 4),
    )
    if not candidates:
        raise MediaError("No usable moments were detected in this video.")

    features = [
        candidate_features(c, energy=profile.to_dict(), visuals=visuals, scenes=scenes,
                           language_hint=project.language)
        for c in candidates
    ]
    await progress(80, "scoring_moments")

    # score_candidates is synchronous (blocking provider calls). Run it in a
    # worker thread and collect usage rows there, then persist them on the
    # event loop — AsyncSession must never cross threads.
    usage_queue: list[dict] = []
    import asyncio

    selected, scoring_meta = await asyncio.to_thread(
        score_candidates,
        features,
        language=project.language,
        target_clips=target_clips,
        use_deep_model=use_deep,
        allow_overlap=allow_overlap,
        usage_sink=usage_queue.append,
    )
    for payload in usage_queue:
        await _record_usage(session, user_id=user.id, project_id=project.id, payload=payload)
    if scoring_meta.get("llm_error"):
        warnings.append(f"LLM scoring fell back to heuristics: {scoring_meta['llm_error']}")
    await progress(90, "building_clips")

    # ── 6. Persist clips ────────────────────────────────────
    existing = (
        await session.scalars(select(Clip).where(Clip.project_id == project.id))
    ).all()
    rendered = [c for c in existing if c.status == "ready"]
    for c in existing:
        if c.status != "ready":
            await session.delete(c)
    await session.flush()

    created: list[Clip] = []
    for scored in selected:
        crop = plan_clip_crop(visuals, scored.start, scored.end)
        clip_words = words_in_range(words, scored.start, scored.end)
        cues = _build_cues(scored, clip_words, transcript_row)
        clip = Clip(
            project_id=project.id,
            user_id=user.id,
            start_s=round(scored.start, 2),
            end_s=round(scored.end, 2),
            duration_s=round(scored.end - scored.start, 2),
            title=scored.title[:200],
            hook=(scored.hook or "")[:300],
            text=scored.text,
            score=scored.score,
            score_breakdown=scored.breakdown,
            explanation=scored.explanation[:1200],
            tags=scored.tags,
            status="suggested",
            preset=DEFAULT_PRESET,
            crop_x=crop["crop_x"],
            fit_mode="crop",
            subtitle_json={
                "cues": [{"start": c.start, "end": c.end, "text": _cue_text(c)} for c in cues],
                "words": clip_words,
                "keywords": sorted(extract_keywords(clip_words)) if clip_words else [],
                "edited": False,
                "strategy": crop["strategy"],
                "crop_confidence": crop["confidence"],
            },
        )
        session.add(clip)
        created.append(clip)
    await session.commit()
    await progress(94, "generating_thumbnails")

    # ── 7. Thumbnails ───────────────────────────────────────
    storage = get_storage()
    for clip in created:
        try:
            tpath = work / f"thumb_{clip.id}.jpg"
            make_thumb(
                str(src), tpath,
                at_s=clip.start_s + min(1.2, max(0.2, clip.duration_s / 3)),
                src_w=info.width, src_h=info.height, crop_x=clip.crop_x or 0.5,
            )
            key = f"{user.id}/{project.id}/thumbs/{clip.id}.jpg"
            storage.save_file(key, tpath)
            clip.thumb_key = key
        except Exception as exc:
            log.warning("thumbnail failed for %s: %s", clip.id, exc)

    analysis = {
        "media": info.to_dict(),
        "audio": {
            "speech_regions": len(regions),
            "speech_seconds": round(sum(b - a for a, b in regions), 1),
            "dynamic_range_db": round(audio_mod.dynamic_range_db(profile), 2),
            "hop_s": profile.hop_s,
            "energy_preview": profile.to_dict()["db"][:: max(1, len(profile.db) // 240)],
        },
        "transcript": {
            "provider": asr_result.provider if asr_result else "none",
            "language": project.language,
            "segments": len(segments),
            "words": len(words),
            "error": asr_error,
        },
        "visuals": {
            "available": visuals.get("available", False),
            "face_coverage": visuals.get("face_coverage", 0.0),
            "mean_motion": visuals.get("mean_motion", 0.0),
            "sampled_fps": visuals.get("sampled_fps"),
        },
        "scenes": {"count": len(scenes), "cuts": scenes[:60]},
        "candidates": scoring_meta,
        "warnings": warnings,
    }
    project.analysis = analysis
    project.status = "analyzed"
    project.stage = "completed"
    project.progress = 100
    project.error = None
    await session.commit()
    await progress(100, "completed")

    user.minutes_used = round((user.minutes_used or 0.0) + info.duration_s / 60, 3)
    await session.commit()
    return {"clips": len(created), "analysis": analysis}


def _cue_text(cue: Cue) -> str:
    return " ".join(str(w.get("w", "")) for w in cue.words).strip()


def _build_cues(scored, clip_words: list[dict], transcript_row: Transcript | None) -> list[Cue]:
    preset = get_preset(DEFAULT_PRESET)
    if clip_words:
        return group_cues(clip_words, max_words=int(preset["max_words"]))
    # No word timings: fall back to segment text with proportional alignment.
    if transcript_row and transcript_row.segments:
        rel = []
        for seg in transcript_row.segments:
            s, e = float(seg["start"]), float(seg["end"])
            if e <= scored.start or s >= scored.end:
                continue
            rel.extend(
                sentences_to_words(
                    (seg.get("text") or "").strip(),
                    max(0.0, s - scored.start),
                    min(scored.end, e) - scored.start,
                )
            )
        if rel:
            return group_cues(rel, max_words=int(preset["max_words"]))
    return []


async def render_project_clips(
    session: AsyncSession,
    project: Project,
    user: User,
    *,
    clip_ids: list[str] | None = None,
    preset_override: str | None = None,
    fit_override: str | None = None,
    progress: ProgressFn = _noop,
) -> dict:
    stmt = select(Clip).where(Clip.project_id == project.id)
    if clip_ids:
        stmt = stmt.where(Clip.id.in_(clip_ids))
    clips = list((await session.scalars(stmt.order_by(Clip.score.desc()))).all())
    if not clips:
        raise ValueError("No clips selected for rendering")

    src = _materialize(project)
    info = probe(str(src))
    work = _workdir(project.id)
    storage = get_storage()
    transcript_row = await session.scalar(
        select(Transcript).where(Transcript.project_id == project.id)
    )
    all_words = (transcript_row.words if transcript_row else []) or []

    project.status = "rendering"
    project.stage = "rendering_clips"
    await session.commit()

    rendered: list[str] = []
    failures: list[dict] = []
    total = len(clips)
    for idx, clip in enumerate(clips):
        clip.status = "rendering"
        await session.commit()
        base_pct = int(idx / total * 95)
        stage = f"rendering_clip_{idx + 1}_of_{total}"
        await progress(base_pct, stage)
        try:
            preset_name = preset_override or clip.preset or DEFAULT_PRESET
            fit = fit_override or clip.fit_mode or "crop"
            ass_text, used_captions = _ass_for_clip(clip, all_words, preset_name)
            ass_path = work / f"clip_{clip.id}.ass"
            ass_path.write_text(ass_text, encoding="utf-8")

            out = work / f"clip_{clip.id}.mp4"

            render_clip(
                str(src),
                out,
                start_s=clip.start_s,
                end_s=clip.end_s,
                src_w=info.width,
                src_h=info.height,
                crop_x=clip.crop_x if clip.crop_x is not None else 0.5,
                fit_mode=fit,
                ass_path=ass_path if used_captions else None,
                width=1080,
                height=1920,
                threads=settings.ffmpeg_threads,
                has_audio=info.has_audio,
                on_progress=None,
            )
            key = f"{user.id}/{project.id}/clips/{clip.id}.mp4"
            storage.save_file(key, out)
            clip.render_key = key
            clip.render_error = None
            clip.status = "ready"
            clip.preset = preset_name
            clip.fit_mode = fit

            thumb_key = f"{user.id}/{project.id}/thumbs/{clip.id}.jpg"
            if not clip.thumb_key or not storage.exists(thumb_key):
                tpath = work / f"thumb_{clip.id}.jpg"
                make_thumb(
                    str(src), tpath, at_s=clip.start_s + 1.0,
                    src_w=info.width, src_h=info.height, crop_x=clip.crop_x or 0.5,
                )
                storage.save_file(thumb_key, tpath)
                clip.thumb_key = thumb_key
            rendered.append(clip.id)
            out.unlink(missing_ok=True)
        except Exception as exc:  # keep going: one bad clip must not kill the batch
            log.warning("render failed for clip %s: %s", clip.id, exc)
            clip.status = "failed"
            clip.render_error = str(exc)[:500]
            failures.append({"clip_id": clip.id, "error": str(exc)[:300]})
        await session.commit()

    user.clips_rendered = (user.clips_rendered or 0) + len(rendered)
    project.status = "ready" if rendered else "failed"
    project.stage = "completed" if rendered else "render_failed"
    project.progress = 100 if rendered else 0
    if not rendered and failures:
        project.error = failures[0]["error"]
    await session.commit()
    await progress(100, "completed")

    try:
        shutil.rmtree(work, ignore_errors=True)
    except OSError:
        pass
    return {"rendered": rendered, "failures": failures, "count": len(rendered)}


def _ass_for_clip(clip: Clip, all_words: list[dict], preset_name: str) -> tuple[str, bool]:
    """Build ASS text from edited cues, auto cues, or transcript words."""
    data = clip.subtitle_json or {}
    preset = get_preset(preset_name)
    cues_payload = data.get("cues") or []
    edited = bool(data.get("edited"))

    if edited and cues_payload:
        cues = []
        for c in cues_payload:
            start = float(c.get("start", 0))
            end = float(c.get("end", 0))
            text = str(c.get("text", "")).strip()
            if not text or end <= start:
                continue
            cues.append(Cue(start, end, sentences_to_words(text, start, end)))
        if cues:
            keywords = extract_keywords([w for c in cues for w in c.words])
            return (
                build_ass(cues, preset=preset_name, keywords=keywords, title=None),
                True,
            )

    words = all_words
    if not words and data.get("words"):
        words = data["words"]
    clip_words = words_in_range(words, clip.start_s, clip.end_s) if words else []
    if clip_words:
        cues = group_cues(clip_words, max_words=int(preset["max_words"]))
        keywords = extract_keywords(clip_words)
        return build_ass(cues, preset=preset_name, keywords=keywords), True

    if cues_payload:
        cues = [
            Cue(float(c["start"]), float(c["end"]), sentences_to_words(
                str(c["text"]), float(c["start"]), float(c["end"])))
            for c in cues_payload
            if str(c.get("text", "")).strip()
        ]
        if cues:
            keywords = extract_keywords([w for c in cues for w in c.words])
            return build_ass(cues, preset=preset_name, keywords=keywords), True

    return build_ass([], preset=preset_name), False


async def delete_project_assets(project: Project) -> int:
    """Remove every stored asset belonging to a project (user-isolated prefix)."""
    storage = get_storage()
    prefixes = set()
    if project.source_key and "/" in project.source_key:
        prefixes.add(f"{project.source_key.split('/')[0]}/{project.id}")
    prefixes.add(project.id)
    removed = sum(storage.delete_prefix(p + "/") for p in prefixes)
    work = settings.work_root / project.id
    if work.exists():
        shutil.rmtree(work, ignore_errors=True)
    return removed


def dumps(obj: Any) -> str:  # small helper used by worker logging
    return json.dumps(obj, default=str)
