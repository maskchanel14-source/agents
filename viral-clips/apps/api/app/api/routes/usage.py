from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.db import get_db
from app.models import AiUsage, User
from app.schemas import UsageOut
from app.services.metering import usage_summary

router = APIRouter(prefix="/usage", tags=["usage"])


@router.get("", response_model=UsageOut)
async def usage(
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    summary = await usage_summary(session, user)
    cost = await session.scalar(
        select(func.coalesce(func.sum(AiUsage.cost_usd), 0.0)).where(AiUsage.user_id == user.id)
    )
    calls = await session.scalar(
        select(func.count(AiUsage.id)).where(AiUsage.user_id == user.id)
    )
    return UsageOut(
        **summary,
        ai_cost_usd=round(float(cost or 0.0), 4),
        ai_calls=int(calls or 0),
    )


@router.get("/ai-breakdown")
async def ai_breakdown(
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    rows = (
        await session.execute(
            select(
                AiUsage.provider,
                AiUsage.model,
                AiUsage.task,
                func.count(AiUsage.id),
                func.coalesce(func.sum(AiUsage.cost_usd), 0.0),
                func.coalesce(func.sum(AiUsage.prompt_tokens + AiUsage.completion_tokens), 0),
            )
            .where(AiUsage.user_id == user.id)
            .group_by(AiUsage.provider, AiUsage.model, AiUsage.task)
        )
    ).all()
    return [
        {
            "provider": r[0],
            "model": r[1],
            "task": r[2],
            "calls": int(r[3]),
            "cost_usd": round(float(r[4]), 6),
            "tokens": int(r[5]),
        }
        for r in rows
    ]
