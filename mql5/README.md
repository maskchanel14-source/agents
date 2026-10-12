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
4. **Tapi tidak menembusnya** (`InpMaxPenetrationATR = 1.5`):
   `Low >= EMA21 - 1.5 × ATR`. Tembus terlalu dalam = breakdown, bukan pullback.
5. **Rejection**: `Close > EMA21` **dan** `Close > Open`
6. **Kualitas rejection** (`InpRejectionClose = 0.50`):
   bar harus close di **50% atas** dari range-nya, yaitu
   `(Close - Low) / (High - Low) >= 0.50`.
   Bounce yang close balik dekat low-nya = rejection lemah = setup yang gagal.
   Set `0` untuk mematikan.
7. Jarak entry dari EMA21 tidak lebih dari `1.2 × ATR` (tidak chasing)
8. RSI(14) di zona 45–80 **dan** RSI naik
9. ADX(14) ≥ 15 (market trending, bukan sideways)
10. ATR(14)/harga di antara 0.02% – 0.50% (tidak mati, tidak kacau)
11. Spread ≤ batas, jam trading aktif, tidak kena cooldown / daily loss limit

SELL adalah kebalikan persisnya.

### Setup B — Momentum breakout (BARU, penyumbang frekuensi utama)

Setup A saja **terlalu jarang** — harga harus balik dulu ke EMA baru ditolak.
Itu sebabnya versi sebelumnya cuma entry 3 hari sekali. Setup B menambah
entry yang jauh lebih sering muncul:

1. Bias H1 searah **dan** struktur EMA searah (sama seperti Setup A)
2. `Close[1] > High[2..N]` → tembus high `N` bar sebelumnya
   (`InpBreakoutLookback = 5`)
3. `Close > Open` (bar bullish)
4. RSI ≥ `InpBreakoutRSI` (default 55; untuk SELL: RSI ≤ 45)
5. Tidak overextended: `Close - EMA21 <= 2.0 × ATR`

SL/TP **identik** dengan Setup A (fungsi `BuildStop` yang sama), jadi
manajemen risikonya konsisten di kedua setup.

Keduanya bisa dinyalakan/dimatikan sendiri-sendiri lewat
`InpUsePullbackEntry` dan `InpUseBreakoutEntry`.

### Kenapa sebelumnya cuma 3 hari sekali

Sepuluh filter yang **berkali-kali**, bukan bertambah. Kalau tiap filter
lolos ~50%, sepuluh filter = `0.5^10 ≈ 0.1%` bar yang lolos. Itu sebabnya
frekuensinya hancur. Perubahan yang dilakukan:

| Parameter | Lama | Baru | Alasan |
|---|---|---|---|
| `InpUseBreakoutEntry` | — | **true** | Setup kedua, penyumbang frekuensi terbesar |
| `InpTrendRequirePrice` | — | **false** | H1 cukup struktur EMA, tidak perlu harga lewati EMA juga |
| `InpADX_Min` | 18 | **15** | ADX M5 noisy, 18 terlalu ketat |
| RSI band BUY | 50–78 | **45–80** | diperlukan |
| `InpRejectionClose` | 0.55 | **0.50** | diperlukan |
| `InpMaxPenetrationATR` | 1.0 | **1.5** | harga yang nyentuh EMA wajar lewat sedikit |
| `InpCooldownBars` | 3 | **1** | cooldown 15 menit buang banyak sinyal |
| `InpMaxHoldBars` | 12 | **8** | turnover lebih cepat, cocok scalping |
| `InpMaxDailyTrades` | 12 | **30** | plafon harian tidak lagi jadi pembatas |

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
| `InpMaxSpreadATR` | 0.10 | **0.10** (jangan longgar ini — paling bernilai) |
| `InpBE_OffsetATR` | 0.10 | **0.15** (menutup spread yang lebih lebar) |
| `InpSL_ATR` | 2.0 | **2.0 – 2.5** |
| `InpRR` | 1.2 | **1.0 – 1.2** |
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

