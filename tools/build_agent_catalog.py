#!/usr/bin/env python3
"""Build AGENT_CATALOG.json from agent source files.

Scans ``agents/*.md`` (if present) and ``plugins/*/agents/*.md``, parses the
YAML frontmatter (stdlib only, no PyYAML needed) and emits one entry per agent
file with a coarse category, a one-liner, and a "when to use" hint.

Usage:
    python3 tools/build_agent_catalog.py            # writes AGENT_CATALOG.json
    python3 tools/build_agent_catalog.py --check    # exit 1 if file is stale
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "AGENT_CATALOG.json"

CATEGORIES = (
    "trading",
    "coding",
    "frontend",
    "backend",
    "security",
    "marketing",
    "data",
    "devops",
    "docs",
    "business",
)

# Explicit agent-name -> category map. Names are the frontmatter ``name``
# (falls back to file stem). Anything unmapped falls back to PLUGIN_CATEGORY.
NAME_CATEGORY: dict[str, str] = {
    # trading
    "quant-analyst": "trading",
    "risk-manager": "trading",
    # frontend / design / mobile
    "accessibility-expert": "frontend",
    "design-system-architect": "frontend",
    "flutter-expert": "frontend",
    "frontend-developer": "frontend",
    "ios-developer": "frontend",
    "mobile-developer": "frontend",
    "ui-designer": "frontend",
    "ui-ux-designer": "frontend",
    "ui-visual-validator": "frontend",
    "gallery-researcher": "frontend",
    "image-generator": "frontend",
    "prompt-crafter": "frontend",
    "playwright": "frontend",
    # backend
    "backend-architect": "backend",
    "django-pro": "backend",
    "fastapi-pro": "backend",
    "graphql-architect": "backend",
    "dotnet-architect": "backend",
    "event-sourcing-architect": "backend",
    "temporal-python-pro": "backend",
    "payment-integration": "backend",
    "blockchain-developer": "backend",
    "database-architect": "backend",
    "database-optimizer": "backend",
    "database-admin": "backend",
    # security
    "backend-security-coder": "security",
    "frontend-security-coder": "security",
    "mobile-security-coder": "security",
    "security-auditor": "security",
    "threat-modeling-expert": "security",
    "malware-analyst": "security",
    "reverse-engineer": "security",
    "firmware-analyst": "security",
    "policy-enforcer": "security",
    "receipt-verifier": "security",
    "review-policy-author": "security",
    # marketing
    "content-marketer": "marketing",
    "search-specialist": "marketing",
    "sales-automator": "marketing",
    "social-publishing-publisher": "marketing",
    # data / ML / AI
    "data-engineer": "data",
    "data-scientist": "data",
    "ml-engineer": "data",
    "mlops-engineer": "data",
    "ai-engineer": "data",
    "prompt-engineer": "data",
    "vector-database-engineer": "data",
    "sql-pro": "data",
    "llm-finetuning-architect": "data",
    "llm-finetuning-eval-engineer": "data",
    "llm-finetuning-training-engineer": "data",
    "julia-pro": "data",
    # devops / infra / ops
    "cloud-architect": "devops",
    "deployment-engineer": "devops",
    "devops-troubleshooter": "devops",
    "kubernetes-architect": "devops",
    "terraform-specialist": "devops",
    "hybrid-cloud-architect": "devops",
    "network-engineer": "devops",
    "observability-engineer": "devops",
    "service-mesh-expert": "devops",
    "incident-responder": "devops",
    "dgx-spark-ops-engineer": "devops",
    "deploy-with-verification": "devops",
    "prod-logs-health-check": "devops",
    "session-start": "devops",
    "session-end": "devops",
    "bash-pro": "devops",
    "posix-shell-pro": "devops",
    "performance-engineer": "devops",
    # docs
    "api-documenter": "docs",
    "c4-code": "docs",
    "c4-component": "docs",
    "c4-container": "docs",
    "c4-context": "docs",
    "docs-architect": "docs",
    "mermaid-expert": "docs",
    "reference-builder": "docs",
    "tutorial-engineer": "docs",
    "pptx-deck-creation-builder": "docs",
    # business
    "business-analyst": "business",
    "startup-analyst": "business",
    "hr-pro": "business",
    "legal-advisor": "business",
    "customer-support": "business",
}

# Plugin -> category fallback for agents not covered above.
PLUGIN_CATEGORY: dict[str, str] = {
    "seo-analysis-monitoring": "marketing",
    "seo-content-creation": "marketing",
    "seo-technical-optimization": "marketing",
    "content-marketing": "marketing",
    "quantitative-trading": "trading",
}


def parse_frontmatter(text: str) -> dict[str, str]:
    """Minimal YAML frontmatter parser for flat key/value pairs.

    Supports plain scalars, quoted scalars and folded/literal block scalars
    (``>``, ``>-``, ``|``, ``|-``). Good enough for agent frontmatter.
    """
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not m:
        return {}
    lines = m.group(1).splitlines()
    data: dict[str, str] = {}
    i = 0
    while i < len(lines):
        line = lines[i]
        km = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if not km:
            i += 1
            continue
        key, val = km.group(1), km.group(2).strip()
        if val in (">", ">-", "|", "|-", ">+", "|+"):
            block: list[str] = []
            i += 1
            while i < len(lines) and (
                lines[i].startswith((" ", "\t")) or not lines[i].strip()
            ):
                block.append(lines[i].strip())
                i += 1
            sep = "\n" if val.startswith("|") else " "
            data[key] = sep.join(b for b in block if b).strip()
            continue
        if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
            val = val[1:-1]
        data[key] = val
        i += 1
    return data


def split_sentences(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z\"(])", text)
    return [p.strip() for p in parts if p.strip()]


USE_RE = re.compile(
    r"\b(use (?:proactively|this agent|it|when|for|after|at|during|before|to)|"
    r"delegates? here|invoke (?:for|when)|use\b)",
    re.IGNORECASE,
)


def derive_fields(desc: str, body: str) -> tuple[str, str]:
    sentences = split_sentences(desc)
    one_liner = sentences[0] if sentences else ""
    when = ""
    for s in sentences:
        if USE_RE.search(s) and s is not one_liner:
            when = s
            break
    if not when and sentences and USE_RE.search(sentences[0]):
        when = sentences[0]
    if not when:
        # Fall back to the body's first "When"/"Use" bullet or heading content.
        bm = re.search(
            r"(?im)^#+\s*(when to use|use this agent when)[^\n]*\n+(.+?)(?:\n#|\Z)",
            body,
            re.DOTALL,
        )
        if bm:
            first = [
                ln.strip("-* ").strip() for ln in bm.group(2).splitlines() if ln.strip()
            ]
            if first:
                when = "Use when: " + first[0]
    if not when:
        rest = (" ".join(sentences[1:2]) or one_liner).rstrip(".")
        if rest:
            rest = rest[0].lower() + rest[1:]
        when = "Use when you need an agent that " + rest + "."
    return one_liner, when


def categorize(name: str, plugin: str) -> str:
    if name in NAME_CATEGORY:
        return NAME_CATEGORY[name]
    # Duplicate agents are namespaced as "<plugin>-<agent>" in frontmatter.
    base = name[len(plugin) + 1 :] if plugin and name.startswith(plugin + "-") else name
    if base in NAME_CATEGORY:
        return NAME_CATEGORY[base]
    if plugin in PLUGIN_CATEGORY:
        return PLUGIN_CATEGORY[plugin]
    if name.startswith("seo-"):
        return "marketing"
    return "coding"


def collect() -> list[dict[str, str]]:
    files = sorted(ROOT.glob("agents/*.md")) + sorted(
        ROOT.glob("plugins/*/agents/*.md")
    )
    entries: list[dict[str, str]] = []
    for f in files:
        text = f.read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        body = text.split("---", 2)[-1] if text.startswith("---") else text
        name = fm.get("name") or f.stem
        rel = f.relative_to(ROOT).as_posix()
        plugin = f.parts[-3] if rel.startswith("plugins/") else ""
        one_liner, when = derive_fields(fm.get("description", ""), body)
        entries.append(
            {
                "name": name,
                "category": categorize(name, plugin),
                "one_liner": one_liner,
                "when_to_use": when,
                "plugin": plugin,
                "model": fm.get("model", "inherit"),
                "path": rel,
            }
        )
    entries.sort(
        key=lambda e: (CATEGORIES.index(e["category"]), e["name"], e["plugin"])
    )
    return entries


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--check", action="store_true", help="fail if AGENT_CATALOG.json is stale"
    )
    args = ap.parse_args()
    entries = collect()
    payload = json.dumps(entries, indent=2, ensure_ascii=False) + "\n"
    if args.check:
        current = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        if current != payload:
            print(
                "AGENT_CATALOG.json is stale; run tools/build_agent_catalog.py",
                file=sys.stderr,
            )
            return 1
        return 0
    OUT.write_text(payload, encoding="utf-8")
    counts: dict[str, int] = {}
    for e in entries:
        counts[e["category"]] = counts.get(e["category"], 0) + 1
    print(
        f"wrote {OUT.name}: {len(entries)} agents ({len({e['name'] for e in entries})} unique names)"
    )
    for c in CATEGORIES:
        print(f"  {c:10s} {counts.get(c, 0)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
