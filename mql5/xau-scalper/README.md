# XAUScalperEA — EA scalping XAUUSD (MQL5)

EA scalping XAUUSD: konfirmasi trend M15 → konfluensi pullback M1 → entry market,
dengan manajemen risiko fixed-fractional, partial take-profit, break-even cepat,
trailing ATR, dan circuit-breaker harian/Drawdown.

**Tanpa martingale. Tanpa grid. Tanpa averaging.** Setiap posisi punya SL sejak
detik pertama — itu satu-satunya cara yang konsisten untuk mendapat DD kecil.

---

## 1. Instalasi (3 langkah)

1. Copy `Experts/XAUScalperEA.mq5` ke:
   `File → Open Data Folder → MQL5/Experts/` (bisa ditaruh di subfolder).
2. Buka **MetaEditor** → buka file → **Compile** (F7).
   Target: `0 errors, 0 warnings`.
3. Di MetaTrader 5: buka chart **XAUUSD timeframe M1**, drag `XAUScalperEA` ke
   chart, centang **Allow Algo Trading**, pastikan tombol **AutoTrading** hijau.

> Pasang di chart XAUUSD walaupun `InpSymbol` diisi manual — EA butuh tick dari
> simbol yang diperdagangkan. Kalau simbol broker kamu bersuffix (`XAUUSD.m`,
> `XAUUSD#`, `GOLD`, dll), EA mencarinya otomatis dan menulis hasilnya di log.

### Cek log saat pertama kali dipasang

```
XAUScalperEA initialized
  symbol      : XAUUSD
  digits      : 3   point=0.001   tickSize=0.001   tickValue=0.1
  lot step    : 0.01  min=0.01  max=100.00
  deviation   : 150 points
  GMT offset  : 3 h  (server time - GMT)
  account     : hedging  currency=USD
```

Kalau baris `digits` bukan 3 padahal broker kamu 3-digit, set
`InpDigitsOverride = 3`.

---

## 2. Kenapa EA ini aman untuk broker 3-digit

Semua input jarak — `InpMaxSpreadUSD`, `InpSLMinUSD`, `InpSLMaxUSD`,
`InpATRMinUSD`, `InpMaxDeviationUSD` — satuannya **dolar AS (price unit)**,
bukan point. Jadi:

| Broker | Contoh harga | `_Digits` | `_Point` | `InpMaxSpreadUSD=0.45` berarti |
|---|---|---|---|---|
| 3-digit | `4000.123` | 3 | 0.001 | 450 point = $0.45 |
| 2-digit | `4000.12` | 2 | 0.01 | 45 point = $0.45 |

Artinya nilai yang sama bekerja identik di dua jenis broker. `_Digits` hanya
dipakai untuk pembulatan harga dan konversi deviasi ke point.
`1 dollar = 10^digits point`.

---

## 3. Logika entry (5 komponen konfluensi)

Sinyal dievaluasi **sekali per bar M1 yang baru close** (bukan per tick).

| # | Komponen | Syarat BUY | Syarat SELL |
|---|---|---|---|
| 1 | Arah trend M15 | EMA(20) > EMA(50) | EMA(20) < EMA(50) |
| 2 | Kekuatan trend | ADX(14) ≥ 18 (opsional) | sama |
| 3 | Sentuh pullback | `low ≤ EMA21(M1) + 0.05×ATR` **dan** `close > EMA21` | `high ≥ EMA21 − 0.05×ATR` **dan** `close < EMA21` |
| 4 | Candle penolakan | `close > open` dan sumbu bawah ≥ 25% range | `close < open` dan sumbu atas ≥ 25% range |
| 5 | Zona RSI(14) | 45 ≤ RSI ≤ 85 | 15 ≤ RSI ≤ 55 |

Entry hanya terjadi kalau **skor ≥ `InpConfluenceMin`** (default 4 dari 5).
Menaikkan ke 5 = lebih sedikit sinyal, WR lebih tinggi. Menurunkan ke 3 =
lebih banyak sinyal, WR lebih rendah.

**Filter yang menolak entry (bukan skor, tapi gerbang):**

- ATR(M1,14) di luar `InpATRMinUSD`..`InpATRMaxUSD` (market mati / spike news)
- spread > `InpMaxSpreadUSD`
- di luar sesi, atau Jumat lewat jam `InpFridayCloseHourGMT`
- sedang dalam jendela news (`InpUseNewsFilter`, filter currency USD)
- daily loss sudah kena, daily target sudah capai, atau DD maksimal tercapai
- jumlah posisi/trade harian sudah penuh
- masih dalam cooldown setelah trade rugi (`InpCooldownBars`)

**Stop loss** diambil dari struktur: swing low/high `InpSLLookback` bar terakhir
± `InpSLBufferMult × ATR`, lalu di-clamp ke `InpSLMinUSD`..`InpSLMaxUSD`.

---

## 4. Logika exit

1. **TP1 (partial)** — saat profit ≥ `InpTP1_R × R`, `InpTP1Pct`% volume
   ditutup, sisanya SL dipindah ke break-even + `InpBEOffsetR × R`.
   Ini mekanisme utama yang mengangkat win rate.
2. **Trailing ATR** — setelah profit ≥ `InpTrailStartR × R`, SL mengikuti harga
   sejauh `InpTrailATRMult × ATR`, hanya bergerak menguntungkan.
3. **Runner TP2** — posisi TP di `InpTP2_R × R` (default 2.5R). Kalau trailing
   sudah lebih tinggi dari TP, TP yang dieksekusi duluan.
