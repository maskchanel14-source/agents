# DECISIONS.md — Keputusan Engineering Bot Arbitrase Polymarket

File ini mencatat setiap keputusan ambigu + alasannya (sesuai misi: ambil opsi paling
masuk akal, catat, lanjut — tanpa menunggu konfirmasi).

## D0. Batasan platform sesi ini (2026-10-20)

| Keputusan | Alasan |
|---|---|
| Semua kerja di-commit ke branch sesi `arena/4cbec802-agents` (bukan `feat/polymarket-arb-bot`) | Arena.ai mengikat sesi ke branch ini; branch lain tidak ter-associate ke sesi dan dilarang oleh environment. PR dibuka dari branch ini. Setara fungsi dengan permintaan "branch feature, jangan push main". |
| Push hanya ke `arena/4cbec802-agents`, PR dari branch itu | Aturan environment; `main` tidak pernah disentuh. |
| Live trading TIDAK diaktifkan; tidak ada order/signature asli yang dibuat | Misi melarang; mode live terkunci ganda (env `LIVE_TRADING=true` + file konfirmasi lokal `LIVE_TRADING_CONFIRMED`). |
| Domain Polymarket (gamma/clob/ws/docs) tidak dapat di-socket dari sandbox (egress terbatas ke github/npm/pypi); dokumentasi resmi dibaca via page-fetch tool, koneksi live diverifikasi user di Windows | Data riset tetap dari sumber resmi (docs.polymarket.com, diakses 2026-10-20). Klien API diuji dengan fixture + mock; recorder disediakan untuk merekam live dari mesin user. |

## D1. Repo & struktur

| Keputusan | Alasan |
|---|---|
| Bot ditaruh di root repo sebagai package `bot/` + `tests/` + `config/` + `start_bot.bat`, dokumentasi di `docs/`, README monorepo diberi section baru (tidak ditimpa) | Repo ini adalah monorepo skills (`plugins/`, `tools/`) yang berguna sebagai library skill; konten lama harus dipertahankan. DoD meminta path root (`start_bot.bat`, `README.md`, `DECISIONS.md`). |
| Bahasa Python 3.11 + asyncio (default misi) | Tersedia di environment & Windows; ekosistem test lengkap. |
| HTTP/WS server+client memakai `aiohttp` | Satu dependency untuk REST client, WS client (reconnect), dan dashboard server; wheel Windows tersedia (tidak butuh compiler). |
| Frontend dashboard: vanilla JS + CSS + font lokal di-bundle, tanpa build step, tanpa CDN | Syarat 5b: jalan offline, jalan langsung dari repo di PC Windows. |
| DB: SQLite (stdlib `sqlite3`) | Persist state/peluang/trade tanpa dependency server. |

## D2. Audit & dependency pihak ketiga

Aturan misi: audit kode pihak ketiga yang menyentuh wallet; lebih baik dependency
resmi daripada copy-paste. Hasil audit (2026-10-20):

| Paket | Sumber | Keputusan | Hasil audit |
|---|---|---|---|
| `aiohttp` | PyPI (aio-libs, widely used) | dipakai | Tidak ada postinstall mencurigakan; pure HTTP/WS. Tidak menyentuh wallet. |
| `PyYAML` | PyPI | dipakai | Loader `safe_load` saja (hindari arbitrary object). |
| `python-dotenv` | PyPI | dipakai | Loader env standar. |
| `websockets` | PyPI | dipakai (opsional, fallback WS) | Library WS standar. |
| `pytest`, `pytest-asyncio`, `pytest-cov`, `hypothesis` | PyPI | dev only | Test tooling standar. |
| `py-clob-client` (Polymarket resmi) | GitHub Polymarket/py-clob-client | OPTIONAL, hanya untuk mode live (`requirements-live.txt`); mode paper/backtest tidak membutuhkannya | Live executor hanya meng-import saat `LIVE_TRADING=true`. Tidak di-copy ke repo. Kode signing resmi (EIP-712) diimplementasi sendiri dari spesifikasi docs (bukan copy-paste), untuk simulator & unit test. |
| Repo luar lain (bot arb open-source) | — | DILEWATI | Tidak ada yang menyentuh wallet yang lolos audit & diperlukan; strategi arb diimplementasi dari spesifikasi resmi. |

