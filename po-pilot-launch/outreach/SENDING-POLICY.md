# Patokan kirim email — Small Signal Studio

Berlaku untuk semua email keluar dari `smallsignalstudiolife@gmail.com`, baik
outreach partner, follow-up, maupun balasan audit. Dokumen ini yang dipakai
sebagai sumber kebenaran, bukan ingatan.

Terakhir diverifikasi: 29 Oktober 2026.

---

## 1. Jawaban singkatnya

Batas resmi Google untuk Gmail gratis adalah **500 email per hari**. Batas itu
bukan patokan yang berguna, karena angkanya soal kuota teknis, bukan soal reputasi.
Akun bisa kena rate limit jauh sebelum 500 kalau rasio keluhan dan bounce-nya buruk.

**Patokan yang kita pakai: 10 email/hari di minggu pertama, 20 di minggu kedua,
30 setelahnya. Langit-langit mutlak 40/hari dan 15/jam.**

Angka ini bukan karangan. Turunannya dijelaskan di bagian 3 dan 4.

---

## 2. Angka resmi, dan kenapa tidak dipakai sebagai target

| Akun | Batas harian resmi | Sumber |
| --- | --- | --- |
| Gmail gratis (@gmail.com) | 500 email/hari, 500 penerima per email | Gmail Help, "Limits for sending & getting mail" |
| Google Workspace (berbayar) | 2.000 pesan/hari, 10.000 penerima/hari, 3.000 penerima eksternal/hari | Workspace Admin Help, "Gmail sending limits" |
| Workspace (mail merge) | 1.500/hari | idem |
| Workspace (trial) | 500/hari | idem |

Semua batas dihitung atas **rolling 24 jam**, bukan per tengah malam. Kalau
terlampaui, pengiriman berhenti 1 sampai 24 jam. Di Workspace, akun bisa
disuspend dan harus dipulihkan manual.

Konsekuensinya: 500/hari itu pintu darurat, bukan anggaran. Yang menentukan
email masuk ke Inbox atau Spam adalah tiga rasio di bawah ini.

---

## 3. Tiga ambang yang sebenarnya menentukan

**a. Spam complaint rate.** Google menetapkan ambang **di bawah 0,3%** di
Postmaster Tools sebagai syarat untuk semua pengirim, dan sanksinya bukan
peringatan: pesan mulai masuk spam atau ditolak.

Hitung sendiri untuk volume kita. Satu orang menekan "Report spam" dari 30
email = **3,3%**. Dari 300 email = **0,33%**, masih di atas ambang. Artinya:

> Pada volume kecil, satu keluhan spam saja sudah cukup untuk merusak akun.
> Karena itu kualitas daftar lebih menentukan daripada jumlah kiriman.

Praktik yang aman adalah menjaga di bawah 0,1%, dan pada volume kita itu berarti
targetnya **nol keluhan**, bukan "sesedikit mungkin".

**b. Bounce rate.** Google memblokir pengiriman sampai 24 jam kalau terlalu banyak
alamat tidak valid atau memantul. Patokan kita **di bawah 2%**, dan tiap alamat
diverifikasi dulu: alamat publik di situs perusahaan, ditambah cek MX domain
seperti yang sudah dilakukan untuk tujuh penerima pertama.

**c. Volume yang naik mendadak.** Pedoman resmi Google meminta volume dinaikkan
perlahan, dikirim dengan laju konsisten, dan **hindari kiriman bergerombol**.
Run 17 Oktober melanggar tiga-tiganya: 30 email dalam 5,5 jam, dan berakhir dengan
limit kirim aktif sekitar pukul 09:00 PDT.

---

## 4. Patokan harian

Fase dihitung dari tanggal kiriman pertama di `ledger.json`.

| Fase | Hari | Maks per hari | Jeda antar email | Maks per jam |
| --- | --- | --- | --- | --- |
| Warm-up | 1–7 | 10 | 4 menit | 10 |
| Naik | 8–14 | 20 | 4 menit | 12 |
| Tetap | 15+ | 30 | 3 menit | 15 |
| Langit-langit mutlak | kapan pun | 40 | — | 15 |

Kenapa jeda 3–4 menit: pola kirim yang terlalu rapi dan cepat adalah sinyal
otomatis. Jeda ini juga menjaga agar kesalahan (salah nama, tautan mati) ketahuan
setelah 2–3 email, bukan setelah 30.

Dengan jadwal ini, 300 email tercapai di akhir minggu keempat. Itu jumlah yang
dibutuhkan untuk dua klien pada reply rate 5% dan closing 20%.

---

## 5. Aturan berhenti

Berhenti berarti berhenti hari itu, bukan "kurangi sedikit".

- **4 kegagalan beruntun** → stop sampai besok. Ini persis pola yang muncul 17 Oktober.
- **Error 4.7.28** (kuota DKIM/SPF/IP) → stop minimal 10 menit, lalu coba satu koneksi.
- **2 bounce dalam 20 kiriman terakhir** → stop, bersihkan daftar, baru lanjut.
- **1 keluhan spam** → stop 7 hari dan audit ulang seluruh kriteria penyaringan.
- **Balasan apa pun dari penerima** → stop sekuens untuk orang itu. Follow-up otomatis dibatalkan.

---

## 6. Aturan per penerima

