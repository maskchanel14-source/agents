"""File-based kill switch. Presence of the file halts new orders and triggers cancel-all."""

from __future__ import annotations

from pathlib import Path


class KillSwitch:
    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self._manual: str | None = None

    def trigger_manual(self, reason: str) -> None:
        self._manual = reason

    def is_active(self) -> bool:
        return self._manual is not None or self.path.exists()

    def reason(self) -> str | None:
        if self._manual is not None:
            return f"manual:{self._manual}"
        if self.path.exists():
            return f"file:{self.path.name}"
        return None

    def activate_file(self, reason: str) -> None:
        """Create the kill-switch file (used by operators/scripts)."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(reason + "\n", encoding="utf-8")

    def clear_file(self) -> None:
        if self.path.exists():
            self.path.unlink()
