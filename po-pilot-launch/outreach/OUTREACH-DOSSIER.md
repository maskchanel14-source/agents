# Dossier outreach: audit purchasing untuk partner akuntansi

Status per 29 Oktober 2026. Dokumen ini merangkum apa yang sudah dikirim, apa yang
dibatasi, siapa berikutnya, dan kapan harus bergerak. Angka diambil dari
`ledger.json`, bukan dari ingatan.

---

## 1. Angka pokok

| Ukuran | Nilai |
| --- | --- |
| Email terkirim | 20 |
| Dalam jendela waktu | 63 menit, 28 Okt 19:43 sampai 20:46 UTC |
| Domain berbeda | 20, satu email per domain |
| Bounce | 0 |
| Balasan | 0 |
| Anggaran hari ini | 20 dari 20 terpakai |

Nol balasan bukan kegagalan pada tahap ini. Dua puluh kiriman dingin dengan
penargetan wajar menghasilkan 0 sampai 1 balasan. Yang menentukan adalah apa yang
terjadi pada hari ke-3 dan ke-7.

## 2. Siapa yang dikirimi

**Gelombang 1, tujuh firma akuntansi.** ConnectBooks, Social Commerce Accountants,
Think Accounting, Bookkeeper Superhero, Fox Clever, Rocket Bookkeeper, EcomBalance.

**Gelombang 2, enam fractional CFO.** TYM Consulting, Ascent CFO, CFO Lifeline,
Mastery CFO, MT Bachani CPA, Judith Hobdell.

**Gelombang 3, tujuh campuran.** Elver Accountants, Custom CPA, James Scott,
Onflair, DTCCOO Ventures, DTC Ventures, NorthPeak.

Pembagiannya disengaja. Enam CFO menerima sudut kas: reorder point yang jadi
tebakan, dan biayanya muncul sebagai inventory, bukan expense, sehingga tidak
pernah tampak di P&L sebagai kesalahan. Tujuh akuntan menerima sudut costing dan
pencocokan invoice.

## 3. Kenapa akuntan, bukan agency desain

Rencana pertama adalah menghubungi agency Shopify. Itu pembeli yang salah. Agency
desain menyerahkan toko selesai peluncuran dan tidak menyentuh purchase order lagi.
Yang punya masalahnya adalah orang yang tiap bulan harus mencocokkan invoice
supplier ke PO yang sudah hilang.

Konsekuensi kedua: tawarannya bukan "rekrut saya". Bookkeeper dengan 40 klien tidak
akan menyerahkan daftar kliennya. Tawarannya adalah subkontrak dengan harga tetap di
belakang engagement yang sudah ada, dan satu kalimat yang mengerjakan seluruh
bujukan: **klien tetap milik mereka, dan hasil kerjanya mereka tagih sendiri.**

## 4. Celah pasar yang dipakai

Aplikasi pengganti Stocky berlimpah dan murah: Stockful 19,99 dolar per bulan,
Monocle 47, Prediko 49, ReplenishRadar 99, Cin7 349. Semuanya menjual sistem baru
untuk dijalankan mulai sekarang.

Tidak satu pun membangun ulang riwayat yang sudah ada, karena itu kerja tangan,
bukan perangkat lunak. Itulah celahnya: pekerjaan sekali jalan dengan lingkup tetap
yang mengubah ekspor mati menjadi catatan biaya dan supplier yang bisa dipakai.

## 5. Fakta yang menopang setiap email

| Fakta | Sumber |
| --- | --- |
| Stocky berhenti penuh 31 Agustus 2026 | Shopify Help Center |
| Ekspor read-only terbuka "at least 90 days" setelahnya, tanpa tanggal akhir | Shopify Help Center |
| Karena itu penutupan paling cepat 29 November 2026 | turunan dari dua baris di atas |
| Supplier tidak pernah bisa diekspor dari Stocky | Shopify Help Center |
| Riwayat PO dan stocktake tidak pindah ke alat bawaan Shopify | Shopify Help Center |
| Alat bawaan Shopify menjaga kuantitas, bukan average cost dan landed cost | Woodard Report, 23 Juli 2026 |

