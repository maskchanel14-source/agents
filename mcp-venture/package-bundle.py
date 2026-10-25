#!/usr/bin/env python3
"""Create a clean Gumroad source bundle without node_modules, dist, or secrets."""
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "phase4" / "po-pilot-gumroad-bundle.zip"
INCLUDE = [
    ROOT / "po-pilot-mcp",
    ROOT / "phase4" / "n8n-templates",
    ROOT / "phase4" / "prompt-pack.md",
]
EXCLUDE_DIRS = {"node_modules", "dist", ".git", ".next", "coverage"}
EXCLUDE_NAMES = {".env", ".env.local", ".env.production"}

with ZipFile(OUT, "w", ZIP_DEFLATED) as zf:
    for item in INCLUDE:
        paths = [item] if item.is_file() else sorted(item.rglob("*"))
        for path in paths:
            if not path.is_file() or any(part in EXCLUDE_DIRS for part in path.parts):
                continue
            if path.name in EXCLUDE_NAMES or path.name.endswith(".log"):
                continue
            if "node_modules" in path.parts or "dist" in path.parts:
                continue
            zf.write(path, path.relative_to(ROOT))
print(f"Created {OUT} ({OUT.stat().st_size:,} bytes)")
