# XAUUSD Scalper (MQL5 Expert Advisor)

Scalping EA untuk **XAUUSD (Gold)** di M5 (bisa M1), berbasis momentum
EMA-cross + RSI, dengan lapisan risiko berlapis (circuit breaker harian,
batas spread, simulasi margin sebelum kirim order).

> **Ringkasan (Bahasa):** EA ini enter long/short ketika EMA cepat cross EMA
> lambat (bar sudah close, bukan bar berjalan), dikonfirmasi RSI, dan hanya
> kalau spread sehat, volatilitas (ATR) dalam rentang normal, dan jam
> sesinya pas (default 07:00–16:00 waktu server = London+New York).
> Stop loss/take profit dihitung dari ATR (bukan angka mati). Risk per trade
> default 0.5% equity, maksimal 10 trade/hari, dan **EA otomatis berhenti
> open posisi baru** kalau rugi harian > 2% atau ada 4 loss beruntun.
> **Belum terbukti profit** — harus di-backtest dulu (protokol di bawah)
> sebelum dipakai sungguhan.

⚠️ **Disclaimer:** research artifact, bukan nasihat keuangan. Scalping gold
berisiko tinggi (spread + komisi + volatilitas berita). Tidak ada jaminan
profit. Gunakan akun demo dulu.

## 🛑 Verdict backtest (2026-10-12) — JANGAN DIPAKE LIVE

Backtest 21 tahun data XAUUSD asli (H1 + D1, protokol train/val/test + grid +
Monte Carlo — detail di `backtest/out/REPORT.md`):

- **Strategi v1 RUGI di semua split** (H1: −0.35R/trade train, −0.38R test;
  PF 0.34; seluruh 36 kombinasi parameter negatif).
- Iterasi struktural menemukan **break-even +1R adalah pembunuh utama**
  (tanpa BE: −0.30R → −0.01R di train), tapi varian terbaik tetap negatif di
  test set (−0.20R). D1+trend sempat +0.036R di train tapi gagal di val/test.
- **Kesimpulan: family strategi EMA-cross+RSI ini TIDAK punya edge yang
  robust di data ini.** Lapisan risiko (breaker, sizing, kap) bekerja sesuai
  desain — yang salah adalah logika entry-nya.
- Langkah berikutnya (di laporan): re-spec strategi (entry pullback +
  regime filter, buang BE), dan jalankan protokol M5 di Strategy Tester MT5
  dengan data tick asli dari broker.

## Files

| File | Isi |
|------|-----|
| `XauUsdScalper.mq5` | EA-nya (single file, self-contained) |
| `spec.md` | Spec + acceptance criteria + musyawarah 4 suara (council) |
| `REVIEW.md` | Jejak review adversarial 2 penguji (santa-method) + skor |
| `README.md` | File ini |

## Cara kerja

**Entry (per bar baru, hanya bar yang sudah close):**
1. Gate: belum halted → trade hari ini < max → bukan weekend → dalam sesi →
   bukan jam blok Jumat → spread ≤ `InpMaxSpreadPts` → ATR(last closed bar)
   dalam rentang `[InpAtrMin, InpAtrMax]`.
2. Sinyal: EMA fast cross atas EMA slow + RSI > level → **BUY** (di ask).
   Cross bawah + RSI < level → **SELL** (di bid).
3. Sizing: `lots = equity × risk% / loss-per-lot(jarak SL)` — clamp ke lot
   min/maks broker & `InpMaxLot`; skip kalau di bawah lot minimum.
4. Pre-send simulation: mode trade FULL, margin simulasi ≤ 50% free margin,
   SL/TP hormati stops level broker, lot dalam batas broker.

**Exit:**
- SL/TP: `1.5 × ATR` / `2.25 × ATR` (rasio 1.5R) saat entry.
- Break-even: setelah profit +1R, SL pindah ke harga entry (+buffer kecil);
  **TP asli tidak disentuh**.
- Trailing: setelah BE, SL mengikuti `1.5 × ATR` (hanya makin ketat).
- Time exit: kalau belum BE dalam 12 bar → close (scalp tidak boleh jadi
  "hold" tanpa risiko).

**Circuit breaker (dievaluasi setiap tick, bukan per trade):**
- Rugi harian (equity vs awal hari server) ≥ 2% → stop entry sampai hari
  server berikutnya.
- 4 loss beruntun → stop entry sampai hari berikutnya.
- Maksimal 10 entry/hari, maksimal 1 posisi terbuka.

**Statistik (di chart comment + log):** total trade, win rate, expectancy
dalam R/trade, max consecutive loss. `OnTester()` mengembalikan expectancy
(R/trade) sebagai metrik kustom di Strategy Tester.

## Install

1. Salin `XauUsdScalper.mq5` ke `MQL5/Experts/` (File → Open Data Folder di MT5).
2. Buka MetaEditor, F7 (Compile) — harus 0 error.
3. Di MT5: chart **XAUUSD M5**, drag EA ke chart, centang *Algo Trading*
   dan *Allow live trading* (untuk backtest cukup algo).
