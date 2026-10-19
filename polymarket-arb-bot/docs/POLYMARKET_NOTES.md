# Polymarket — catatan riset (sumber resmi)

Tanggal pengambilan: **2026-10-19** (UTC). Semua poin di bawah diambil dari dokumentasi
resmi `docs.polymarket.com` (lewat `fetch_page`) dan data Gamma/CLOB publik. Jika docs
berubah, dokumen ini harus diperbarui sebelum mode `live` dipertimbangkan.

> Catatan lingkungan: dari sandbox, host `clob.polymarket.com`, `gamma-api.polymarket.com`,
> dan `ws-subscriptions-clob.polymarket.com` **tidak bisa dijangkau langsung** (TLS error,
> hanya `github.com`, `pypi.org`, `registry.npmjs.org` yang diizinkan). Data REST real
> diambil lewat tool `fetch_page` dan disimpan sebagai fixture di `tests/fixtures/`.

## 1. Arsitektur API

| Surface | Base | Dipakai bot untuk |
|---|---|---|
| Gamma REST | `https://gamma-api.polymarket.com` | Discovery event/market, metadata fee, tick, min size, neg-risk |
| CLOB REST | `https://clob.polymarket.com` | Orderbook `GET /book?token_id=` (read-only di paper) |
| CLOB WS market | `wss://ws-subscriptions-clob.polymarket.com/ws/market` | Orderbook real-time |
| CLOB WS user | `wss://ws-subscriptions-clob.polymarket.com/ws/user` | (belum dipakai; live only) |

Sumber: https://docs.polymarket.com/getting-started/api.md

## 2. Orderbook

- Endpoint: `GET https://clob.polymarket.com/book?token_id=<asset_id>` → `bids`, `asks`,
  `tick_size`, `min_order_size`, `neg_risk`, `last_trade_price`, `hash`, `timestamp` (ms).
- **Urutan level tidak konsisten di dokumen**: contoh REST menaruh bids naik & asks turun
  (best di ujung array), contoh WS menaruh keduanya naik. Bot **selalu mengurutkan ulang**
  (bids desc, asks asc) — tidak mengandalkan urutan input.
  Sumber: https://docs.polymarket.com/market-data/prices-order-books.md
- Fixture nyata (`tests/fixtures/books/xi_yes_book.json`) mengonfirmasi: REST `/book` untuk
  market Xi Jinping memakai `tick_size` `0.001`, `min_order_size` `5`.
- WS market channel: subscribe `{"assets_ids":[...], "type":"market", "custom_feature_enabled": true}`.
  Event: `book` (snapshot penuh), `price_change` (delta: `size` = agregat baru per level,
  `0` = hapus level, `side` BUY/SELL), `tick_size_change`, `last_trade_price`,
  `best_bid_ask` (butuh `custom_feature_enabled`). Heartbeat: kirim teks `PING` tiap 10 detik.
  Sumber: https://docs.polymarket.com/api-reference/wss/market.md
- Tidak ada nomor sekuens eksplisit per event di docs → bot memakai **timestamp monoton per
  asset** untuk membuang event out-of-order, dan menandai buku stale setiap reconnect sampai
  snapshot `book` baru datang.

## 3. Market: identifier, outcome, versi

- Identifier: `id`, `slug`, `conditionId`. Outcome YES/NO → token/position ID.
- Gamma `clobTokenIds` (JSON string) untuk **CTF / v1**; `positionIds` (array) untuk
  **Polymarket Protocol V2 / v2**. Pilih berdasarkan `market.version`. Index 0 = YES, 1 = NO
  pada market biner. Sumber: https://docs.polymarket.com/market-data/market-details.md
- **Protocol V2 (pUSD)**: collateral sekarang **pUSD** (ERC-20, 6 desimal, di-backing USDC),
  bukan USDC.e langsung. Wrap USDC.e→pUSD lewat `CollateralOnramp`
  (`0x93070a847efEf7F70739046A929D47a521F5B8ee`). Sumber: https://docs.polymarket.com/concepts/pusd.md
- Market Gamma contoh (Xi Jinping, v1) membawa: `negRisk:false`, `feesEnabled:true`,
  `feeSchedule:{exponent:1, rate:0.04, takerOnly:true, rebateRate:0.25}`,
  `orderPriceMinTickSize:0.001`, `orderMinSize:5`, `makerBaseFee`/`takerBaseFee` (1000).
  Fixture: `tests/fixtures/markets/xi_jinping_binary.json` (dipangkas dari respons nyata).

