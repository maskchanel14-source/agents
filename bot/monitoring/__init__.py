"""Monitoring: structured logging + metrics + notifikasi opsional."""

from __future__ import annotations

import json
import logging
import logging.handlers
import os
import time
from pathlib import Path
from typing import Optional


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(record.created)) + f".{int(record.msecs):03d}Z",
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def setup_logging(log_dir: Path | str, *, level: str = "INFO", max_bytes: int = 10_485_760, backups: int = 5) -> logging.Logger:
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    root = logging.getLogger("bot")
    root.setLevel(getattr(logging, level.upper(), logging.INFO))
    root.handlers.clear()

    fh = logging.handlers.RotatingFileHandler(
        log_path / "bot.log", maxBytes=max_bytes, backupCount=backups, encoding="utf-8"
    )
    fh.setFormatter(JsonFormatter())
    root.addHandler(fh)

    sh = logging.StreamHandler()
    sh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    root.addHandler(sh)
    return root


class Metrics:
    """Metrik ringkas untuk dashboard."""

    def __init__(self) -> None:
        self.started_at = time.time()
        self.counters: dict[str, int] = {}
        self.gauges: dict[str, float] = {}
        self.events: list[dict] = []

    def inc(self, name: str, n: int = 1) -> None:
        self.counters[name] = self.counters.get(name, 0) + n

    def set_gauge(self, name: str, value: float) -> None:
        self.gauges[name] = value

    def event(self, kind: str, message: str, **extra) -> None:
        self.events.append({"ts": time.time(), "kind": kind, "message": message, **extra})
        if len(self.events) > 500:
            self.events = self.events[-500:]

    def snapshot(self) -> dict:
        return {
            "uptime_s": time.time() - self.started_at,
            "counters": dict(self.counters),
            "gauges": dict(self.gauges),
            "recent_events": self.events[-50:],
        }


def send_notification(message: str, *, enabled: Optional[bool] = None) -> bool:
    """Notifikasi opsional Telegram/Discord via env (default OFF). Tidak pernah kirim secret."""
    if enabled is False:
        return False
    tg_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    tg_chat = os.environ.get("TELEGRAM_CHAT_ID", "")
    discord = os.environ.get("DISCORD_WEBHOOK_URL", "")
    sent = False
    if tg_token and tg_chat:
        try:
            import urllib.request
            req = urllib.request.Request(
                f"https://api.telegram.org/bot{tg_token}/sendMessage",
                data=json.dumps({"chat_id": tg_chat, "text": message[:3500]}).encode(),
                headers={"Content-Type": "application/json"},
            )
            urllib.request.urlopen(req, timeout=5)
            sent = True
        except Exception:
            logging.getLogger("bot.monitoring").warning("telegram notify failed", exc_info=True)
    if discord:
        try:
            import urllib.request
            req = urllib.request.Request(
                discord,
                data=json.dumps({"content": message[:1800]}).encode(),
                headers={"Content-Type": "application/json"},
            )
            urllib.request.urlopen(req, timeout=5)
            sent = True
        except Exception:
            logging.getLogger("bot.monitoring").warning("discord notify failed", exc_info=True)
    return sent
