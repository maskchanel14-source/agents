# REPORT.md — Laporan Akhir Bot Arbitrase Polymarket

Tanggal: 2026-10-20 · Sesi otonom · Branch: `arena/4cbec802-agents` (PR dari branch ini).

## 1. Apa yang sudah jadi (dengan bukti)

| Komponen | Status | Bukti |
|---|---|---|
| Riset dokumentasi resmi (fee, neg-risk, orderbook, WS, auth, resolusi, rate limit, order wire format) | ✅ | `docs/POLYMARKET_NOTES.md` (sumber URL per klaim, diakses 2026-10-20) |
| `bot/costs.py` — model biaya tunggal, 100% Decimal | ✅ | 95% coverage; unit test cocok dengan **tabel fee resmi** docs (26 kasus) + property tests identitas konservasi kas |
| `docs/COST_MODEL.md` — rumus + sumber | ✅ | File tersedia; rumus `fee = C × rate × (p(1-p))^e`, rounding 5dp, min fee 0.00001 |
| Strategi A (intra-market binary: buy pair + mint&sell) | ✅ | `tests/test_strategies.py` end-to-end |
| Strategi B (multi-outcome/neg-risk: buy-all-YES, buy-all-NO, konversi) + validasi exhaustive | ✅ | Test membuktikan skip saat ada outcome "Other" & saat tanpa flag neg-risk |
| Strategi C (cross-market logis) | ✅ gated, default **OFF** | Hanya pasangan kriteria-resolusi **identik literal** (payoff terbukti deterministik); keraguan → skip. Aktifkan via config setelah review. |
| Strategi D (cross-venue) | ⏭ SKIP (stub) | Tidak ada venue dengan kriteria resolusi terverifikasi identik (DECISIONS D4) |
| Scanner menyeluruh + ranking + SQLite (SEMUA peluang tercatat) | ✅ | `bot/scanner.py`; `tests/test_execution_scanner.py` memverifikasi persist & ranking |
| Risk layer (hard limits, kill switch, circuit breaker, order-rate, reconciliation hook) | ✅ | 98% coverage `bot/risk/limits.py`; test tiap limit |
| Paper executor + fill probability model (FOK/FAK) | ✅ | `tests/test_execution_scanner.py` (FOK all-or-nothing, FAK partial, risk reject) |
| Live executor | ✅ terkunci | Menolak semua aksi tanpa `LIVE_TRADING=true` + `live_trading.confirmed` (test memverifikasi penolakan) |
| Dashboard HUD "ARC-TERMINAL" (vanilla JS, offline, 127.0.0.1, SSE, token+2-step, export CSV/JSON, waterfall, funnel, tab, a11y, reduced-motion) | ✅ | `tests/test_dashboard_http.py` (index/state/SSE/token/2-step/export); screenshot: lihat keterbatasan §3 |
| Launcher `start_bot.bat` (menu PAPER/BACKTEST/LIVE/test/record, venv+marker, pengaman ketik LIVE) + `start_bot_background.bat` + `stop_bot.bat` | ✅ | CRLF+ASCII terverifikasi; validasi statis label/goto/quote (`tests/test_launcher_bat.py`) |
| Backtest anti-lookahead + parameter sweep 36 kombinasi | ✅ | `tests/test_backtest.py`; `report_out/backtest_report.json` |
| Paper-run summary | ✅ (dari fixture — live tidak mungkin dari sandbox) | `logs/paper_run_summary.json`: 566 peluang terdeteksi, 272 gugur setelah biaya, 3 dieksekusi (risk cap), PnL simulasi **+$4,59** setelah SEMUA biaya |
| Docs: README (Quick start Windows + checklist + wallet setup + compliance), DECISIONS, CHECKPOINT, FEASIBILITY, COST_MODEL, POLYMARKET_NOTES | ✅ | File di root & `docs/` |
| Secret scan | ✅ bersih | Tidak ada key/secret di repo; `.env` di gitignore; tidak ada mekanisme anti-geoblock |
| Test suite | ✅ **157 hijau** | `report_out/coverage.txt` — total 83%; costs.py 95%, risk 98%, models 98%, state/scanner 96%, data layer 78–87%, engine 70% |

## 2. Angka kunci (dari paper-run replay fixture SINTETIS — bukan live)

Sumber: `data/fixtures/synthetic_small.json` (4.800 event, 4 market, detik-granularitas).

- Peluang gross terdeteksi: **566** kandidat (599 scan cycles).
- Lolos semua biaya: **294** (52%); **gugur setelah biaya: 272 (48%)** — alasan dominan
  `below_safety_margin` (fee+slippage+haircut memakan edge tipis).

- Rata-rata net edge: tergantung cap modal (±$0,30–$3,07 per peluang pada cap $25–$100)
  — lihat sweep di `report_out/backtest_report.json`.

- **Lifetime peluang: ±1,2 detik** → latency eksekusi adalah faktor penentu;
  fill-probability model sudah memperhitungkan hal ini (paper PnL tidak optimis).