### XAUUSD (gold): apa yang berbeda dan kenapa

Gold bukan EURUSD. Dua hal yang bikin setting default kurang optimal:

1. **`SYMBOL_TRADE_STOPS_LEVEL` lebih lebar.** Broker gold sering
   menetapkan 100-300 points. Kalau ATR(14) M5 gold = 150-250 points,
   itu berarti broker mengharuskan SL minimal = 1.0-1.5 ATR. Jarak
   trail juga terkena floor yang sama: trail 0.7 ATR di-clamp ke
   floor broker. Trail terasa "gak muncul" karena profit yang
   dibutuhkan buat aktifkan trail = jarak trail itu sendiri (yang
   di-clamp).

2. **Spread relatif lebih lebar.** Gold M5 retail spread = 0.10-0.20 ATR.
   Simulasi: begitu spread >= 0.10 ATR, **semua konfigurasi rugi** tanpa
   edge entri yang nyata.

**Setting yang disarankan untuk XAUUSD:**

| Parameter | Default | Rekomendasi XAUUSD |
|---|---|---|
| `InpSL_ATR` | 2.0 | **2.5** - room buat trail dan broker floor |
| `InpRR` | 1.2 | **1.0 - 1.2** - TP lebih dekat |
| `InpSwingLookback` | 12 | **16 - 20** - gold swing lebih besar |
| `InpMaxSpreadATR` | 0.25 | **0.20** - ketatkan sedikit, tapi jangan terlalu ketat |
| `InpTightenStartATR` | 2.5 | **2.0** - tighten lebih awal |
| `InpRiskPercent` | 1.0 | **0.5** - SL lebar = lot kecil |

Simulasi Monte Carlo (20k trial per konfigurasi, spread 0.15 ATR,
drift +0.02/bar, hold 16 bar):

```
minStp=1.0 ATR (tipikal gold):
  sl2.5 rr1.2  ->  -0.029 ATR/trade    <- terbaik
  sl3.0 rr1.0  ->  -0.036 ATR/trade
  sl2.0 rr1.0  ->  -0.053 ATR/trade
  sl1.5 rr1.5  ->  -0.064 ATR/trade    <- default lama (terburuk)

minStp=1.5 ATR:
  sl2.5 rr1.2  ->  -0.027 ATR/trade    <- terbaik
  sl3.0 rr1.0  ->  -0.040 ATR/trade
  sl1.5 rr1.5  ->  -0.072 ATR/trade    <- default lama (terburuk)
```

**Pola konsisten di SEMUA level broker min-stop:** SL lebih lebar +
RR lebih kecil = lebih baik. SL sempit 1.5 ATR terburuk di mana-mana.
Kenapa? Trail di-clamp ke broker floor, profit untuk aktifkan trail
juga naik ke floor yang sama = trail cuma jadi breakeven. SL 2.5 ATR
memberi ruang di atas floor broker supaya trail benar-benar bisa kerja.

Yang gak bisa diselesaikan tuning: kalau entri gak punya edge nyata
(>0.15 ATR per trade), rugi ~0.1 ATR/trade berapapun setting-nya.
Lihat bagian 6c buat data lengkap.


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

## 6b. Kenapa EA ini bisa hampir MC, dan apa yang sudah diperbaiki

**Penyebab utamanya bug di perhitungan lot.** Ini penting dipahami karena
perilakunya **berlawanan dengan intuisi**.

Ukuran lot dihitung dari risiko:

```
lot = (equity × risk%) / (jarak SL × nilai per 1.0 harga per lot)
```

Masalahnya: **SL yang lebih lebar menghasilkan lot yang lebih kecil.**
Kalau lot hasil hitungan itu jatuh **di bawah lot minimum broker**,
`NormalizeVolume()` akan membulatkannya **naik** ke lot minimum —
dan risiko aslinya ikut **berlipat**, tanpa peringatan apa pun.

