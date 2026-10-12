# ApexScalper — MQL5 Scalping EA

Expert Advisor scalping multi-konfluensi untuk MetaTrader 5, dengan **trailing stop**,
manajemen risiko berbasis persentase equity, dan **dukungan penuh akun 3 digit**.

File: `ApexScalper.mq5`

---

## 1. Jawaban singkat: BACKTEST DI TIMEFRAME BERAPA?

| Setting | Nilai | Catatan |
|---|---|---|
| **Timeframe chart** | **M5** | Ini `InpSignalTF`. EA membaca sinyal di M5. |
| **Trend filter** | **H1** | `InpTrendTF`. Tester MT5 membuat data H1 otomatis. |
| **Model** | **"Every tick based on real ticks"** | ⚠️ **WAJIB**. Lihat bawah. |
| **Periode** | **12–24 bulan**, minimal 6 bulan | Scalping butuh banyak sampel. |
| **Spread** | Real / sesuai broker | Jangan pakai "Current" kalau spread brokerimu dinamis. |
| **Deposit** | Sesuai rencana real (mis. $1000) | Karena lot dihitung dari % equity. |
| **Leverage** | Sesuai akun real | Mempengaruhi cek margin. |

### Kenapa M5, bukan M1?
- Akun **3 digit** punya ketelitian harga lebih kasar (1 point = 0.001, setara 10 pip di broker 5 digit).
  Di M1, jarak SL yang realistis jadi "kegedean" relatif terhadap noise → banyak sinyal palsu.
- **M5 adalah sweet spot**: target scalping masih masuk akal, tapi noise dan biaya spread
  relatif lebih kecil terhadap target.
- Kalau mau lebih agresif, M1 bisa dicoba — TP: `InpSL_ATR` → 1.0, `InpRR` → 1.5,
  `InpADX_Min` → 22.

### ⚠️ Model backtest WAJIB "Every tick based on real ticks"
Untuk EA scalping, 3 model lain menghasilkan **angka palsu**:
- "Open prices only" — tidak bisa simulasikan trailing stop & SL intrabar.
- "1 minute OHLC" — SL/TP intrabar tidak akurat.
- "Every tick" (bukan real ticks) — MT5 menginterpolasi tick sintetis; spread tidak realistis.

Kalau terminalmu tidak punya data real tick, download dulu:
`Tools → History Center` (F2), atau klik kanan di Strategy Tester → **"Download ticks"**.

---

## 2. Cara pakai

1. Copy `ApexScalper.mq5` ke:
   `<Terminal Data Folder>/MQL5/Experts/`
2. Buka MetaEditor → **Compile** (F7). Harus `0 errors, 0 warnings`.
3. Buka chart **M5** → drag EA ke chart.
4. Centang **Allow Algo Trading** dan **Allow DLL imports** (tidak wajib, EA tidak pakai DLL).
5. Backtest: `Ctrl+R` → set seperti tabel di atas → Start.

---

## 3. Logika strategi

EA hanya masuk di **pullback searah trend**, bukan mengejar harga.

### Filter trend (H1)
- `Close > EMA50` **dan** `EMA50 > EMA200` → bias **BUY**
- `Close < EMA50` **dan** `EMA50 < EMA200` → bias **SELL**
- Kondisi di antara → **flat, tidak trading** (hindari market choppy)

### Sinyal entry (M5, dievaluasi di bar yang sudah close)
Semua harus terpenuhi untuk **BUY**:
1. Bias H1 = UP
2. `EMA8 > EMA21` (momentum jangka pendek searah)
3. Bar menyentuh/menembus `EMA20` (`Low <= EMA20`) lalu **ditolak**
   (`Close > EMA20` **dan** `Close > Open`) — ini konfirmasi rejection
4. Jarak entry dari EMA20 tidak lebih dari `1.2 × ATR` (tidak chasing)
5. RSI(14) di zona 50–78 **dan** RSI naik
6. ADX(14) ≥ 18 (market trending, bukan sideways)
7. ATR(14)/harga di antara 0.02% – 0.50% (tidak mati, tidak kacau)
8. Spread ≤ batas, jam trading aktif, tidak kena cooldown / daily loss limit

SELL adalah kebalikan persisnya.

### Stop Loss & Take Profit
- **SL**: swing low/high `N` bar terakhir + buffer `0.25 × ATR`,
  di-clamp ke minimum `0.8 × ATR` dan maksimum `3.0 × ATR`.
  Kalau SL lebih lebar dari `3.0 × ATR` → **trade dibatalkan** (risk/reward jelek).
- **TP**: `jarak SL × InpRR` (default 1:2).

