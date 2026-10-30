"""Provider-agnostic LLM interface + retry/telemetry helper."""
from __future__ import annotations

import logging
import random
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from app.core.config import settings

log = logging.getLogger(__name__)

Message = dict[str, Any]


class LLMError(RuntimeError):
    pass


@dataclass
class LLMResult:
    text: str
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    latency_ms: int = 0
    raw: dict = field(default_factory=dict)


class LLMProvider(ABC):
    name: str = "unknown"

    @abstractmethod
    def _call(
        self,
        messages: list[Message],
        *,
        model: str,
        max_tokens: int,
        temperature: float,
        json_mode: bool,
    ) -> LLMResult: ...

    def complete(
        self,
        messages: list[Message],
        *,
        model: str | None = None,
        max_tokens: int | None = None,
        temperature: float = 0.3,
        json_mode: bool = True,
    ) -> LLMResult:
        """Call with bounded retries, jittered backoff and latency accounting."""
        model = model or settings.llm_model_fast
        max_tokens = max_tokens or settings.llm_max_output_tokens
        last_err: Exception | None = None
        for attempt in range(1, settings.llm_max_retries + 1):
            started = time.perf_counter()
            try:
                res = self._call(
                    messages,
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    json_mode=json_mode,
                )
                res.latency_ms = int((time.perf_counter() - started) * 1000)
                return res
            except Exception as exc:  # network / rate limit / provider error
                last_err = exc
                wait = min(2**attempt * 0.4, 8) + random.uniform(0, 0.5)
                log.warning(
                    "LLM call failed (attempt %s/%s) model=%s: %s",
                    attempt,
                    settings.llm_max_retries,
                    model,
                    exc,
                )
                if attempt < settings.llm_max_retries:
                    time.sleep(wait)
        raise LLMError(f"{self.name} request failed: {last_err}") from last_err
