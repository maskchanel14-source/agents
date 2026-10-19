# Gaya bahasa: catatan dan aturan penulisan

Dokumen ini mencatat repo humanizer yang dibaca, aturan yang diambil, aturan yang ditolak, dan aturan turunan untuk bahasa Indonesia. Semua aturan di sini berlaku untuk teks presentasi dan catatan pembicara, bukan untuk kutipan langsung, nama obat, angka, satuan, dan istilah di `daftar_istilah.md`.

## 1. Repo yang dibaca

| Repo | Yang dibaca | Dipakai untuk |
|---|---|---|
| blader/humanizer | `SKILL.md` bagian katalog pola 7–24 | Pola ritme, struktur kalimat, dan larangan klise |
| hardikpandya/stop-slop | `references/structures.md`, `references/phrases.md` | Deteksi struktur berulang dan frasa pengisi |
| conorbronsdon/avoid-ai-writing | `SKILL.md`, `references/patterns.md` | Kontrak penyuntingan, larangan em dash, inflasi signifikansi, dan disiplin gaya |

Catatan: `avoid-ai-writing` versi di repo ini menaruh katalog pola di `references/patterns.md`, bukan di `skills/avoid-ai-writing/references/pattern-catalog.md`. Semua aturan yang diambil berasal dari file yang benar-benar ada dan sudah dibaca.

Ketiga repo itu berbahasa Inggris. Aturannya tidak diterjemahkan kata per kata. Yang diambil adalah prinsipnya, lalu dicocokkan dengan kebiasaan tulisan akademik Indonesia. Bila ada aturan repo yang bertentangan dengan aturan 3B dan 3C dari arahan tugas, aturan tugas yang menang.

## 2. Aturan yang diambil

### Ritme dan panjang kalimat

- Campur kalimat pendek dan panjang. Kalimat pendek dipakai untuk kesimpulan langkah, kalimat panjang untuk penjelasan mekanisme.
- Jangan membuat tiga kalimat berturut-turut dengan pola buka yang sama.
- Jangan menutup setiap bagian dengan kalimat rangkuman yang mengulang isi. Satu rangkuman di akhir bagian cukup.
- Paragraf tidak harus sama panjang. Di slide, satu pesan per slide lebih penting daripada keseimbangan visual teks.

### Kalimat dan struktur

- Buang pola "bukan X, tetapi Y" yang dipakai berulang. Satu kali untuk koreksi klinis yang benar-benar penting masih boleh.
- Buang kalimat yang mengaburkan pelaku: "dapat dilakukan" diganti dengan pelaku yang jelas bila pelakunya diketahui, misalnya "operator mereduksi oklusal".
- Buang pembuka yang menjelaskan konteks umum sebelum masuk ke pokok, misalnya "Dalam dunia kedokteran gigi modern".
- Buang frasa transisi yang tidak menambah makna: "Selain itu", "Lebih lanjut", "Pada akhirnya", "Yang perlu dicatat".
- Jangan memakai kalimat tanya retoris sebagai pembuka slide.
- Jangan memakai tiga kata sifat berderet untuk memperkuat klaim.
- Jangan menaikkan kepentingan temuan: "sangat penting", "revolusioner", "mengubah paradigma" hanya dipakai bila sumber menyatakannya.

### Kosakata

- Buang kata penguat kosong: "benar-benar", "sangat", "secara signifikan" bila tidak ada uji statistik.
- "Signifikan" hanya dipakai untuk perbedaan statistik yang dilaporkan sumber.
- Hindari "menunjukkan bahwa" berulang; variasikan dengan "dilaporkan", "ditemukan", "hasilnya".
- Hindari metafora dan slogan. Judul slide menyatakan temuan, bukan perumpamaan.
- Hindari tanda pisah panjang (em dash) di teks Indonesia. Pakai koma, titik, atau kurung.
- Hindari tanda panah di teks. Bila perlu alur, pakai kalimat atau diagram.
- Tanpa emoji, tanpa label gaya produk, tanpa gaya telegram.

### Kejujuran sumber

- Setiap angka harus punya sumber di catatan pembicara dan footer sitasi.
- Bila sumber berbeda, tulis rentang dan sebutkan sumbernya. Jangan merata-ratakan.
- Bila data tidak ada, tulis "data tidak ditemukan". Jangan mengisi dengan perkiraan.
- Jangan menulis pengalaman pribadi yang tidak ada. Contoh kasus diberi label "kasus ilustratif".
- Jangan menambah kepastian yang tidak ada di sumber. "Berkaitan dengan" tidak boleh menjadi "menyebabkan" bila desain studi hanya kohort.

## 3. Aturan yang ditolak dan alasannya

