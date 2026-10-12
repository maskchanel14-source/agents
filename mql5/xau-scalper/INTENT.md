# Statement of Intent — XAUScalperEA

Dihasilkan dengan skill `interview-me` (ekstraksi intent sebelum ada kode) lalu
`constraint-driven-development` (mengunci quality bar dalam angka).

**Status: menunggu konfirmasi eksplisit kamu (ya / koreksi).** Saya sudah
mengimplementasikan v1 sesuai butir di bawah supaya kamu bisa langsung
di-compile dan di-backtest — tapi kalau ada satu baris yang salah, koreksi di
sini lebih murah daripada mengubah EA nanti.

---

## Restate

| Item | Isi |
|---|---|
| **Outcome** | Satu file `XAUScalperEA.mq5` yang bisa di-compile di MetaEditor tanpa edit, dipasang di chart XAUUSD M1, dan melakukan scalping dengan win rate setinggi mungkin **tanpa** mengorbankan drawdown. |
| **User** | Kamu sendiri, trader retail, broker dengan XAUUSD **3 digit** (harga seperti `4000.123`, `_Point = 0.001`). |
| **Why now** | Butuh EA yang WR-nya tinggi dan profitnya besar, tapi tetap aman — bukan EA "WR 95%" yang sebenarnya martingale. |
| **Success** | (1) Compile 0 error 0 warning di MetaEditor; (2) lolos walk-forward out-of-sample dengan PF ≥ 1.3 dan max DD ≤ 6%; (3) win rate out-of-sample ≥ 55% dengan ≥ 200 trade (cukup sampel, bukan kebetulan). |
| **Constraint (paling mengikat)** | Drawdown. Karena itu: **tanpa martingale, tanpa grid/averaging** — kamu sudah memilih ini. Konsekuensinya WR realistis 55–70%, bukan 90%. |
| **Out of scope** | Martingale/grid, multi-pair, copy-trade, dashboard visual berbasis objek chart, pending-order entry (v1 market entry), dan "janji profit" dalam bentuk apa pun. |

## Yang saya kunci dari jawabanmu

| Pertanyaan | Jawabanmu | Implikasi di kode |
|---|---|---|
| Format harga XAUUSD | **3 desimal** (`4000.123`) | Semua jarak SL/TP/spread/ATR dalam **USD (price unit)** → otomatis benar di 2-digit maupun 3-digit. `_Digits` dibaca otomatis, ada `InpDigitsOverride` kalau mau dipaksa 3. |
| Mesin | **Scalper murni, fixed SL/TP, TANPA martingale/grid** | Maksimal `InpMaxPositions` posisi, `InpMaxPerDirection` per arah, lot dari % risk, bukan lot naik saat kalah. |
| Timeframe & sesi | **Entry M1, konfirmasi trend M15, sesi London–NY** | `InpTrendTF = PERIOD_M15` (EMA 20/50 + ADX), `InpSignalTF = PERIOD_M1`, sesi default 08:00–20:00 GMT (offset broker dideteksi otomatis). |
| Exit | **TP bertahap: partial 50% di 1R, sisanya trailing + BE cepat** | `InpTP1_R=1.0`, `InpTP1Pct=50`, `InpTP2_R=2.5`, `InpBEOffsetR=0.10`, trailing ATR `InpTrailATRMult=1.2`. |
| Sizing & proteksi | **Auto lot 0.5%/trade + daily loss 2% + auto-stop DD 6%** | `InpRiskPerTradePct=0.5`, `InpMaxDailyLossPct=2.0`, `InpMaxDrawdownPct=6.0`, `InpDDAction=DD_CLOSE_AND_STOP`. |

## Satu temuan yang perlu kamu putuskan

Dengan risk 0.5%/trade dan asumsi sistem sehat (WR 60%, R:R 1.45), simulasi
Monte-Carlo 4000 jalur × 1000 trade (`tools/winrate_power.py`) memberi:

- median max DD **4.5%**, persentil-95 **6.7%**, terburuk **10.0%**
- **10.8% jalur menembus batas DD 6%** — artinya circuit-breaker 6% akan
  mematikan sistem yang sehat kira-kira 1 dari 9 kali (bukan karena sistemnya
  rusak, tapi karena varians normal).

Pilihan:
- **(a) Tetap 6%** → DD benar-benar kecil, tapi sesekali EA berhenti padahal
  sistemnya masih valid (kamu tinggal reset manual).
- **(b) Naikkan ke 8–10%** → guard hanya aktif saat benar-benar rusak.

Default saat ini 6% sesuai pilihanmu.

## Konfirmasi

Balas **"ya"** kalau butir di atas sudah sesuai, atau sebut nomor/baris yang
perlu diubah.
