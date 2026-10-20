"""Notifikasi opsional Telegram/Discord — DEFAULT OFF.

Hanya terkirim jika `notifications.enabled: true` DAN URL webhook diisi lewat
env (`TELEGRAM_BOT_TOKEN`/`TELEGRAM_CHAT_ID` atau `DISCORD_WEBHOOK_URL`).
Tidak pernah mengandung secret; pesan hanya teks status bot.
"""

from __future__ import annotations

import logging
from typing import Optional

log = logging.getLogger("bot.notify")

try:
    import aiohttp
except ImportError:  # pragma: no cover
    aiohttp = None


class Notifier:
    def __init__(self, enabled: bool = False, telegram_token: str = "", telegram_chat_id: str = "",
                 discord_webhook: str = "", session: Optional["aiohttp.ClientSession"] = None) -> None:
        self.enabled = enabled and bool(telegram_token or discord_webhook)
        self.telegram_token = telegram_token
        self.telegram_chat_id = telegram_chat_id
        self.discord_webhook = discord_webhook
        self._session = session

    async def send(self, message: str) -> bool:
        """Kirim pesan singkat; gagal senyap (log warning) tanpa mengganggu bot."""
        if not self.enabled:
            return False
        if aiohttp is None:
            return False
        ok = False
        session = self._session or aiohttp.ClientSession()
        try:
            if self.telegram_token and self.telegram_chat_id:
                url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
                async with session.post(url, json={"chat_id": self.telegram_chat_id, "text": message[:4000]}) as r:
                    ok = r.status == 200
            if self.discord_webhook:
                async with session.post(self.discord_webhook, json={"content": message[:1900]}) as r:
                    ok = ok or r.status in (200, 204)
        except Exception as exc:  # noqa: BLE001 - notifikasi tidak boleh menjatuhkan bot
            log.warning("notify gagal: %s", exc)
        finally:
            if session is not self._session and session is not None:
                await session.close()
        return ok
