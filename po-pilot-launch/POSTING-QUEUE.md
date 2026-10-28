# POSTING QUEUE — PO Pilot

Semua teks di bawah siap tempel. Urutannya sudah diatur dari yang paling aman ke paling berisiko.
Aturan besi: **satu kanal, satu teks, jangan pernah posting teks yang sama dua kali.** Copy-paste identik
antar-subreddit adalah cara tercepat kena shadowban.

Link dilengkapi `?src=` supaya kelihatan lead datang dari kanal mana (masuk ke kolom `source` di Supabase).

| # | Kanal | Siapa | Link yang dipakai | Ekspektasi |
|---|---|---|---|---|
| 1 | Shopify Community Forum | kamu | `https://po-pilot-henna.vercel.app/?src=shopify-community` | 1–3 penjualan |
| 2 | r/shopify | kamu | `https://po-pilot-henna.vercel.app/?src=reddit-shopify` | 2–5 |
| 3 | r/Bookkeeping | kamu | `https://po-pilot-henna.vercel.app/?src=reddit-bookkeeping` | 1–3 |
| 4 | Show HN | kamu | `https://po-pilot-henna.vercel.app/?src=hn` | 0–10 (variasi tinggi) |
| 5 | X / Twitter thread | kamu | `https://po-pilot-henna.vercel.app/?src=x` | 0–2 |
| 6 | LinkedIn | kamu | `https://po-pilot-henna.vercel.app/?src=linkedin` | 0–2 (agency $249) |
| 7 | dev.to / Medium | kamu | `https://po-pilot-henna.vercel.app/?src=devto` | 0–3 |
| 8 | Halaman SEO + sitemap | **sudah dikerjakan** | `/stocky-alternative/`, `/stocky-export-guide/` | 2–8 minggu |

Jadwal: kanal 1 hari ini, kanal 2 besok, kanal 3 lusa, kanal 4 di hari kerja pagi WIB (jam 20.00–22.00 WIB
= pagi Pantai Timur AS), kanal 5–6 menyusul, kanal 7 kapan saja.

---

## 1. Shopify Community Forum

Kategori: **Shopify Discussions** atau **Retail and Point of Sale**. Paling aman karena tidak ada sistem karma.

**Judul:**
```
Rebuilding Stocky's supplier lead times and carton rounding from the exported PO CSVs (what worked)
```

**Isi:**
```
When Stocky went read-only after August 31, two gaps hit purchasing immediately:

1. There was never a "Download suppliers" button, so vendor lead times, pack multiples and MOQs only exist
   inside your historical purchase orders. Whatever you don't export while the read-only window is open
   has to be reconstructed from invoices by hand later.
2. Shopify's native Purchase Orders are a good filing cabinet for drafts, but Admin doesn't calculate
   stockout-adjusted reorder points, doesn't round quantities to supplier case packs, and doesn't check a
   vendor's minimum order value or free-freight threshold.

What worked for us, in order:

- Export PO history first, not products. Products you can re-export any time; PO history is the part with
  an expiry date.
- Derive lead time per vendor from received_at minus created_at across every PO. Use the standard
  deviation, not just the average — that's your safety stock.
- Infer the case pack from the quantities you actually ordered. If every order is a multiple of 12, the
  pack is 12.
- Record MOQ twice: minimum units AND minimum order dollars. Most stores track one and get burned by the
  other.

I wrote the full 12-step version up here, free, no email required:
https://po-pilot-henna.vercel.app/stocky-export-guide/?src=shopify-community

Happy to dig into weird CSV column headers if anyone is still untangling their export.
```

---

## 2. r/shopify

**Aturan main:** taruh link GitHub open-source di body (bukan link jualan). Link checkout hanya di komentar
kalau ditanya. Balas komentar dalam 2 jam pertama.

**Judul:**
```
Stocky went read-only and never let us export supplier rules, so I rebuilt the purchasing math from the PO CSVs
```

