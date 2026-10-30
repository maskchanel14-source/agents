"""Subtitle caption presets (6 built-in styles) + plan gating."""
from __future__ import annotations

from typing import Any

PRESETS: dict[str, dict[str, Any]] = {
    "modern_podcast": {
        "label": "Modern Podcast",
        "font": "DejaVu Sans",
        "size": 56,
        "primary": "#FFFFFF",
        "highlight": "#5EEAD4",
        "outline_color": "#000000",
        "back_color": None,
        "outline": 4,
        "shadow": 2,
        "bold": False,
        "uppercase": False,
        "max_words": 5,
        "karaoke": True,
        "alignment": 2,
        "margin_v": 260,
        "spacing": 0,
        "fade_ms": 120,
        "tier": "free",
    },
    "bold_viral": {
        "label": "Bold Viral",
        "font": "DejaVu Sans",
        "size": 82,
        "primary": "#FFFFFF",
        "highlight": "#FACC15",
        "outline_color": "#000000",
        "back_color": None,
        "outline": 7,
        "shadow": 3,
        "bold": True,
        "uppercase": True,
        "max_words": 3,
        "karaoke": True,
        "alignment": 2,
        "margin_v": 300,
        "spacing": 1,
        "fade_ms": 80,
        "tier": "free",
    },
    "minimal_clean": {
        "label": "Minimal Clean",
        "font": "DejaVu Sans",
        "size": 46,
        "primary": "#F8FAFC",
        "highlight": "#F8FAFC",
        "outline_color": "#000000",
        "back_color": None,
        "outline": 3,
        "shadow": 0,
        "bold": False,
        "uppercase": False,
        "max_words": 7,
        "karaoke": False,
        "alignment": 2,
        "margin_v": 200,
        "spacing": 0,
        "fade_ms": 150,
        "tier": "free",
    },
    "cinematic": {
        "label": "Cinematic",
        "font": "DejaVu Serif",
        "size": 50,
        "primary": "#FFF7ED",
        "highlight": "#FDBA74",
        "outline_color": "#0B0B0F",
        "back_color": None,
        "outline": 4,
        "shadow": 4,
        "bold": False,
        "uppercase": False,
        "max_words": 6,
        "karaoke": False,
        "alignment": 2,
        "margin_v": 300,
        "spacing": 2,
        "fade_ms": 220,
        "tier": "pro",
    },
    "keyword_highlight": {
        "label": "Highlighted Keywords",
        "font": "DejaVu Sans",
        "size": 62,
        "primary": "#FFFFFF",
        "highlight": "#38BDF8",
        "outline_color": "#020617",
        "back_color": "#020617",
        "outline": 5,
        "shadow": 0,
        "bold": True,
        "uppercase": False,
        "max_words": 4,
        "karaoke": True,
        "alignment": 2,
        "margin_v": 280,
        "spacing": 0,
        "fade_ms": 100,
        "boxed": False,
        "tier": "pro",
    },
    "professional_edu": {
        "label": "Professional Educational",
        "font": "DejaVu Sans",
        "size": 50,
        "primary": "#FFFFFF",
        "highlight": "#7DD3FC",
        "outline_color": "#000000",
        "back_color": None,
        "outline": 4,
        "shadow": 1,
        "bold": False,
        "uppercase": False,
        "max_words": 6,
        "karaoke": False,
        "alignment": 2,
        "margin_v": 240,
        "spacing": 0,
        "fade_ms": 140,
        "tier": "business",
    },
}

DEFAULT_PRESET = "bold_viral"


def preset_names() -> list[str]:
    return list(PRESETS)


def get_preset(name: str | None) -> dict[str, Any]:
    return PRESETS.get(name or DEFAULT_PRESET, PRESETS[DEFAULT_PRESET])


def preset_allowed_for_plan(name: str | None, plan: str) -> bool:
    order = {"free": 0, "pro": 1, "business": 2}
    tier = get_preset(name).get("tier", "free")
    return order.get(plan, 0) >= order.get(tier, 0)
