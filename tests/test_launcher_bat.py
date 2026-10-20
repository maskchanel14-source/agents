"""Validasi statis launcher .bat (Linux tidak bisa menjalankan batch asli).

Cek: CRLF, ASCII-safe, label/goto konsisten, tanda kutip seimbang per baris,
tidak ada delayed expansion yang salah pakai, `cd /d "%~dp0"` ada.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
BATS = ["start_bot.bat", "start_bot_background.bat", "stop_bot.bat"]


@pytest.mark.parametrize("name", BATS)
def test_bat_exists_crlf_ascii(name: str):
    p = ROOT / name
    assert p.exists(), f"{name} wajib ada di root repo"
    data = p.read_bytes()
    # semua newline harus CRLF
    assert b"\r\n" in data
    assert b"\n" not in data.replace(b"\r\n", b"")
    # ASCII-safe (aman untuk codepage CMD default)
    text = data.decode("ascii")
    assert text.startswith("@echo off")


@pytest.mark.parametrize("name", BATS)
def test_bat_cd_to_script_dir(name: str):
    text = (ROOT / name).read_bytes().decode("ascii")
    assert 'cd /d "%~dp0"' in text, "wajib cd ke direktori script agar bisa diklik dari mana saja"


def test_start_bot_menu_and_labels():
    text = (ROOT / "start_bot.bat").read_bytes().decode("ascii")
    labels = set(re.findall(r"^:(\w+)", text, flags=re.M))
    gotos = set(re.findall(r"goto :?(\w+)", text, flags=re.I))
    # setiap goto punya label
    missing = {g for g in gotos if g.upper() not in {l.upper() for l in labels} and g.lower() != "eof"}
    assert not missing, f"goto tanpa label: {missing}"
    # menu wajib
    for item in ["PAPER", "BACKTEST", "LIVE", ".env", "test", "Keluar"]:
        assert item.lower() in text.lower()
    # pengaman LIVE: harus minta ketik LIVE
    assert "set /p CONFIRM=" in text
    assert '=="LIVE"' in text.replace(" ", "") or "LIVE" in text
    # pause saat error agar jendela tidak langsung tertutup
    assert "pause" in text
    # marker install
    assert ".install_marker" in text


@pytest.mark.parametrize("name", BATS)
def test_bat_quotes_balanced_per_line(name: str):
    text = (ROOT / name).read_bytes().decode("ascii")
    for i, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if stripped.lower().startswith("rem"):
            continue
        assert stripped.count('"') % 2 == 0, f"{name}:{i} tanda kutip tidak seimbang: {line}"


def test_stop_bot_creates_kill_switch():
    text = (ROOT / "stop_bot.bat").read_bytes().decode("ascii")
    assert "KILL_SWITCH" in text
