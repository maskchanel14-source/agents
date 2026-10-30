"""In-process sliding-window rate limiter (single node).

For multi-node deployments swap the store for Redis (`INCR` + `EXPIRE`); the
interface stays identical.
"""
from __future__ import annotations

import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request, status

_buckets: dict[str, deque[float]] = defaultdict(deque)


def limit(request: Request, *, key: str, max_calls: int, window_s: int) -> None:
    identity = key
    ip = request.client.host if request.client else "unknown"
    bucket_key = f"{key}:{ip}"
    now = time.monotonic()
    q = _buckets[bucket_key]
    while q and now - q[0] > window_s:
        q.popleft()
    if len(q) >= max_calls:
        retry = int(window_s - (now - q[0])) + 1
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded for {identity}. Retry in {retry}s.",
            headers={"Retry-After": str(retry)},
        )
    q.append(now)


def reset() -> None:
    _buckets.clear()
