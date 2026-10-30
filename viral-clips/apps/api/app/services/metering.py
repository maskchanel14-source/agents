"""Usage metering and plan enforcement (credits = processing minutes)."""
from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models import Clip, Project, User


class QuotaError(RuntimeError):
    pass


async def plan_for(user: User) -> dict:
    return settings.plan(user.plan)


async def usage_summary(session: AsyncSession, user: User) -> dict:
    plan = settings.plan(user.plan)
    projects = await session.scalar(
        select(func.count(Project.id)).where(Project.user_id == user.id)
    )
    clips = await session.scalar(
        select(func.count(Clip.id)).where(Clip.user_id == user.id)
    )
    return {
        "plan": {
            "name": user.plan,
            "label": plan["label"] if "label" in plan else user.plan.title(),
            **{k: plan[k] for k in (
                "minutes_per_month",
                "max_clips_per_video",
                "max_projects",
                "max_upload_mb",
                "max_video_minutes",
                "features",
            ) if k in plan},
        },
        "minutes_used": round(user.minutes_used, 2),
        "minutes_remaining": round(max(0.0, plan["minutes_per_month"] - user.minutes_used), 2),
        "projects": int(projects or 0),
        "clips": int(clips or 0),
        "clips_rendered": int(user.clips_rendered or 0),
    }


async def check_can_create_project(session: AsyncSession, user: User) -> None:
    plan = settings.plan(user.plan)
    count = await session.scalar(
        select(func.count(Project.id)).where(Project.user_id == user.id)
    ) or 0
    if count >= plan["max_projects"]:
        raise QuotaError(
            f"Plan limit reached: {plan['max_projects']} projects on the "
            f"{user.plan} plan. Delete a project or upgrade."
        )


async def check_minutes(session: AsyncSession, user: User, minutes: float) -> None:
    plan = settings.plan(user.plan)
    if user.minutes_used + minutes > plan["minutes_per_month"]:
        remaining = max(0.0, plan["minutes_per_month"] - user.minutes_used)
        raise QuotaError(
            f"Not enough processing minutes: {minutes:.1f} min needed, "
            f"{remaining:.1f} min remaining on the {user.plan} plan."
        )


async def record_minutes(session: AsyncSession, user: User, minutes: float) -> None:
    user.minutes_used = round((user.minutes_used or 0.0) + minutes, 3)
    await session.commit()


def clamp_target_clips(target: int, plan: dict) -> int:
    return max(1, min(int(target), int(plan["max_clips_per_video"])))