**Isi:**
```
Two things bit our purchasing workflow when Stocky went read-only:

1. Vendor lead times, carton multiples and MOQs only lived inside Stocky's purchase order history. No
   "download suppliers" button, no supplier export.
2. Native Admin POs store drafts fine, but they don't adjust velocity for days a SKU was out of stock,
   don't round to case packs, and don't enforce a vendor's dollar minimum or free-freight threshold.

Most replacement apps we looked at price per SKU per month once you're past a few hundred SKUs. Shopify's
own storefront MCP only handles shopper carts and checkout, nothing on purchasing or AP.

So I rebuilt the purchasing side as a small MIT-licensed MCP server (`po-pilot-mcp`, TypeScript, runs
locally in Claude Desktop / Cursor / n8n, no database, no required API keys):

- `migrate_stocky_csv_snapshot` — drop in the exported Stocky PO CSV, it computes each vendor's observed
  lead time (mean + stdev from Created → Received), infers carton multiples from order history and grabs
  the latest unit cost per SKU.
- `build_supplier_purchase_orders` — stockout-adjusted velocity, Z-score safety stock, carton rounding,
  MOQ/free-freight top-ups, landed cost with tariff + freight, outputs the Shopify Draft PO CSV and the
  POS transfer CSV (SKU, Barcode, Quantity).
- `reconcile_po_three_way_match` — PO vs dock receiving vs supplier invoice, catches silent unit-cost
  creep and short-ships, outputs a debit memo plus verified-only QuickBooks/Xero bill CSVs.

Free and MIT on GitHub (`npx -y po-pilot-mcp@1.0.0`, has `demo_mode: true` if you want to test the math
before touching store data):
https://github.com/maskchanel14-source/po-pilot-mcp

I also wrote up the export checklist we used before the read-only window closes, since that part expires:
https://po-pilot-henna.vercel.app/stocky-export-guide/?src=reddit-shopify

If you have weird Stocky CSV headers or multi-location transfer quirks, drop a sample header row in the
comments and I'll add parser support.
```

---

## 3. r/Bookkeeping

**Judul:**
```
A deterministic 3-way match I open-sourced for clients whose supplier invoices drift from the PO
```

**Isi:**
```
For wholesale and Shopify inventory clients, supplier invoices routinely drift from the original PO:
$0.25–$0.50 per unit creep, short-shipped cartons billed in full, freight above the agreed cap.

I got tired of doing the same comparison in Excel, so I open-sourced a small tool that runs a penny-exact
3-way match across PO, dock receiving log and vendor invoice, then outputs:

1. A line-by-line variance audit classified HOLD_AND_DISPUTE / APPROVE_SHORT_PAY / APPROVE_FULL_PAYMENT
2. QuickBooks Online and Xero bill CSVs containing only verified received quantities at contracted PO
   costs, so unapproved surcharges never reach AP
3. A formatted vendor debit memo you can send to the supplier's AR team

It's deterministic on purpose — no LLM guessing at the arithmetic. MIT, runs locally via
`npx -y po-pilot-mcp@1.0.0` with `demo_mode: true`: https://github.com/maskchanel14-source/po-pilot-mcp

The part I'd genuinely like feedback on: split-pallet receiving, tariff surcharges, and credit memo
workflows. The 3-way match in the written-up form is here:
https://po-pilot-henna.vercel.app/?src=reddit-bookkeeping
```

---

## 4. Show HN

**Aturan:** judul tanpa clickbait, jangan minta upvote, jangan taruh link jualan di body. Jawab pertanyaan
teknis dengan detail — HN menghukum marketing dan menghargai keputusan desain.

**Judul:**
```
Show HN: Deterministic purchase-order math for Shopify, as an MCP server
```

**Isi:**
```
Stocky, Shopify's inventory/purchasing app, went read-only on 31 Aug 2026. The awkward part isn't the
inventory count — it's that vendor lead times, carton multiples and MOQs only ever lived inside its
purchase order records, and there was no supplier export.

I built po-pilot-mcp: an MCP server that takes your exported CSVs (or an optional read-only Admin token)
and does the arithmetic in plain code rather than in the model:

- stockout-adjusted daily velocity (units / (days - stockout days))
- Z-score safety stock, reorder point, ABC tiering
- carton rounding, MOQ unit floor, minimum-order-dollar and free-freight top-up
- landed cost with tariff + freight, optional Open-to-Buy cash cap
- 3-way match (PO vs receiving vs invoice) producing QBO/Xero bill CSVs

Design choices worth arguing about: it's stateless with no database, it never writes to the store, demo
mode is the default so the first run touches no real data, and the CSV parsers tolerate renamed columns
because every exporter renames them.

TypeScript, MIT, no required API keys: https://github.com/maskchanel14-source/po-pilot-mcp
Happy to answer questions about the matching rules or the CSV edge cases.
```

