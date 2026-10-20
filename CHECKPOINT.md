# CHECKPOINT.md — Status progres bot arbitrase Polymarket

Terakhir diperbarui: 2026-10-20 (sesi otonom, dikerjakan sendiri).

## Task list (urutan pengerjaan sesuai misi §8)

- [x] T0.1 Scan repo (skills/tools/helper) → hasil di DECISIONS.md D1-D2
- [x] T0.2 Riset dokumentasi resmi Polymarket → `docs/POLYMARKET_NOTES.md`
- [x] T0.3 Scaffold: requirements, .env.example, config, DECISIONS, CHECKPOINT
- [ ] T1 `bot/costs.py` + `docs/COST_MODEL.md` + unit test (fee/gas/slippage/rounding/partial-fill)
- [ ] T2 Data layer: Gamma discovery (paginasi penuh), CLOB REST, WS feed (reconnect, sharding), staleness, coverage metrics
- [ ] T3 Scanner menyeluruh (pipeline bertahap, ranking net profit, SQLite logging semua peluang)
- [ ] T4 Recorder data + fixture + `docs/FEASIBILITY.md` (go/no-go)
- [ ] T5 Strategi A (intra-market binary) + tests
- [ ] T6 Strategi B (multi-outcome / neg-risk) + tests
- [ ] T7 Risk layer (limits, kill switch, circuit breaker, reconciliation) + tests
- [ ] T8 Execution simulator (paper, fill model, FOK/FAK) + live stub terkunci + tests
- [ ] T9 Dashboard HUD "ARC-TERMINAL" (server + frontend + verifikasi)
- [ ] T10 Launcher `.bat` + lint + README Windows + checklist manual
- [ ] T11 Paper run (replay + smoke live-path mock) + ringkasan log
- [ ] T12 Strategi C/D: implementasi ter-gate; keputusan aktif/skip dengan alasan
- [ ] T13 Backtest + parameter sweep (tanpa lookahead)
- [ ] T14 Dokumentasi akhir: README, REPORT.md, COST_MODEL, FEASIBILITY; secret scan; coverage report
- [ ] T15 PR dari branch sesi ke main dengan ringkasan + checklist pre-live

## Status komponen

| Komponen | Status |
|---|---|
| Riset docs (fees, neg-risk, orderbook, WS, auth, resolusi, rate limit, order wire format) | SELESAI — `docs/POLYMARKET_NOTES.md` |
| DECISIONS.md | SELESAI (terus diperbarui) |
| costs.py | BELUM |
| data/ | BELUM |
| strategies/ | BELUM |
| risk/ | BELUM |
| execution/ | BELUM |
| state/ | BELUM |
| dashboard/ | BELUM |
| launcher | BELUM |

## Hambatan aktif

1. Egress sandbox tidak mencapai host Polymarket → live scan/record harus dijalankan
   user di Windows; semua komponen live diverifikasi via mock + fixture di sini.

## Langkah berikutnya

Implementasi `bot/costs.py` + tests (inti), lalu data layer → scanner → strategi.