4. Pastikan EA satu instance per simbol (jangan dua chart sama magic).

## Parameter (inti)

| Param | Default | Keterangan |
|-------|---------|------------|
| `InpTimeframe` | PERIOD_CURRENT | Pakai **M5** (M1 = makan spread) |
| `InpEmaFast` / `InpEmaSlow` | 9 / 21 | Sinyal cross |
| `InpRsiPeriod` / `InpRsiLevel` | 7 / 50 | Konfirmasi momentum |
| `InpAtrMin` / `InpAtrMax` | 0.30 / 4.00 | Gate volatilitas (mati/sedang spike) |
| `InpSlAtrMult` / `InpTpAtrMult` | 1.50 / 2.25 | SL/TP dalam kelipatan ATR |
| `InpUseBreakEven` / `InpBreakEvenR` | true / 1.0 | BE setelah +1R |
| `InpTrailAtrMult` | 1.50 | Trailing setelah BE |
| `InpTimeExitBars` | 12 | Time exit (sebelum BE) |
| `InpSessionStart` / `InpSessionEnd` | 7 / 16 | Sesi (jam **server**) |
| `InpMaxSpreadPts` | 45 | Skip kalau spread melebar |
| `InpFridayBlockHour` | 20 | Tidak entry Jumat malam |
| `InpRiskPercent` | 0.50 | Risk/trade % equity |
| `InpMaxDailyLossPct` | 2.00 | Circuit breaker harian |
| `InpMaxConsecLosses` | 4 | Circuit breaker loss beruntun |
| `InpMaxDailyTrades` | 10 | Kapasitas trade/hari |
| `InpMaxLot` | 5.0 | Atasan lot |
| `InpSlippagePts` | 20 | Batas slippage |
| `InpMagic` / `InpComment` | 20261012 / XAUUSD-SCALP | Isolasi order |
| `InpVerbose` | false | Log tiap gate yang di-skip (debug) |

**Hanya 4 param yang boleh di-optimize:** `InpEmaFast`, `InpEmaSlow`,
`InpSlAtrMult`, `InpTpAtrMult`. Sisanya = guard risiko, jangan diutak-atik
saat optimasi (anti-overfit).

## Protokol backtest (WAJIB sebelum pakai)

1. Strategy Tester → XAUUSD M5, **"Every tick based on real ticks"**, 2–3 tahun,
   spread & komisi sesuai broker asli.
2. Bagi data: **train 60% / validation 20% / test 20%**. Optimasi hanya di
   train; validasi di validation; konfirmasi di test (jangan mengintip).
3. Walk-forward: jendela 6 bulan, re-optimasi tiap jendela.
4. **Gate go-live (test set):** expectancy > 0; max drawdown < 10%; profit
   factor > 1.3; Monte Carlo 1000 shuffle urutan trade → P(equity akhir < 90%
   awal) < 10%.
5. Kalau gagal gate → iterasi strategi (jangan "dipaksa lolos"). Setelah lolos:
   **akun demo ≥ 4 minggu** sebelum uang asli.

## Catatan operasional

- Jam sesi/blok Jumat pakai **jam server broker** (bukan jam lokal kamu).
- Trailing ATR membaca bar yang sedang berjalan (shift 0) — disengaja untuk
  exit; **sinyal tidak pernah** membaca bar terbuka (anti look-ahead).
- Order gagal (REQUOTE dsb.) **tidak di-retry buta** — sinyal itu dianggap
  hangus, bar berikutnya dievaluasi ulang dari nol.
- Kalau EA di-re-attach di tengah trade terbuka: BE/trailing nonaktif (state
  hilang), SL/TP tetap berjalan.
- Satu instance per simbol.

## Provenance — skill & agent yang dipakai (dua repo)

| Repo | Skill / Agent | Peran |
|------|---------------|-------|
| agents | `plugins/quantitative-trading/` (quant-analyst, risk-manager, backtesting-frameworks, risk-metrics-calculation) | Desain strategi, sizing R-multiple, protokol backtest, dashboard metrik |
| agents | `plugins/before-you-build` | Pre-mortem sebelum coding (verdict: HIGH risk) |
| agents | `plugins/comprehensive-review` | Lensa penguji arsitektur/security di round review |
| affan (ECC) | `skills/llm-trading-agent-security` | Circuit breaker, hard limits, pre-send simulation, slippage, audit log |
| affan (ECC) | `skills/intent-driven-development` | Acceptance criteria (AC1–AC7) sebelum coding |
| affan (ECC) | `skills/council` | Musyawarah 4 suara (skeptic/pragmatist/critic) untuk keputusan strategi |
| affan (ECC) | `agents/gan-planner/gan-generator/gan-evaluator` | Spec → build → rubric ketat |
| affan (ECC) | `skills/santa-method` + `agents/silent-failure-hunter` | 2 penguji independen, keduanya harus PASS (lihat REVIEW.md) |
| affan (ECC) | `skills/verification-loop` | Verifikasi statis (adaptasi: tidak ada compiler MQL5 di sandbox ini) |