DIPAKAI dari repo skills monorepo ini (guidance, bukan runtime):
`tdd-workflows` (disiplin red-green-refactor untuk costs.py & strategies),
`unit-testing` (struktur test & coverage), `debugging-toolkit` / `error-debugging`
(akar masalah saat test gagal), `comprehensive-review` (review mandiri sebelum PR),
`python-development/async-python-patterns` (arsitektur asyncio), 
`python-development/python-anti-patterns` (checklist review),
`ui-design/design-system-patterns` + `visual-design-foundations` (HUD design system),
`blockchain-web3/web3-testing` (prinsip test untuk modul yang menyentuh on-chain),
`security-scanning` (secret scan akhir).

DILEWATI (tidak relevan): skill konten/marketing/shopify/game/mobile/Solidity-ERC
spesifik, `frontend-mobile-development` (butuh framework build — kami pakai vanilla JS),
`dataviz` (tidak ada di repo; visualisasi dibuat manual vanilla canvas/SVG).

## D3. Model biaya (inti)

| Keputusan | Alasan |
|---|---|
| Semua kalkulasi `Decimal` (dari string), bukan float | Syarat misi; presisi uang. |
| Fee: `fee = C × rate × (p×(1-p))^exponent`, dibulatkan 5 desimal (ROUND_HALF_UP), min 0.00001 USDC else 0 | Rumus resmi docs/trading/fees: `fee = C × feeRate × p × (1-p)`; `exponent` dari `feeSchedule` ("exponent applied to the price component"); exponent=1 persis rumus resmi & tabel resmi (dicek unit test terhadap tabel Crypto/Sports/Finance). |
| Fee rate diambil per-market dari Gamma `feeSchedule`; jika tidak tersedia → peluang INVALID | Aturan misi (fail-closed). |
| Maker rebate & taker rebate TIDAK mengurangi biaya (default OFF, dicatat terpisah) | Konservatif; rebate dibayar harian & tier-dependent, bukan saat trade. |
| Gas on-chain: untuk operasi user (approve/split/merge/redeem/convert). Eksekusi taker via CLOB = gas 0 bagi user (settlement oleh operator exchange; hybrid-decentralized) | Docs concepts/prices-orderbook: matching off-chain, settlement on-chain oleh operator; user tidak bayar gas per trade. Gas tetap dimodelkan untuk konversi neg-risk & redeem via config (estimasi gas × POL/USD). |
| Slippage: walk-the-book per level (fee per level, bukan fee pada harga rata-rata) | Fee tergantung p; p di tiap level berbeda. Lebih akurat & konservatif. |
| Urutan level book TIDAK diasumsikan; selalu sort sendiri | REST doc: asks descending; contoh WS: ascending. Defensive. |
| Ukuran optimal: min(depth semua leg, cap modal per trade, cap exposure, cap event) lalu floor ke size decimals; tolak jika notional < `orderMinSize` (USDC) | Struktur market resmi. |
| Pembulatan konservatif: harga beli di-ceil ke tick, harga jual di-floor ke tick, size di-floor | Menghindari profit palsu dari pembulatan. |
| Peluang hanya VALID jika net profit > safety_margin (config) SETELAH semua biaya | Syarat misi. |
| Annualized return dihitung dengan modal terkunci sampai endDate (atau estimasi resolusi), ditolak jika < threshold | Opportunity cost modal. |
| Latency/staleness: snapshot > N ms (default 3000) → tolak | Syarat misi. |
| Haircut resolusi ambigu (config) + blacklist kriteria tidak jelas (regex/heuristik + manual list) | Risiko UMA dispute. |
| Fee tidak tersedia / parse gagal → INVALID, bukan assume 0 | Fail-closed. |

## D4. Strategi

| Keputusan | Alasan |
|---|---|
| A. Intra-market binary: beli YES ask + NO ask jika total semua biaya < $1 payout | Misi §3A. Pakai ask, bukan last/mid. |
| B. Multi-outcome: Σ ask semua YES < 1 (setelah biaya) → beli semua leg; varian NO-side via konversi neg-risk dihitung terpisah | Misi §3B. Validasi mutually-exclusive & exhaustive via flag negRisk + deteksi "Other"/placeholder → haircut atau skip. |
| C. Cross-market logis: diimplementasi dengan gate ketat (resolusi kata per kata harus cocok via similarity + keyword-exclusion), default OFF sampai lolos validasi presisi | Misi §3C "opsional, aktifkan hanya jika presisi bisa dijamin". |
| D. Cross-venue: interface + stub terflag, default OFF, tidak aktif (tidak ada venue lain yang kriterianya identik terverifikasi) | Misi §3D. |
| Strategi yang tidak lengkap datanya di-skip, bukan ditebak | Akurasi > kecepatan. |

