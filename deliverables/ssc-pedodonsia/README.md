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
| `daftar_istilah.md` | Istilah yang dibekukan dan aturan ejaan | QC konsistensi |
| `build_pptx.py` | Skrip pembangun PPTX dari struktur deck | Regenerasi bila isi berubah |

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

## Yang perlu diganti sebelum dipakai

1. Nama pemateri dan tanggal pada slide 1 (`[nama]`, `[tanggal]`).
2. Dua kotak placeholder pada slide 13: foto klinis okusal gigi 85 dan radiograf bitewing. Ganti dengan foto Anda sendiri, jangan memakai foto dari internet.
3. Bila ingin menambah logo institusi, letakkan di sudut kanan bawah footer dan jaga tinggi maksimal 0,25 inci agar tidak menabrak nomor slide.

## Batasan

- Data biaya dan ketersediaan SSC di Indonesia tidak ditemukan pada sumber primer. Bagian biaya tidak diisi angka dari situs klinik.
- Beberapa angka berasal dari abstrak atau guideline tanpa nomor halaman lengkap; DOI atau PMID dicantumkan pada `research_notes.md`.
- Materi ini edukasi. Bukan pengganti pertimbangan klinis pada pasien tertentu.
