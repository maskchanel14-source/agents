"""Configuration loading and the live-trading gate.

Precedence: YAML file (``config/default.yaml`` unless overridden) — there are
deliberately few env overrides, and NONE can enable live trading on their own.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path
from typing import Any

import yaml

from .costs import DEFAULT_GAS_UNITS, CostParams, GasEstimate
from .money import dec

MODES = ("backtest", "paper", "live")
DEFAULT_CONFIG = Path(__file__).resolve().parents[2] / "config" / "default.yaml"
LIVE_CONFIRMATION_FILE = Path(__file__).resolve().parents[2] / "config" / "LIVE_CONFIRMED.txt"


class LiveGateError(RuntimeError):
    """Raised when live mode is requested without every required gate."""


@dataclass(frozen=True)
class RiskLimits:
    max_notional_per_trade: Decimal = dec("50")
    max_exposure_per_market: Decimal = dec("100")
    max_exposure_per_event: Decimal = dec("200")
    max_total_exposure: Decimal = dec("500")
    max_daily_loss: Decimal = dec("25")
    max_orders_per_minute: int = 30
    max_consecutive_errors: int = 5
    circuit_cooldown_s: int = 300
    max_quoted_spread: Decimal = dec("0.25")  # reject books with a wider spread (anomaly)


@dataclass(frozen=True)
class Thresholds:
    min_net_profit_usdc: Decimal = dec("0.05")
    min_net_pct: Decimal = dec("0.002")
    min_annualized_pct: Decimal = dec("0.20")
    max_book_age_ms: int = 1500
    max_book_skew_ms: int = 1000
    max_shares_per_trade: Decimal = dec("500")
    min_shares: Decimal = dec("5")


@dataclass(frozen=True)
class DataSettings:
    gamma_base: str = "https://gamma-api.polymarket.com"
    clob_base: str = "https://clob.polymarket.com"
    ws_url: str = "wss://ws-subscriptions-clob.polymarket.com/ws/market"
    cache_ttl_s: int = 300
    market_refresh_s: int = 600
    events_page_size: int = 100
    max_events: int = 500
    http_timeout_s: float = 10.0
    max_requests_per_10s: int = 200  # local throttle, far below documented limits
    scan_interval_ms: int = 500
    max_assets: int = 400  # subscription budget (most liquid markets first)
    exclude_ambiguous: bool = True  # blacklist markets with thin/unclear resolution criteria
    blacklist_condition_ids: tuple[str, ...] = ()  # explicit operator blacklist


@dataclass(frozen=True)
class Settings:
    mode: str
    strategies: Mapping[str, bool]
    limits: RiskLimits
    thresholds: Thresholds
    costs: CostParams
    data: DataSettings
    db_path: Path
    kill_switch_path: Path
    recordings_dir: Path
    reports_dir: Path
    exit_method_binary: str = "merge"
    raw: dict[str, Any] = field(default_factory=dict, compare=False)


def _d(section: Mapping[str, Any], key: str, default: Any) -> Any:
    return section.get(key, default)


def _dec(section: Mapping[str, Any], key: str, default: Any) -> Decimal:
    """YAML floats are converted via str so decimal values stay exact (e.g. 0.25)."""
    return dec(str(_d(section, key, default)))


def load_settings(path: Path | None = None, mode_override: str | None = None) -> Settings:
    cfg_path = Path(path) if path else DEFAULT_CONFIG
    raw: dict[str, Any] = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
    root = Path(cfg_path).resolve().parents[1]  # project root (config/..)

    mode = mode_override or raw.get("mode", "paper")
    if mode not in MODES:
        raise ValueError(f"unknown mode {mode!r}; expected one of {MODES}")

    lim = raw.get("risk", {})
    limits = RiskLimits(
        max_notional_per_trade=_dec(lim, "max_notional_per_trade", "50"),
        max_exposure_per_market=_dec(lim, "max_exposure_per_market", "100"),
        max_exposure_per_event=_dec(lim, "max_exposure_per_event", "200"),
        max_total_exposure=_dec(lim, "max_total_exposure", "500"),
        max_daily_loss=_dec(lim, "max_daily_loss", "25"),
        max_orders_per_minute=int(_d(lim, "max_orders_per_minute", 30)),
        max_consecutive_errors=int(_d(lim, "max_consecutive_errors", 5)),
        circuit_cooldown_s=int(_d(lim, "circuit_cooldown_s", 300)),
        max_quoted_spread=_dec(lim, "max_quoted_spread", "0.25"),
    )

    th = raw.get("thresholds", {})
    thresholds = Thresholds(
        min_net_profit_usdc=_dec(th, "min_net_profit_usdc", "0.05"),
        min_net_pct=_dec(th, "min_net_pct", "0.002"),
        min_annualized_pct=_dec(th, "min_annualized_pct", "0.20"),
        max_book_age_ms=int(_d(th, "max_book_age_ms", 1500)),
        max_book_skew_ms=int(_d(th, "max_book_skew_ms", 1000)),
        max_shares_per_trade=_dec(th, "max_shares_per_trade", "500"),
        min_shares=_dec(th, "min_shares", "5"),
    )

    cs = raw.get("costs", {})
    gas_raw = cs.get("gas", {})
    units = dict(DEFAULT_GAS_UNITS)
    units.update({k: int(v) for k, v in cs.get("gas_units", {}).items()})
    costs = CostParams(
        gas=GasEstimate(
            gas_price_gwei=_dec(gas_raw, "fallback_gas_price_gwei", "200"),
            pol_usd=_dec(gas_raw, "fallback_pol_usd", "1.0"),
            source="config_fallback",
        ),
        gas_units=units,
        gasless_relayer=bool(_d(cs, "gasless_relayer", False)),
        safety_margin_rate=_dec(cs, "safety_margin_rate", "0.001"),
        base_resolution_haircut=_dec(cs, "base_resolution_haircut", "0.001"),
        ambiguous_resolution_haircut=_dec(cs, "ambiguous_resolution_haircut", "0.01"),
        per_day_resolution_haircut=_dec(cs, "per_day_resolution_haircut", "0.0002"),
        uma_resolution_hours=_dec(cs, "uma_resolution_hours", "48"),
        merge_lockup_hours=_dec(cs, "merge_lockup_hours", "0.25"),
        sell_lockup_hours=_dec(cs, "sell_lockup_hours", "0.1"),
        leg_fail_probability=_dec(cs, "leg_fail_probability", "0.05"),
        p_unknown_resolution=_dec(cs, "p_unknown_resolution", "0.005"),
        opportunity_cost_annual_rate=_dec(cs, "opportunity_cost_annual_rate", "0.04"),
    )

    dt = raw.get("data", {})
    data = DataSettings(
        gamma_base=str(_d(dt, "gamma_base", DataSettings.gamma_base)),
        clob_base=str(_d(dt, "clob_base", DataSettings.clob_base)),
        ws_url=str(_d(dt, "ws_url", DataSettings.ws_url)),
        cache_ttl_s=int(_d(dt, "cache_ttl_s", 300)),
        market_refresh_s=int(_d(dt, "market_refresh_s", 600)),
        events_page_size=int(_d(dt, "events_page_size", 100)),
        max_events=int(_d(dt, "max_events", 500)),
        http_timeout_s=float(_d(dt, "http_timeout_s", 10.0)),
        max_requests_per_10s=int(_d(dt, "max_requests_per_10s", 200)),
        scan_interval_ms=int(_d(dt, "scan_interval_ms", 500)),
        max_assets=int(_d(dt, "max_assets", 400)),
        exclude_ambiguous=bool(_d(dt, "exclude_ambiguous", True)),
        blacklist_condition_ids=tuple(str(x).lower() for x in _d(dt, "blacklist_condition_ids", []) or []),
    )

    paths = raw.get("paths", {})
    return Settings(
        mode=mode,
        strategies=dict(raw.get("strategies", {})),
        limits=limits,
        thresholds=thresholds,
        costs=costs,
        data=data,
        db_path=root / _d(paths, "db", "state/bot.sqlite"),
        kill_switch_path=root / _d(paths, "kill_switch", "state/KILL_SWITCH"),
        recordings_dir=root / _d(paths, "recordings", "data/recordings"),
        reports_dir=root / _d(paths, "reports", "reports"),
        exit_method_binary=str(_d(raw.get("strategies_params", {}), "exit_method_binary", "merge")),
        raw=raw,
    )


def check_live_gate(
    mode: str,
    env: Mapping[str, str],
    confirmation_file: Path = LIVE_CONFIRMATION_FILE,
) -> None:
    """Refuse live mode unless BOTH ``LIVE_TRADING=true`` and the local file exist.

    This only gates *arming*. Even when it passes, ``LiveExecutor`` still refuses to
    sign or send orders without an explicitly configured signer (none ships here).
    """
    if mode != "live":
        return
    if env.get("LIVE_TRADING", "").strip().lower() != "true":
        raise LiveGateError("live mode refused: LIVE_TRADING env is not 'true'")
    if not confirmation_file.is_file():
        raise LiveGateError(f"live mode refused: confirmation file missing ({confirmation_file.name})")