4. **Time stop** — posisi yang masih terbuka setelah `InpMaxBarsInTrade` bar M1
   dan sedang profit, ditutup.
5. **Tutup akhir sesi** — `InpCloseAtSessionEnd = true` (default), tidak ada
   posisi menginap. Ini sengaja: scalper + gap weekend = musuh DD.

**Restart-safe:** besaran R disimpan di komentar order (`XSCALP#1.85`). Kalau EA
atau terminal restart di tengah posisi, EA membaca kembali R dari komentar dan
menebak stage dari posisi SL relatif terhadap harga entry.

---

## 5. Parameter yang paling berpengaruh

| Input | Default | Arah tuning | Rentang aman untuk optimasi |
|---|---|---|---|
| `InpConfluenceMin` | 4 | ↑ WR naik, trade turun | 3 – 5 |
| `InpSLMinUSD` / `InpSLMaxUSD` | 0.80 / 4.00 | ↑ SL lebar = WR naik, R:R turun | 0.6–1.5 / 3–6 |
| `InpTP1_R` | 1.00 | ↑ WR turun, profit per trade naik | 0.8 – 1.5 |
| `InpTP1Pct` | 50 | ↑ WR naik, runner mengecil | 30 – 70 |
| `InpTP2_R` | 2.50 | ↑ profit naik, WR sedikit turun | 1.5 – 4.0 |
| `InpTrailATRMult` | 1.20 | ↑ jarak trail = runner lebih lama | 0.8 – 2.0 |
| `InpATRMinUSD` / `InpATRMaxUSD` | 0.15 / 4.00 | filter volatilitas | 0.10–0.30 / 3–6 |
| `InpMaxSpreadUSD` | 0.45 | ↓ = kualitas entry naik, kuantitas turun | 0.30 – 0.60 |
| `InpSessionStartGMT` / `EndGMT` | 08:00 / 20:00 | persempit ke 12:00–18:00 untuk kualitas | — |
| `InpRiskPerTradePct` | 0.5 | **jangan dioptimasi** — ini preferensi risiko, bukan edge | 0.25 – 1.0 |

`InpRiskPerTradePct`, `InpMaxDailyLossPct`, `InpMaxDrawdownPct` adalah
**kebijakan risiko**, bukan parameter edge. Jangan dimasukkan ke optimasi —
mengoptimasi ukuran lot hanya mengoptimasi keberuntungan.

---

## 6. Preset

| File | Untuk |
|---|---|
| `presets/XAUScalper-Conservative.set` | Akun kecil / prop-firm: risk 0.25%, DD stop 4%, konfluensi 5/5, sesi 12:00–18:00 GMT |
| `presets/XAUScalper-Balanced.set` | Default EA (sesuai jawabanmu) |
| `presets/XAUScalper-Aggressive.set` | Lebih banyak trade & runner lebih panjang: konfluensi 3/5, TP2 3R |

Cara pakai: Strategy Tester → klik kanan input EA → **Load** → pilih file `.set`.
File preset dibuat oleh `tools/make_sets.py` langsung dari source supaya nama
parameternya tidak pernah meleset.

---

## 7. Sebelum live: protokol validasi

Baca **[`docs/VALIDATION.md`](docs/VALIDATION.md)**. Ringkasnya:

- Minimal 200 trade out-of-sample sebelum kamu percaya angka WR
  (`tools/winrate_power.py` menjelaskan kenapa 150 trade belum cukup untuk
  membedakan WR 55% dari lempar koin).
- Walk-forward, bukan sekali optimasi.
- Jalankan `python3 tools/winrate_power.py --wr <WR> --n <trade>` untuk
  mengecek apakah hasil backtest-mu signifikan atau sekadar varians.

---

## 8. Troubleshooting

| Gejala di log / chart | Penyebab & solusi |
|---|---|
| `ERROR: symbol 'XAUUSD' not found` | Simbol broker bersuffix aneh → isi `InpSymbol` persis seperti di Market Watch, atau biarkan kosong (pakai simbol chart) |
| Dashboard: `Session: closed` terus | `InpSessionMode=SESSION_GMT` tapi offset broker salah → cek baris `GMT offset` di log; jika aneh, ganti ke `SESSION_SERVER` dan isi jam server |
| `SL/TP rejected by broker stops level` | SL terlalu dekat → naikkan `InpSLMinUSD` |
| `Lot size is 0` | Equity terlalu kecil untuk SL sejauh itu → turunkan `InpSLMaxUSD` atau kecilkan `InpRiskPerTradePct` |
| Tidak ada trade sama sekali | Cek dashboard: spread, sesi, news block, ATR range. Matikan `InpUseNewsFilter` dulu saat testing (kalender sering kosong di Strategy Tester) |
| `CalendarValueHistory` selalu gagal | Wajar di Strategy Tester tanpa data kalender — EA mengabaikan filter (tidak memblokir) |
| Partial close gagal → `Position too small to split` | Lot minimum broker terlalu besar → posisi ditutup penuh di TP1 (aman, hanya kurang optimal) |
| EA berhenti total | `InpMaxDrawdownPct` tercapai → `g_halted=true`. Reset dengan memasang ulang EA |

---

## 9. Disclaimer

Trading emas/XAUUSD berisiko tinggi dan sangat dipengaruhi broker (spread,
slippage, kualitas feed). Backtest bukan jaminan hasil live. Jalankan di akun
demo minimal 4–6 minggu sebelum uang sungguhan. Tidak ada satu pun parameter di
EA ini yang bisa mengubah sistem buruk menjadi sistem baik — yang bisa dilakukan
EA hanyalah menjaga kerugian tetap terdefinisi.
