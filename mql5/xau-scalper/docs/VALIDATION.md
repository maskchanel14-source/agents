# Protokol Validasi — XAUScalperEA

Ditulis memakai kerangka `experimental-design` + `statistical-power`:
tujuannya bukan "mendapat angka bagus", melainkan **membuktikan angka itu
bukan kebetulan dan bukan hasil mengintip masa depan**.

EA tanpa protokol ini = kurva equity yang indah di backtest dan hancur di live.
Baca dokumen ini sebelum kamu percaya satu angka pun.

---

## 0. Kenapa ini perlu

Sebuah EA dengan 60 parameter yang dioptimasi terhadap 200.000 bar M1 akan
selalu menghasilkan kurva equity naik — itu bukan edge, itu **curve fitting**.
Protokol di bawah memaksa dua hal:

1. **Cukup sampel** — win rate butuh ratusan trade sebelum bisa dibedakan dari
   lempar koin (`statistical-power`).
2. **Data yang dipakai untuk memilih parameter ≠ data yang dipakai untuk
   menilai hasilnya** (`experimental-design`: hold-out / walk-forward).

---

## 1. Data

| Syarat | Nilai |
|---|---|
| Simbol | XAUUSD milik broker kamu sendiri (bukan data vendor lain) |
| Timeframe | M1 (EA juga membaca M15) |
| Periode | Minimal **24 bulan**, ideal 36–48 bulan |
| Model tick di Strategy Tester | **"Every tick based on real ticks"** — bukan "1 minute OHLC". Scalper M1 hidup/mati oleh urutan tick; model OHLC akan memberi hasil palsu yang terlalu bagus. |
| Spread | Gunakan spread **aktual saat ini**, lalu uji ulang dengan spread ×2 (lihat §6) |

Kalau terminal kamu tidak punya tick history yang cukup: download dulu di
`Tools → History Center` / Symbols → XAUUSD → download M1, lalu jalankan
tester sekali agar terminal membangun cache tick.

---

## 2. Pertanyaan statistis yang wajib dijawab dulu

Jalankan:

```bash
python3 tools/winrate_power.py --wr 0.60 --n 150 --avg-win 1.45 --avg-loss 1.0 \
                               --risk 0.5 --trades 1000 --dd-limit 6.0
```

Output aktual untuk skenario itu:

```
 Observed win rate      : 60.0%  (90/150 trades)
 95% CI (Wilson)        : 52.0% .. 67.5%
 Expectancy per trade   : +0.470R   (+0.235% of equity per trade)

 Q2 - trades needed before the win rate is NOT a coin flip
      true WR 55% -> n =   783
      true WR 58% -> n =   305
      true WR 60% -> n =   194
      true WR 65% -> n =    85
      true WR 70% -> n =    47

 Q3 - n needed before expectancy is provably > 0 : 52
      luck probability of your win count: 0.0088

 Q4 - Monte-Carlo over 1000 trades at 0.5% risk (4000 paths)
      median final equity : 1020.2   (5th pct 729.6 / 95th pct 1426.3)
      median max DD       : 4.5%
      95th pct max DD     : 6.7%
      worst of 4000 paths : 10.0%
      paths breaching DD guard of 6.0% : 10.8%
```

**Cara membacanya:**

- WR 60% dari 150 trade punya interval 52%–67,5%. Klaim "WR saya 60%" dari
  sampel segitu sebenarnya hanya mengatakan "antara 52% dan 67,5%".
- Untuk membuktikan WR 60% itu nyata (bukan koin), butuh **194 trade**.
  Untuk WR 55% butuh **783 trade**. Makin kecil edge-nya, makin banyak sampel
  yang dibutuhkan — ini sebabnya `InpOptMinTrades = 200` ada di `OnTester()`.
- Menariknya, **expectancy lebih mudah dibuktikan daripada win rate**: butuh
  hanya 52 trade karena R:R 1.45 memberi sinyal lebih kuat daripada sekadar
  menang/kalah. Jadi nilai utama yang kamu kejar adalah **expectancy**, dan WR
  hanyalah salah satu inputnya.
- **10,8% jalur yang sehat tetap menembus DD 6%** dalam 1000 trade. Jadi kalau
  circuit-breaker kamu menyala, itu belum tentu tanda sistem rusak — lihat §5.

---

## 3. Prosedur optimasi

### Parameter yang BOLEH dioptimasi (maksimal 7)

Pilih maksimal 7 sekaligus. Lebih dari itu, ruang pencarian melebihi jumlah
sampel dan yang kamu-fit adalah noise.

| Parameter | Rentang | Step |
|---|---|---|
| `InpSLMinUSD` | 0.60 – 1.50 | 0.10 |
| `InpSLMaxUSD` | 3.00 – 6.00 | 0.50 |
| `InpSLBufferMult` | 0.10 – 0.50 | 0.05 |
| `InpTP1_R` | 0.80 – 1.50 | 0.10 |
| `InpTP2_R` | 1.50 – 4.00 | 0.25 |
| `InpTrailATRMult` | 0.80 – 2.00 | 0.10 |
| `InpATRMinUSD` | 0.10 – 0.30 | 0.05 |

### Parameter yang DILARANG dioptimasi

`InpRiskPerTradePct`, `InpMaxDailyLossPct`, `InpMaxDrawdownPct`,
`InpMaxLot`, `InpMaxPositions`. Ini kebijakan risiko. Mengoptimasinya = memilih
ukuran taruhan berdasarkan masa lalu = jalan pintas menuju margin call.

### Pengaturan

- Algoritma: **Slow complete algorithm** (parameter sedikit) atau
  **Genetic algorithm** bila lebih dari 5 parameter.
