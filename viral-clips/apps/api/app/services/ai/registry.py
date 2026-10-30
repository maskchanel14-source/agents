"""Provider selection + fallback chain. Secrets stay server-side only."""
from __future__ import annotations

import logging

from app.core.config import settings

from .base import LLMProvider
from .openai_compat import AnthropicProvider, OpenAICompatibleProvider

log = logging.getLogger(__name__)

_PRESETS: dict[str, dict] = {
    "openai": {"base_url": "https://api.openai.com/v1", "name": "openai"},
    "groq": {"base_url": "https://api.groq.com/openai/v1", "name": "groq"},
    "ollama": {"base_url": "http://127.0.0.1:11434/v1", "name": "ollama"},
    "together": {"base_url": "https://api.together.xyz/v1", "name": "together"},
    "gemini": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai",
        "name": "gemini",
    },
}

_cached: LLMProvider | None = None
_cached_key: tuple | None = None


def get_llm() -> LLMProvider | None:
    """Return a configured provider, or None when only local heuristics run."""
    global _cached, _cached_key
    if settings.llm_provider == "heuristic":
        return None

    provider = settings.llm_provider
    if provider == "auto":
        if settings.llm_api_key:
            provider = "openai"
        elif settings.llm_base_url:
            provider = "ollama"
        else:
            return None

    key = (provider, settings.llm_base_url, settings.llm_api_key)
    if _cached is not None and _cached_key == key:
        return _cached

    if provider == "anthropic":
        if not settings.llm_api_key:
            return None
        _cached = AnthropicProvider(settings.llm_api_key)
    elif provider in _PRESETS:
        preset = _PRESETS[provider]
        base_url = settings.llm_base_url or preset["base_url"]
        if provider != "ollama" and not settings.llm_api_key:
            return None
        _cached = OpenAICompatibleProvider(base_url, settings.llm_api_key, preset["name"])
    else:
        log.warning("unknown LLM provider %r, falling back to heuristics", provider)
        return None
    _cached_key = key
    return _cached


def reset_llm_cache() -> None:
    """Test helper."""
    global _cached, _cached_key
    _cached, _cached_key = None, None
