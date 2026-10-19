from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests" / "fixtures"))  # synth.py for fixtures

import pytest

from polymarket_arb.config import load_settings


@pytest.fixture(scope="session")
def settings():
    return load_settings()


@pytest.fixture
def tmp_db(tmp_path):
    return tmp_path / "state.sqlite"
