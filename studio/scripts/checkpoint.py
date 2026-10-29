"""Append a verified database snapshot to LOG.md; never fabricate market activity.

Usage: python3 studio/scripts/checkpoint.py snapshot.json
The GitHub workflow obtains the snapshot from the public, aggregate-only status
endpoint. This script also works with an operator-supplied connector result.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REQUIRED = {
    "product",
    "buyer",
    "channel",
    "status",
    "commitments",
    "paid_customers",
    "collected_cents",
    "outreach_started_at",
    "hard_stop_at",
    "decision",
    "skill_used",
    "snapshot_at",
}


def validate_snapshot(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict) or not REQUIRED.issubset(data):
        raise ValueError("Snapshot is missing required fields")
    for key in ("commitments", "paid_customers", "collected_cents"):
        if type(data[key]) is not int or data[key] < 0:
            raise ValueError(f"{key} must be a nonnegative integer")
    for key in ("product", "buyer", "channel", "status", "decision", "skill_used"):
        if (
            not isinstance(data[key], str)
            or not data[key].strip()
            or "|" in data[key]
            or "\n" in data[key]
        ):
            raise ValueError(f"Invalid single-line field: {key}")
    for key in ("hard_stop_at", "snapshot_at"):
        if not isinstance(data[key], str):
            raise TypeError(f"{key} must be a timestamp string")
        stamp = data[key]
        normalized = (
            (stamp[:-3] + "+00:00")
            if stamp.endswith("+00")
            else stamp.replace("Z", "+00:00")
        )
        parsed = datetime.fromisoformat(normalized)
        if parsed.tzinfo is None:
            raise ValueError(f"{key} needs a timezone")
    if data["outreach_started_at"] is not None:
        if not isinstance(data["outreach_started_at"], str):
            raise TypeError("outreach_started_at must be a timestamp string or null")
        stamp = data["outreach_started_at"]
        parsed = datetime.fromisoformat(
            (stamp[:-3] + "+00:00")
            if stamp.endswith("+00")
            else stamp.replace("Z", "+00:00")
        )
        if parsed.tzinfo is None:
            raise ValueError("outreach_started_at needs a timezone")
    return data


def render_row(data: dict[str, Any]) -> str:
    data = validate_snapshot(data)
    timestamp = data["snapshot_at"]
    normalized = (
        (timestamp[:-3] + "+00:00")
        if timestamp.endswith("+00")
        else timestamp.replace("Z", "+00:00")
    )
    stamp = (
        datetime.fromisoformat(normalized)
        .astimezone(timezone.utc)
        .strftime("%Y-%m-%d %H:%M")
    )
    channel = (
        data["channel"]
        if data["outreach_started_at"]
        else f"Not posted. Selected: {data['channel']}"
    )
    values = [
        stamp,
        f"{data['product']} ({data['status']}; {data['commitments']}/3 commitments)",
        data["buyer"],
        channel,
        f"{data['collected_cents'] / 100:.2f}",
        data["skill_used"],
        data["decision"],
    ]
    return "| " + " | ".join(values) + " |"


def append_once(text: str, row: str) -> str:
    if row in text.splitlines():
        return text
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.startswith("|---"):
            end = index + 1
            while end < len(lines) and lines[end].startswith("|"):
                end += 1
            lines.insert(end, row)
            return "\n".join(lines) + "\n"
    raise ValueError("LOG.md checkpoint table not found")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    data = json.loads(Path(sys.argv[1]).read_text())
    path = ROOT / "LOG.md"
    updated = append_once(path.read_text(), render_row(data))
    path.write_text(updated)
    print("Checkpoint appended (database-verified snapshot).")


if __name__ == "__main__":
    main()
