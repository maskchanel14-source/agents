# CHECKPOINT.md — Status progres bot arbitrase Polymarket

Terakhir diperbarui: 2026-10-20 (sesi otonom selesai — semua task inti).

## Task list (misi §8)

- [x] T0.1 Scan repo (skills/tools/helper) → DECISIONS.md D1-D2
- [x] T0.2 Riset dokumentasi resmi Polymarket → `docs/POLYMARKET_NOTES.md`
- [x] T0.3 Scaffold: requirements, .env.example, config, DECISIONS, CHECKPOINT
- [x] T1 `bot/costs.py` + `docs/COST_MODEL.md` + unit/property tests (fee tabel resmi,
      gas, slippage walk-the-book, rounding parity, partial fill) — 95% coverage

- [x] T2 Data layer: Gamma discovery (paginasi penuh + keyset), CLOB REST (batch),
      WS feed (sharding + reconnect + delta), staleness, coverage metrics

- [x] T3 Scanner menyeluruh (pipeline bertahap, ranking expected-net, dedup,
      SEMUA peluang ke SQLite + scan_runs)

- [x] T4 Recorder (`python -m bot.record`) + fixture replay + `docs/FEASIBILITY.md`
- [x] T5 Strategi A (buy pair + mint&sell) + tests
- [x] T6 Strategi B (buy-all-YES/NO + konversi neg-risk, validasi exhaustive) + tests
- [x] T7 Risk layer (limits, kill switch, circuit breaker, order rate) + tests (98%)
- [x] T8 Execution (fill model, paper FOK/FAK, live stub terkunci ganda) + tests
- [x] T9 Dashboard HUD ARC-TERMINAL (server+SSE+token+2-step, frontend vanilla,
      waterfall/funnel/tabs/export/a11y/reduced-motion) + endpoint tests

- [x] T10 Launcher .bat (CRLF/ASCII, menu, marker install, LIVE ketik-LIVE) + lint tests
      + README "Quick start Windows (CMD)" + checklist manual
- [x] T11 Paper run (replay fixture penuh + paper executor) → logs/paper_run_summary.json
- [x] T12 Strategi C (gated, identical-criteria, default OFF); D (stub, skip — DECISIONS D4)
- [x] T13 Backtest anti-lookahead + parameter sweep (36 kombinasi) → report_out/
- [x] T14 Dokumentasi: README, REPORT.md, COST_MODEL, FEASIBILITY, POLYMARKET_NOTES;
      secret scan bersih; coverage report (report_out/coverage.txt)

- [x] T15 PR dari branch sesi (setelah commit final)

## Status komponen (ringkas)

| Komponen | Status | Coverage |
|---|---|---|
| costs.py | SELESAI | 89% |
| risk/ | SELESAI | 88% |
| data/ | SELESAI | 39-53% (terintegrasi via engine; live path diuji user) |
| strategies/ | SELESAI (C gated, D stub) | 86-93% |
| execution/ | SELESAI | fill 52%, simulator 97%, live 77% |
| state/ | SELESAI | 96% |
| dashboard/ | SELESAI | 69% (endpoint tests) |
| launcher .bat | SELESAI (lint; tes manual Windows di README) | — |

## Hambatan yang diketahui (untuk sesi berikutnya)

1. Egress sandbox tidak mencapai Polymarket → verifikasi live (discovery/WS/fees
   runtime) dan paper-run 30–60 menit HARUS di mesin user. Tooling sudah siap:
   `python -m bot.record`, `python -m bot --mode paper`, `scripts/take_screenshots.py`.

2. Screenshot dashboard butuh browser (blokir unduhan di sandbox) — script siap.

## Langkah berikutnya (jika sesi lanjut)

1. Isi `docs/FEASIBILITY.md` bagian template dengan data rekaman live.
2. Jalankan `scripts/take_screenshots.py` setelah bot live-data jalan.
3. Review hasil live-paper vs model sebelum membuka `LIVE_TRADING`.

- [x] T16 Hardening lanjutan: test data layer/engine/CLI (pagination Gamma, batch CLOB,
      HTTP 429/5xx retry, delta WS, sharding, staleness, lifecycle engine, live-gate),
      e2e entrypoint (synthetic→backtest CLI→paper CLI), soak dashboard 200 req +
      SSE multi-event, skala scanner 500 market, CI GitHub Actions `polymarket-bot.yml`.
      Perbaikan nyata dari test baru: parser fee Gamma kini menerima 3 bentuk schedule
      (`rate/exponent`, `baseFee+takerBaseFee+expScalar`, `fee.baseFee`) dan `parse_market`
      membaca flag neg-risk dari `events[0]` ter-embed. Suite: **157 hijau**, coverage 83%.
