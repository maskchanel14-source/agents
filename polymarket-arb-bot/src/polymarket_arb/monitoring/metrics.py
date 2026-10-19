"""Counters -> summary dict (written to reports/ and printed by the CLI)."""

from __future__ import annotations

from collections import Counter
from typing import Any


def summarize_counters(counters: Counter) -> dict[str, Any]:
    prefixes: dict[str, dict[str, int]] = {}
    for key, value in sorted(counters.items()):
        head, _, rest = key.partition(":")
        prefixes.setdefault(head, {})[rest or key] = int(value)
    return {"counters": {k: dict(v) for k, v in prefixes.items()}}
