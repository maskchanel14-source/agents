"""Circuit breaker: open after N consecutive failures, cool down, then retry."""

from __future__ import annotations


class CircuitBreaker:
    def __init__(self, max_consecutive_errors: int, cooldown_s: int) -> None:
        if max_consecutive_errors < 1:
            raise ValueError("max_consecutive_errors must be >= 1")
        self.max_errors = max_consecutive_errors
        self.cooldown_ms = cooldown_s * 1000
        self.consecutive_errors = 0
        self.open_until_ms: int | None = None

    def record_failure(self, now_ms: int) -> bool:
        """Return True if this failure opened the breaker."""
        self.consecutive_errors += 1
        if self.consecutive_errors >= self.max_errors and self.open_until_ms is None:
            self.open_until_ms = now_ms + self.cooldown_ms
            return True
        return False

    def record_success(self) -> None:
        self.consecutive_errors = 0
        self.open_until_ms = None

    def is_open(self, now_ms: int) -> bool:
        if self.open_until_ms is None:
            return False
        if now_ms >= self.open_until_ms:
            # half-open: allow a retry; a failure re-opens immediately
            self.open_until_ms = None
            self.consecutive_errors = self.max_errors - 1
            return False
        return True
