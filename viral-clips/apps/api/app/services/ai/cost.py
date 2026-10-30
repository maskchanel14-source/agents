"""USD cost estimation for LLM + ASR usage (per 1M tokens / per audio minute)."""
from __future__ import annotations

# $/1M tokens (input, output). Update as vendor pricing changes.
TOKEN_PRICES: dict[str, tuple[float, float]] = {
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-4o": (2.50, 10.00),
    "gpt-4.1-mini": (0.40, 1.60),
    "gpt-4.1": (2.00, 8.00),
    "claude-3-5-haiku-latest": (0.80, 4.00),
    "claude-sonnet-4-20250514": (3.00, 15.00),
    "llama-3.3-70b-versatile": (0.59, 0.79),
    "llama-3.1-8b-instant": (0.05, 0.08),
    "gemini-2.0-flash": (0.10, 0.40),
}
DEFAULT_PRICE = (1.0, 3.0)

# Whisper-style pricing, USD per minute of audio
ASR_MINUTE_PRICES = {
    "whisper-1": 0.006,
    "whisper-large-v3": 0.00185,  # Groq
    "whisper-large-v3-turbo": 0.00067,
    "faster_whisper": 0.0,  # self-hosted
    "fixture": 0.0,
    "none": 0.0,
}


def estimate_cost_usd(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    pin, pout = TOKEN_PRICES.get(model, DEFAULT_PRICE)
    return round(prompt_tokens / 1e6 * pin + completion_tokens / 1e6 * pout, 6)


def estimate_asr_cost_usd(model: str, audio_seconds: float) -> float:
    per_min = ASR_MINUTE_PRICES.get(model, 0.006)
    return round(audio_seconds / 60 * per_min, 6)
