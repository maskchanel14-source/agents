#!/usr/bin/env python3
"""Bar-level proxy backtest for XAUUSD_AgentEA v1 (Gold Session Trend-Pullback).

Stdlib only. Fetches a few *small* public XAUUSD OHLC samples from GitHub on
demand (cached under /tmp, never committed), ports the EA's rules 1:1 at bar
level, and prints honest statistics.

THIS IS A LOGIC / SANITY CHECK, NOT EVIDENCE OF PROFITABILITY:
  * a few thousand bars per sample -> tiny trade counts
  * bar-level fills (SL wins ties), constant spread, no slippage/commission/swap
  * indicator implementations approximate MT5's (EMA/ATR/RSI/ADX)
  * sample timezones inferred from the hourly range profile, see SAMPLES

Usage:
    python3 proxy_backtest.py                 # defaults, all samples
    python3 proxy_backtest.py --stress        # + spread x1.5 and +/-1 step neighbourhood
    python3 proxy_backtest.py --json out.json # also dump machine-readable results
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import math
import os
import sys
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass, replace
from datetime import UTC, datetime, timedelta

CACHE = os.environ.get("XAU_PROXY_CACHE", "/tmp/xauusd-proxy-data")
MAX_BYTES = 1_000_000  # hard cap per sample (128MB sandbox budget)

# Small public samples (each < 250 KB). fmt describes the column layout.
SAMPLES = [
    {
        "id": "h1_2024",
        "repo": "SandileJ/Analysing_GOLD",
        "path": "DATA/XAUUSD60.csv",
        "fmt": "mt_csv",  # 2024.04.30,11:00,O,H,L,C,V
        "tf_min": 60,
        "regime_tf_min": 240,  # H1 signal -> H4 regime (EA default is M15 -> H1)
        "gmt_offset": 3,  # broker time GMT+3 (EEST); range profile peaks 12-14 GMT -> consistent
        "spread": 0.30,  # USD per oz, assumed typical retail spread at the 2024 price level
    },
    {
        "id": "m15_2025_12",
        "repo": "Aleckqhie/quant_learning-journey-",
        "path": "data/raw/XAUUSD15(1).csv",
        "fmt": "mt_csv",
        "tf_min": 15,
        "regime_tf_min": 60,
        "gmt_offset": 2,  # broker time GMT+2 (EET winter); range profile peaks 13-15 GMT -> consistent
        "spread": 0.40,
    },
    {
        "id": "m15_2026_08",
        "repo": "ripper7375/trading-alerts-saas-public",
        "path": "davintrade-stack-d-and-e/engine-1-5-new/OHLCV_XAUUSD_M15.txt",
        "fmt": "tsv_unix_cohl",  # ts, symbol, tf, close, open, high, low, volume
        "tf_min": 15,
        "regime_tf_min": 60,
        # unix epoch -> UTC; confirmed by the hourly range profile peaking 12-15 GMT
        "gmt_offset": 0,
        "spread": 0.45,
    },
]


@dataclass(frozen=True)
class Params:
    # mirrors XAUUSD_AgentEA.mq5 inputs (v1 defaults, fixed BEFORE running this script)
    ema_signal: int = 20
    atr_period: int = 14
    rsi_period: int = 14
    ema_fast_regime: int = 50
    ema_slow_regime: int = 200
    adx_period: int = 14
    adx_min: float = 20.0
    slope_bars: int = 3
    pullback_bars: int = 6
    touch_atr: float = 0.25
    max_chase_atr: float = 1.0
    atr_avg_bars: int = 100
    vol_ratio_min: float = 0.6
    vol_ratio_max: float = 2.5
    sl_buffer_atr: float = 0.25
    sl_min_atr: float = 1.0
    sl_max_atr: float = 2.5
    tp_rr: float = 2.0
    be_trigger_r: float = 1.0
    be_buffer_r: float = 0.1
    trail_start_r: float = 1.5
    trail_atr: float = 1.0
    max_bars_in_trade: int = 48
    session_start_gmt: int = 7
    session_end_gmt: int = 20
    friday_last_entry_gmt: int = 18
    friday_close_gmt: int = 20
    max_spread_atr: float = 0.15
    risk_pct: float = 0.5
    max_trades_day: int = 3
    daily_loss_pct: float = 2.0
    kill_dd_pct: float = 15.0


@dataclass
class Bar:
    t: datetime  # bar open time, broker/server clock (naive)
    o: float
    h: float
    l: float
    c: float


# ----------------------------------------------------------------------------- data


def fetch(sample: dict) -> str:
    os.makedirs(CACHE, exist_ok=True)
    fn = os.path.join(CACHE, sample["id"] + ".txt")
    if os.path.exists(fn):
        with open(fn, encoding="utf-8") as fh:
            return fh.read()
    url = f"https://api.github.com/repos/{sample['repo']}/contents/{urllib.parse.quote(sample['path'])}"
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github.raw",
            "User-Agent": "xauusd-factory",
        },
    )
    tok = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if tok:
        req.add_header("Authorization", f"token {tok}")
    with urllib.request.urlopen(req, timeout=30) as r:
        data = r.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise RuntimeError(
            f"{sample['id']}: sample exceeds {MAX_BYTES} bytes, refusing (sandbox budget)"
        )
    text = data.decode("utf-8", "replace")
    with open(fn, "w", encoding="utf-8") as fh:
        fh.write(text)
    return text


def parse(sample: dict, text: str) -> list[Bar]:
    bars: list[Bar] = []
    if sample["fmt"] == "mt_csv":
        for row in csv.reader(io.StringIO(text)):
            if len(row) < 6:
                continue
            try:
                t = datetime.strptime(
                    row[0].strip() + " " + row[1].strip(), "%Y.%m.%d %H:%M"
                )
                o, h, l, c = (float(x) for x in row[2:6])
            except ValueError:
                continue
            bars.append(Bar(t, o, h, l, c))
    elif sample["fmt"] == "tsv_unix_cohl":
        for row in csv.reader(io.StringIO(text), delimiter="\t"):
            if len(row) < 7 or not row[0].strip().isdigit():
                continue
            t = datetime.fromtimestamp(int(row[0]), tz=UTC).replace(tzinfo=None)
            c, o, h, l = (float(x) for x in row[3:7])
            bars.append(Bar(t, o, h, l, c))
    else:
        raise ValueError(sample["fmt"])
    bars.sort(key=lambda b: b.t)
    dedup: list[Bar] = []
    for b in bars:
        if dedup and dedup[-1].t == b.t:
            continue
        dedup.append(b)
    return dedup


def resample(bars: list[Bar], tf_min: int) -> list[Bar]:
    out: list[Bar] = []
    for b in bars:
        minutes = b.t.hour * 60 + b.t.minute
        start = b.t.replace(hour=0, minute=0) + timedelta(
            minutes=(minutes // tf_min) * tf_min
        )
        if out and out[-1].t == start:
            x = out[-1]
            x.h, x.l, x.c = max(x.h, b.h), min(x.l, b.l), b.c
        else:
            out.append(Bar(start, b.o, b.h, b.l, b.c))
    return out


# ----------------------------------------------------------------------------- indicators (MT5-like)


def ema(vals: list[float], n: int) -> list[float]:
    k = 2.0 / (n + 1)
    out, prev = [], vals[0]
    for v in vals:
        prev = v * k + prev * (1 - k)
        out.append(prev)
    return out


def atr_sma(bars: list[Bar], n: int) -> list[float]:
    # MT5 iATR = simple moving average of True Range
    tr = []
    for i, b in enumerate(bars):
        pc = bars[i - 1].c if i else b.c
        tr.append(max(b.h - b.l, abs(b.h - pc), abs(b.l - pc)))
    out, s = [], 0.0
    for i, v in enumerate(tr):
        s += v
        if i >= n:
            s -= tr[i - n]
        out.append(s / min(i + 1, n))
    return out


def rsi_wilder(closes: list[float], n: int) -> list[float]:
    out = [50.0]
    ag = al = 0.0
    for i in range(1, len(closes)):
        d = closes[i] - closes[i - 1]
        g, lo = max(d, 0.0), max(-d, 0.0)
        if i <= n:
            ag += g / n
            al += lo / n
        else:
            ag = (ag * (n - 1) + g) / n
            al = (al * (n - 1) + lo) / n
        out.append(100.0 if al == 0 else 100.0 - 100.0 / (1 + ag / al))
    return out


def adx_mt5(bars: list[Bar], n: int) -> list[float]:
    # MT5 iADX: EMA-smoothed +DI/-DI (on DM/TR ratios), ADX = EMA of DX
    k = 2.0 / (n + 1)
    pdi = mdi = adx = 0.0
    out = [0.0]
    for i in range(1, len(bars)):
        b, p = bars[i], bars[i - 1]
        up, dn = b.h - p.h, p.l - b.l
        pdm = up if (up > dn and up > 0) else 0.0
        mdm = dn if (dn > up and dn > 0) else 0.0
        tr = max(b.h - b.l, abs(b.h - p.c), abs(b.l - p.c))
        pp = 100 * pdm / tr if tr else 0.0
        mm = 100 * mdm / tr if tr else 0.0
        pdi = pp * k + pdi * (1 - k)
        mdi = mm * k + mdi * (1 - k)
        dx = 100 * abs(pdi - mdi) / (pdi + mdi) if (pdi + mdi) else 0.0
        adx = dx * k + adx * (1 - k)
        out.append(adx)
    return out


# ----------------------------------------------------------------------------- simulation


@dataclass
class Trade:
    side: int
    entry_t: datetime
    entry: float
    sl: float
    tp: float
    r_dist: float
    risk_money: float
    exit_t: datetime | None = None
    exit: float = 0.0
    reason: str = ""
    r_mult: float = 0.0


def run(bars: list[Bar], sample: dict, p: Params, spread: float) -> dict:
    off = timedelta(hours=sample["gmt_offset"])
    reg = resample(bars, sample["regime_tf_min"])
    closes = [b.c for b in bars]
    e_sig = ema(closes, p.ema_signal)
    a_sig = atr_sma(bars, p.atr_period)
    r_sig = rsi_wilder(closes, p.rsi_period)
    rc = [b.c for b in reg]
    e_f, e_s, adx = (
        ema(rc, p.ema_fast_regime),
        ema(rc, p.ema_slow_regime),
        adx_mt5(reg, p.adx_period),
    )
    reg_tf = timedelta(minutes=sample["regime_tf_min"])

    warm_reg = p.ema_slow_regime + p.slope_bars + 5
    warm_sig = max(p.atr_avg_bars, p.pullback_bars, p.ema_signal * 3) + 2

    equity = peak = 10_000.0
    curve = [equity]
    trades: list[Trade] = []
    pos: Trade | None = None
    pos_bars = 0
    day_key = None
    day_start_eq = equity
    day_trades = 0
    killed = False
    ri = -1  # index of last *closed* regime bar
    blocked = {"session": 0, "spread": 0, "vol": 0, "day_limit": 0}

    def close_pos(t: Trade, price: float, when: datetime, why: str) -> None:
        nonlocal equity, peak
        pnl_price = (price - t.entry) * t.side
        t.exit, t.exit_t, t.reason = price, when, why
        t.r_mult = pnl_price / t.r_dist
        equity += t.risk_money * t.r_mult
        peak = max(peak, equity)
        trades.append(t)

    for i in range(1, len(bars) - 1):
        b = bars[i]  # bar i has just CLOSED; we act at open of bar i+1
        nxt = bars[i + 1]
        gmt_next = nxt.t - off

        # --- manage open position through bar i+1 (SL first = pessimistic)
        # (we manage here using bar i's data then fill new entries on nxt open)
        if pos is not None:
            pos_bars += 1
            hi_bid, lo_bid = b.h, b.l
            hi_ask, lo_ask = b.h + spread, b.l + spread
            if pos.side > 0:
                if lo_bid <= pos.sl:
                    close_pos(pos, min(pos.sl, b.o), b.t, "sl")
                    pos = None
                elif hi_bid >= pos.tp:
                    close_pos(pos, pos.tp, b.t, "tp")
                    pos = None
            else:
                if hi_ask >= pos.sl:
                    close_pos(pos, max(pos.sl, b.o + spread), b.t, "sl")
                    pos = None
                elif lo_ask <= pos.tp:
                    close_pos(pos, pos.tp, b.t, "tp")
                    pos = None
            if pos is not None:
                # end-of-bar management: BE, trailing, time exit, Friday close
                atr = a_sig[i]
                px = b.c if pos.side > 0 else b.c + spread
                gain_r = (px - pos.entry) * pos.side / pos.r_dist
                if gain_r >= p.be_trigger_r:
                    be = pos.entry + pos.side * p.be_buffer_r * pos.r_dist
                    if (be - pos.sl) * pos.side > 0:
                        pos.sl = be
                if gain_r >= p.trail_start_r:
                    tr = px - pos.side * p.trail_atr * atr
                    if (tr - pos.sl) * pos.side > 0:
                        pos.sl = tr
                gmt_now = nxt.t - off
                fri_close = (
                    gmt_now.weekday() == 4 and gmt_now.hour >= p.friday_close_gmt
                )
                if pos_bars >= p.max_bars_in_trade or fri_close:
                    exit_px = nxt.o if pos.side > 0 else nxt.o + spread
                    close_pos(
                        pos, exit_px, nxt.t, "time" if not fri_close else "friday"
                    )
                    pos = None
        curve.append(equity)
        if equity <= peak * (1 - p.kill_dd_pct / 100):
            killed = True

        # --- day bookkeeping (server day of the bar we would enter on)
        dk = nxt.t.date()
        if dk != day_key:
            day_key, day_start_eq, day_trades = dk, equity, 0

        # --- regime index: last regime bar fully closed by nxt.t
        while ri + 1 < len(reg) and reg[ri + 1].t + reg_tf <= nxt.t:
            ri += 1
        if killed or pos is not None or i < warm_sig or ri < warm_reg:
            continue

        # --- filters
        h = gmt_next.hour
        if (
            not (p.session_start_gmt <= h < p.session_end_gmt)
            or (gmt_next.weekday() == 4 and h >= p.friday_last_entry_gmt)
            or gmt_next.weekday() >= 5
        ):
            blocked["session"] += 1
            continue
        if day_trades >= p.max_trades_day or equity <= day_start_eq * (
            1 - p.daily_loss_pct / 100
        ):
            blocked["day_limit"] += 1
            continue
        atr = a_sig[i]
        if atr <= 0:
            continue
        if spread > p.max_spread_atr * atr:
            blocked["spread"] += 1
            continue
        avg_atr = sum(a_sig[i - p.atr_avg_bars + 1 : i + 1]) / p.atr_avg_bars
        ratio = atr / avg_atr if avg_atr > 0 else 0
        if not (p.vol_ratio_min <= ratio <= p.vol_ratio_max):
            blocked["vol"] += 1
            continue

        # --- regime (closed regime bar ri, slope vs ri - slope_bars)
        rcl = rc[ri]
        bull = (
            rcl > e_f[ri] > e_s[ri]
            and e_f[ri] > e_f[ri - p.slope_bars]
            and adx[ri] >= p.adx_min
        )
        bear = (
            rcl < e_f[ri] < e_s[ri]
            and e_f[ri] < e_f[ri - p.slope_bars]
            and adx[ri] >= p.adx_min
        )
        if not (bull or bear):
            continue

        win = range(i - p.pullback_bars + 1, i + 1)
        side = 0
        if bull:
            touched = min(bars[j].l - e_sig[j] for j in win) <= p.touch_atr * atr
            trig = (
                b.c > e_sig[i]
                and b.c > bars[i - 1].h
                and r_sig[i] > 50
                and (b.c - e_sig[i]) <= p.max_chase_atr * atr
            )
            if touched and trig:
                side = 1
        if bear and side == 0:
            touched = min(e_sig[j] - bars[j].h for j in win) <= p.touch_atr * atr
            trig = (
                b.c < e_sig[i]
                and b.c < bars[i - 1].l
                and r_sig[i] < 50
                and (e_sig[i] - b.c) <= p.max_chase_atr * atr
            )
            if touched and trig:
                side = -1
        if side == 0:
            continue

        # --- order construction (fill at next open; buy at ask, sell at bid)
        entry = nxt.o + spread if side > 0 else nxt.o
        if side > 0:
            swing = min(bars[j].l for j in win)
            raw = entry - (swing - p.sl_buffer_atr * atr)
        else:
            swing = max(bars[j].h for j in win)
            raw = (swing + p.sl_buffer_atr * atr) - entry
        r_dist = min(max(raw, p.sl_min_atr * atr), p.sl_max_atr * atr)
        sl = entry - side * r_dist
        tp = entry + side * p.tp_rr * r_dist
        pos = Trade(side, nxt.t, entry, sl, tp, r_dist, equity * p.risk_pct / 100)
        pos_bars = 0
        day_trades += 1

    if pos is not None:
        last = bars[-1]
        close_pos(pos, last.c if pos.side > 0 else last.c + spread, last.t, "eod")

    return summarize(trades, curve, bars, blocked, killed)


def summarize(
    trades: list[Trade],
    curve: list[float],
    bars: list[Bar],
    blocked: dict,
    killed: bool,
) -> dict:
    rs = [t.r_mult for t in trades]
    wins = [r for r in rs if r > 0]
    losses = [r for r in rs if r <= 0]
    gp, gl = sum(wins), -sum(losses)
    peak, mdd = curve[0], 0.0
    for v in curve:
        peak = max(peak, v)
        mdd = max(mdd, (peak - v) / peak)
    reasons: dict[str, int] = {}
    for t in trades:
        reasons[t.reason] = reasons.get(t.reason, 0) + 1
    return {
        "bars": len(bars),
        "from": bars[0].t.isoformat(sep=" "),
        "to": bars[-1].t.isoformat(sep=" "),
        "trades": len(trades),
        "longs": sum(1 for t in trades if t.side > 0),
        "shorts": sum(1 for t in trades if t.side < 0),
        "win_rate_pct": round(100 * len(wins) / len(rs), 1) if rs else 0.0,
        "profit_factor": round(gp / gl, 2) if gl > 0 else (math.inf if gp > 0 else 0.0),
        "expectancy_r": round(sum(rs) / len(rs), 3) if rs else 0.0,
        "net_return_pct": round(100 * (curve[-1] / curve[0] - 1), 2),
        "max_dd_pct": round(100 * mdd, 2),
        "exit_reasons": reasons,
        "blocked_bars": blocked,
        "kill_switch_hit": killed,
    }


# ----------------------------------------------------------------------------- CLI


def fmt_row(name: str, r: dict) -> str:
    pf = "inf" if r["profit_factor"] == math.inf else f"{r['profit_factor']:.2f}"
    return (
        f"| {name} | {r['trades']} ({r['longs']}L/{r['shorts']}S) | {r['win_rate_pct']:.1f}% | {pf} | "
        f"{r['expectancy_r']:+.3f} | {r['net_return_pct']:+.2f}% | {r['max_dd_pct']:.2f}% |"
    )


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument(
        "--stress", action="store_true", help="spread x1.5 and +/-1 step neighbourhood"
    )
    ap.add_argument("--json", help="write results JSON to this path")
    args = ap.parse_args()

    base = Params()
    variants: list[tuple[str, Params, float]] = [("default", base, 1.0)]
    if args.stress:
        variants += [
            ("spread x1.5", base, 1.5),
            ("pullback_bars 4", replace(base, pullback_bars=4), 1.0),
            ("pullback_bars 8", replace(base, pullback_bars=8), 1.0),
            ("tp_rr 1.5", replace(base, tp_rr=1.5), 1.0),
            ("tp_rr 2.5", replace(base, tp_rr=2.5), 1.0),
            ("adx_min 15", replace(base, adx_min=15.0), 1.0),
            ("adx_min 25", replace(base, adx_min=25.0), 1.0),
        ]

    results: dict = {"params": asdict(base), "samples": {}}
    header = "| variant | trades | win | PF | exp (R) | net | maxDD |\n|---|---|---|---|---|---|---|"
    for s in SAMPLES:
        try:
            bars = parse(s, fetch(s))
        except Exception as exc:  # noqa: BLE001
            print(f"[skip] {s['id']}: {exc}", file=sys.stderr)
            continue
        print(
            f"\n### {s['id']}  ({len(bars)} bars, {bars[0].t:%Y-%m-%d} .. {bars[-1].t:%Y-%m-%d}, "
            f"signal M{s['tf_min']} / regime M{s['regime_tf_min']}, spread {s['spread']}, GMT+{s['gmt_offset']} inferred)"
        )
        print(header)
        results["samples"][s["id"]] = {"meta": {k: v for k, v in s.items()}, "runs": {}}
        for name, p, mult in variants:
            r = run(bars, s, p, s["spread"] * mult)
            results["samples"][s["id"]]["runs"][name] = r
            print(fmt_row(name, r))
        d = results["samples"][s["id"]]["runs"]["default"]
        print(
            f"exit reasons: {d['exit_reasons']} | bars blocked by filter: {d['blocked_bars']}"
        )

    runs = [v["runs"]["default"] for v in results["samples"].values()]
    n = sum(r["trades"] for r in runs)
    if n:
        exp = sum(r["expectancy_r"] * r["trades"] for r in runs) / n
        results["pooled_default"] = {"trades": n, "expectancy_r": round(exp, 3)}
        print(f"\npooled default: {n} trades, trade-weighted expectancy {exp:+.3f} R")

    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(results, fh, indent=2, default=str)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
