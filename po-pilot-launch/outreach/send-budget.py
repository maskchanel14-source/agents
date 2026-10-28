#!/usr/bin/env python3
"""Enforce the sending policy in SENDING-POLICY.md.

The ledger is the single source of truth for what has gone out. Nothing here
talks to Gmail; it only decides whether a send is allowed and records it when
it happens.

Usage:
    python3 send-budget.py status
    python3 send-budget.py check                 # exit 1 when no budget left
    python3 send-budget.py record --to x@y.com --subject "..." --campaign partner
    python3 send-budget.py stop --reason "2 bounces" --days 3
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

LEDGER = Path(__file__).with_name("ledger.json")

# Phase table. Days are counted from the first recorded send.
PHASES = [
    # (from_day, to_day, max_per_day, min_gap_minutes, max_per_hour)
    # Amended 29 Oct 2026: owner asked for 20 in 24 hours. Phase 1 raised to 20
    # per day with a 3 minute gap and 15 per hour, which keeps the pacing smooth
    # rather than bursty. See SENDING-POLICY.md section 4.
    (1, 7, 20, 3, 15),
    (8, 14, 25, 3, 15),
    (15, 10_000, 30, 3, 15),
]
ABSOLUTE_DAILY_CEILING = 40
ABSOLUTE_HOURLY_CEILING = 15
MAX_PER_RECIPIENT_30D = 3
MAX_PER_DOMAIN_PER_WEEK = 1
STOP_AFTER_CONSECUTIVE_FAILURES = 4


def now() -> datetime:
    return datetime.now(timezone.utc)


def load() -> dict:
    if not LEDGER.exists():
        return {"sends": [], "stops": [], "failures": []}
    data = json.loads(LEDGER.read_text())
    data.setdefault("sends", [])
    data.setdefault("stops", [])
    data.setdefault("failures", [])
    return data


def save(data: dict) -> None:
    LEDGER.write_text(json.dumps(data, indent=2) + "\n")


def parse(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def first_send(data: dict) -> datetime | None:
    if not data["sends"]:
        return None
    return min(parse(s["ts"]) for s in data["sends"])


def phase_for(data: dict) -> tuple[int, int, int, int]:
    """Return (day_number, max_per_day, min_gap_minutes, max_per_hour)."""
    start = first_send(data)
    if start is None:
        day = 1
    else:
        day = (now() - start).days + 1
    for lo, hi, per_day, gap, per_hour in PHASES:
        if lo <= day <= hi:
            return day, per_day, gap, per_hour
    return day, PHASES[-1][2], PHASES[-1][3], PHASES[-1][4]


def active_stop(data: dict) -> dict | None:
    for stop in data["stops"]:
        if parse(stop["until"]) > now():
            return stop
    return None


def sent_between(data: dict, start: datetime, end: datetime) -> list[dict]:
    return [s for s in data["sends"] if start <= parse(s["ts"]) < end]


def domain_of(address: str) -> str:
    return address.rsplit("@", 1)[-1].lower()


def consecutive_failures(data: dict) -> int:
    count = 0
    for entry in reversed(data["failures"]):
        if entry.get("kind") == "failure":
            count += 1
        else:
            break
    return count


def verdict(to: str | None = None) -> tuple[bool, list[str]]:
    data = load()
    problems: list[str] = []
    notes: list[str] = []

    stop = active_stop(data)
    if stop:
        problems.append(f"hard stop until {stop['until']}: {stop['reason']}")

    if consecutive_failures(data) >= STOP_AFTER_CONSECUTIVE_FAILURES:
        problems.append(f"{consecutive_failures(data)} consecutive failures, stop for the day")

    day, per_day, gap, per_hour = phase_for(data)
    ceiling = min(per_day, ABSOLUTE_DAILY_CEILING)
    hour_ceiling = min(per_hour, ABSOLUTE_HOURLY_CEILING)

    last_24h = sent_between(data, now() - timedelta(hours=24), now())
    if len(last_24h) >= ceiling:
        problems.append(f"daily budget spent: {len(last_24h)}/{ceiling} in the last 24h")

    last_hour = sent_between(data, now() - timedelta(hours=1), now())
    if len(last_hour) >= hour_ceiling:
        problems.append(f"hourly budget spent: {len(last_hour)}/{hour_ceiling} in the last hour")

    if data["sends"]:
        last = max(parse(s["ts"]) for s in data["sends"])
        ready_at = last + timedelta(minutes=gap)
        if now() < ready_at:
            wait = int((ready_at - now()).total_seconds() // 60) + 1
            problems.append(f"gap not met: wait {wait} more minute(s)")

    if to:
        dom = domain_of(to)
        month = [s for s in data["sends"] if domain_of(s["to"]) == dom
                 and now() - parse(s["ts"]) < timedelta(days=30)]
        week = [s for s in month if now() - parse(s["ts"]) < timedelta(days=7)]

        same = [s for s in month if s["to"].lower() == to.lower()]
        if len(same) >= MAX_PER_RECIPIENT_30D:
            problems.append(f"{to} already got {len(same)} emails in 30 days (cap {MAX_PER_RECIPIENT_30D})")
        if week:
            problems.append(f"{dom} already contacted this week ({week[0]['to']})")

    notes.append(f"phase day {day}: {per_day}/day, {gap} min gap, {per_hour}/hour")
    notes.append(f"used today: {len(last_24h)}/{ceiling}, this hour: {len(last_hour)}/{hour_ceiling}")
    return (not problems), problems + notes


def cmd_status(_: argparse.Namespace) -> int:
    ok, lines = verdict()
    data = load()
    print(f"ledger: {LEDGER}")
    print(f"total sends: {len(data['sends'])}")
    print(f"allowed now: {'yes' if ok else 'no'}")
    for line in lines:
        print(f"  {line}")
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    ok, lines = verdict(args.to)
    for line in lines:
        print(f"  {line}")
    print("OK" if ok else "BLOCKED")
    return 0 if ok else 1


def cmd_record(args: argparse.Namespace) -> int:
    ok, lines = verdict(args.to)
    if not ok and not args.force:
        for line in lines:
            print(f"  {line}")
        print("refused. nothing recorded. use --force only if a human decided to override.")
        return 1
    data = load()
    data["sends"].append(
        {
            "ts": now().isoformat(timespec="seconds").replace("+00:00", "Z"),
            "to": args.to,
            "domain": domain_of(args.to),
            "subject": args.subject or "",
            "campaign": args.campaign or "unlabelled",
            "message_id": args.message_id or "",
        }
    )
    save(data)
    print(f"recorded: {args.to}")
    return 0


def cmd_fail(args: argparse.Namespace) -> int:
    data = load()
    data["failures"].append(
        {
            "ts": now().isoformat(timespec="seconds").replace("+00:00", "Z"),
            "kind": "ok" if args.ok else "failure",
            "detail": args.detail or "",
        }
    )
    save(data)
    print("failure logged" if not args.ok else "success logged")
    return 0


def cmd_stop(args: argparse.Namespace) -> int:
    data = load()
    until = now() + timedelta(days=args.days)
    data["stops"].append(
        {
            "ts": now().isoformat(timespec="seconds").replace("+00:00", "Z"),
            "until": until.isoformat(timespec="seconds").replace("+00:00", "Z"),
            "reason": args.reason,
        }
    )
    save(data)
    print(f"stopped until {until.date()} : {args.reason}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("status", help="show budget and phase").set_defaults(func=cmd_status)

    check = sub.add_parser("check", help="exit 1 if a send is not allowed")
    check.add_argument("--to", help="address you intend to email")
    check.set_defaults(func=cmd_check)

    record = sub.add_parser("record", help="log a send after it went out")
    record.add_argument("--to", required=True)
    record.add_argument("--subject", default="")
    record.add_argument("--campaign", default="")
    record.add_argument("--message-id", default="")
    record.add_argument("--force", action="store_true")
    record.set_defaults(func=cmd_record)

    fail = sub.add_parser("fail", help="log a delivery failure or a success, for stop rules")
    fail.add_argument("--ok", action="store_true")
    fail.add_argument("--detail", default="")
    fail.set_defaults(func=cmd_fail)

    stop = sub.add_parser("stop", help="record a hard stop")
    stop.add_argument("--reason", required=True)
    stop.add_argument("--days", type=int, default=1)
    stop.set_defaults(func=cmd_stop)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