### Trailing stop (sudah aktif secara default)
1. **Breakeven**: saat profit ≥ `1.0 × ATR`, SL dipindah ke entry + `0.10 × ATR`.
2. **Trailing**: saat profit ≥ `1.0 × ATR`, SL mengikuti harga pada jarak `1.0 × ATR`.
3. SL **hanya boleh mengencang**, tidak pernah melebar.
4. Modifikasi hanya dilakukan kalau perbaikannya ≥ `0.05 × ATR` (hindari spam request).
5. Selalu menghormati `SYMBOL_TRADE_STOPS_LEVEL` dan `SYMBOL_TRADE_FREEZE_LEVEL` broker.

### Exit tambahan
- **Time stop**: posisi ditutup setelah `12` bar M5 (default 1 jam) kalau belum kena SL/TP.
  Scalp yang ngambang tidak boleh ditahan berhari-hari.

---

## 4. Penting untuk akun 3 digit

EA ini **digit-agnostic**: semua jarak (SL, TP, trailing, buffer) dihitung dalam
**satuan harga dari ATR**, bukan dalam point. Jadi perilakunya identik di broker
3, 4, maupun 5 digit.

Money management juga benar di semua digit karena memakai:

```
value per 1.0 price move per lot = tick_value / tick_size
lot = (equity × risk%) / (jarak_SL × value_per_price_move)
```

Ini otomatis menyesuaikan kontrak broker, tanpa asumsi "1 lot = $10/pip".

### Yang perlu kamu tahu soal 3 digit
- `_Point = 0.001`. Untuk EURUSD itu **= 10 pip** (di broker 5 digit, 1 pip = 0.0001).
- Artinya **SL harus kelipatan 0.001**. SL 12 pip akan ter-normalize jadi 10 atau 20 pip.
  Ini keterbatasan broker, bukan bug EA. EA mengkompensasi lewat **ukuran lot**,
  jadi risiko rupiahnya tetap sesuai persen yang kamu set.
- `InpMaxSpreadPoints` auto = **3 point** untuk akun 3/4 digit, dan **20 point**
  untuk akun 5/6 digit. Cek log saat EA load untuk melihat nilai yang dipakai.
  Kalau broker 3 digit-mu spreadnya 2 point, nilai 3 sudah pas.

### Parameter yang disarankan untuk akun 3 digit

| Parameter | Default | Rekomendasi 3 digit |
|---|---|---|
| `InpSignalTF` | M5 | **M5** (jangan M1) |
| `InpRiskPercent` | 1.0 | **0.5 – 1.0** |
| `InpMaxSpreadPoints` | 0 (auto) | biarkan auto → 3 |
| `InpBE_OffsetATR` | 0.10 | **0.15** (menutup spread yang lebih lebar) |
| `InpTrailStartATR` | 1.0 | **1.0 – 1.2** |
| `InpSL_ATR` | 1.5 | **1.5 – 2.0** |

---

## 5. Urutan optimasi yang disarankan

Jangan langsung optimasi semua parameter (overfitting). Urutan yang aman:

1. **Baseline** — jalankan dengan default di M5, 12 bulan, real ticks. Catat hasilnya.
2. **Filter** — optimasi `InpADX_Min` (15–25) dan `InpATR_MinPct`/`InpATR_MaxPct`.
3. **Exit** — optimasi `InpRR` (1.5 / 2.0 / 2.5 / 3.0) dan `InpTrailStartATR`,
   `InpTrailDistATR`.
4. **Session** — coba `InpSessionStartHour`/`EndHour` sesuai pair.
5. **Walk-forward** — optimasi di 12 bulan, lalu **forward test di 3 bulan berikutnya**
   yang tidak dipakai saat optimasi. Kalau hasilnya anjlok, berarti overfit.

## 6. Checklist sebelum live

- [ ] Backtest model **real ticks**, hasil profit & drawdown masuk akal
- [ ] Forward test minimal 2–4 minggu di demo
- [ ] Spread broker saat live ≤ `InpMaxSpreadPoints`
- [ ] `InpRiskPercent` sesuai toleransi (0.5% untuk akun kecil)
- [ ] VPS dekat server broker, latency rendah
- [ ] Recover factor > 1.5, Profit factor > 1.3, Expected payoff > 0

---

## 7. Disclaimer

Trading forex/CFD berisiko tinggi. Hasil backtest **bukan janji hasil live**:
tidak mengikutsertakan slippage nyata, requote, komisi penuh, dan perubahan kondisi pasar.
Gunakan di akun demo dulu. Kamu bertanggung jawab penuh atas risiko akunmu.
