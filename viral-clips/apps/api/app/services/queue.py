"""Background job queue abstraction.

inline — a bounded thread pool inside the API process (single-node dev/demo).
rq     — Redis-backed RQ queue consumed by dedicated worker containers
         (production; keep long FFmpeg renders off the API box).
"""
from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Protocol

from app.core.config import settings

log = logging.getLogger(__name__)


class JobQueue(Protocol):
    def enqueue(self, job_id: str) -> None: ...


class InlineQueue:
    """Runs jobs in a daemon thread pool. Video work is CPU-bound: keep 1-2."""

    def __init__(self, max_workers: int | None = None):
        self.pool = ThreadPoolExecutor(
            max_workers=max_workers or settings.job_max_workers,
            thread_name_prefix="vc-job",
        )

    def enqueue(self, job_id: str) -> None:
        from app.worker import run_job

        log.info("enqueue inline job %s", job_id)
        self.pool.submit(run_job, job_id)


class RQQueue:
    def __init__(self) -> None:
        from redis import Redis
        from rq import Queue

        self.redis = Redis.from_url(settings.redis_url)
        self.queue = Queue("viral-clips", connection=self.redis, default_timeout=7200)

    def enqueue(self, job_id: str) -> None:
        self.queue.enqueue("app.worker.run_job", job_id, job_timeout=7200)


_queue: JobQueue | None = None


def get_queue() -> JobQueue:
    global _queue
    if _queue is None:
        if settings.queue_backend == "rq":
            _queue = RQQueue()
        else:
            _queue = InlineQueue()
    return _queue


def reset_queue() -> None:
    global _queue
    _queue = None