## 4. Trading constraints

- **Tick size**: harga order harus kelipatan `minimum_tick_size`. Nilai bisa 0.1, 0.01, 0.005,
  0.0025 (khusus World Cup tertentu), 0.001, 0.0001. Baca dari market, jangan asumsikan.
- **Min order size**: docs menyebut "minimum USDC notional" di market-details, tapi field
  book menyebut "min_order_size" tanpa satuan. Bot menerapkan **keduanya** (shares ≥ min DAN
  notional ≥ min) — konservatif. Dicatat di `DECISIONS.md`.
  Sumber: https://docs.polymarket.com/market-data/market-details.md#trading-constraints
- Order: `makerAmount`/`takerAmount` dalam base unit 6 desimal (contoh BUY 10 share @0.52 →
  `makerAmount=5200000`, `takerAmount=10000000`). Sumber: https://docs.polymarket.com/trading/place-orders.md

## 5. Tipe order

- **GTC / GTD** (limit). GTD harus ≥ 3 menit ke depan; efektif hidup = `expiration - 60`.
- **FAK** (Fill and Kill): isi sebisanya, sisanya dibatalkan — default market order.
- **FOK** (Fill or Kill): isi penuh atau tidak sama sekali.
- Market order: BUY `amount` = notional USD pra-fee; **fee dibebankan di atas amount**
  (pakai `maxSpend` untuk batas total). Market order wajib `expiration="0"`.
- `postOnly` hanya untuk GTC/GTD (maker). Bot ini **taker-only** (FAK/FOK).
- `secondsDelay` (market.trading.secondsDelay) → order marketable bisa `delayed`. Bot
  memperlakukan `delayed` sebagai pending, bukan fill.
- Sumber: https://docs.polymarket.com/trading/place-orders.md

## 6. Fee (sumber kebenaran: `feeSchedule` per market)

- Rumus resmi: **`fee = C × feeRate × p × (1 − p)`** (C = jumlah share, p = harga share).
- Parameter per kategori: Crypto 0.07; Sports 0.05; Finance/Politics/Mentions/Tech 0.04;
  Economics/Culture/Weather/Other 0.05; **Geopolitics 0 (fee-free)**. Maker fee = 0.
  Maker rebate: 20–25% (Crypto 20%, lainnya 25%).
- Fee **dibulatkan 5 desimal**; fee terkecil 0.00001 USDC. Bot membulatkan **ke atas** (konservatif).
- Fee adalah **USDC**, simetris di sekitar p = 0.5.
- Parameter runtime: `market.trading.feeSchedule` = `{rate, exponent, takerOnly, rebateRate}`
  dan `feesEnabled`. Bot hanya menghitung fee jika `exponent == 1` (bentuk yang didokumentasikan);
  bentuk lain → peluang ditolak (`fee_model_unverified`).
- Sumber: https://docs.polymarket.com/trading/fees.md ; https://docs.polymarket.com/market-data/market-details.md#trading-fees

## 7. Neg-risk (multi-outcome)

- Event dengan outcome saling eksklusif: hanya satu market bisa YES. Market punya flag
  `negRisk`; event punya `enableNegRisk` dan `negRiskAugmented`.
- **Konversi**: 1 No di satu market → 1 Yes di setiap market lain pada event yang sama
  (atomik lewat Router / NegRiskModule untuk v2; Neg Risk Adapter untuk CTF).
- **Augmented neg-risk** (ada outcome "Other" / placeholder yang bisa muncul belakangan):
  hanya trade outcome yang bernama; **outcome "Other" dihindari**. Bot men-skip event augmented
  dan event yang memuat market `negRiskOther=true`.
- Sumber: https://docs.polymarket.com/concepts/negative-risk.md

## 8. Posisi: split / merge / redeem

- **Split**: 1 pUSD → 1 YES + 1 NO (setiap pasangan lengkap). **Merge**: kebalikannya —
  pasangan YES+NO kembali jadi 1 pUSD (tanpa menunggu resolusi). **Redeem**: setelah resolusi,
  token pemenang = $1, pecundang = $0.
