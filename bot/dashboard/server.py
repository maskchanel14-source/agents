"""Dashboard server "ARC-TERMINAL" — HANYA 127.0.0.1 (misi §5b).

- SSE untuk push data real-time (throttled).
- Aksi kontrol (pause/resume/kill) butuh token lokal acak + konfirmasi dua langkah.
- Crash dashboard TIDAK mempengaruhi bot (task terpisah, semua error di-catch).
- Tidak pernah menampilkan private key/API secret.
"""

from __future__ import annotations

import asyncio
import csv
import io
import json
import logging
import secrets
import time
from pathlib import Path

from aiohttp import web

log = logging.getLogger("bot.dashboard")

STATIC_DIR = Path(__file__).resolve().parent / "static"


class DashboardServer:
    def __init__(self, engine, *, host: str = "127.0.0.1", port: int = 8788, throttle_fps: float = 4.0) -> None:
        self.engine = engine
        self.host = host
        self.port = port
        self.throttle_fps = max(0.5, throttle_fps)
        self.control_token = secrets.token_hex(16)
        self.paused = False
        self._started_at = time.time()
        self.app = web.Application()
        self._setup_routes()

    def _setup_routes(self) -> None:
        self.app.router.add_get("/", self.handle_index)
        self.app.router.add_get("/api/state", self.handle_state)
        self.app.router.add_get("/api/stream", self.handle_stream)
        self.app.router.add_get("/api/token", self.handle_token)
        self.app.router.add_post("/api/control/{action}", self.handle_control)
        self.app.router.add_get("/api/export/{kind}", self.handle_export)
        self.app.router.add_static("/static/", STATIC_DIR, show_index=False)

    # -- handlers ----------------------------------------------------------

    async def handle_index(self, request: web.Request) -> web.Response:
        index = STATIC_DIR / "index.html"
        html = index.read_text(encoding="utf-8")
        html = html.replace("__ARC_TOKEN__", self.control_token)
        return web.Response(text=html, content_type="text/html")

    async def handle_token(self, request: web.Request) -> web.Response:
        # token hanya untuk halaman lokal ini (bind 127.0.0.1)
        return web.json_response({"token": self.control_token})

    def _safe_state(self) -> dict:
        try:
            state = self.engine.dashboard_state()
            state["dashboard"] = {
                "uptime_s": time.time() - self._started_at,
                "paused": self.paused,
                "throttle_fps": self.throttle_fps,
            }
            state["logs"] = self._log_tail(80)
            state["health"] = self._health()
            return state
        except Exception as exc:
            log.exception("dashboard state failed")
            return {"error": str(exc)}

    def _log_tail(self, n: int) -> list[dict]:
        """Ambil N baris terakhir dari log terstruktur bot (tanpa mengganggu bot)."""
        try:
            log_file = Path(self.engine.root) / self.engine.cfg.get("monitoring", {}).get("log_dir", "logs") / "bot.log"
            if not log_file.exists():
                return []
            lines = log_file.read_text(encoding="utf-8", errors="replace").splitlines()[-n:]
            out = []
            for line in lines:
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    out.append({"level": "INFO", "msg": line[:300], "ts": ""})
            return out
        except Exception:
            return []

    def _health(self) -> dict:
        info: dict = {"cpu_pct": None, "rss_mb": None}
        try:
            import os
            if hasattr(os, "times"):
                t = os.times()
                info["cpu_times"] = {"user": t.user, "system": t.system}
            with open("/proc/self/status", "r", encoding="utf-8") as fh:
                for line in fh:
                    if line.startswith("VmRSS:"):
                        info["rss_mb"] = round(int(line.split()[1]) / 1024, 1)
                        break
        except Exception:
            pass
        try:
            import psutil  # opsional
            info["cpu_pct"] = psutil.cpu_percent(interval=None)
            info["rss_mb"] = round(psutil.Process().memory_info().rss / 1048576, 1)
        except Exception:
            pass
        return info

    async def handle_state(self, request: web.Request) -> web.Response:
        return web.json_response(self._safe_state())

    async def handle_stream(self, request: web.Request) -> web.StreamResponse:
        resp = web.StreamResponse(
            status=200,
            reason="OK",
            headers={
                "Content-Type": "text/event-stream",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )
        await resp.prepare(request)
        try:
            while True:
                if self.paused:
                    payload = {"dashboard": {"paused": True}, "status": self.engine.status.as_dict()}
                else:
                    payload = self._safe_state()
                data = json.dumps(payload, default=str)
                await resp.write(f"data: {data}\n\n".encode("utf-8"))
                await asyncio.sleep(1.0 / self.throttle_fps)
        except (asyncio.CancelledError, ConnectionResetError, BrokenPipeError):
            pass
        except Exception:
            log.debug("sse stream closed", exc_info=True)
        return resp

    async def handle_control(self, request: web.Request) -> web.Response:
        action = request.match_info.get("action", "")
        token = request.headers.get("X-ARC-Token", "")
        try:
            body = await request.json()
        except Exception:
            body = {}
        if not secrets.compare_digest(token, self.control_token):
            return web.json_response({"ok": False, "error": "invalid token"}, status=403)

        # konfirmasi dua langkah untuk aksi berbahaya
        dangerous = {"kill", "resume_after_kill"}
        if action in dangerous and body.get("confirm") != "CONFIRM":
            return web.json_response({
                "ok": False,
                "error": "two-step confirmation required: kirim {\"confirm\": \"CONFIRM\"}",
            }, status=400)

        if action == "pause":
            self.paused = True
            return web.json_response({"ok": True, "paused": True})
        if action == "resume":
            self.paused = False
            return web.json_response({"ok": True, "paused": False})
        if action == "kill":
            self.engine.risk.trigger_kill_switch("dashboard kill switch")
            log.warning("KILL SWITCH diaktifkan dari dashboard")
            return web.json_response({"ok": True, "killed": True})
        if action == "resume_after_kill":
            self.engine.risk.resume()
            log.warning("kill switch DIBERSIHKAN dari dashboard (resume_after_kill)")
            return web.json_response({"ok": True, "killed": False, "resumed": True})
        return web.json_response({"ok": False, "error": f"unknown action {action}"}, status=400)

    async def handle_export(self, request: web.Request) -> web.Response:
        kind = request.match_info.get("kind", "")
        db = self.engine.db
        if kind == "opportunities":
            rows = db.recent_opportunities(5000)
            return self._csv_response("opportunities.csv", rows)
        if kind == "trades":
            rows = db.trades(5000)
            return self._csv_response("trades.csv", rows)
        if kind == "pnl":
            rows = db.pnl_history(5000)
            return web.json_response(rows)
        return web.json_response({"error": "unknown export"}, status=404)

    def _csv_response(self, filename: str, rows: list[dict]) -> web.Response:
        buf = io.StringIO()
        if rows:
            writer = csv.DictWriter(buf, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        return web.Response(
            text=buf.getvalue(),
            headers={
                "Content-Type": "text/csv; charset=utf-8",
                "Content-Disposition": f'attachment; filename="{filename}"',
            },
        )

    async def start(self, open_browser: bool = False) -> None:
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        url = f"http://{self.host}:{self.port}/"
        log.info("ARC-TERMINAL dashboard listening on %s (bind %s only)", url, self.host)
        if open_browser:
            try:
                import webbrowser
                webbrowser.open(url)
            except Exception:
                log.warning("gagal membuka browser otomatis — buka manual: %s", url)
        # pertahankan referensi agar tidak GC
        self._runner = runner


async def run_dashboard(engine, *, host: str = "127.0.0.1", port: int = 8788, open_browser: bool = False, throttle_fps: float = 4.0) -> None:
    server = DashboardServer(engine, host=host, port=port, throttle_fps=throttle_fps)
    try:
        await server.start(open_browser=open_browser)
    except OSError as exc:
        log.error("dashboard gagal start (port %s): %s — bot tetap berjalan", port, exc)
        return
    try:
        await asyncio.Event().wait()  # hidup sampai di-cancel
    except asyncio.CancelledError:
        log.info("dashboard dihentikan")
        raise