Contoh nyata (EURUSD 3 digit, ATR ≈ 0.0008, `minLot = 0.01`, risk 1%):

| Equity | SL | Lot hitungan | Lot dipakai | **Risiko asli** |
|---|---|---|---|---|
| $1000 | 4 ATR | 0.0312 | 0.0300 | 0.96% ✅ |
| $300 | 4 ATR | 0.0094 | **0.01** | **1.07%** |
| $100 | 4 ATR | 0.0031 | **0.01** | **3.20%** ← 3,2× lipat |
| $100 | 5 ATR | 0.0025 | **0.01** | **4.00%** ← 4× lipat |

Perhatikan polanya: **makin lebar SL, makin parah.** Jadi pelebaran SL
yang Anda minta justru memicu bug ini lebih sering. Di akun kecil dengan
rentetan loss, 4% per trade sangat cepat menggerus equity sampai dekat MC.

### Perbaikan yang sudah dilakukan

1. **`InpSkipIfLotTooSmall` (default `true`)** — kalau lot minimum broker
   berarti risiko melebihi target, **trade dibatalkan** dan dicatat di log:
   ```
   SKIP: min lot 0.01 implies 3.20 % risk but target is 1.00 % - stop too wide for this account size
   ```
   Set `false` kalau Anda tetap mau masuk — log akan tetap memperingatkan.
2. **`InpMaxLot`** — plafon lot keras per trade (`0` = tanpa batas).
3. **`InpMinMarginLevelPct` (default 400%)** — tolak entry kalau margin level
   *setelah* masuk posisi bakal jatuh di bawah itu. Ini yang langsung menjaga
   dari margin call; cek free margin saja tidak cukup.
4. **`InpMaxDrawdownPct` (default 25%)** — berhenti trading kalau drawdown
   dari **peak equity** sudah segitu. Daily loss limit saja tidak cukup,
   karena rentetan loss kecil harian tetap menumpuk jadi drawdown besar.
5. **`InpEquityFloorPct` (default 50%)** — berhenti total kalau equity
   tinggal setengah dari saat EA dipasang.

Semua statusnya tampil di panel chart (baris `Risk guard`), dan log akan
mencetak `HALT: ...` begitu ada breaker yang aktif.

### Rekomendasi kalau akun Anda kecil

Lot minimum adalah musuh akun kecil. Urut yang aman:

1. Biarkan `InpSkipIfLotTooSmall = true`. Kalau log penuh `SKIP`, itu
   artinya **SL terlalu lebar untuk ukuran akun Anda** — persempit
   `InpSL_MaxATR` (mis. `5.0` → `3.0`), atau tambah modal.
2. Turunkan `InpRiskPercent` ke `0.5`.
3. Kalau pakai `InpFixedLot`, **Anda mematikan semua manajemen risiko di
   atas**. Pakai hanya kalau Anda tahu persis apa yang Anda lakukan.

---

---

## 6c. Diagnosa: kenapa hasilnya tetap jelek (dan apa yang TIDAK bisa diselesaikan dengan tuning)

Bagian ini penting, karena kesimpulannya **berlawanan dengan apa yang
kelihatannya salah**.

### Hipotesis yang salah, dan kenapa salah

Dugaan awal: **time stop membunuh trade** — target 3.3 ATR tidak mungkin
tercapai dalam 8 bar (40 menit), jadi semua trade mati kena time stop.

Ini **salah**, dan simulasi Monte Carlo membuktikannya:

```
OLD  SL2.2 RR1.5 hold8  arm1.2 tr1.2 BE1.0 -> TP  9.5%  SL 76.7%  TIME 13.9%
NEW  SL1.5 RR1.5 hold12 arm0.8 tr0.7 BE0.6 -> TP  9.6%  SL 90.4%  TIME  0.0%
```

Time stop cuma kena **0-14%** trade. Yang dominan adalah **SL/trailing
(77-90%)**. Jadi time stop bukan masalahnya.

