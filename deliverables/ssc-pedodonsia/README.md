# SSC pada gigi desidui dan gigi permanen muda: berkas presentasi

Folder ini berisi satu paket presentasi 10 menit untuk IIK Bhaktiwiyata, ditambah dokumen pendukung. Semua angka di slide dapat dilacak ke `research_notes.md`.

## Berkas

| Berkas | Isi | Dipakai untuk |
|---|---|---|
| `ssc-pedodonsia.html` | Deck utama, 18 slide, interaktif | Presentasi langsung, dibuka di browser |
| `ssc-pedodonsia.pptx` | Cadangan statis 18 slide + catatan pembicara | Bila ruang presentasi hanya menyediakan PowerPoint |
| `ssc-pedodonsia.pdf` | Cetakan 13,333 × 7,5 inci, 18 halaman | Dibagikan atau dicetak sebagai handout |
| `research_notes.md` | Catatan riset, 33 sumber Vancouver, tingkat bukti | Rujukan angka dan klaim |
| `protokol_klinis.md` | Protokol lengkap 10 langkah + Hall + penyulit + checklist | Dibawa ke klinik |
| `gaya_bahasa.md` | Repo humanizer yang dibaca, aturan yang diambil dan ditolak | Catatan metode penulisan |
| `catatan_skill_repo.md` | Skill repo yang dipakai dan dilewati, beserta alasannya | Jejak pemakaian repo |
| `daftar_istilah.md` | Istilah yang dibekukan dan aturan ejaan | QC konsistensi |
| `build_pptx.py` | Skrip pembangun PPTX dari struktur deck | Regenerasi bila isi berubah |
| `assets/art/` | Enam ilustrasi anatomi beranotasi (`fig-*.svg` sumber, `fig-*.jpg` untuk deck) | Gambar slide 1, 4, 6, 7, 8, 12 |
| `assets/src/` | Berkas ilustrasi asli tanpa anotasi | Arsip bila potongan gambar perlu dibuat ulang |
| `tools/build_art.py` | Penulis anotasi: titik penunjuk, garis, dan label di atas gambar | Regenerasi ilustrasi |
| `tools/render_svg.js` | Render SVG ke JPEG 2x | Dipakai setelah `build_art.py` |
| `tools/print_pdf.js` | Cetak deck HTML ke PDF 13,333 × 7,5 inci | Regenerasi handout |

## Mengapa HTML menjadi versi utama

PowerPoint bisa memuat hyperlink dan catatan pembicara, tetapi tidak bisa menampilkan pop-up kesalahan per langkah, tab perbandingan yang berganti tanpa animasi, kasus bercabang, dan kuis dengan umpan balik langsung tanpa makro atau add-in. Deck HTML memakai satu berkas tanpa dependensi, berjalan luring, dan tetap bisa dicetak ke PDF. Karena itu HTML dipakai sebagai versi presentasi, sedangkan PPTX disediakan sebagai cadangan agar isi tetap bisa dibuka di komputer tanpa browser modern.

## Cara memakai deck HTML

- Panah kiri dan kanan, Page Up dan Page Down, atau spasi untuk berpindah slide.
- Tombol `Agenda` di kanan atas mengembalikan ke halaman agenda. Setiap butir agenda juga bisa diklik.
- Tombol `Catatan (N)` membuka catatan pembicara. Tombol `Cetak` membuka dialog cetak; pilih lanskap dan aktifkan latar belakang grafis.
- Pada slide 7, klik langkah di kolom kiri atau gunakan tombol Sebelumnya dan Berikutnya. Bagian kesalahan sudah terbuka dan bisa ditutup.
- Pada slide 9 dan 12, klik tab untuk membandingkan.
- Pada slide 13, pilih keputusan kasus; alasan muncul dan pilihan diringkas agar dua pertanyaan muat di satu layar.
- Pada slide 14, lima soal ditampilkan satu per satu dengan penjelasan dan skor akhir.

## Ilustrasi

Tujuh slide memakai ilustrasi anatomi beranotasi: sampul, prinsip SSC, preparasi, langkah klinis (instrumen), Hall Technique, dan alternatif estetik. Isinya penampang molar desidui dengan crown terpasang, gigi yang sudah dipreparasi dengan crown di atasnya, gigi dengan karies tertutup crown Hall, deretan instrumen, dan tiga jenis mahkota posterior.

Cara kerjanya: gambar dasar ada di `assets/src`, dipotong ke `assets/art/photo-*.jpg`, lalu diberi titik penunjuk dan label oleh `assets/art/build_art.py`. Skrip itu menulis SVG, dan `tools/render_svg.js` mengubahnya menjadi JPEG 2x yang dipakai deck HTML maupun PPTX. Untuk mengubah label atau posisi penunjuk, sunting `build_art.py` lalu jalankan:

```
python3 assets/art/build_art.py
NODE_PATH=<node_modules> node tools/render_svg.js 2
python3 build_pptx.py
NODE_PATH=<node_modules> node tools/print_pdf.js
```

Catatan penting: gambar ini adalah render ilustrasi yang dibuat untuk deck, bukan foto pasien dan bukan gambar berhak cipta dari internet. Untuk pengajaran, sebutkan bahwa ini ilustrasi skematik. Slide kasus tetap memakai placeholder yang harus diisi foto klinis dan radiograf milik sendiri.

## Yang perlu diganti sebelum dipakai

1. Nama pemateri dan tanggal pada slide 1 (`[nama]`, `[tanggal]`).
2. Dua kotak placeholder pada slide 13: foto klinis okusal gigi 85 dan radiograf bitewing. Ganti dengan foto Anda sendiri, jangan memakai foto dari internet.
3. Bila ingin menambah logo institusi, letakkan di sudut kanan bawah footer dan jaga tinggi maksimal 0,25 inci agar tidak menabrak nomor slide.

## Catatan revisi

- Slide 9, 10, dan 12 diperbaiki: panel tab yang tidak aktif tidak lagi ikut tercetak, kartu penyulit tidak lagi bertumpuk, dan teks yang terpotong sudah dipindahkan ke catatan pembicara.
- Nomor daftar pustaka di slide sekarang sama dengan nomor di `research_notes.md`.
- Pada PDF, slide bertab hanya menampilkan tab yang aktif saat dicetak. Untuk melihat tab lain, buka `ssc-pedodonsia.html`.
- PDF dibuat ulang dari HTML dengan Chromium; ukuran halaman 13,333 x 7,5 inci.

### Revisi ilustrasi

- Sketsa vektor lama pada sampul, slide prinsip, preparasi, Hall, dan alternatif diganti ilustrasi anatomi bergambar dengan label penunjuk.
- Grafik retensi pada slide alternatif dipadatkan agar ilustrasi tiga mahkota mendapat ruang.
- Panel langkah klinis menampilkan foto instrumen pada langkah 8 (trim, crimp, contour).
- PDF dan PPTX dibangun ulang dari sumber yang sama supaya isi ketiga berkas tidak berbeda.

## Batasan

- Data biaya dan ketersediaan SSC di Indonesia tidak ditemukan pada sumber primer. Bagian biaya tidak diisi angka dari situs klinik.
- Beberapa angka berasal dari abstrak atau guideline tanpa nomor halaman lengkap; DOI atau PMID dicantumkan pada `research_notes.md`.
- Materi ini edukasi. Bukan pengganti pertimbangan klinis pada pasien tertentu.