- Kriteria: **Custom (OnTester)**. EA sudah menyediakannya:

  ```
  score = (profit / max(DD,1)) × min(PF,10) + recovery_factor × 100
  skor  = -1.000.000 bila trade < InpOptMinTrades
  ```

  Jadi run dengan 40 trade dan profit fantastis otomatis dibuang
  (pelindung overfit paling murah yang ada).

---

## 4. Walk-forward (wajib)

Bukan satu optimasi lalu dipakai. Potong data menjadi jendela berjalan:

| Langkah | Isi |
|---|---|
| In-sample (optimasi) | 3 bulan |
| Out-of-sample (uji) | 1 bulan, **tidak pernah disentuh optimasi** |
| Geser | 1 bulan ke depan, ulangi |
| Minimal jendela | 8 (≈ 24 bulan data: 8×1 bulan OOS) |

### Gerbang kelulusan (semua harus ya)

| # | Metrik — dihitung **gabungan semua jendela OOS** | Syarat |
|---|---|---|
| 1 | Profit factor | ≥ 1.30 |
| 2 | Expectancy per trade | > 0.15R |
| 3 | Jumlah trade OOS | ≥ 200 |
| 4 | Win rate OOS vs in-sample | selisih ≤ 5 poin persen (lebih dari itu = overfit) |
| 5 | Max DD OOS | ≤ 1.5 × max DD in-sample, **dan** ≤ 6% |
| 6 | Recovery factor | ≥ 2.0 |
| 7 | Jendela OOS rugi | ≤ 2 dari 8 |
| 8 | Bulan terburuk OOS | masih < batas daily-loss yang kamu terima |

Gagal di nomor 4 adalah sinyal overfit yang paling umum: WR in-sample 72%,
OOS 54% → parameter itu sedang menghafal noise.

---

## 5. Robustness check (30 menit, menyelamatkan akun)

1. **Uji spread ganda**: jalankan ulang OOS dengan spread broker ×2 dan ×3.
   Kalau PF turun di bawah 1.15, edge-mu sebenarnya cuma "spread tipis".
2. **Uji geser waktu (jitter)**: ubah `InpSessionStartGMT` ± 30 menit. Hasil
   seharusnya berubah sedikit, bukan runtuh. Runtuh = kamu fit jam tertentu.
3. **Uji tetangga parameter**: ambil parameter terbaik, lalu ubah satu per satu
   ±1 step. Kalau tetangganya jauh lebih buruk, kamu sedang duduk di **jarum**,
   bukan di **plateau**. Pilih nilai di tengah plateau yang terluas.
4. **Uji simbol tetangga** (opsional): jalankan di XAGUSD atau pair emas lain di
   broker yang sama. Edge yang struktural biasanya masih positif (lebih lemah);
   yang negatif total = kemungkinan besar curve fit.
5. **Uji DD guard**: sengaja set `InpMaxDrawdownPct` ke nilai yang kira-kira
   akan tersentuh. Pastikan EA benar-benar berhenti dan menutup posisi
   (`InpDDAction = DD_CLOSE_AND_STOP`). Fitur proteksi yang belum pernah diuji
   sama dengan tidak ada.

---

## 6. Backtest vs live: yang biasanya berbeda

| Faktor | Cara mengurangi |
|---|---|
| Slippage saat news | Sudah ada `InpMaxDeviationUSD` + filter news. Turunkan jadi 0.05 kalau broker sering requote |
| Spread melebar | `InpMaxSpreadUSD` adalah filter utama. Mulai dari 0.45 lalu lihat di Market Watch jam 08:00–09:00 GMT |
| Eksekusi VPS | Jalankan di VPS dekat server broker; latensi > 100 ms mengubah hasil M1 |
| Partial close ditolak | Sebagian broker (terutama netting + cent account) punya aturan volume minimum aneh; EA sudah fallback ke close penuh di TP1 |
| Kalender kosong di tester | Wajar. Saat live pastikan `Tools → Options → Events` aktif kalau `InpUseNewsFilter = true` |

---

## 7. Monitoring live

**Harian (2 menit)**

- Jumlah trade vs rata-rata backtest (jauh lebih sedikit → cek spread/sesi)
- Apakah ada `Order failed` di log tab **Experts**
- Realized WR rolling 50 trade (bukan harian — harian terlalu bising)

**Mingguan**

- Bandingkan max DD live vs persentil-95 Monte-Carlo (§2). DD live yang
  konsisten di atasnya = broker/eksekusi berbeda dari asumsi, turunkan
  `InpRiskPerTradePct` dulu sebelum mengubah apa pun.

**Bulanan**

- Ulangi walk-forward dengan data bulan berjalan (sebagai OOS baru)
- Putuskan: **parameter drift** (re-optimasi wajar) atau **regime change**
  (hentikan EA). Bedanya: kalau metrik memburuk perlahan → drift; kalau
  memburuk mendadak dan PF < 1.0 selama 2 bulan berturut → regime change.

---

## 8. Checklist sebelum uang sungguhan

- [ ] Compile 0 error / 0 warning
- [ ] Data M1 ≥ 24 bulan, model "every tick based on real ticks"
- [ ] ≥ 8 jendela walk-forward, semua gerbang §4 lolos
- [ ] Total trade OOS ≥ 200
- [ ] Lolos uji spread ×2
- [ ] Parameter berada di plateau, bukan di jarum
- [ ] Sudah uji bahwa circuit-breaker DD benar-benar menyala
- [ ] Demo minimal 4–6 minggu dengan ukuran lot live
- [ ] VPS + AutoTrading + Allow Algo Trading aktif
- [ ] `InpRiskPerTradePct` ditetapkan dari toleransi rugimu, bukan dari backtest
