"""Shared FastAPI dependencies: authentication, authorization, DB session."""
from __future__ import annotations

import logging

import jwt
from fastapi import Cookie, Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import get_db
from app.core.security import decode_local_token, decode_supabase_token
from app.models import User

log = logging.getLogger(__name__)


async def _user_from_token(session: AsyncSession, token: str) -> User:
    # 1) local HS256 token
    try:
        payload = decode_local_token(token)
        user = await session.get(User, payload["sub"])
        if user:
            return user
    except jwt.PyJWTError:
        pass

    # 2) Supabase-issued token
    if settings.supabase_jwt_secret:
        try:
            payload = decode_supabase_token(token)
            sub = payload.get("sub")
            email = (payload.get("email") or "").lower()
            user = await session.scalar(select(User).where(User.supabase_sub == sub))
            if user is None and email:
                user = await session.scalar(select(User).where(User.email == email))
                if user is not None and not user.supabase_sub:
                    user.supabase_sub = sub
                    await session.commit()
            if user is None and email:
                user = User(email=email, display_name=payload.get("name"), supabase_sub=sub)
                session.add(user)
                await session.commit()
            if user:
                return user
        except jwt.PyJWTError as exc:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid Supabase token") from exc

    raise HTTPException(
        status.HTTP_401_UNAUTHORIZED,
        "Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_user(
    session: AsyncSession = Depends(get_db),
    authorization: str | None = Header(default=None),
    vc_token: str | None = Cookie(default=None, alias=settings.cookie_name),
) -> User:
    token = None
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1].strip()
    elif vc_token:
        token = vc_token
    if not token:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return await _user_from_token(session, token)


def owned(user: User, obj) -> None:
    """Guard every user-scoped resource access (data isolation)."""
    owner_id = getattr(obj, "user_id", None)
    if owner_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not found")