- Kontrak: Router `0x12121212006e4CD160D18e3f00711DA5c3372600` (v2, standard & neg-risk);
  CTF CtfCollateralAdapter `0xAdA100Db00Ca00073811820692005400218FcE1f`;
  NegRisk adapter `0xadA2005600Dec949baf300f4C6120000bDB6eAab`; pUSD `0xC011a7E12a19f7B1f670d46F03B03f3342E82DFB`.
- Operasi ini butuh gas (POL) kecuali lewat Relayer (gasless, butuh API key relayer).
  Sumber: https://docs.polymarket.com/trading/positions/manage.md ; https://docs.polymarket.com/resources/contracts.md

## 9. Resolusi

- Market prediction: **UMA Optimistic Oracle**. Challenge 2 jam; bila disengketa → 24–48 jam
  debat + ~48 jam vote DVM; total disengketa **4–6 hari**. Bond proposal ≈ 750 pUSD.
  Hasil 50/50 mungkin (`is_50_50_outcome`). Sumber: https://docs.polymarket.com/concepts/resolution.md
- Up/Down market: Chainlink TWAP (bukan UMA).
- Implikasi: strategi yang menahan posisi sampai resolusi wajib memberi haircut risiko
  (lihat `docs/COST_MODEL.md`).

## 10. Rate limit (IP-based, Cloudflare; per 10 detik kecuali disebut)

- Gamma `/markets` 300, `/events` 500, listing gabungan 900.
- CLOB `/book` 1500; `/books` 500; `/price` 1500; `/markets` (tick) 200.
- Trading (per signer, token bucket): `POST /order` burst 5000/10s, sustained 120000/10min;
  `POST /orders` 2000/10s; `DELETE /cancel-all` 250/10s.
- Bot memakai throttle lokal konservatif (jauh di bawah batas) — lihat `config/default.yaml`.
  Sumber: https://docs.polymarket.com/api-reference/rate-limits.md

## 11. Autentikasi (hanya relevan untuk live)

- L1: EIP-712 `ClobAuth` → `POST /auth/api-key` atau `GET /auth/derive-api-key`.
- L2: HMAC-SHA256 atas `timestamp + METHOD + path + body`, key = base64-decode(secret),
  hasil urlsafe base64. Header: `POLY_ADDRESS, POLY_SIGNATURE, POLY_TIMESTAMP, POLY_API_KEY, POLY_PASSPHRASE`.
- Order: ditandatangani EIP-712. **Bot ini tidak menandatangani apa pun** (lihat `DECISIONS.md`).
  Sumber: https://docs.polymarket.com/getting-started/api.md

## 12. Geografi & hukum (BLOKER untuk live)

- **Indonesia**: Komdigi memblokir Polymarket pada Mei 2026 dan menyatakan prediction market
  sebagai judi online ilegal. Sumber: https://www.coindesk.com/policy/2026/05/25/indonesia-blocks-polymarket-calling-prediction-market-online-gambling-in-disguise
  dan https://en.antaranews.com/news/416715/indonesia-blocks-polymarket-in-attempts-to-eradicate-online-gambling
- Daftar pembatasan Polymarket (docs geoblock) juga memuat US, GB, FR, DE, IT, NL, SG, TH, TW, dll.
  Sumber: https://docs.polymarket.com/api-reference/geoblock ; https://help.polymarket.com/en/articles/13364163-geographic-restrictions
- **Bot tidak memuat logika untuk menghindari geoblock** (tidak ada proxy/VPN). Live trading
  dari Indonesia kemungkinan melanggar hukum setempat — ini harus dikonfirmasi pengguna
  dengan penasihat hukum sebelum mode live mana pun diaktifkan.

## 13. Sumber tambahan yang diperiksa

- `py-clob-client` (PyPI 0.34.6, lisensi tidak tercantum di metadata PyPI, deskripsi
  "Python client for the Polymarket CLOB"). **Tidak dipakai** di build ini: fitur utamanya
  adalah penandatanganan order, yang tidak diaktifkan; dokumen resmi kini mengarahkan ke
  SDK terpadu dan Protocol V2.
- PyPI `polymarket` 0.1.2 — paket pihak ketiga (MattMaximo) untuk ekspor histori odds.
  **Tidak dipakai** (bukan SDK resmi).
