"""Shared builders: a seeded book store + strategy context over the synthetic universe."""

from __future__ import annotations

from collections import Counter

from polymarket_arb.config import load_settings
from polymarket_arb.data.book_store import BookStore
from polymarket_arb.execution.book_view import PaperBookView
from polymarket_arb.runner import _register
from polymarket_arb.strategies.common import StrategyContext
from polymarket_arb.universe import build_universe
from tests.fixtures.synth import BASE_MS, initial_books, universe_events

NOW = BASE_MS + 500


def universe():
    settings = load_settings()
    return build_universe(universe_events(), max_assets=settings.data.max_assets)


def seeded(msgs=None, received=BASE_MS):
    """Return (store, uni) with the synthetic initial books applied at ``received``."""
    uni = universe()
    store = BookStore()
    _register(store, uni)
    for m in msgs if msgs is not None else initial_books(BASE_MS):
        store.apply_message(m, received)
    return store, uni


def ctx_for(store, now_ms: int = NOW, books=None):
    settings = load_settings()
    view = books if books is not None else PaperBookView(store)
    return StrategyContext(
        costs=settings.costs,
        thresholds=settings.thresholds,
        limits=settings.limits,
        books=view,
        now_ms=now_ms,
        stats=Counter(),
    )