- Maksimal **1 email pembuka per domain per minggu**. Jangan kirim ke `info@` dan
  `hello@` dari perusahaan yang sama.
- Maksimal **3 email total per orang per 30 hari**: pembuka, follow-up hari ke-3,
  follow-up hari ke-7. Tidak ada email keempat.
- Jangan pernah memakai alamat yang sama dua kali, termasuk setelah ganti template.
- Kalau ada yang minta "remove", catat di ledger dan jangan pernah kirim lagi.

---

## 7. Aturan format

- Teks biasa. Tanpa lampiran di email pertama, tanpa logo, tanpa gambar.
- Maksimal dua tautan per email, satu per paragraf.
- Subjek di bawah 60 karakter, huruf kecil, tanpa tanda seru, tanpa emoji.
- Satu CTA berupa pertanyaan yang bisa dijawab satu kata.
- Baris opt-out di setiap email, bukan hanya yang pertama.
- Laju balasan dan nomor telepon boleh ada, tapi bukan di badan email pertama.

---

## 8. Identitas pengirim: Small Signal Studio

Semua email keluar dengan display name **Small Signal Studio**, bukan nama
perorangan. Parameter `from_address` menerima format
`Small Signal Studio <smallsignalstudiolife@gmail.com>`; sudah diuji dengan draf
lalu dihapus, dan header `From:` keluar persis begitu. Tidak perlu ubah setelan akun.

### Domain: dikoreksi 29 Oktober 2026

Catatan sebelumnya di dokumen ini salah dan sudah dibuang. `smallsignalstudio.com`
**bukan milik kita**. Domain itu dijalankan pihak lain yang memuat empat aplikasi
konsumen (Sippin', Batten, TaleSnack, Glossio). DNS-nya bukan wewenang kita dan
tidak boleh disentuh.

Tiga akibatnya:

1. Tidak ada domain sendiri untuk DKIM dan DMARC. Pengirim tetap @gmail.com.
2. Jangan pernah menautkan `smallsignalstudio.com` di email. Penerima akan
   mendarat di halaman aplikasi yang tidak berhubungan, lalu bertanya apakah kita
   entitas yang sama.
3. Nama "Small Signal Studio" bertabrakan dengan pihak yang sudah memegang
   domain .com-nya. Ini risiko brand, bukan risiko teknis. Sebelum nama ini
   dipakai di ratusan email, keputusannya harus diambil sadar, bukan diwarisi.

### Opsi domain, dicek 29 Oktober 2026

| Domain | Status | Catatan |
| --- | --- | --- |
| smallsignalstudio.com | dipakai pihak lain | jangan dipakai, jangan ditautkan |
| smallsignal.studio | NXDOMAIN, tampak bebas | nama sama, TLD beda, tetap bersinggungan dengan .com |
| smallsignalstudio.co | NXDOMAIN, tampak bebas | paling dekat ke nama sekarang |
| smallsignalstudio.id | NXDOMAIN, tampak bebas | butuh KTP; mengirim sinyal "Indonesia" ke pembeli AS/UK |
| popilot.io | NXDOMAIN, tampak bebas | nama produk, tidak bentrok |
| popilot.com, po-pilot.com, popilot.app, getpopilot.com | sudah dipakai | tidak tersedia |

"Tampak bebas" berarti NXDOMAIN saat dicek, bukan bukti bisa dibeli. Konfirmasi
di registrar sebelum nama itu dipakai di email mana pun.

### Rekomendasi

Untuk penjualan ke bookkeeper AS dan UK, nama yang menjelaskan pekerjaannya
mengalahkan nama studio. **PO Pilot** sudah menjadi nama produk, sudah dipakai di
halaman audit, dan `popilot.io` tampak bebas. Mengirim sebagai PO Pilot
menghilangkan tabrakan nama sepenuhnya.

Itu keputusan pemilik brand, bukan keputusan teknis. Sampai diputuskan, yang
berlaku sekarang: display name **Small Signal Studio**, tanpa tautan domain, dan
tanda tangan hanya menunjuk halaman audit.

```
Small Signal Studio
Purchasing data for Shopify brands
https://po-pilot-henna.vercel.app/audit/
```

## 9. Cara menegakkan

Anggaran tidak berguna kalau cuma niat. Dua berkas:

- `outreach/ledger.json` menyimpan setiap kiriman: waktu, penerima, domain,
  kampanye, id pesan Gmail, status.
- `outreach/send-budget.py` membaca ledger dan menolak kiriman yang melewati
  patokan.

```bash
python3 outreach/send-budget.py status
python3 outreach/send-budget.py check
python3 outreach/send-budget.py record --to info@contoh.com --subject "..." --campaign partner
```

`check` keluar dengan kode 1 kalau anggaran hari ini habis atau jeda belum lewat.
Kirim hanya kalau `check` lolos.

---

## 10. Sumber

- Gmail Help, Limits for sending & getting mail: <https://support.google.com/mail/answer/22839>
- Gmail Help, Email sender guidelines (spam rate di bawah 0,3%, SPF/DKIM, aturan display name, SMTP 4.7.28): <https://support.google.com/mail/answer/81126>
- Google Workspace Admin Help, Gmail sending limits: <https://support.google.com/a/answer/166852>
- Postmaster Tools: <https://gmail.com/postmaster>
