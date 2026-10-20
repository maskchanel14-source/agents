"""Ambil screenshot dashboard dengan headless browser (Playwright).

Jalankan di mesin yang punya browser (Windows / CI), SETELAH bot berjalan:

    python -m bot --mode paper --no-open-browser
    python scripts/take_screenshots.py --url http://127.0.0.1:8788/

Output: docs/screenshots/overview-<size>.png, scanner-<size>.png, dst.

Dependency: pip install playwright && playwright install chromium
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

SIZES = {
    "desktop": (1920, 1080),
    "laptop": (1366, 768),
    "wide": (2560, 1080),
}


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--url", default="http://127.0.0.1:8788/")
    p.add_argument("--out", default=str(Path(__file__).resolve().parents[1] / "docs" / "screenshots"))
    args = p.parse_args(argv)

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Playwright belum terpasang: pip install playwright && playwright install chromium")
        return 1

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    errors: list[str] = []

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        for name, (w, h) in SIZES.items():
            page = browser.new_page(viewport={"width": w, "height": h})
            page.on("console", lambda msg: errors.append(f"[{name}] console.{msg.type}: {msg.text}")
                    if msg.type == "error" else None)
            page.on("pageerror", lambda exc: errors.append(f"[{name}] pageerror: {exc}"))
            page.goto(args.url, wait_until="networkidle")
            # skip boot sequence bila masih tampil
            skip = page.locator("#boot-skip")
            if skip.count() and skip.is_visible():
                skip.click()
            page.wait_for_timeout(1500)
            page.screenshot(path=str(out / f"overview-{name}.png"))
            # tab scanner
            page.click('button[data-tab="scanner"]')
            page.wait_for_timeout(600)
            page.screenshot(path=str(out / f"scanner-{name}.png"))
            # tab risk
            page.click('button[data-tab="risk"]')
            page.wait_for_timeout(400)
            page.screenshot(path=str(out / f"risk-{name}.png"))
            page.close()
        browser.close()

    print(f"Screenshot tersimpan di {out}")
    if errors:
        print("ERROR console terdeteksi:")
        for e in errors:
            print(" -", e)
        return 2
    print("Tidak ada error console.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
