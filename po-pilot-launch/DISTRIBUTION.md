# DISTRIBUTION — halaman PO Pilot

Dokumen kerja untuk menyebarkan halaman. Ditulis supaya bisa dijalankan tanpa mengingat apa pun dari chat.

## 1. URL kanonik (pakai ini, jangan yang lain)

| Halaman | URL | Fungsi |
|---|---|---|
| Landing + checkout | `https://po-pilot-henna.vercel.app/` | konversi ($49 / $249 / cloud $29) |
| Perbandingan | `https://po-pilot-henna.vercel.app/stocky-alternative/` | menangkap pencarian "stocky alternative" |
| Checklist 12 poin | `https://po-pilot-henna.vercel.app/stocky-export-guide/` | lead magnet, tanpa email |
| Jasa audit | `https://po-pilot-henna.vercel.app/audit/` | pendapatan cepat: $250 / $450 / $750 per klien |
| Gambar sosial | `https://po-pilot-henna.vercel.app/og.png` | 1200×630, dipakai otomatis oleh OG/Twitter card |

Jangan bagikan URL deployment (`po-pilot-<hash>-small-signal-studio.vercel.app`) — itu di balik login Vercel
dan akan tampil sebagai halaman login, bukan toko.

## 2. Link ber-UTM per kanal

`?src=` masuk ke kolom `source` di tabel `leads`, jadi kamu bisa lihat kanal mana yang menghasilkan email.
Ganti `src` sesuai tabel di `POSTING-QUEUE.md`:

```
https://po-pilot-henna.vercel.app/?src=shopify-community
https://po-pilot-henna.vercel.app/?src=reddit-shopify
https://po-pilot-henna.vercel.app/?src=reddit-bookkeeping
https://po-pilot-henna.vercel.app/?src=hn
https://po-pilot-henna.vercel.app/?src=x
https://po-pilot-henna.vercel.app/?src=linkedin
https://po-pilot-henna.vercel.app/?src=devto
```

Untuk post yang menyasar kata kunci, arahkan ke halaman panduan, bukan ke landing:
`…/stocky-export-guide/?src=reddit-shopify` — pengunjung dapat nilai dulu, lead-nya tetap tercatat.

## 3. Yang sudah aktif dan bisa diukur

- **Vercel Web Analytics** (cookieless) + **Speed Insights** — sudah dipasang di ketiga halaman.
  Baca di: Vercel → project `po-pilot` → tab **Analytics**. Yang perlu dilihat: pengunjung per halaman,
  referrer (kanal mana), dan berapa yang lanjut ke checkout Polar.
- **Supabase `audit_requests`** — permintaan jasa audit. Query cepat:
  ```sql
  select created_at, email, store_url, sku_count, vendor_count, tier, timeline, pain, status
  from public.audit_requests order by created_at desc limit 50;
  ```
  Balas dengan draft Gmail "Re: your purchasing audit — scope and price confirmed", lalu ubah `status`
  menjadi `quoted` / `won` / `lost` supaya bisa dihitung konversinya.
- **Supabase `leads`** — isi form. Query cepat:
  ```sql
  select created_at, email, store_url, sku_range, source
  from public.leads order by created_at desc limit 100;
  ```
  `source` kosong artinya kunjungan langsung; kalau `source` didominasi satu kanal, gandakan usaha di situ.
- **`/sitemap.xml`** dan **`/robots.txt`** sudah dilayani (sudah diverifikasi live). Google butuh 2–8 minggu
  untuk mengindeks halaman baru — jangan menilai jalur SEO sebelum 30 hari.
- **OG/Twitter card** sudah terpasang di ketiga halaman dengan `og:image` 1200×630. Artinya kalau link
  ditempel di X/LinkedIn/WhatsApp, yang muncul kartu bergambar, bukan link telanjang.

## 4. Yang tinggal kamu klik (5 menit, sekali saja)

1. **Google Search Console** → tambahkan property `po-pilot-henna.vercel.app`.
   Verifikasi lewat **DNS TXT** (paling tahan lama) atau **file HTML**: kalau pakai file HTML, kirim isi
   filenya ke saya — saya taruh di `site/public/` dan deploy, lalu kamu klik Verify.
   Setelah terverifikasi: Submit sitemap `https://po-pilot-henna.vercel.app/sitemap.xml`.
2. **Bing Webmaster Tools** → import dari Search Console (satu klik setelah langkah 1).
3. **Vercel → Analytics → Enable** untuk project `po-pilot` (kalau belum aktif di dashboard).

## 5. Batas teknis yang perlu kamu tahu

- Saya **tidak bisa** posting ke Reddit, X, LinkedIn, HN, dev.to, Medium, MCPize, Glama, Smithery.
  Tidak ada koneksi/token untuk itu, dan mendaftar butuh email/HP kamu.
- Saya **tidak bisa** mengubah repo `po-pilot-mcp` (token sandbox read-only → 403), jadi deskripsi repo,
  topics, dan release notes harus kamu ubah sendiri. Itu salah satu sumber traffic yang belum dimanfaatkan:
  deskripsi repo saat ini mengarah ke checkout Polar, lebih baik diarahkan ke halaman panduan.
- Saya **tidak bisa** submit sitemap ke Google/Bing karena `google.com` dan `bing.com` diblokir dari sandbox.
  Ping manual: Search Console (langkah 4).
- Saya **bisa** mengubah halaman, deploy, dan mengukur — itu yang sudah dikerjakan.

## 5b. Kenapa halaman /audit yang paling cepat menghasilkan uang

Target $1.500: butuh **22 penjualan $49**, atau **2 klien $750**, atau **3 klien $450**.
Satu klien jasa = 5–15 penjualan kit. Karena itu outreach agency (kanal 6 di `POSTING-QUEUE.md`)
sebaiknya diarahkan ke `/audit/`, bukan ke checkout $49:

```
https://po-pilot-henna.vercel.app/audit/?src=agency-email
https://po-pilot-henna.vercel.app/audit/?src=linkedin
```

Aturan main yang penting: **jangan janji tanggal sebelum melihat file**. Baris pertama balasan selalu
konfirmasi lingkup + harga + tanggal, baru minta CSV.

## 6. Ritme 10 menit/hari

| Waktu | Aksi |
|---|---|
| Pagi | buka Vercel Analytics: berapa pengunjung & dari mana |
| Pagi | buka `leads`: ada lead baru? kirim template #1 dari Gmail Drafts |
| Siang | balas semua komentar/DM — ini yang menentukan post naik atau tenggelam |
| Malam | catat 1 baris: `tanggal · kanal · pengunjung · lead · penjualan` |

Kalau setelah 7 hari satu kanal menghasilkan >40 pengunjung tapi 0 lead, masalahnya di halaman (bukan kanal):
cek apakah tombol checkout terlihat tanpa scroll, dan apakah harga muncul sebelum FAQ.