### Masalah yang sebenarnya: spread

Simulasi yang sama, tapi sekarang **spread dihitung sebagai biaya**
(random walk tanpa drift = entri tanpa edge, jadi ini baseline yang jujur):

| Konfigurasi | sp=0 | sp=0.05 | sp=0.10 | sp=0.15 | sp=0.20 | sp=0.30 |
|---|---|---|---|---|---|---|
| OLD sl2.2 arm1.2 tr1.2 | +0.058 | -0.002 | -0.068 | **-0.111** | -0.149 | -0.258 |
| NEW sl1.5 arm0.8 tr0.7 | +0.058 | -0.001 | -0.047 | **-0.096** | -0.149 | -0.243 |
| ALT1 sl1.5 arm1.0 tr0.5 | +0.061 | +0.005 | -0.038 | **-0.084** | -0.141 | -0.246 |

(satuan: ATR per trade. Spread ~0.10-0.20 ATR itu normal untuk EURUSD M5
di akun retail.)

**Bacanya:**

1. **Semua konfigurasi rugi begitu spread >= 0.10 ATR.**
2. Selisih antar konfigurasi cuma **~0.03 ATR**, sementara biaya spread
   **0.10-0.26 ATR**. Artinya: **tuning geometri exit itu bukan tuasnya.**
3. Dengan entri yang tanpa edge, sistem rugi ~0.1 ATR per trade
   **berapapun** setting SL/TP/trail-nya.

Kesimpulannya: **tidak ada setting exit yang bisa menyelamatkan EA ini.**
Entri harus ngasih edge nyata yang **lebih besar dari ~0.15 ATR per trade**.
Itu yang harus dikejar, bukan SL/TP.

### Yang sudah dilakukan berdasarkan data ini

1. **`InpMaxSpreadATR = 0.10` (BARU)** — tolak entry kalau spread lebih
   dari 10% ATR. Ini perbaikan paling bernilai di ronde ini.
   Filter spread lama (`InpMaxSpreadPoints`) pakai **points**, yang tidak
   ada artinya: 20 points itu murah kalau ATR 80 points, tapi mematikan
   kalau ATR 30 points. Biaya harus diukur terhadap volatilitas yang
   ditradingkan.
2. **Geometri exit disesuaikan** — SL 2.2->1.5 ATR, trail 1.2->0.7 ATR,
   BE 1.0->0.6 ATR, hold 8->12 bar, tighten 3.0->1.6 ATR.
   Ini **perbaikan nyata tapi kecil** (-0.123 -> -0.091 ATR per trade).
   Jangan berharap ini yang bikin profit.
3. **Instrumentasi exit-by-reason + R-multiple (BARU)** — EA sekarang
   ngitung dan nge-print **`R avg`** dan distribusi R di log, plus baris
   `Exits: TP / SL / TIME / other` di panel. MT5 report **tidak** ngasih
   ini, padahal ini satu-satunya cara ngebedain "entri yang jelek" dari
   "biaya yang makan edge".

### Cara baca output R

```
--- EXIT STATS (OnDeinit) ---
  TP   :   12 trades  net +145.20
  SL   :  198 trades  net -310.40
  TIME :    3 trades  net   +2.10
  R avg: -0.041 over 213 scored trades
  R dist: bigLoss  8.5% | loss 22.1% | scratch 38.0% | win 27.2% | bigWin  4.2%
```

- **`scratch + win` dominan, tapi net negatif** -> spread/commission makan
  edge. Turunkan `InpMaxSpreadATR`, atau cari pair/sesi dengan spread lebih
  kecil.
- **`bigLoss` dominan** -> entri salah, atau SL terlalu ketat.
- **`R avg` negatif tapi `bigWin` lumayan** -> ada edge, tapi exit-nya
  nge-potong terlalu cepat. Longgarin `InpTrailDistATR`.
