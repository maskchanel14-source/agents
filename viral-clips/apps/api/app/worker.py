"""Job runner. Used by the inline thread pool (dev) and RQ workers (prod).

Entry points are synchronous so RQ can import them directly:

    rq worker -u $REDIS_URL viral-clips        # consumes app.worker.run_job
"""
from __future__ import annotations

import asyncio
import logging
import sys
import traceback
from datetime import UTC, datetime

from app.core.db import SessionLocal, init_db
from app.models import Job, Project, User
from app.services.pipeline import analyze_project, render_project_clips

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s :: %(message)s"
)
log = logging.getLogger("worker")


async def _update(session, job: Job, project: Project | None, pct: int, stage: str) -> None:
    job.progress = max(job.progress, pct)
    job.stage = stage
    if project is not None:
        project.progress = pct
        project.stage = stage
    await session.commit()


async def _run(job_id: str) -> None:
    async with SessionLocal() as session:
        job = await session.get(Job, job_id)
        if job is None:
            log.error("job %s not found", job_id)
            return
        if job.status in {"done", "failed"}:
            return
        job.status = "running"
        job.started_at = datetime.now(UTC)
        job.stage = "starting"
        await session.commit()

        project = await session.get(Project, job.project_id) if job.project_id else None
        user = await session.get(User, job.user_id)
        if user is None:
            job.status, job.error = "failed", "user missing"
            await session.commit()
            return

        async def progress(pct: int, stage: str) -> None:
            await _update(session, job, project, pct, stage)

        try:
            if job.type == "analyze" and project is not None:
                project.status = "analyzing"
                await session.commit()
                result = await analyze_project(
                    session, project, user, options=job.payload or {}, progress=progress
                )
            elif job.type == "render" and project is not None:
                payload = job.payload or {}
                result = await render_project_clips(
                    session,
                    project,
                    user,
                    clip_ids=payload.get("clip_ids"),
                    preset_override=payload.get("preset"),
                    fit_override=payload.get("fit_mode"),
                    progress=progress,
                )
            else:
                raise ValueError(f"unsupported job type: {job.type}")

            job.status = "done"
            job.result = {"summary": _summarise(result)}
            job.progress = 100
            job.stage = "completed"
            job.finished_at = datetime.now(UTC)
            await session.commit()
            log.info("job %s done: %s", job_id, job.result["summary"])
        except Exception as exc:
            log.exception("job %s failed", job_id)
            job.status = "failed"
            job.error = str(exc)[:1000]
            job.stage = "failed"
            job.finished_at = datetime.now(UTC)
            if project is not None:
                project.status = "failed"
                project.error = str(exc)[:1000]
                project.stage = "failed"
            await session.commit()
            traceback.print_exc(file=sys.stderr)


def _summarise(result: dict) -> str:
    if "clips" in result:
        return f"{result['clips']} clips generated"
    if "count" in result:
        return f"{result['count']} clips rendered"
    return "done"


def run_job(job_id: str) -> None:
    """Synchronous entry point for RQ / the inline pool."""
    asyncio.run(_run(job_id))


async def _bootstrap() -> None:
    await init_db()


if __name__ == "__main__":  # manual run: python -m app.worker <job_id>
    if len(sys.argv) > 1:
        run_job(sys.argv[1])
