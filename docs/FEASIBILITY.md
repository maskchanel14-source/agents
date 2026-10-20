# FEASIBILITY.md — Go/No-Go Berbasis Data (misi §3b)

Terakhir diperbarui: 2026-10-20.

## Status: ⚠️ GO BERSYARAT — menunggu rekaman live 2–4 jam dari mesin dengan
akses jaringan Polymarket (angka di bawah dari fixture SINTETIS + pipeline asli,
BUKAN data live — egress sandbox ke Polymarket diblokir, lihat DECISIONS.md D0/D9).

> **Kejujuran data:** semua angka bagian "Hasil replay (SYNTHETIS)" berasal dari
> generator `bot/backtest/synthetic.py` yang MENANAM peluang arbitrase sesekali
> untuk menguji pipeline. Angka ini membuktikan **sistem pendeteksian bekerja
> end-to-end**, BUKAN estimasi profit di pasar nyata. Jangan ditafsirkan sebagai
> expected PnL live. Template laporan live ada di bagian 4 — jalankan
> `python -m bot.record` lalu `python -m bot.backtest.run` untuk mengisinya.

## 1. Cara merekam data live (wajib sebelum keputusan final)

```bat
:: rekam 2-4 jam orderbook live (semua market aktif yang ditrade-able)
venv\Scripts\python.exe -m bot.record --minutes 180 --out data\recordings

:: analisis: peluang gross vs net, lifetime, funnel
venv\Scripts\python.exe -m bot.backtest.run --fixture data\recordings\recording.db --sweep
```

Recorder menyimpan: snapshot orderbook per asset (SQLite), metadata market
(`markets_meta.json`), dan `run_summary.json` (cakupan: market dipantau vs total).

## 2. Hasil replay (SYNTHETIS) — pipeline end-to-end

Sumber: `data/fixtures/synthetic_small.json` (4.800 event, 4 market, 600 tick
1 detik, seed=7). Perintah: `python -m bot.backtest.run --sweep`.

| Metrik | Nilai |
|---|---|
| Event orderbook direplay | 4.800 (berurutan waktu, anti-lookahead) |
| Scan cycles | 599 |
| Peluang gross terdeteksi (kandidat) | 566 |
| Lolos SEMUA biaya (valid) | 294 (52%) |
| Gugur setelah biaya | 272 (48%) — semua `below_safety_margin` |
| Rata-rata net edge (per peluang, $50 cap) | ±$1,54 (efek ukuran optimal) |
| Lifetime peluang valid | ±1,2 detik (karakter generator: peluang ditanam 1 tick) |
| Paper-executed (risk cap aktif) | 3 trade, 8 leg |
| PnL simulasi setelah semua biaya | **+$4,59** (fee, slippage, gas, haircut, safety sudah dipotong) |

Paper-run summary lengkap: `logs/paper_run_summary.json` (regenerasi dengan
`python -m bot.paper_run`).

**Interpretasi jujur:** pada fixture ini hampir separuh kandidat gugur oleh
safety margin + fee setelah dihitung ulang penuh — persis perilaku yang diinginkan
("akurasi > jumlah trade"). Peluang yang lolos bertahan ±1 detik → **latency
eksekusi adalah faktor penentu di live**; fill probability model sudah memperhitungkan
ini dan paper PnL memakai model tersebut (tidak optimis).

## 3. Sensitivitas parameter (36 kombinasi sweep)

`python -m bot.backtest.run --sweep` (lihat `report_out/backtest_report.json`):

- `max_capital_per_trade` berdampak linear pada net per peluang (ukuran optimal
  memakai penuh cap) — risiko konsentrasi dikontrol `risk/limits.py`, bukan di sini.
- `safety_margin` 0.002→0.02: pada fixture ini jumlah valid stabil (edge yang
  ditanam cukup besar); pada data live margin ini adalah filter utama — JANGAN
  menurunkannya di bawah $0,005/pair tanpa bukti live.
- `min_annualized_return` 0.05→0.30: tidak mengubah valid di fixture (edge pendek
  = annualized besar); pada market ber-EndDate jauh gate ini bekerja keras
  (terverifikasi unit test `test_annualized_gate_rejects`).

## 4. Template laporan LIVE (isi setelah rekaman)

| Metrik | Nilai live | Cara ukur |
|---|---|---|
| Total market aktif (Gamma) | _?_ | `run_summary.json -> discovery_stats.raw` |
| Market dipantau vs total | _?_ | coverage di `report_out/backtest_report.json` |
| Peluang gross / jam | _?_ | `opportunities` / jam rekaman |
| Lolos semua biaya / jam | _?_ | `valid` / jam rekaman |
| % gugur setelah biaya | _?_ | `rejected / opportunities` |
| Rata-rata net edge (setelah semua biaya) | _?_ | `avg_net_edge` |
| Rata-rata lifetime peluang (detik) | _?_ | `avg_lifetime_s` |
| Sebaran alasan penolakan | _?_ | `rejection_stats` |

**Kriteria go/no-go final** (berlaku untuk data live):
- GO jika: ≥1 peluang bersih/jam dengan net edge > safety margin × 2 DAN lifetime
  median > 2× latency eksekusi (±1,5–3 detik) DAN fill-prob rata-rata ≥ 0,5.
- NO-GO (untuk mode live; sistem tetap dipakai untuk paper/monitoring) jika:
  hampir semua peluang gugur setelah fee+slippage, atau lifetime < 1 detik
  (edge hanya hidup di dalam latency kita) — laporkan apa adanya.

## 5. Di mana edge hilang (analisis berbasis model)

Urutan "pemakan" edge (dari pengamatan pipeline):

1. **Slippage walk-the-book** — tipisnya depth di sisi ask membuat harga efektif
   naik melewati $1 untuk pasangan YES+NO begitu ukuran > top level.
2. **Trading fee taker** — market ber-fee (crypto 0.07 / sports 0.05) memotong
   ±$0,017–0,025 per pasang pada harga tengah; hanya market fee-0 / edge besar
   yang selamat.
3. **Safety margin + haircut risiko** — disengaja: menahan eksekusi marginal.
4. **Min order notional (5 USDC)** — menolak peluang mikro yang mungkin masih
   positif setelah biaya, karena tidak bisa dieksekusi legal.

## 6. Cakupan & data quality

- Discovery penuh via Gamma (`closed=false`, paginasi offset+keyset) — bukan sampel.
- WS market channel (sharded) + REST `/books` rekonsiliasi 60 detik.
- Staleness gate 3 detik (configurable) — peluang dari snapshot basi DITOLAK.
- Fee schedule hilang → market di-SKIP (fail-closed) dan tercatat di alasan skip.
- Outcome "Other"/placeholder pada event neg-risk → strategi B SKIP event itu.

## 7. Keputusan

**GO bersyarat** untuk melanjutkan ke tahap live-preparation (sudah selesai:
risk layer, kill switch, live executor terkunci). **Aktifasi live TUNGGU** sampai:
(1) laporan live di atas terisi dari rekaman 2–4 jam, (2) kriteria go terpenuhi,
(3) checklist manual di README diselesaikan user (wallet khusus, approval,
review config, pengaman LIVE_TRADING).
