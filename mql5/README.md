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

Tiga EMA dengan **tiga peran berbeda** (sebelumnya EMA20 dan EMA21 dipakai
berbarengan untuk dua fungsi — itu redundan dan sudah diperbaiki):

| EMA | Periode | Peran |
|---|---|---|
| `EMA_Fast` | 8 | Momentum jangka pendek |
| `EMA_Pullback` | 21 | Garis yang harus disentuh harga (trigger entry) |
| `EMA_Trend` | 50 | Struktur trend yang **tidak boleh** ditembus pullback |

Semua harus terpenuhi untuk **BUY**:
1. Bias H1 = UP
2. **Struktur EMA**: `EMA21 > EMA50` **dan** `EMA8 > EMA50`.
   Ini memastikan kita beli *pullback di dalam uptrend*, bukan menangkap
   pisau jatuh. `EMA8 > EMA50` (bukan `EMA8 > EMA21`) sengaja lebih longgar
   supaya pullback yang agak dalam tetap ke-trigger.
3. **Bar menyentuh garis pullback**: `Low <= EMA21`
4. **Tapi tidak menembusnya** (`InpMaxPenetrationATR = 1.0`):
   `Low >= EMA21 - 1.0 × ATR`. Tembus terlalu dalam = breakdown, bukan pullback.
5. **Rejection**: `Close > EMA21` **dan** `Close > Open`
6. **Kualitas rejection** (`InpRejectionClose = 0.55`):
   bar harus close di **55% atas** dari range-nya, yaitu
   `(Close - Low) / (High - Low) >= 0.55`.
   Bounce yang close balik dekat low-nya = rejection lemah = setup yang gagal.
   Set `0` untuk mematikan.
7. Jarak entry dari EMA21 tidak lebih dari `1.2 × ATR` (tidak chasing)
8. RSI(14) di zona 50–78 **dan** RSI naik
9. ADX(14) ≥ 18 (market trending, bukan sideways)
10. ATR(14)/harga di antara 0.02% – 0.50% (tidak mati, tidak kacau)
11. Spread ≤ batas, jam trading aktif, tidak kena cooldown / daily loss limit

SELL adalah kebalikan persisnya.

### Stop Loss & Take Profit (SL sengaja dibuat lebih lega)
- **SL**: swing low/high `12` bar terakhir + buffer `0.40 × ATR`,
  di-clamp ke minimum `1.2 × ATR` dan maksimum `5.0 × ATR`.
  Kalau SL lebih lebar dari `5.0 × ATR` → **trade dibatalkan** (risk/reward jelek).
- Fallback kalau `InpUseSwingSL = false`: SL = `2.2 × ATR`.
- **TP**: `jarak SL × InpRR` (default **1:1.5**, turun dari 1:2).

Kenapa SL dilebarkan dan RR diturunkan: SL ketat di akun 3 digit gampang
kena stop-hunt karena ketelitian harganya kasar. Tapi SL lebar tanpa
pengaman = rugi besar. Makanya **trailing-lah yang jadi pengamannya** — lihat bawah.

> ⚠️ Karena lot dihitung dari risiko (`risk% ÷ jarak SL`), **SL lebih lebar =
> lot otomatis lebih kecil**. Ini memang benar secara manajemen risiko, bukan bug.
> Kalau mau lot tetap besar, naikkan `InpRiskPercent` (hati-hati) atau pakai
> `InpFixedLot`.

### Trailing stop (sudah aktif secara default — dan sekarang 3 tahap)
1. **Breakeven**: saat profit ≥ `1.0 × ATR`, SL pindah ke entry + `0.10 × ATR`.
2. **Trailing awal**: saat profit ≥ `1.2 × ATR`, SL mengikuti harga pada
   jarak `1.2 × ATR` (artinya SL pertama kali pindah **tepat di entry**).
3. **Ratchet / pengencangan** (`InpUseTrailTighten`, baru):
   saat profit ≥ `3.0 × ATR`, jarak trail **dikencangkan** jadi `0.8 × ATR`
   supaya sebagian besar pergerakan terkunci.

> **Invariant penting** (dijaga di kode, bukan cuma di default):
> trailing **tidak boleh aktif sebelum profit ≥ jarak trail-nya**.
> Soalnya kalau `TrailStart < TrailDist`, update pertama menaruh SL di
> `harga − TrailDist` padahal profitnya lebih kecil dari itu — jadi SL
> mendarat **di bawah entry**. Dengan SL awal yang lebar, itu berarti SL
> melompat dari beberapa ATR jauhnya ke sedikit di bawah entry, dan trade
> mati kena retrace biasa. Kode memakai `max(TrailStart, TrailDist)` supaya
> ini gak bisa terjadi berapa pun nilai yang kamu set.
4. SL **hanya boleh mengencang**, tidak pernah melebar.
5. Modifikasi hanya dilakukan kalau perbaikannya ≥ `0.05 × ATR` (hindari spam request).
6. Selalu menghormati `SYMBOL_TRADE_STOPS_LEVEL` dan `SYMBOL_TRADE_FREEZE_LEVEL` broker.

**Ini konsep kuncinya**: SL jauh di awal memberi ruang napas, lalu trailing
mengambil ruang itu kembali sedikit demi sedikit begitu trade bergerak untung.
Jadi secara efektif risiko awal besar, tapi risiko *realized* mengecil.

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
| `InpRiskPercent` | 1.0 | **0.5 – 1.0** (lot menyusut karena SL lebih lebar) |
| `InpMaxSpreadPoints` | 0 (auto) | biarkan auto → 3 |
| `InpBE_OffsetATR` | 0.10 | **0.15** (menutup spread yang lebih lebar) |
| `InpTrailStartATR` | 0.8 | **0.8 – 1.0** |
| `InpSL_ATR` | 2.2 | **2.0 – 2.5** |
| `InpSL_MinATR` | 1.2 | **1.2 – 1.5** (jangan di bawah ini di 3 digit) |
| `InpRR` | 1.5 | **1.5 – 2.0** |
| `InpSwingLookback` | 12 | **12 – 16** |

### Kalau sinyal terlalu sedikit
Fitur baru (`InpUseStackFilter`, `InpRejectionClose`, `InpMaxPenetrationATR`)
memang bikin sinyal **lebih sedikit tapi lebih bersih**. Kalau hasilnya
terlalu sepi, longgarkan bertahap — jangan langsung semua:

1. `InpRejectionClose` → `0.40` (atau `0` untuk matikan)
2. `InpMaxPenetrationATR` → `1.5`
3. `InpADX_Min` → `15`
4. Terakhir: `InpUseStackFilter` → `false`

Urutan ini dari yang paling sedikit pengaruhnya ke yang paling besar.
Ubah satu-satu dan catat hasilnya, biar tahu mana yang bikin beda.

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