Tanggal 29 November adalah satu-satunya klaim di seluruh materi yang punya tenggat,
dan itu juga satu-satunya yang bisa diverifikasi penerima dalam tiga puluh detik.

## 6. Batas kirim yang berlaku

Batas resmi Gmail gratis 500 per hari. Angka itu kuota teknis, bukan anggaran
reputasi. Ambang yang sebenarnya menentukan adalah keluhan spam di bawah 0,3 persen.
Pada volume 20, satu keluhan saja sudah 5 persen.

Patokan yang dipakai: 20 per hari, jarak 3 menit, 15 per jam, langit-langit 40.
Ditegakkan oleh `send-budget.py` yang membaca `ledger.json` dan menolak kiriman
yang melewati batas.

Aturan berhenti: empat kegagalan beruntun, dua bounce dalam dua puluh kiriman, atau
satu keluhan spam. Berhenti berarti berhenti, bukan "kurangi sedikit".

## 7. Yang membatasi sekarang bukan Gmail

Dua puluh kiriman menghabiskan sepertiga kolam firma akuntansi dan CFO ecommerce
berbahasa Inggris yang memenuhi syarat: alamat publik di situs sendiri, MX hidup,
dan alasan spesifik untuk menghubungi mereka.

Perkiraan realistis ukuran kolam itu 60 sampai 90 firma. Dengan 20 per hari, habis
dalam empat hari.

Batch 3 sudah disiapkan dan belum dikirim: Unloop, Fusion CPA, The Ecommerce
Accountants, Irvine Bookkeeping, lalu tiga 3PL sebagai tes terpisah (Encore, ShipCalm,
SHIPHYPE). Tujuh firma. Segmen 3PL dicatat sebagai eksperimen, bukan keyakinan,
karena mereka menagih per order dan per pallet sehingga advisory 250 dolar terasa
asing bagi mereka.

## 8. Jadwal yang tidak bisa digeser

| Tanggal | Tindakan |
| --- | --- |
| 31 Oktober | Follow-up hari ke-3 untuk 20 penerima. Satu informasi baru: jebakan MOQ unit versus minimum order value. |
| 4 November | Follow-up hari ke-7. Hanya tenggat, tanpa tawaran. |
| Setelah itu | Berhenti. Tidak ada email keempat. |

Balasan apa pun membatalkan sekuens untuk alamat itu, permanen.

## 9. Aritmatika target

Target 1.500 dolar. Dua engagement 750 dolar, atau tiga engagement 450 dolar.
Pada reply rate 5 persen dan closing 20 persen dari balasan, itu berarti 200 sampai
300 kiriman tertarget.

Dua puluh sudah terkirim. Sisanya butuh kolam yang lebih besar, atau segmen baru,
atau harga yang lebih tinggi per engagement. Yang tidak akan berhasil adalah
menambah volume tanpa memperbaiki penargetan.

## 10. Empat hal yang bukan pekerjaan saya

Pembelian domain, penyetelan mailbox, pengiriman dari akun sendiri, dan keputusan
apakah nama studio dipertahankan. Yang terakhir sudah diputuskan pemilik pada
29 Oktober: tetap Small Signal Studio, tetap dari Gmail, domain ditunda.

---

## Lampiran: berkas yang menyertai dokumen ini

| Berkas | Isi |
| --- | --- |
| `SENDING-POLICY.md` | Batas kirim, aturan stop, kebijakan identitas pengirim |
| `PARTNER-RESEARCH.md` | Riset pasar, harga pembanding, alasan memilih dan menolak |
| `SENT-2026-10-29.md` | Tujuh kiriman pertama dan teks follow-up |
| `SENT-2026-10-28-batch2.md` | Tiga belas kiriman berikutnya |
| `TARGETS-BATCH-3.md` | Tujuh target berikutnya, terverifikasi |
| `ledger.json` | Catatan setiap kiriman, sumber angka di dokumen ini |
| `send-budget.py` | Penegak batas kirim |
