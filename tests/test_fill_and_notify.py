"""Test FillModel (probabilitas fill paper trading) + Notifier (Telegram/Discord)."""

from __future__ import annotations

import asyncio
import random

from bot.decimal_utils import D
from bot.execution.fill_model import FillModel, FillModelConfig
from bot.models import OrderBookSnapshot, WalkFill

NOW = 1_792_464_000_000


def book(ask_size="100", recv_ms=NOW):
    return OrderBookSnapshot.from_levels("a1", [], [("0.50", ask_size)], ts_ms=NOW, recv_ms=recv_ms)


def walk(req="10", filled="10", price="0.50"):
    f = D(filled)
    return WalkFill(
        requested_shares=D(req), filled_shares=f,
        notional=f * D(price), avg_price=D(price),
        levels_used=((D(price), f),), fully_filled=True,
    )


# ---------------------------------------------------------------- fill model --

def test_leg_prob_small_order_fresh_book_high():
    m = FillModel()
    p = m.leg_fill_probability(book(), walk("10"), now_ms=NOW)
    # 0.95 - 0.5*(10/100) - 0 - 0.00005*350 = 0.8825
    assert p == D("0.8825")


def test_leg_prob_full_depth_and_staleness_decay():
    m = FillModel()
    p_small = m.leg_fill_probability(book(), walk("10"), now_ms=NOW)
    p_big = m.leg_fill_probability(book(), walk("100"), now_ms=NOW)
    assert p_big < p_small  # makin besar relatif ke depth, makin kecil peluang
    p_stale = m.leg_fill_probability(book(), walk("10"), now_ms=NOW + 1000)
    assert p_stale < p_small  # data basi menambah risiko harga bergerak
    # staleness ekstrem -> ter-clamp ke min_fill_prob
    p_dead = m.leg_fill_probability(book(recv_ms=NOW - 10**7), walk("100"), now_ms=NOW)
    assert p_dead == m.cfg.min_fill_prob


def test_leg_prob_edge_cases():
    m = FillModel()
    assert m.leg_fill_probability(book(), walk("0", "0"), now_ms=NOW) == D(0)  # request 0
    p_empty = m.leg_fill_probability(OrderBookSnapshot.from_levels("a1", [], [], ts_ms=NOW, recv_ms=NOW), walk(), now_ms=NOW)
    # book kosong -> depth_frac=1 (penalti maksimum): 0.95-0.5-0.0175
    assert p_empty == D("0.4325")
    assert p_empty < m.leg_fill_probability(book(), walk("10"), now_ms=NOW)
    # hasil selalu dalam [min, 1]
    for ms in (0, 100, 5000):
        p = m.leg_fill_probability(book(), walk("100"), now_ms=NOW + ms)
        assert m.cfg.min_fill_prob <= p <= D(1)


def test_bundle_prob_is_product_of_legs():
    m = FillModel()
    legs = [(book(), walk("10")), (book(), walk("10"))]
    p1 = m.leg_fill_probability(book(), walk("10"), now_ms=NOW)
    pb = m.bundle_fill_probability(legs, now_ms=NOW)
    assert pb == max(m.cfg.min_fill_prob, p1 * p1)
    assert pb < p1  # bundle selalu lebih sulit dari leg tunggal
    assert m.bundle_fill_probability([], now_ms=NOW) == D(1)  # tidak ada leg -> pasti


def test_from_config_overrides():
    cfg = FillModelConfig.from_config(
        {"base_fill_prob": "0.8", "latency_penalty_per_ms": "0.001"}, latency_ms=100
    )
    assert cfg.base_fill_prob == D("0.8") and cfg.latency_ms == 100
    m = FillModel(cfg)
    # 0.8 - 0.5*0.1 - 0 - 0.001*100 = 0.65
    assert m.leg_fill_probability(book(), walk("10"), now_ms=NOW) == D("0.65")


def test_simulate_partial_deterministic_with_seed():
    m = FillModel()
    w = walk("100", "100")
    # rng selalu "beruntung" (random < p) -> fill penuh apa adanya
    class Lucky:
        def random(self): return 0.0
        def uniform(self, a, b): return 1.0
    assert m.simulate_partial(w, D("0.9"), Lucky()) is w

    # rng selalu "sial" -> partial: filled menyusut proporsional, notional konsisten
    class Unlucky:
        def random(self): return 0.999
        def uniform(self, a, b): return 0.25
    out = m.simulate_partial(w, D("0.9"), Unlucky())
    assert not out.fully_filled
    assert out.filled_shares == D("25")  # 100 * 0.25
    assert out.notional == out.avg_price * out.filled_shares
    assert out.requested_shares == w.requested_shares
    assert out.shortfall_shares == D("75")

    # seed nyata: hasil reproducible
    a = m.simulate_partial(w, D("0.5"), random.Random(42))
    b = m.simulate_partial(w, D("0.5"), random.Random(42))
    assert a.filled_shares == b.filled_shares


# ------------------------------------------------------------------ notifier --

class _FakeResp:
    def __init__(self, status):
        self.status = status

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False


class _FakeSession:
    def __init__(self, status=200, boom=False):
        self.status = status
        self.boom = boom
        self.posts = []

    def post(self, url, json=None):
        self.posts.append((url, json))
        if self.boom:
            raise RuntimeError("network down")
        return _FakeResp(self.status)


def test_notifier_sends_telegram_and_discord():
    from bot.monitoring.notify import Notifier

    async def run():
        sess = _FakeSession(200)
        n = Notifier(enabled=True, telegram_token="tok", telegram_chat_id="42",
                     discord_webhook="https://discord/hook", session=sess)
        assert n.enabled
        assert await n.send("halo") is True
        urls = [u for u, _ in sess.posts]
        assert any("api.telegram.org" in u for u in urls)
        assert any("discord" in u for u in urls)
        # token tidak bocor ke payload chat
        tg_payload = [p for u, p in sess.posts if "telegram" in u][0]
        assert "tok" not in str(tg_payload["chat_id"])

        # status non-200 telegram, discord 204 -> tetap True
        sess2 = _FakeSession(204)
        n2 = Notifier(enabled=True, discord_webhook="https://discord/hook", session=sess2)
        assert await n2.send("x") is True

        # pesan panjang dipotong aman
        sess3 = _FakeSession(200)
        n3 = Notifier(enabled=True, telegram_token="t", telegram_chat_id="1", session=sess3)
        assert await n3.send("y" * 5000) is True
        assert len(sess3.posts[0][1]["text"]) <= 4000
    asyncio.run(run())


def test_notifier_failures_are_silent():
    from bot.monitoring.notify import Notifier

    async def run():
        sess = _FakeSession(boom=True)
        n = Notifier(enabled=True, telegram_token="t", telegram_chat_id="1", session=sess)
        assert await n.send("x") is False  # tidak raise

        sess5 = _FakeSession(500)
        n5 = Notifier(enabled=True, telegram_token="t", telegram_chat_id="1", session=sess5)
        assert await n5.send("x") is False  # HTTP 500 -> False
    asyncio.run(run())
