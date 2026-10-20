# COST_MODEL.md — Model Biaya (sumber kebenaran tunggal: `bot/costs.py`)

Semua angka dihitung dengan `Decimal`. Tidak ada angka hardcode yang tidak bisa
ditelusuri ke dokumentasi resmi / API. Riset: `docs/POLYMARKET_NOTES.md` §5–6.
Diakses: 2026-10-20, https://docs.polymarket.com/trading/fees,
https://docs.polymarket.com/market-data/market-details.

## 1. Trading fee (taker)

Rumus resmi:

```
fee = C × feeRate × (p × (1 - p)) ^ exponent
```

- `C` = jumlah share, `p` = harga share (0..1), `feeRate`/`exponent` dari Gamma
  `feeSchedule` per market (`rate`, `exponent`, `takerOnly`, `rebateRate`).

- Dokumen resmi menuliskan `fee = C × feeRate × p × (1 - p)` — itu kasus `exponent = 1`
  (semua market yang terdokumentasi). Interpretasi `exponent` = pangkat komponen
  harga `p(1-p)`; diuji unit test terhadap tabel resmi.

- **Hanya taker bayar; maker 0.**
- Pembulatan: **HALF_UP 5 desimal**; hasil < **0.00001 USDC** → 0.
- Fee dihitung **per level walk-the-book** (tiap match di harga berbeda punya p
  berbeda) lalu dijumlahkan.

- Tabel fee resmi (100 share, Crypto 0.07 dst.) diverifikasi unit test — nilai tabel
  di docs dibulatkan 2 desimal (cents), nilai presisi kita 5 desimal.

- Kategori rate: Crypto 0.07 · Sports/Econ/Culture/Weather/Other 0.05 ·
  Finance/Politics/Mentions/Tech 0.04 · Geopolitics 0 · Combos 0.05.

- **Fee schedule tidak tersedia → peluang INVALID** (fail-closed, `RejectReason.FEE_UNKNOWN`).

## 2. Slippage (walk-the-book)

- Isi dari level terbaik ke dalam, **per level**: `notional = Σ price_i × size_i`.
- `slippage_cost = notional − best_price × filled_shares`.
- Urutan level dinormalisasi (sort sendiri) karena REST vs WS beda urutan.
- Ukuran trade = **min(depth semua leg, batas modal, batas risiko)**, dipilih dari
  kandidat breakpoint depth + batas modal, yang **net profit total maksimum**
  (edge per bundle menurun saat menyentuh level lebih dalam → optimum di breakpoint).

- Size dibulatkan **floor** ke size decimals (2) — tidak pernah menambah ukuran.

## 3. Pembulatan / presisi order

Paritas dengan `py-clob-client` `ROUNDING_CONFIG` (diuji):

| Tick | Price dec | Size dec | Amount dec |
|---|---|---|---|
| 0.1 | 1 | 2 | 3 |
| 0.01 | 2 | 2 | 4 |
| 0.005 | 3 | 2 | 5 |
| 0.0025 | 4 | 2 | 6 |
| 0.001 | 3 | 2 | 5 |
| 0.0001 | 4 | 2 | 6 |

Urutan (docs trading/place-orders):

1. harga ≤ price decimals;
2. share di-floor ke size decimals;
3. USD amount: jika desimal > amount decimals → ceil ke amount+4, lalu floor ke amount;
4. konversi ke integer 6 desimal (`makerAmount`/`takerAmount`).

BUY: `makerAmount` = USD, `takerAmount` = share. SELL: kebalikannya.
`rounding_cost` di model = selisih encoding vs nilai eksak (konservatif terhadap kita).

## 4. Gas / on-chain (Polygon)

- **Trading via CLOB tidak kena gas user** (matching off-chain, settlement on-chain
  oleh operator; sumber: concepts/prices-orderbook). Relayer API tersedia untuk tx
  wallet tanpa pegang POL.

- Operasi user yang kena gas: `approve`, `split`, `merge`, `redeem`, `convert_neg_risk`.
- `gas_cost = units × gas_price_gwei × 1e-9 × POL_USD`.
- Nilai runtime: gas price & POL/USD dari RPC bila `POLYGON_RPC_URL` tersedia;
  fallback konservatif di config (`gas_price_gwei_fallback: 100`, `pol_usd_fallback: 0.25`).

- Approval diamortisasi: `gas(approve) / amortize_approvals_over_trades` per order.
- Strategi A jalur **merge** (YES+NO → 1 pUSD) kena `gas(merge)`; jalur hold-to-resolution
  kena `gas(redeem)` saat klaim; Strategi A2 (mint & sell) kena `gas(split)`.

## 5. Risiko lain yang diperhitungkan (haircut $)

| Komponen | Formula | Alasan |
|---|---|---|
| `leg_risk_cost` | `capital × leg_risk_haircut_pct` (default 0.2%) | Probabilitas partial fill / salah satu leg tidak terisi (expected loss unhedged). FOK menekan ini; haircut tetap diambil. |
| `resolution_risk_cost` | `payout × (ambig_pct jika ambigu) + payout × pct_per_day × hari` | Risiko dispute UMA (resolusi bisa 4–6 hari) + kriteria ambigu. |
| `rounding_cost` | selisih encoding pembulatan | Pembulatan bisa menghapus profit. |
| `safety_margin` | `max($ per bundle, % × capital)` (default $0.005) | Margin pengaman wajib sebelum net > 0. |

## 6. Opportunity cost modal

- `annualized_return = (net / capital) × (365 / hari_tertahan)`.
- Hari tertahan per exit path:
  - **merge** (pasangan YES+NO → pUSD): default 2 jam operasional;
  - **mint&sell** (split + jual kedua leg): default 1 jam;
  - **hold ke resolusi** (bundle multi-outcome): sampai `endDate`.
- Gate: `annualized_return ≥ min_annualized_return` (default 15%/tahun) atau
  peluang DITOLAK (`ANNUALIZED_TOO_LOW`).

- Latency/staleness: snapshot berumur > `max_book_age_ms` (default 3000 ms) →
  DITOLAK (`STALE_DATA`).

## 7. Output per Opportunity (wajib)

`gross_edge`, `notional`, `trading_fees`, `slippage_cost`, `gas_cost`,
`leg_risk_cost`, `resolution_risk_cost`, `rounding_cost`, `safety_margin`,
`net_profit ($ dan %)`, `capital_required`, `annualized_return`,
`bundle_size` (ukuran optimal), `fill_probability`, `expected_net_profit`,
status valid/ditolak + `reject_reason` + `reject_detail`.

Semua peluang (valid & ditolak) disimpan ke SQLite untuk dashboard & analisis.

## 8. Fee & biaya yang TIDAK dihitung (sengaja)

- **Taker rebate / maker rebate** — dibayar harian, tier-dependent (opsional, default
  OFF, tercatat terpisah jika diaktifkan).

- Biaya deposit/withdraw via bridge/pihak ketiga (MoonPay dll) — di luar jalur bot.
- Pajak — tanggung jawab user.

## 9. Formula ringkas per bundle

```
net_total = payout_total + sell_notional
            − buy_notional − collateral_total
            − fees − gas − leg_risk − resolution_risk − rounding − safety

capital_total = buy_notional + fees + gas + collateral_total
```

Ukuran optimal `size*` = argmax `net_total(size)` s.t.
`size ≥ min_order_notional per leg`, `capital_total ≤ max_capital_per_trade_usd`,
depth cukup di semua leg. Diuji: `tests/test_costs.py`,
`tests/test_costs_properties.py` (identitas konservasi kas = anti "biaya tak terhitung").