| Aturan repo | Alasan ditolak |
|---|---|
| Target nol em dash dengan pembersihan otomatis seluruh teks | Teks Indonesia memakai tanda pisah untuk rentang angka dan sitasi. Pembersihan otomatis bisa merusak "1,0–1,5 mm". Aturan dipakai secara manual, hanya untuk tanda pisah dalam kalimat. |
| Detektor dan skor AI | Tidak dipakai. Tugas melarang alat humanizer otomatis untuk teks klinis, dan skor detektor tidak mengukur kebenaran isi. |
| Menghapus semua kata bold | Slide butuh penekanan pada angka dan istilah kunci. Bold dipakai terbatas, maksimal dua per slide. |
| Mengubah struktur menjadi naratif penuh | Slide adalah media visual. Daftar dan tabel dipertahankan bila memang berisi langkah, kriteria, atau perbandingan. |
| Menambah pengalaman, opini, atau sikap penulis | Tidak boleh. Semua kalimat harus bisa dilacak ke sumber atau ke kasus ilustratif yang diberi label. |
| Gaya percakapan kasual dan kontraksi | Presentasi akademik Indonesia memakai ragam formal. Catatan pembicara boleh lebih luwes, tetapi tetap tanpa slang. |
| Aturan tanda kutip keriting dan tipografi Inggris | Tidak relevan untuk bahasa Indonesia. Yang dijaga adalah konsistensi tanda baca dan spasi. |

## 4. Turunan aturan untuk bahasa Indonesia

Pola AI dalam bahasa Indonesia yang perlu dihindari:

1. Pembuka seremonial: "Di era digital yang serba cepat ini", "Seiring dengan perkembangan zaman". Ganti langsung ke masalah klinis.
2. Kalimat yang mengulang judul: judul "Pentingnya SSC" lalu kalimat pertama "SSC sangat penting". Buang.
3. Rangkaian nomina abstrak: "peningkatan kualitas pelayanan prima yang berkelanjutan". Ganti dengan tindakan konkret.
4. Kata "mampu" dan "dapat" yang menumpuk. Satu modal per kalimat cukup.
5. "Tidak hanya ... tetapi juga ..." berulang. Maksimal satu kali per presentasi.
6. "Merupakan" berlebihan. Ganti dengan "adalah" atau susun ulang kalimat.
7. "Dalam hal ini", "adapun", "sebagaimana diketahui" sebagai pengisi. Buang.
8. "Mari kita" dan "kita semua tahu". Presentasi akademik tidak perlu mengajak.
9. Kesimpulan yang mengulang semua poin. Cukup tiga hal yang harus diingat.
10. Judul bergaya slogan: "SSC: Solusi Cerdas Gigi Kuat". Ganti dengan pernyataan: "SSC menutup seluruh mahkota dan tahan fraktur".
11. Tanda seru. Tidak dipakai.
12. Campuran ejaan Inggris dan Indonesia dalam satu istilah: "preparasi tooth" atau "pulpotomi gigi deciduous". Pilih satu bentuk sesuai `daftar_istilah.md`.

## 5. Contoh perbaikan

| Sebelum | Sesudah | Alasan |
|---|---|---|
| "Dalam era kedokteran gigi modern yang terus berkembang, SSC merupakan solusi yang sangat penting dan efektif untuk berbagai permasalahan gigi desidui." | "SSC dipakai pada molar desidui dengan karies luas atau setelah pulpotomi." | Membuang pembuka konteks dan klaim tanpa angka |
| "Tidak hanya memberikan perlindungan, tetapi juga memberikan estetika yang baik serta kenyamanan." | "SSC melindungi seluruh mahkota. Estetika logam menjadi keterbatasannya." | Memisahkan klaim dan keterbatasan |
| "Berdasarkan berbagai penelitian yang ada, dapat disimpulkan bahwa SSC sangat baik." | "Cochrane 2015: risiko kegagalan mayor RR 0,18 (95% CI 0,06–0,56)." | Angka menggantikan klaim umum |
| "Perlu diketahui bahwa keberhasilan tindakan ini sangat dipengaruhi oleh berbagai faktor yang kompleks." | "Retensi ditentukan oleh kontur dan crimping margin." | Menyebut faktor yang konkret |

## 6. Checklist sebelum final

- [ ] Setiap judul slide adalah pernyataan, bukan slogan atau metafora.
- [ ] Tidak ada emoji, tanda seru, panah, atau label gaya produk.
- [ ] Tidak ada lebih dari satu pola "bukan X, tetapi Y" dalam satu bagian.
- [ ] Tidak ada kalimat pembuka yang menjelaskan konteks umum.
- [ ] Setiap angka punya sitasi di footer atau catatan pembicara.
- [ ] Istilah di `daftar_istilah.md` tidak diubah, diterjemahkan, atau diparafrase.
- [ ] Istilah "desidui" dieja konsisten.
- [ ] Catatan pembicara ditulis dalam kalimat yang bisa diucapkan, bukan poin-poin yang dibacakan.
- [ ] Tidak ada pengalaman pribadi yang tidak ada.
- [ ] Konflik sumber ditampilkan, tidak disatukan.
