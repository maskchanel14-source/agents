from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, owned
from app.core.db import get_db
from app.models import Job, User
from app.schemas import JobOut

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/{job_id}", response_model=JobOut)
async def get_job(
    job_id: str,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    job = await session.get(Job, job_id)
    if job is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Job not found")
    owned(user, job)
    return JobOut.model_validate(job)


@router.get("", response_model=list[JobOut])
async def list_jobs(
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    limit_: int = Query(default=25, alias="limit", ge=1, le=100),
    project_id: str | None = None,
):
    stmt = select(Job).where(Job.user_id == user.id)
    if project_id:
        stmt = stmt.where(Job.project_id == project_id)
    stmt = stmt.order_by(Job.created_at.desc()).limit(limit_)
    return [JobOut.model_validate(j) for j in (await session.scalars(stmt)).all()]