- PnL simulasi sesi paper-run: **+$4,59** (3 trade / 8 leg, exposure cap $150 bekerja).

> ⚠️ Fixture ini MENANAM peluang untuk menguji pipeline. Angka live bisa jauh lebih
> buruk (edge nyata biasanya hilang oleh fee+slippage). Laporan live wajib diisi
> dengan `python -m bot.record` (2–4 jam) — template & kriteria go/no-go di
> `docs/FEASIBILITY.md`.

## 3. Keterbatasan & hal yang BELUM terverifikasi (jujur)

1. **Data live Polymarket belum terekam** — sandbox memblokir egress ke host
   Polymarket. Klien API ditulis dari spesifikasi resmi dan diuji via fixture/mock;
   koneksi live (Gamma discovery, WS subscribe, REST books) perlu diverifikasi dengan
   `python -m bot.record` di mesin user.

2. **Screenshot dashboard belum ada** — unduhan browser headless diblokir di sandbox.
   `scripts/take_screenshots.py` siap dijalankan (Playwright) + checklist visual di
   `docs/screenshots/README.md`. Endpoint/SSE/token sudah lolos test HTTP.

3. **Test .bat asli belum dijalankan di Windows** — hanya validasi statis
   (CRLF/ASCII/label/goto/quote). Checklist manual 5 menit ada di README.

4. **Paper run 30–60 menit terhadap live data** belum dilakukan (butuh item 1).
   Pengganti: replay 4.800 event + paper executor penuh (tercatat, di atas).

5. **Gas POL/USD & fee schedule runtime** — diverifikasi dari API saat runtime;
   nilai fallback konservatif dipakai bila RPC/API tidak tersedia (fail-closed untuk
   fee: peluang INVALID, tidak pernah assume 0).

6. `py-clob-client` (live) belum diuji end-to-end dengan akun nyata — by design
   (sesi ini dilarang menandatangani transaksi).

## 4. Risiko yang tersisa

- **Risiko eksekusi live**: partial fill antar-leg (FOK meminimalkan; haircut 0,2%
  tetap diambil), latency ~350 ms (config), dan pergeseran harga sebelum order tiba.

- **Risiko resolusi UMA**: dispute memperlambat payout 4–6 hari; haircut 0,02%/hari
  modal + 1% untuk kriteria ambigu; market "Other"/placeholder di-skip.

- **Risiko konfigurasi**: safety margin/annualized threshold yang diturunkan seenaknya
  akan membuka peluang marginal — semua parameter ada di `config/default.yaml`.

- **Risiko operasional**: rate limit IP-based; bot memakai token-bucket 70% limit resmi
  dan backoff 429. Reconciliation posisi dengan API live perlu diuji di lapangan.
- **Risiko model**: interpretasi `feeSchedule.exponent` = pangkat `p(1-p)` (konsisten
  dengan rumus resmi untuk e=1; semua market terdokumentasi e=1). Jika Polymarket
  mengubah formula, update `bot/costs.py` + uji ulang tabel fee.

## 5. Langkah manual SEBELUM live (checklist untuk user)

1. [ ] Isi laporan live di `docs/FEASIBILITY.md` (rekam 2–4 jam) — pastikan kriteria GO.
2. [ ] Buat **hot wallet khusus** (saldo kecil), isi `.env` (private key + API key CLOB
       L1/L2). JANGAN pakai wallet utama. Jangan commit `.env`.

3. [ ] Set `LIVE_TRADING=true` di `.env` DAN buat file `live_trading.confirmed`
       (isi manual, mis. tanggal + tanda tangan pemilik).

4. [ ] Review `config/default.yaml`: `max_capital_per_trade_usd` mulai dari $25,
       `max_daily_loss_usd`, `safety_margin_usd`, `min_annualized_return`.

5. [ ] Jalankan `start_bot.bat` → menu `1` PAPER dulu minimal 30–60 menit terhadap
       data live; bandingkan PnL simulasi dengan ekspektasi.

6. [ ] Uji kill switch: `stop_bot.bat` saat bot berjalan → bot berhenti bersih.
7. [ ] Baru kemudian menu `3` LIVE (ketik `LIVE`) dengan durasi terbatas + pantau
       dashboard (badge LIVE merah).

8. [ ] Pahami biaya & risiko: `docs/COST_MODEL.md`, `docs/POLYMARKET_NOTES.md` §9
       (UMA dispute), compliance/geoblock di README.

## 6. Cara memverifikasi sendiri (5 menit)

```bat
venv\Scripts\python.exe -m pytest tests/ -q            :: 157 test hijau
venv\Scripts\python.exe -m bot.backtest.run --sweep    :: laporan feasibility sintetis
venv\Scripts\python.exe -m bot.paper_run               :: paper run summary
venv\Scripts\python.exe -m bot --mode paper            :: bot + dashboard HUD
```

Di Linux/CI: perintah sama (ganti `venv\Scripts\python.exe` dengan `python`).
