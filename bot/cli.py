"""CLI entrypoint: `python -m bot --mode paper|backtest|live` (misi §5c)."""

from __future__ import annotations

import argparse
import asyncio
import logging
import signal
import sys
from pathlib import Path

from .config.loader import ROOT, load_config, load_env, live_trading_enabled
from .engine import build_engine_async
from .monitoring import setup_logging

log = logging.getLogger("bot.cli")


def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="python -m bot",
        description="Bot arbitrase Polymarket (default: PAPER — simulasi, tanpa order asli)",
    )
    p.add_argument("--mode", choices=["paper", "backtest", "live"], default="paper",
                   help="mode operasi (default: paper)")
    p.add_argument("--config", default=None, help="path config YAML (default: config/default.yaml)")
    p.add_argument("--no-dashboard", action="store_true", help="jalankan tanpa dashboard web")
    p.add_argument("--port", type=int, default=None, help="port dashboard (default: 8788)")
    p.add_argument("--duration", type=float, default=None,
                   help="hentikan otomatis setelah N detik (berguna untuk smoke test)")
    p.add_argument("--no-open-browser", action="store_true", help="jangan buka browser otomatis")
    return p.parse_args(argv)


async def async_main(args: argparse.Namespace) -> int:
    load_env()
    cfg = load_config(Path(args.config) if args.config else None)

    logging_cfg = cfg.get("monitoring", {})
    setup_logging(
        ROOT / logging_cfg.get("log_dir", "logs"),
        level=str(logging_cfg.get("log_level", "INFO")),
        max_bytes=int(logging_cfg.get("log_max_bytes", 10_485_760)),
        backups=int(logging_cfg.get("log_backup_count", 5)),
    )

    mode = args.mode
    if mode == "live" and not live_trading_enabled():
        log.error(
            "Mode live DITOLAK: butuh LIVE_TRADING=true di .env DAN file "
            "live_trading.confirmed. Menjalankan mode paper sebagai gantinya."
        )
        mode = "paper"

    log.info("starting bot in %s mode", mode.upper())
    engine = await build_engine_async(cfg, mode=mode, root=ROOT)

    dashboard_task = None
    if not args.no_dashboard and cfg.get("dashboard", {}).get("enabled", True):
        from .dashboard.server import run_dashboard
        dash_cfg = cfg.get("dashboard", {})
        port = args.port or int(dash_cfg.get("port", 8788))
        dashboard_task = asyncio.create_task(
            run_dashboard(
                engine,
                host=str(dash_cfg.get("host", "127.0.0.1")),
                port=port,
                open_browser=bool(dash_cfg.get("open_browser", True)) and not args.no_open_browser,
                throttle_fps=float(dash_cfg.get("throttle_fps", 4)),
            ),
            name="dashboard",
        )

    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, stop_event.set)
        except NotImplementedError:  # Windows
            signal.signal(sig, lambda *_: stop_event.set())

    await engine.start()
    try:
        if args.duration:
            await asyncio.wait_for(stop_event.wait(), timeout=args.duration)
        else:
            await stop_event.wait()
    except asyncio.TimeoutError:
        pass
    finally:
        log.info("shutting down (clean)...")
        await engine.stop()
        if dashboard_task:
            dashboard_task.cancel()
            try:
                await dashboard_task
            except (asyncio.CancelledError, Exception):
                pass
    return 0


def main(argv=None) -> int:
    args = parse_args(argv)
    try:
        return asyncio.run(async_main(args))
    except KeyboardInterrupt:
        print("\nInterrupted — bot dihentikan dengan bersih.")
        return 130


if __name__ == "__main__":
    sys.exit(main())
