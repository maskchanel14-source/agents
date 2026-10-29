#!/usr/bin/env python3
"""Pre-send gate for Small Signal Studio outreach.

Wraps Harvey's deterministic gate (`vendor/harvey/harvey/gate.py`, MIT) and adds
the rules that live in Harvey's `prompts/writer.md` but that its own gate does
not check mechanically.

Harvey's gate catches: bad address, do-not-contact, subject length, the 220 word
hard ceiling, unrendered merge tags, banned spam phrases, more than one link,
missing postal address, HTML in the body.

This adds, from the same repo's writer rules: em dashes, the vague CTAs the rules
ban, opening with I or We, exclamation marks, number of questions, the 75 word
target for a first email, bullet or bold formatting, and tracking parameters on
links.

Usage:
    python3 pre_send_gate.py FILE.md          # audit a file of drafts
    python3 pre_send_gate.py --text "..."     # audit one body
    python3 pre_send_gate.py --selftest       # prove the checks fire
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "vendor" / "harvey"))

from harvey.gate import URL_RE, pre_send_check  # noqa: E402

# Targets from prompts/writer.md rule 10, and skills/email_frameworks.md
# ("Under 75 words for email 1").
WORD_TARGET = {"email1": 75, "email2": 75, "email3": 40, "followup": 40}
HARD_CEILING = 220  # Harvey's own MAX_BODY_WORDS

# Banned by prompts/writer.md rule 6 and by the "What Makes Bad Cold Email" list.
OPT_OUT_RE = re.compile(
    r'(?im)^.*\breply\s+["\u201c]?\s*(no thanks|stop|unsubscribe|remove|opt out).*$'
)

VAGUE_CTAS = (
    "worth a quick look", "worth a quick chat", "worth a quick call",
    "worth a look", "worth a conversation", "quick question",
    "let me know if you're interested", "let me know if interested",
)
# Rule 7.
WEAK_OPENERS = (
    "i'd love to", "i would love to", "just wanted to", "reaching out because",
    "just following up", "hope this finds you well", "hope you're doing well",
    "i know you're busy", "circling back", "no pressure", "no obligation",
)
# Rule 9 / formatting.
BULLET_RE = re.compile(r"^\s*(?:[-*+]\s|\d+[.)]\s)", re.MULTILINE)
BOLD_RE = re.compile(r"\*\*|__|\*[^*\n]+\*")
# Tracking parameters are the thing Harvey's data section says costs 8-12% of
# inbox placement. Not the same as a link, so it gets its own check.
TRACKING_RE = re.compile(r"[?&](?:utm_[a-z]+|src|ref|fbclid|gclid)=", re.IGNORECASE)


@dataclass
class Verdict:
    ok: bool
    reasons: list[str] = field(default_factory=list)
    words: int = 0
    links: int = 0
    questions: int = 0

    def line(self, label: str) -> str:
        mark = "PASS" if self.ok else "FAIL"
        detail = "; ".join(self.reasons) if self.reasons else "clean"
        return f"  [{mark}] {label}  ({self.words}w, {self.links} link, {self.questions}q)  {detail}"


def check(
    body: str,
    subject: str = "A subject",
    to_email: str = "someone@example.com",
    kind: str = "email1",
    postal_address: str = "",
    do_not_contact=(),
) -> Verdict:
    """Run Harvey's gate, then the writer-rule checks on top."""
    reasons: list[str] = []

    base = pre_send_check(
        to_email=to_email,
        subject=subject,
        body=body,
        kind="sequence",
        postal_address=postal_address,
        do_not_contact=do_not_contact,
    )
    reasons.extend(base.reasons)

    text = body or ""
    lowered = text.lower()
    words = len(text.split())
    links = URL_RE.findall(text)

    # The compliance opt-out is a device, not a CTA. Harvey's own default
    # (compliance.opt_out_line) is itself a question, so count questions on the
    # body with that line removed, or every compliant email fails rule 13.
    cta_text = OPT_OUT_RE.sub("", text)
    questions = cta_text.count("?")
    if kind != "followup" and not OPT_OUT_RE.search(text):
        reasons.append("no opt-out line (CAN-SPAM, Harvey compliance.opt_out_line)")

    # Harvey rule 1: never an em dash.
    if "\u2014" in text or "--" in text:
        reasons.append("em dash present (writer rule 1)")

    # Harvey rule 6 and the bad-email list.
    for phrase in VAGUE_CTAS:
        if phrase in lowered:
            reasons.append(f"vague CTA: '{phrase}'")
            break

    # Harvey rule 7.
    for phrase in WEAK_OPENERS:
        if phrase in lowered:
            reasons.append(f"weak opener: '{phrase}'")
            break

    # Harvey rule 8: start with them, not yourself.
    first = (text.strip().split() or [""])[0].strip(",.:;!").lower()
    if first in {"i", "we", "i'm", "we're", "our", "my"}:
        reasons.append("opens with I/We (writer rule 8)")

    # Harvey rule 9.
    if "!" in text:
        reasons.append("exclamation mark (writer rule 9)")

    # Harvey rule 13: exactly one question or CTA.
    if questions > 1:
        reasons.append(f"{questions} questions, exactly one allowed (writer rule 13)")

    # Rule 10: length target by position in the sequence.
    target = WORD_TARGET.get(kind, 75)
    if words > target:
        reasons.append(f"{words} words, target for {kind} is {target} (writer rule 10)")
    if words > HARD_CEILING:
        reasons.append(f"{words} words, over Harvey's hard ceiling of {HARD_CEILING}")

    # Harvey rules 5 and the formatting ban.
    if BULLET_RE.search(text):
        reasons.append("bullet or numbered list in a cold email (writer rule 5)")
    if BOLD_RE.search(text):
        reasons.append("bold or italic markup (writer rule 5)")

    # Deliverability: tracking parameters. Harvey's 2026 data section.
    if TRACKING_RE.search(text):
        reasons.append("tracking parameter in a link (costs 8-12% inbox placement)")

    return Verdict(ok=not reasons, reasons=reasons, words=words, links=len(links), questions=questions)