## D5. Eksekusi & risiko

| Keputusan | Alasan |
|---|---|
| Default mode = `paper`; `live` butuh `LIVE_TRADING=true` + `live_trading.confirmed` + passphrase `LIVE` di launcher | Pengaman ganda sesuai misi 5c. |
| Order eksekusi (simulasi & live): limit marketable FAK/FOK dengan max/min price guard | Docs: market order = limit marketable; FAK sisa dibatalkan (minimalkan leg risk); FOK untuk arb penuh. |
| Leg risk: FOK utama; fallback FAK + model expected loss unhedged (prob partial × sisi berlawanan) | Misi §4. |
| Fill probability model: f(depth buffer, umur book, ukuran relatif, latency) — dipakai paper trading | Misi §3b (jangan optimis). |
| Kill switch: file `KILL_SWITCH` + endpoint dashboard (token + konfirmasi 2 langkah) | Misi 5b/6. |
| Idempotency order: client order id deterministik (opportunity id + leg + nonce) | Misi §6. |
| Reconciliation posisi/order dengan API berkala + saat start | Misi §6. |

## D6. Dashboard

| Keputusan | Alasan |
|---|---|
| aiohttp server bind `127.0.0.1` saja, SSE untuk push data (satu arah, cukup untuk HUD) | Aman & sederhana; WS hanya untuk aksi kontrol via POST + token. |
| Nama dashboard "ARC-TERMINAL" (original), estetika HUD gelap-cyan tanpa aset Marvel | Misi 5b melarang aset berhak cipta. |
| Font: bundle lokal (dihasilkan sebagai glyph CSS sederhana / font OFL di-download manual oleh user jika perlu — default memakai sistem monospace stack) | Sandbox tidak boleh mengunduh font pihak ketiga sembarangan; lisensi bebas diperlukan. Keputusan: pakai `ui-monospace, 'Cascadia Mono', Consolas` stack + styling techno, TANPA file font eksternal (aman lisensi, offline). |
| Dashboard crash tidak boleh mematikan bot (task terpisah, error di-catch) | Misi 5b. |
| Sound OFF default; `prefers-reduced-motion` dihormati; update di-throttle ~4 fps | Misi 5b. |

## D7. Launcher Windows

| Keputusan | Alasan |
|---|---|
| `start_bot.bat` CRLF, ASCII-safe, `cd /d "%~dp0"`, menu, marker install, pause saat error | Misi 5c. |
| `start_bot_background.bat` + `stop_bot.bat` (kill switch file) | Misi 5c (opsional, prioritas rendah). |
| Validasi .bat di Linux: static lint (label/goto/quote/CRLF/ascii) + dokumentasi checklist manual Windows | Linux tidak bisa menjalankan batch asli. |

## D8. Data & FEASIBILITY

| Keputusan | Alasan |
|---|---|
| `python -m bot.record` merekam orderbook live (WS/REST) ke SQLite/NDJSON; fixture replay untuk backtest | Misi §3b, §7. |
| Karena sandbox tidak bisa konek ke Polymarket, FEASIBILITY.md berisi (a) hasil replay fixture yang TEREKAM + (b) template laporan + instruksi menjalankan recorder di Windows; angka live ditandai "belum terverifikasi" | Kejujuran sesuai misi; jangan mengarang angka live. |
| Backtest tanpa lookahead: replay event berurutan waktu, keputusan hanya dari data ≤ t | Misi §5d. |

## D9. Belum selesai / terblokir

- Live paper-run 30–60 menit terhadap data Polymarket asli: TIDAK mungkin dari sandbox
  (egress diblokir). Pengganti: replay fixture + recorder siap pakai + checklist untuk
  menjalankan `python -m bot --mode paper` di Windows (lihat REPORT.md).
- Angka gas POL/USD live: fallback config konservatif, runtime RPC opsional.
- Verifikasi emulator batch .bat: tidak tersedia di Linux → static lint + checklist manual.
