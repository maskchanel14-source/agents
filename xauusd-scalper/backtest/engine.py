"""
Python mirror of XauUsdScalper.mq5 — bar-based backtest engine.

Mirrors the MQL5 EA logic 1:1 (spec.md):
  - EMA fast/slow cross + RSI confirm, evaluated on CLOSED bars only
  - ATR band gate, session filter, Friday block, max-trades/day
  - ATR-scaled SL/TP, break-even at +N R, ATR trailing (after BE),
    time exit (before BE only)
  - fixed-fractional risk sizing (on CASH at entry — no look-ahead),
    daily-loss + consecutive-loss circuit breakers

Honesty notes (caveats of the bar-based mirror vs MT5 Strategy Tester):
  * Entries at bar OPEN; intra-bar exit ambiguity resolved conservatively
    (SL checked before BE trigger, before TP; SL & TP in one bar -> SL wins).
  * Trailing uses ATR of the last CLOSED bar (MQL5 uses the forming bar).
  * Breaker evaluated at bar close (MQL5 on every tick).
  * BE/SL can trigger from the entry bar itself (intra-bar ordering assumed
    open -> SL -> BE -> TP, conservative).
  * Costs: flat round-trip cost per oz (spread + slippage) — the dataset has
    no variable spread.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List

import numpy as np
import pandas as pd

# ----------------------------------------------------------------------
# indicators (MQL5-flavoured)
# ----------------------------------------------------------------------

def ema(s: np.ndarray, period: int) -> np.ndarray:
    out = np.full_like(s, np.nan, dtype=np.float64)
    if len(s) < period:
        return out
    alpha = 2.0 / (period + 1.0)
    out[period - 1] = s[:period].mean()
    for i in range(period, len(s)):
        out[i] = alpha * s[i] + (1 - alpha) * out[i - 1]
    return out


def rsi_sma(c: np.ndarray, period: int) -> np.ndarray:
    """MQL5 RSI: SMA(up) / (SMA(up)+SMA(dn)) * 100."""
    out = np.full(len(c), np.nan)
    if len(c) <= period:
        return out
    d = np.diff(c)
    up = np.where(d > 0, d, 0.0)
    dn = np.where(d < 0, -d, 0.0)
    us = pd.Series(up).rolling(period).mean().to_numpy()
    ds = pd.Series(dn).rolling(period).mean().to_numpy()
    with np.errstate(divide="ignore", invalid="ignore"):
        r = np.where((us + ds) > 0, 100.0 * us / (us + ds), 50.0)
    out[1:] = r  # r[j] covers price change ending at bar j+1
    return out


def atr_sma(h: np.ndarray, l: np.ndarray, c: np.ndarray, period: int) -> np.ndarray:
    """MQL5 ATR: SMA of true range."""
    n = len(c)
    out = np.full(n, np.nan)
    if n < period:
        return out
    tr = np.empty(n)
    tr[0] = h[0] - l[0]
    pc = c[:-1]
    tr[1:] = np.maximum(h[1:] - l[1:], np.maximum(np.abs(h[1:] - pc), np.abs(l[1:] - pc)))
    m = pd.Series(tr).rolling(period).mean().to_numpy()
    out[period - 1:] = m[period - 1:]
    return out


# ----------------------------------------------------------------------
# config
# ----------------------------------------------------------------------

@dataclass
class Cfg:
    ema_fast: int = 9
    ema_slow: int = 21
    rsi_period: int = 7
    rsi_level: float = 50.0
    atr_period: int = 14
    atr_min: float = 1.0      # H1-scaled (MQL5 default 0.30 is M5-scaled)
    atr_max: float = 15.0     # H1-scaled
    sl_mult: float = 1.5
    tp_mult: float = 2.25
    use_be: bool = True
    be_r: float = 1.0
    trail_mult: float = 1.5
    time_exit_bars: int = 12
    session_start: int = 7    # data-local hours
    session_end: int = 16
    friday_block_hour: int = 20
    risk_pct: float = 0.5
    max_daily_loss_pct: float = 2.0
    max_consec_losses: int = 4
    max_daily_trades: int = 10
    min_lot: float = 0.01
    lot_step: float = 0.01
    max_lot: float = 5.0
    cost_per_oz: float = 0.40   # round trip: ~0.30 spread + 0.10 slippage
    starting_equity: float = 10_000.0
    be_buf: float = 0.02
    stops_dist: float = 0.10    # min SL/TP distance (H1 scale)
    trend_ema: int = 0          # 0=off; else long-only above / short-only below EMA(N)


# ----------------------------------------------------------------------
# engine
# ----------------------------------------------------------------------

def run_backtest(df: pd.DataFrame, cfg: Cfg) -> dict:
    """
    df columns: ts (datetime64), o, h, l, c  (sorted ascending, no dups)
    """
    o = df["o"].to_numpy(np.float64)
    h = df["h"].to_numpy(np.float64)
    l = df["l"].to_numpy(np.float64)
    c = df["c"].to_numpy(np.float64)
    ts = df["ts"].to_numpy()
    n = len(c)

    hour = df["ts"].dt.hour.to_numpy()
    weekday = df["ts"].dt.dayofweek.to_numpy()          # 0=Mon..6=Sun
    day_key = (df["ts"].dt.year * 10000 + df["ts"].dt.month * 100
               + df["ts"].dt.day).to_numpy()

    ema_f = ema(c, cfg.ema_fast)
    ema_s = ema(c, cfg.ema_slow)
    rsi = rsi_sma(c, cfg.rsi_period)
    atr = atr_sma(h, l, c, cfg.atr_period)
    ema_t = ema(c, cfg.trend_ema) if cfg.trend_ema > 0 else None

    warm = max(cfg.ema_slow, cfg.atr_period, cfg.rsi_period) + 3
    cash = cfg.starting_equity
    equity = np.full(n, np.nan)

    # day / breaker state
    cur_day = -1
    day_start_eq = cfg.starting_equity
    day_trades = 0
    consec_losses = 0
    halted = False

    # position state
    pos_dir = 0
    entry_px = sl = tp = r0 = lots = risk_amt = 0.0
    be_done = False
    entry_i = -1

    trades: List[dict] = []
    exit_counts = {"SL": 0, "TP": 0, "BE": 0, "TIME": 0, "END": 0}

    def close_pos(i, px, reason):
        nonlocal cash, pos_dir, be_done, risk_amt, consec_losses
        gross = (px - entry_px) * 100.0 * lots * pos_dir
        net = gross - cfg.cost_per_oz * 100.0 * lots
        cash += net
        r = net / risk_amt if risk_amt > 0 else 0.0
        trades.append({
            "entry_i": entry_i, "exit_i": i,
            "entry_ts": str(ts[entry_i]), "exit_ts": str(ts[i]),
            "dir": "buy" if pos_dir > 0 else "sell",
            "lots": round(lots, 2), "entry": round(entry_px, 2),
            "exit": round(px, 2), "pnl": round(net, 2), "r": round(r, 3),
            "reason": reason, "bars_held": i - entry_i,
        })
        exit_counts[reason] += 1
        consec_losses = 0 if net > 0 else consec_losses + 1
        pos_dir = 0
        be_done = False
        risk_amt = 0.0

    def process_exits(i):
        """SL/BE/TP/time-exit for the open position using bar i OHLC.
        Conservative intra-bar order: trailing(update) -> SL -> BE trigger -> TP."""
        nonlocal sl, be_done
        if pos_dir == 0:
            return
        exit_px, exit_reason = 0.0, ""
        # 1) trailing update at bar open (last closed bar ATR)
        if cfg.use_be and be_done and not math.isnan(atr[i - 1]) and atr[i - 1] > 0:
            if pos_dir > 0:
                cand = c[i - 1] - cfg.trail_mult * atr[i - 1]
                if sl == 0.0 or cand > sl + 0.001:
                    sl = cand
            else:
                cand = c[i - 1] + cfg.trail_mult * atr[i - 1]
                if sl == 0.0 or cand < sl - 0.001:
                    sl = cand
        # 2) SL
        if pos_dir > 0 and l[i] <= sl:
            exit_px, exit_reason = sl, ("BE" if be_done else "SL")
        elif pos_dir < 0 and h[i] >= sl:
            exit_px, exit_reason = sl, ("BE" if be_done else "SL")
        # 3) break-even trigger
        if exit_reason == "" and cfg.use_be and not be_done and r0 > 0:
            trig = entry_px + cfg.be_r * r0 * pos_dir
            if (pos_dir > 0 and h[i] >= trig) or (pos_dir < 0 and l[i] <= trig):
                be_done = True
                sl = entry_px + (cfg.be_buf if pos_dir > 0 else -cfg.be_buf)
                if (pos_dir > 0 and l[i] <= sl) or (pos_dir < 0 and h[i] >= sl):
                    exit_px, exit_reason = sl, "BE"
        # 4) TP (tp == 0 -> disabled, trailing/takeover instead)
        if exit_reason == "" and tp > 0 and \
                ((pos_dir > 0 and h[i] >= tp) or (pos_dir < 0 and l[i] <= tp)):
            exit_px, exit_reason = tp, "TP"
        # 5) time exit (before BE only)
        if exit_reason == "" and cfg.time_exit_bars > 0 and not be_done \
                and (i - entry_i) >= cfg.time_exit_bars:
            exit_px, exit_reason = c[i], "TIME"
        if exit_reason:
            close_pos(i, exit_px, exit_reason)

    for i in range(warm, n):
        # ---- exits for pre-existing position --------------------------
        process_exits(i)

        # ---- equity mark at close --------------------------------------
        unreal = (c[i] - entry_px) * 100.0 * lots * pos_dir if pos_dir != 0 else 0.0
        eq = cash + unreal
        equity[i] = eq

        # ---- day rollover ----------------------------------------------
        if day_key[i] != cur_day:
            cur_day = day_key[i]
            day_start_eq = eq
            day_trades = 0
            consec_losses = 0
            halted = False

        # ---- circuit breakers (per bar close, for subsequent entries) --
        if not halted and day_start_eq > 0:
            day_pnl_pct = (eq - day_start_eq) / day_start_eq * 100.0
            if day_pnl_pct <= -cfg.max_daily_loss_pct:
                halted = True
        if not halted and consec_losses >= cfg.max_consec_losses:
            halted = True

        # ---- entry evaluation (new bar, closed-bar signals) ------------
        if pos_dir == 0 and not halted and day_trades < cfg.max_daily_trades \
                and weekday[i] < 5:
            in_session = (cfg.session_start == cfg.session_end) or (
                (cfg.session_start < cfg.session_end and
                 cfg.session_start <= hour[i] < cfg.session_end)
                or (cfg.session_start > cfg.session_end and
                    (hour[i] >= cfg.session_start or hour[i] < cfg.session_end)))
            no_friday_block = not (cfg.friday_block_hour > 0 and weekday[i] == 4
                                   and hour[i] >= cfg.friday_block_hour)
            if in_session and no_friday_block:
                a1 = atr[i - 1]
                if not math.isnan(a1) and a1 > 0 and cfg.atr_min <= a1 <= cfg.atr_max:
                    ef1, ef2, es1, es2, r1 = ema_f[i - 1], ema_f[i - 2], \
                        ema_s[i - 1], ema_s[i - 2], rsi[i - 1]
                    if not any(math.isnan(x) for x in (ef1, ef2, es1, es2, r1)):
                        up = ef2 <= es2 and ef1 > es1
                        dn = ef2 >= es2 and ef1 < es1
                        if cfg.trend_ema > 0 and ema_t is not None:
                            if math.isnan(ema_t[i - 1]):
                                up = dn = False
                            else:
                                up = up and c[i - 1] > ema_t[i - 1]
                                dn = dn and c[i - 1] < ema_t[i - 1]
                        sig = (up and r1 > cfg.rsi_level) or (dn and r1 < cfg.rsi_level)
                        if sig:
                            sl_dist = max(cfg.sl_mult * a1, cfg.stops_dist)
                            tp_dist = (max(cfg.tp_mult * a1, cfg.stops_dist)
                                       if cfg.tp_mult > 0 else 0.0)
                            px = o[i]
                            loss_per_lot = sl_dist * 100.0
                            lots_want = cash * cfg.risk_pct / 100.0 / loss_per_lot
                            lots_w = math.floor(lots_want / cfg.lot_step + 1e-9) * cfg.lot_step
                            lots_w = round(min(max(lots_w, 0.0), cfg.max_lot), 2)
                            if lots_w >= cfg.min_lot:
                                pos_dir = 1 if up else -1
                                entry_px = px
                                sl = px - sl_dist if up else px + sl_dist
                                tp = px + tp_dist if up else px - tp_dist
                                r0 = sl_dist
                                lots = lots_w
                                risk_amt = sl_dist * 100.0 * lots
                                be_done = False
                                entry_i = i
                                day_trades += 1
                                process_exits(i)   # entry bar may exit intrabar

    if pos_dir != 0:
        close_pos(n - 1, c[n - 1], "END")
        equity[n - 1] = cash

    return {
        "trades": trades,
        "equity": equity,
        "ts": ts,
        "atr": atr,
        "exits": exit_counts,
        "final_equity": cash,
    }


# ----------------------------------------------------------------------
# metrics
# ----------------------------------------------------------------------

def split_metrics(trades: List[dict], equity: np.ndarray, lo: int, hi: int,
                  start_eq: float) -> dict:
    sub = [t for t in trades if lo <= t["entry_i"] < hi]
    eq = equity[lo:hi]
    eq = eq[~np.isnan(eq)]
    if len(eq) == 0:
        eq = np.array([start_eq])
    peak = np.maximum.accumulate(eq)
    dd = (eq - peak) / peak
    gross_win = sum(t["pnl"] for t in sub if t["pnl"] > 0)
    gross_loss = -sum(t["pnl"] for t in sub if t["pnl"] <= 0)
    nt = len(sub)
    wins = sum(1 for t in sub if t["pnl"] > 0)
    exp_r = (sum(t["r"] for t in sub) / nt) if nt else 0.0
    consec = mcl = 0
    for t in sub:
        consec = 0 if t["pnl"] > 0 else consec + 1
        mcl = max(mcl, consec)
    return {
        "trades": nt,
        "win_rate_pct": 100.0 * wins / nt if nt else 0.0,
        "expectancy_R": exp_r,
        "net_pnl": sum(t["pnl"] for t in sub),
        "profit_factor": gross_win / gross_loss if gross_loss > 0
                         else (float("inf") if gross_win > 0 else 0.0),
        "max_dd_pct": 100.0 * float(dd.min()) if len(dd) else 0.0,
        "max_consec_losses": mcl,
        "avg_bars": float(np.mean([t["bars_held"] for t in sub])) if nt else 0.0,
    }


def monte_carlo(trades: List[dict], start_eq: float, n_sims: int = 1000, seed: int = 42) -> dict:
    if not trades:
        return {"p_final_below_90": 1.0, "p_min_below_90": 1.0,
                "final_min": start_eq, "final_median": start_eq}
    pnls = np.array([t["pnl"] for t in trades])
    rng = np.random.default_rng(seed)
    finals = np.empty(n_sims)
    mins = np.empty(n_sims)
    for s in range(n_sims):
        order = rng.permutation(len(pnls))
        path = start_eq + np.cumsum(pnls[order])
        finals[s] = path[-1]
        mins[s] = path.min()
    return {
        "p_final_below_90": float((finals < 0.9 * start_eq).mean()),
        "p_min_below_90": float((mins < 0.9 * start_eq).mean()),
        "final_min": float(finals.min()),
        "final_median": float(np.median(finals)),
    }


def fmt_metrics(m: dict) -> str:
    pf = "inf" if m["profit_factor"] == float("inf") else f"{m['profit_factor']:.2f}"
    return (f"trades={m['trades']} win%={m['win_rate_pct']:.1f} expR={m['expectancy_R']:+.3f} "
            f"net=${m['net_pnl']:+,.0f} PF={pf} maxDD={m['max_dd_pct']:.1f}% "
            f"maxConsecLoss={m['max_consec_losses']} avgBars={m['avg_bars']:.1f}")