def parse_drafts(path: Path) -> list[tuple[str, str, str]]:
    """Read `## label | kind` headings followed by an optional Subject: line."""
    drafts: list[tuple[str, str, str]] = []
    label = kind = None
    subject = ""
    body: list[str] = []

    def flush():
        if label and "".join(body).strip():
            drafts.append((label, kind or "email1", f"Subject: {subject}\n\n" + "".join(body).strip()))

    for raw in path.read_text(encoding="utf-8").splitlines(keepends=True):
        if raw.startswith("## "):
            flush()
            head = raw[3:].strip()
            label, _, kind = head.partition("|")
            label, kind, subject, body = label.strip(), kind.strip() or "email1", "", []
            continue
        if label and raw.strip() in {"---", "***", "___"}:
            flush()
            label = kind = None
            subject = ""
            body = []
            continue
        if label and raw.lower().startswith("subject:"):
            subject = raw.split(":", 1)[1].strip()
            continue
        if label:
            body.append(raw)
    flush()
    return drafts


def audit(drafts, postal_address: str = "") -> int:
    failures = 0
    for label, kind, text in drafts:
        subject, _, body = text.partition("\n\n")
        subject = subject.split(":", 1)[1].strip() if ":" in subject else subject
        verdict = check(body, subject=subject, kind=kind, postal_address=postal_address)
        print(verdict.line(f"{label} [{kind}]"))
        failures += 0 if verdict.ok else 1
    print(f"\n{len(drafts)} drafts, {failures} failing, {len(drafts) - failures} clean")
    return 1 if failures else 0


def _rule_test() -> bool:
    import tempfile

    sample = (
        "## a | email1\nSubject: x\n\nFirst body.\n\n---\n\n## b | email1\nSubject: y\n\nSecond body.\n"
    )
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "d.md"
        path.write_text(sample, encoding="utf-8")
        drafts = parse_drafts(path)
    bodies = [text.partition("\n\n")[2] for _, _, text in drafts]
    return len(drafts) == 2 and not any("--" in b for b in bodies)


def selftest() -> int:
    opt = '\n\nNot interested? Reply "no thanks" and I won\'t email again.'
    good = "Hi Sam, your hiring guide asks whether an accountant understands Stocky. Since August it doesn't exist. Want the teardown?" + opt
    bad = "Hi, I hope this finds you well. We'd love to help. Worth a quick look? Also, is Thursday okay?"
    cases = [
        ("clean draft passes", check(good, kind="email1").ok, True),
        ("weak opener caught", any("weak opener" in r for r in check(bad).reasons), True),
        ("vague CTA caught", any("vague CTA" in r for r in check(bad).reasons), True),
        ("two questions caught", any("questions" in r for r in check(bad).reasons), True),
        ("em dash caught", any("em dash" in r for r in check("Hi. This is \u2014 wrong.").reasons), True),
        ("length target caught", any("target for email1" in r for r in check("word " * 90).reasons), True),
        ("tracking param caught", any("tracking parameter" in r for r in check("See https://x.test/a?src=abc here.").reasons), True),
        ("opens with I caught", any("opens with I/We" in r for r in check("I noticed your page.").reasons), True),
        # The opt-out question must not count as a second CTA.
        ("opt-out question exempt", check(good).ok, True),
        ("followup needs no footer", check("Hi Sam, one thing I left out: carton multiples." , kind="followup").ok, True),
        ("missing opt-out caught", any("no opt-out line" in r for r in check("Hi Sam, want the teardown?").reasons), True),
        # A markdown rule must not be swallowed into the body: it used to trip the
        # em dash check on the last draft of every file.
        ("markdown rule not body", _rule_test(), True),
    ]
    failed = 0
    for name, got, want in cases:
        mark = "ok" if got == want else "MISMATCH"
        print(f"  [{mark}] {name}: got {got}, want {want}")
        failed += 0 if got == want else 1
    print(f"\n{len(cases) - failed}/{len(cases)} self-tests pass")
    return 1 if failed else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("file", nargs="?", help="markdown file of drafts")
    ap.add_argument("--text", help="audit a single body")
    ap.add_argument("--kind", default="email1", choices=sorted(WORD_TARGET))
    ap.add_argument("--subject", default="A subject")
    ap.add_argument("--postal", default="", help="postal address that must appear")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return selftest()
    if args.text:
        v = check(args.text, subject=args.subject, kind=args.kind, postal_address=args.postal)
        print(v.line("inline text"))
        return 0 if v.ok else 1
    if args.file:
        return audit(parse_drafts(Path(args.file)), postal_address=args.postal)
    ap.error("give a file, --text, or --selftest")
    return 2


if __name__ == "__main__":
    sys.exit(main())
