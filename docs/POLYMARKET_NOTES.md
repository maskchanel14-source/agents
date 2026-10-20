# Polymarket API & Mechanics — Research Notes

> Sumber utama: dokumentasi resmi https://docs.polymarket.com (diakses 2026-10-20 via
> index `https://docs.polymarket.com/llms.txt`). Setiap klaim di bawah ditelusuri dari
> halaman resmi yang dicantumkan di kolom sumber. JANGAN mengandalkan memori — file ini
> adalah ringkasan runtime-research yang dipakai implementasi.

## 1. Permukaan API (endpoint)

| API | Base URL | Fungsi | Sumber |
|---|---|---|---|
| Gamma API | `https://gamma-api.polymarket.com` | Discovery event/market + metadata | [getting-started/api](https://docs.polymarket.com/getting-started/api) |
| CLOB API | `https://clob.polymarket.com` | Order book, order, trade | [getting-started/api](https://docs.polymarket.com/getting-started/api) |
| Data API | `https://data-api.polymarket.com` | Posisi, aktivitas, analytics (cursor pagination, v2) | [getting-started/api](https://docs.polymarket.com/getting-started/api) |
| Relayer API | `https://relayer-v2.polymarket.com` | Submit tx wallet tanpa pegang POL untuk gas | [getting-started/api](https://docs.polymarket.com/getting-started/api) |
| CLOB Market WS | `wss://ws-subscriptions-clob.polymarket.com/ws/market` | Order book/price/lifecycle stream publik | [api-reference/wss/market](https://docs.polymarket.com/api-reference/wss/market) |
| CLOB User WS | `wss://ws-subscriptions-clob.polymarket.com/ws/user` | Order/trade update terautentikasi | [getting-started/api](https://docs.polymarket.com/getting-started/api) |
| RTDS | `wss://ws-live-data.polymarket.com` | Reference price, komentar, trade activity (legacy; dimigrasi ke PolyBolt) | [getting-started/api](https://docs.polymarket.com/getting-started/api), [migrate/rtds-to-polybolt](https://docs.polymarket.com/migrate/rtds-to-polybolt) |

OpenAPI/AsyncAPI tersedia: `clob-openapi.yaml`, `gamma-openapi.yaml`, `data-openapi.yaml`,
`asyncapi.json` (lihat [llms.txt](https://docs.polymarket.com/llms.txt)).

**Catatan sandbox:** domain Polymarket TIDAK dapat diakses dari lingkungan build ini
(egress dibatasi). Kode klien ditulis terhadap spesifikasi resmi di atas dan diverifikasi
lewat unit test + fixture; koneksi live diuji lewat mock/record-replay.

## 2. Struktur Market (Gamma)

Identitas market: `id` (Gamma), `slug`, `conditionId` (hex 0x…). [market-details](https://docs.polymarket.com/market-data/market-details)

Field penting di response Gamma `GET /markets`:

| Field | Arti |
|---|---|
| `version` | `"v1"` = CTF (token id), `"v2"` = Polymarket Protocol V2 (position id). Versi selain v1/v2 = unsupported → skip |
| `outcomes` | JSON-encoded string array, mis. `["Yes","No"]` |
| `outcomePrices` | JSON-encoded string array |
| `clobTokenIds` | JSON-encoded string array (v1/CTF) |
| `positionIds` | array string (v2). Kedua field bisa terisi — pilih via `version` |
| `conditionId` | id kondisi CTF |
| `state/active, closed, acceptingOrders, enableOrderBook, negRisk, restricted, archived` | status |
| `orderPriceMinTickSize` | tick size aktif (0.1 / 0.01 / 0.005 / 0.0025 / 0.001 / 0.0001) |
| `orderMinSize` | **minimum order size dalam USDC (notional)** — bukan jumlah share! Contoh: `5` |
| `feesEnabled` + `feeSchedule {rate, exponent, takerOnly, rebateRate}` | parameter fee per market |
| `events[]`, `endDate`, `startDate`, `closedTime` | waktu |
| `description` | teks kriteria resolusi (WAJIB dicek untuk cross-market & risiko resolusi) |

- Tick size 0.0025 hanya untuk market World Cup *to advance / moneyline / spreads / totals*.
  Selalu baca nilai aktif dari market, jangan berasumsi. [market-details](https://docs.polymarket.com/market-data/market-details)

- `minOrderSize` = minimum USDC notional per order; order di bawah itu ditolak CLOB.
- Status tradeable: `active && !closed && acceptingOrders`. `restricted` = geo-restricted.
- **Augmented negative risk**: cek di EVENT: `enableNegRisk == true && negRiskAugmented == true`.
  Hanya trade **named outcomes**; outcome placeholder/"Other" jangan ditrade langsung
  (definisi "Other" berubah seiring placeholder diklarifikasi). [concepts/negative-risk](https://docs.polymarket.com/concepts/negative-risk)

## 3. Order Book (CLOB REST)

`GET https://clob.polymarket.com/book?token_id=<asset_id>` [market-data/prices-order-books](https://docs.polymarket.com/market-data/prices-order-books)

Response: `market, asset_id, timestamp (epoch ms), hash, bids[], asks[], min_order_size, tick_size, neg_risk, last_trade_price`.
Level = `{price, size}` (string desimal).

**PENTING — urutan level tidak konsisten antar sumber:**

- Dokumen REST menyebut bids ascending & asks descending (best = elemen terakhir).
- Contoh event WS menampilkan bids & asks keduanya ascending.
→ Implementasi **tidak boleh berasumsi urutan**: selalu sort sendiri (bids desc, asks asc)
sebelum walk-the-book. `hash` dipakai untuk deteksi perubahan antar read.

Harga = probabilitas ($0.00–$1.00). Beli = bayar ask; jual = terima bid. Tidak ada batas
ukuran trading, tapi depth menentukan slippage. 1 pUSD collateral → split jadi pasangan
YES+NO; merge kembali → 1 pUSD. [concepts/prices-orderbook](https://docs.polymarket.com/concepts/prices-orderbook)

## 4. WebSocket Market Channel

`wss://ws-subscriptions-clob.polymarket.com/ws/market` [api-reference/wss/market](https://docs.polymarket.com/api-reference/wss/market)

- Subscribe saat connect: `{"assets_ids": ["<id>", ...], "type": "market"}`
- Tambah subscription: `{"operation": "subscribe", "assets_ids": [...]}`
- Ping/pong: `{}`
- Event masuk (`event_type`):
  - `book` — snapshot penuh: `asset_id, market, bids, asks, timestamp, hash`
  - `price_change` — `price_changes[]: {asset_id, price, size, side (BUY/SELL), hash, best_bid, best_ask}`
  - `last_trade_price` — `price, size, fee_rate_bps, side, transaction_hash`
  - `tick_size_change` — `old_tick_size, new_tick_size`
  - `best_bid_ask` — `best_bid, best_ask, spread`
  - `new_market` — metadata + `description` (kriteria resolusi), `clob_token_ids`, `order_price_min_tick_size`, `group_item_title`
  - `market_resolved` — `winning_asset_id, winning_outcome`

Catatan implementasi: sharding koneksi diperlukan untuk ribuan asset (batasi jumlah asset
per koneksi — dokumentasi tidak menyebut angka eksplisit; default konservatif mis. 500
asset/koneksi, configurable). Reconnect dengan backoff + resubscribe; `book` snapshot
dipakai untuk resinkronisasi setelah `price_change` yang tidak sinkron.

## 5. Fee (INTI biaya) — [trading/fees](https://docs.polymarket.com/trading/fees)

Rumus resmi:

```
fee = C × feeRate × p × (1 - p)
```

- `C` = jumlah share diperdagangkan, `p` = harga share (dalam $, 0..1), `feeRate` = base rate market.
- **Hanya taker yang bayar fee. Maker tidak pernah kena fee.**
- Fee dihitung dalam USDC, simetris di sekitar p=0.5 (trade di 30¢ = trade di 70¢).
- Pembulatan fee: **5 desimal**; fee terkecil **0.00001 USDC**; lebih kecil dari itu → dibulatkan jadi 0.
- Fee per kategori (taker fee rate):

| Kategori | Taker Rate | Maker Rate | Maker Rebate |
|---|---|---|---|
| Crypto | 0.07 | 0 | 20% |
| Sports | 0.05 | 0 | 15% |
| Finance | 0.04 | 0 | 25% |
| Politics | 0.04 | 0 | 25% |
| Economics | 0.05 | 0 | 25% |
| Culture | 0.05 | 0 | 25% |
| Weather | 0.05 | 0 | 25% |
| Other / General | 0.05 | 0 | 25% |
| Mentions | 0.04 | 0 | 25% |
| Tech | 0.04 | 0 | 25% |
| Geopolitics | 0 | 0 | — |
| Combos | 0.05 | 0 | 0% |

- Market Geopolitics & world event = **fee-free**.
- Fee tidak pernah di-set di order; dihitung saat match.
- Parameter per market dibaca dari Gamma `feeSchedule {rate, exponent, takerOnly, rebateRate}`
  (exponent = eksponen komponen harga pada kurva fee; default 1 → rumus di atas).
  **Jika fee rate tidak bisa dibaca → peluang INVALID** (aturan hard di cost model).

- `fee_rate_bps` juga muncul di event `last_trade_price` WS.
- Taker Rebate Program: taker bisa mendapat kembali bagian fee berdasarkan tier
  ([programs/taker-rebates](https://docs.polymarket.com/programs/taker-rebates)).
  **Model biaya konservatif: rebate TIDAK dihitung sebagai pengurang biaya** (hanya
  dicatat sebagai upside opsional, default OFF).

## 6. Ukuran & Pembulatan Order

- `size` pada limit order = **jumlah share** (contoh docs: beli 10 share @ 0.52).
- `orderMinSize` Gamma = **minimum USDC notional** per order (contoh: 5).
- Harga harus kelipatan `tickSize` aktif; ukuran share dibulatkan mengikuti pembagian
  tick (lihat CLOB error jika tidak valid). Cost model WAJIB membulatkan:
  harga ke bawah saat beli (conservative), ukuran share ke bawah (floor) agar notional
  dan fee tidak melebihi perkiraan.

- GTD: expiration minimal **3 menit** ke depan; order expire 1 menit sebelum expiry yang
  ditulis (safety threshold) → lifetime efektif min ±2 menit. [trading/place-orders](https://docs.polymarket.com/trading/place-orders)

- Order type lifetime: **GTC**, **GTD**. Order "market" = limit order yang langsung
  match (harga diset agar marketable). Eksekusi arbitrase memakai limit marketable
  (FOK-style: size penuh atau batal — dipilih via flag `orderType` bila didukung
  endpoint; fallback: batalkan sisa & hitung partial-fill risk).

## 7. Auth (CLOB)

[getting-started/api](https://docs.polymarket.com/getting-started/api) — dua lapis:

1. **L1**: EIP-712 typed data `ClobAuthDomain` (chainId 137, name "ClobAuthDomain", v1),
   message `ClobAuth {address, timestamp, nonce, message}`; message standar:
   `"This message attests that I control the given wallet"`.
   `POST /auth/api-key` (create) atau `GET /auth/derive-api-key` (derive) dengan header
   `POLY_ADDRESS, POLY_SIGNATURE, POLY_TIMESTAMP, POLY_NONCE` → `{apiKey, secret, passphrase}`.

2. **L2**: HMAC-SHA256. `message = timestamp + UPPERCASE(method) + path [+ serialized body]`,
   key = base64Decode(secret), signature = URL-safe base64 (dengan padding).
   Header request: `POLY_ADDRESS, POLY_SIGNATURE, POLY_TIMESTAMP, POLY_API_KEY, POLY_PASSPHRASE`.

Order membutuhkan signature order EIP-712 terpisah (struct order ditandatangani wallet)

- L2 untuk request. Batch: `POST /orders` menerima **1–15** signed order per call; hasil
per-order bisa beda (cek `ok/success` tiap entri). Response status order: `live`, `matched`,
`delayed`. [trading/place-orders](https://docs.polymarket.com/trading/place-orders)

**Aturan bot ini:** private key/API key HANYA dari env. Live executor memakai
`py-clob-client` resmi (dependency optional, di-audit) — sesi ini TIDAK PERNAH menandatangani
transaksi (mode live terkunci).

## 8. Negative Risk (Neg-Risk) — [concepts/negative-risk](https://docs.polymarket.com/concepts/negative-risk)

- Event multi-outcome yang mutually exclusive: **1 NO share di market mana pun bisa
  dikonversi jadi 1 YES share di SETIAP market lain** dalam event (konversi atomik,
  via Router+NegRiskModule di V2 / NegRiskAdapter di CTF).

- `negRisk` flag ada di market; konfigurasi `enableNegRisk` + `negRiskAugmented` ada di event.
- Augmented neg risk: named outcomes + additional outcomes (placeholder) + explicit "Other".
  **Hanya named outcomes yang boleh ditrade.** Jika hasil resolusi tidak bernama → "Other"
  menang. Placeholder tidak ditampilkan UI.

- Validasi strategi B: semua outcome harus mutually exclusive & exhaustive; jika ada
  "Other"/placeholder yang tidak jelas → hitung haircut risiko atau skip.

- Konversi NO→YES semua market lain = mekanisme resmi untuk menutup sisi NO.

## 9. Resolusi (UMA & Chainlink TWAP) — [concepts/resolution](https://docs.polymarket.com/concepts/resolution)

- Prediction market: **UMA Optimistic Oracle**. Proposal (bond ±$750 pUSD) → challenge
  period **2 jam** → jika didispute: proposal kedua → jika dispute lagi: DVM vote (±48 jam).
  Timeline: tidak dispute ±2 jam; dispute penuh **4–6 hari**.

- Outcome vote UMA: Proposer menang / Disputer menang / **Too Early** / **Unknown 50-50**
  (market resolve 50/50: **tiap token redeem $0.50** — pasangan YES+NO tetap bernilai $1.00).

- Up-down market: **Chainlink TWAP** (tanpa proses UMA).
- Setelah resolve: trading berhenti; token menang redeem $1; kalah = 0.
- "Additional context" clarification bisa terbit setelah trading (tidak boleh mengubah
  intent fundamental pertanyaan).

- **Implikasi cost model:** modal terkunci minimal 2 jam, bisa 4–6 hari jika dispute →
  opportunity cost modal dihitung via annualized return; haircut resolusi untuk market
  ambigu / tanggal jauh; blacklist kriteria tidak jelas.

## 10. Posisi, Split/Merge/Redeem, pUSD

- Collateral: **pUSD — Polymarket USD** (token collateral untuk semua trading; lihat
  [concepts/pusd](https://docs.polymarket.com/concepts/pusd)). Docs fee masih menyebut
  "USDC" untuk perhitungan fee; angka 1:1 dalam praktiknya (cek runtime; model memperlakukan
  unit fee dalam USDC-pUSD ekuivalen dan TIDAK mengasumsikan konversi).

- Split 1 pUSD → 1 YES + 1 NO; merge balik; redeem token menang $1. Operasi on-chain
  (split/merge/redeem/convert) butuh gas POL di Polygon. Relayer API tersedia agar
  account tidak perlu pegang POL. [trading/positions/manage](https://docs.polymarket.com/trading/positions/manage)

- Neg-risk convert: 1 NO (market A) → 1 YES (semua market lain). Gas cost relevan untuk
  strategi B jika memakai konversi; strategi beli-semua-leg (buy-all-asks) tidak butuh
  konversi on-chain, cukup order taker.

- Estimasi gas live × gas price × POL/USD harus dihitung saat runtime untuk operasi
  on-chain; untuk pure taker arb (beli leg di book) gas on-chain = hanya settlement
  relayer (estimasi kecil, configurable, default konservatif).

## 11. Rate Limit & Error

- Error code reference: [resources/error-codes](https://docs.polymarket.com/resources/error-codes).
- Rate limit: halaman Builder Tiers & Market Making memuat batas request; implementasi
  memakai token-bucket client-side dengan default konservatif + backoff eksponensial saat
  HTTP 429 (nilai eksplisit di-set di config, diverifikasi runtime dari response header
  bila tersedia).

- Matching engine restart: ada jendela maintenance + **post-only mode** setelah restart —
  hindari eksekusi marketable saat mode itu ([trading/matching-engine](https://docs.polymarket.com/trading/matching-engine)).

## 12. Program Rebate (upside, bukan bagian net edge)

- Taker Rebate: tiered, harian, dalam pUSD ([programs/taker-rebates](https://docs.polymarket.com/programs/taker-rebates)).
- Maker Rebate: bagi hasil fee taker (20–25% tergantung kategori) untuk maker.
- Model biaya TIDAK menghitung rebate (konservatif); kalau diaktifkan via config harus
  tercatat terpisah di laporan.

## 13. Kepatuhan / Geoblock

- Market punya flag `restricted` (geo-restricted). Bot TIDAK boleh punya mekanisme
  menghindari geoblock atau pembatasan akun.

- ToS & pembatasan wilayah diringkas di README (lihat README bagian Compliance).

## 14. Catatan versi (Changelog yang relevan)

- Ada **Protocol V2** (position IDs, pUSD, Router/NegRiskModule) berdampingan dengan CTF v1.
- SDK terpadu baru: `@polymarket/client` (TS) & `polymarket` (Python `AsyncPublicClient`).
  Kita pakai REST/WS langsung (kontrol penuh) — SDK resmi dicatat sebagai alternatif.

- Data API v1 → v2 (cursor pagination, response envelope).
- RTDS → PolyBolt untuk price subscription.
- Halaman changelog dibaca ulang setiap sesi riset: [changelog/predictions](https://docs.polymarket.com/changelog/predictions).

## 15. Keputusan teknis terkait data (ringkas)

1. Discovery penuh via Gamma `GET /markets?closed=false&limit=...&offset/keyset` (paginasi
   penuh; docs memuat `GET /markets/keyset` untuk cursor pagination) + refresh berkala +
   event `new_market`/`market_resolved` dari WS untuk delta real-time.

2. Order book: WS market channel (snapshot `book` + `price_change`), REST `GET /book`
   sebagai fallback & rekonsiliasi berkala (hash compare).

3. Staleness: tolak snapshot dengan umur > N ms (default 3000 ms, configurable).
4. Semua harga/size di-parse ke `Decimal` (BUKAN float), unit: harga = USDC/share,
   size = share, notional = harga × size.

5. Urutan level book dinormalisasi (sort sendiri) — lihat §3.
6. Fee tidak tersedia (field hilang/API error) → peluang INVALID (fail-closed).
