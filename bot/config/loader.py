"""Loader konfigurasi: YAML (config/default.yaml) + env (.env) + CLI override."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Optional

import yaml

try:
    from dotenv import load_dotenv
except ImportError:  # dotenv opsional
    load_dotenv = None

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = ROOT / "config" / "default.yaml"


def load_env(env_path: Optional[Path] = None) -> None:
    """Muat .env dari root repo (tidak menimpa env yang sudah ada)."""
    if load_dotenv is not None:
        load_dotenv(env_path or ROOT / ".env", override=False)


def load_config(path: Optional[Path] = None, overrides: Optional[dict] = None) -> dict:
    cfg_path = Path(path) if path else Path(os.environ.get("BOT_CONFIG") or DEFAULT_CONFIG_PATH)
    if not cfg_path.is_absolute():
        cfg_path = ROOT / cfg_path
    with open(cfg_path, "r", encoding="utf-8") as fh:
        cfg: dict[str, Any] = yaml.safe_load(fh) or {}
    if overrides:
        _deep_update(cfg, overrides)
    return cfg


def _deep_update(base: dict, upd: dict) -> dict:
    for k, v in upd.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            _deep_update(base[k], v)
        else:
            base[k] = v
    return base


def live_trading_enabled() -> bool:
    """Gate ganda mode live: env LIVE_TRADING=true DAN file live_trading.confirmed.

    Sesi pengembangan TIDAK PERNAH mengaktifkan ini (misi §5).
    """
    if os.environ.get("LIVE_TRADING", "").strip().lower() != "true":
        return False
    return (ROOT / "live_trading.confirmed").exists()


def kill_switch_active(path: Optional[str] = None) -> bool:
    p = ROOT / (path or "KILL_SWITCH")
    return p.exists()


def ensure_dotenv_example() -> None:
    """Pastikan .env.example ada (dipakai launcher .bat)."""
    assert (ROOT / ".env.example").exists(), ".env.example wajib ada di root repo"