- **`TIME` tinggi (>30%)** -> target tidak tercapai dalam `InpMaxHoldBars`.
  Naikin `InpMaxHoldBars`, atau kecilkan `InpRR`.

## 7. Troubleshooting: "trailing gak jalan"

Kalau posisi sudah profit tapi SL-nya diam, urutan cek-nya:

### A. Paling sering: minimum jarak stop broker lebih lebar dari jarak trail

**Ini jebakan utama akun 3 digit.** EA memanggil:

```mq5
trailDist = MathMax(trailDist, minStp);   // minStp = SYMBOL_TRADE_STOPS_LEVEL x _Point
```

Broker menolak SL yang terlalu dekat dengan harga. Di akun 3 digit,
`_Point = 0.001`, jadi kalau `SYMBOL_TRADE_STOPS_LEVEL = 10`, maka
`minStp = 0.010`. Sementara ATR EURUSD cuma ≈ `0.0008`, jadi
`1.2 × ATR = 0.00096` — **jauh lebih kecil dari minimum broker**.

Akibatnya: SL tidak boleh diletakkan lebih dekat dari `0.010`, dan trailing
baru bisa jalan setelah profit Anda melewati `0.010` itu sendiri.
Bukan bug EA — ini aturan broker, dan EA **wajib** mematuhinya.

Cara cek: lihat log saat EA di-load.

```
ATR(14)=0.00080000   broker min stop distance=0.01000000 (10.0 points)
broker min stop distance = 12.50 x ATR
WARNING: broker min stop 0.01000000 is WIDER than trail distance 0.00096000
```

Kalau muncul `WARNING` itu, berarti trailing ATR tidak realistis di broker itu.
Pilihannya:

1. **Pakai mode points** (`InpTrailMode = TRAIL_POINTS`) dan set
   `InpTrailDistPoints` **di atas** minimum broker (mis. 12–15 kalau min 10).
2. Atau cari broker dengan `SYMBOL_TRADE_STOPS_LEVEL` lebih kecil.
3. Atau terima bahwa trailing baru aktif di profit besar, dan andalkan
   **breakeven** (`InpBE_StartATR`) sebagai pengaman utama.

### B. Magic number tidak cocok

EA **hanya** mengelola posisi dengan `InpMagic` yang sama. Posisi yang dibuka
manual atau oleh EA lain **tidak akan disentuh** — ini disengaja.

### C. File `.set` lama menimpa parameter baru

Kalau Anda pernah save `.set` dari versi lama, nilai lama (`InpSL_ATR = 1.5`
dan seterusnya) akan menimpa default baru. Cek di tab Inputs, atau hapus
`.set`-nya dan pakai default EA.

### D. Belum recompile

Fitur ratchet (`InpUseTrailTighten`) dan SL lebar baru ada di versi terbaru.
Kalau di tab Inputs **tidak ada** `InpUseTrailTighten`, berarti yang jalan
masih versi lama.

### Cara diagnosis cepat

Set `InpDebugTrailing = true`, lalu lihat tab **Experts** di terminal.
Setiap beberapa detik EA mencetak:

```
TRAILDBG ticket=123 BUY open=1.10000 price=1.10100 curSL=1.09700
 | profit=0.00100 (1.25xATR) | atr=0.00080 armAt=0.01000 (12.50xATR)
 trailDist=0.01000 minStp=0.01000 (12.50xATR) | newSL=1.10000  <== NOT ARMED
```

Perhatikan `armAt` dan `minStp`: kalau keduanya jauh lebih besar dari `atr`,
berarti kasus **A**. Kalau barisnya malah
`no position matches magic ...`, berarti kasus **B**.

---

## 8. Disclaimer

Trading forex/CFD berisiko tinggi. Hasil backtest **bukan janji hasil live**:
tidak mengikutsertakan slippage nyata, requote, komisi penuh, dan perubahan kondisi pasar.
Gunakan di akun demo dulu. Kamu bertanggung jawab penuh atas risiko akunmu.