---

## 5. X / Twitter thread

```
Stocky shut down on Aug 31. Everyone talked about inventory counts.

The real damage was quieter: vendor lead times, carton multiples and MOQs only existed inside Stocky's
purchase order history. There was never a "download suppliers" button.

Thread on rebuilding it from CSVs 🧵

1/ Lead time: received_at − created_at, per vendor, across every past PO. Take the mean for reorder
points, the stdev for safety stock, the max for planning. One number is not enough.

2/ Carton multiples: look at what you actually ordered. If every quantity is a multiple of 12, the pack is
12. Round UP. Ordering 47 when the pack is 12 means you're short, not clever.

3/ MOQ comes in two flavours and stores track one: minimum units per SKU, and minimum order dollars per
vendor. Satisfy the units, miss the free-freight line, pay $60 freight on a $420 order.

4/ Velocity: units ÷ days is wrong for anything that stocked out. Sold-out days drag the average down and
you under-order your best seller. Use units ÷ (days − stockout days).

5/ Safety stock: Z × σ × √lead_time. 95% service = 1.65. If nobody in your store can say where that number
came from, that's the actual problem.

I put the full 12-step checklist up free (no email): https://po-pilot-henna.vercel.app/stocky-export-guide/?src=x
```

---

## 6. LinkedIn (target: agency / 3PL / fractional CFO)

```
Kalau kamu pegang klien Shopify yang masih bikin purchase order di spreadsheet setelah Stocky dimatikan
31 Agustus lalu, bagian tersulitnya bukan stok.

Yang hilang itu aturan vendor: lead time aktual, kelipatan karton, MOQ unit dan MOQ dolar. Semuanya cuma
hidup di riwayat purchase order Stocky, dan tidak ada tombol export supplier.

Yang sekarang saya pakai untuk klien: satu set tool deterministik (MCP) yang membaca CSV ekspor Stocky,
membangun draft PO siap impor ke Shopify Admin, dan menjalankan 3-way match PO vs penerimaan gudang vs
invoice supplier → CSV bill QuickBooks/Xero hanya untuk baris yang benar-benar cocok.

Lisensi Agency $249 sekali bayar untuk sampai 10 toko klien. Core-nya MIT dan gratis dites dulu.

Kalau mau, saya jalankan satu ekspor PO klienmu dan kirim hasil before/after-nya gratis — contoh nyata
lebih meyakinkan daripada halaman marketing saya: https://po-pilot-henna.vercel.app/?src=linkedin
```

---

## 7. dev.to / Medium (artikel, 900–1200 kata)

Judul: **"Stocky is gone: rebuilding Shopify's purchasing rules from a CSV before the export window closes"**

Kerangka: masalah (bukan stok, tapi aturan vendor) → 4 export yang wajib → rumus lead time & safety stock →
jebakan MOQ ganda → 3-way match → link checklist + repo. Ambil isi dari `stocky-export-guide` dan
`stocky-alternative`, jangan tulis ulang dari nol. Taruh link `?src=devto` di paragraf terakhir saja.

---

## Checklist sebelum posting

- [ ] Sudah baca aturan subreddit/forum hari itu (aturan berubah, akun baru sering kena filter otomatis)
- [ ] Link GitHub (gratis) di body, link checkout hanya di komentar
- [ ] 2 jam pertama dipakai untuk balas komentar — ini yang menentukan apakah post naik atau tenggelam
- [ ] Kalau post dihapus moderator: jangan repost teks yang sama, tanya moderatornya dulu
- [ ] Catat hasilnya: kunjungan, lead, penjualan per kanal (`?src=` masuk ke kolom `source`)
