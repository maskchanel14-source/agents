# Iklan Palmer — Mangga Brasil (B2B Indonesia)

**Video:** `renders/mango_palmer_vo.mp4` · 45.50 s · 1080×1920 · 30 fps · 25,1 MB · h264 CRF 16 + AAC 317 kb/s
**Drive:** https://drive.google.com/drive/folders/1U2kwMIImUUnhYYaZvMoobC1SEPaLozd8

**Audio:** narasi Bahasa Indonesia + musik orisinal · −14.0 LUFS · −0.99 dBTP
**Versi sebelumnya (tanpa narasi, SFX lebih keras):** `renders/mango_palmer_final.mp4`

---

## 1. Struktur & naskah

| Waktu | Shot | Visual | Teks di layar | Fungsi |
|---|---|---|---|---|
| 0–5 s | Establishing | Kebun mangga golden hour, kamera drifting naik | "Dari lembah *yang sama,*" / SEPANJANG TAHUN | Menetapkan asal-usul |
| 5–10 s | Hero fruit | Palmer utuh, push-in, light sweep | **510–850** *gram* / PER BUAH · KELAS EKSPOR | Membuktikan ukuran |
| 10–15 s | Tekstur | Potongan crosshatch, pull-back | Padat. *Nyaris tanpa* **SERAT.** | Membuktikan kualitas daging |
| 15–22 s | Angka | Bar data di atas orchard blur | 30 t/ha · 90% pangsa · 12 bulan | Membuktikan skala |
| 22–28 s | Lini varietas | Kartu varietas bertumpuk | Palmer 36% · Tommy 30% · Keitt 22% · Kent 12% | Membuktikan portofolio |
| 28–34 s | Rantai pasok | Packing house, conveyor | PANEN → SORTIR → GRADING → COLD CHAIN → PELABUHAN | Membuktikan operasi |
| 34–39 s | Brix | Wedge macro, tilt | Manis yang *konsisten.* / Brix 14–16 | Membuktikan rasa |
| 39–42 s | Ready | Splash hero | Siap *dikirim.* | Transisi ke CTA |
| 42–45,5 s | End card | Hero blur, pull-back | Kualitas *yang bisa* dijanjikan. / GROSIR · HORECA · EKSPOR | CTA |

### Naskah narasi (Bahasa Indonesia, 9 baris, satu baris per shot)

| Shot | Narasi |
|---|---|
| Establishing | "Dari Lembah São Francisco. Panen sepanjang tahun." |
| Hero fruit | "Palmer. Setengah kilo lebih, per buah. Kelas ekspor." |
| Tekstur | "Daging padat. Nyaris tanpa serat." |
| Angka | "Tiga puluh ton per hektar. Sembilan puluh persen ekspor Brasil lahir di sini." |
| Varietas | "Palmer, Tommy Atkins, Keitt, Kent. Empat varietas, satu standar." |
| Rantai pasok | "Panen, sortir, grading, cold chain, pelabuhan. Satu alur, nol tebak-tebakan." |
| Brix | "Manis yang konsisten. Dan terukur." |
| Ready | "Siap dikirim." |
| End card | "Kualitas yang bisa dijanjikan. Hubungi tim kami." |

Voice: narator pria, Indonesia netral, tempo tenang (bukan gaya iklan hard-sell).
Tiap baris masuk ~0.15 s setelah cut supaya gambar dan suara tetap sejalan.

**Desain suara dibuat sengaja tipis.** Versi pertama dinilai terlalu ramai — boom
di setiap cut, kick pulse, tick data, riser. Sekarang boom / whoosh / riser / tick
diturunkan 45–60%, kick pulse dipotong setengah, dan seluruh bed di-duck −5 dB di
bawah narasi. Fungsi SFX tinggal menandai cut, bukan ikut bercerita.

---

## 2. Fakta yang dipakai (semua terverifikasi)

| Klaim di iklan | Sumber |
|---|---|
| Vale do São Francisco ≈ 90% ekspor mangga Brasil | CBI / FreshPlaza; Embrapa |
| Produktivitas hingga 30 t/ha (nasional 20 t/ha) | Cargo Sapiens, Jul 2025 |
| Palmer 36% · Tommy Atkins 30% · Keitt 22% · Kent 12% ekspor | Profil negara produsen Fruitrop, Embrapa |
| Palmer 510–850 g, daging padat, minim serat, manis & wangi | CBI European market potential for mangoes |
| Ketersediaan sepanjang tahun (Palmer & Tommy Atkins) | CBI / Tridge |
| Brix 14–16 Palmer | Rentang umum Palmer matang optimal; **lihat catatan** |

**Catatan jujur soal Brix:** angka 14–16 Brix adalah rentang khas Palmer matang dari
literatur hortikultura, bukan hasil uji laboratorium atas lot Anda. Sebelum tayang,
ganti dengan hasil refraktometer lot sebenarnya — atau hapus labelnya kalau belum diukur.
Klaim B2B yang tidak bisa dibuktikan lebih merusak daripada tidak ada klaim.

---

## 3. Yang harus Anda ganti sebelum tayang

1. **End card** — tambahkan nama perusahaan, WhatsApp, dan email. Sekarang sengaja generik
   ("HUBUNGI TIM KAMI"). File: `src/Scenes.tsx`, komponen `S9End`.
2. **Brix** — ganti dengan angka lot nyata (lihat catatan di §2).
3. **MOQ** — kalau punya angka konkret (mis. "MOQ 500 kg"), itu lebih kuat daripada
   "HUBUNGI TIM KAMI".

Setelah diubah: `npx remotion render` (~4 menit). Tidak perlu menyentuh file lain.

---

## 4. Aset visual — penting dibaca

Semua visual adalah **fotografi komersial yang dirender khusus untuk iklan ini**
(6 gambar, lihat `assets/`). Bukan footage stok, bukan hasil comotan dari internet.

Kenapa bukan footage asli: sandbox ini memblokir semua host video/gambar resolusi tinggi
(Pexels, Pixabay, Unsplash, Wikimedia CDN). Foto real yang bisa diambil maksimal
645×360 px — kalau dibentangkan ke 1080×1920 hasilnya pecah dan justru terlihat murahan.

**Kalau Anda punya footage asli** (rekaman kebun, packing house, atau produk Anda),
ganti file di `assets/` dengan nama yang sama dan render ulang. Struktur, timing, gerak
kamera, dan teks tidak perlu diubah — `src/Photo.tsx` sudah menangani semua pergerakan.

Untuk iklan yang benar-benar dijual, **footage asli produk Anda sendiri selalu lebih kuat**
daripada render apa pun. Ini versi terbaik yang bisa dibuat tanpa footage.

---

## 5. Spesifikasi teknis

| | |
|---|---|
| Resolusi | 1080 × 1920 (9:16) |
| Frame rate | 30 fps |
| Durasi | 45.50 s (1350 frame + tail) |
| Video | h264 High, CRF 16, 4.09 Mb/s |
| Audio | AAC-LC 48 kHz stereo, 317 kb/s |
| Loudness | −14.0 LUFS integrated |
| True peak | −0.99 dBTP |
| Narasi | TTS, 48 kHz mono, HPF 95 Hz + kompresor 3.2:1 + plate reverb tipis |
| Musik | Orisinal, digenerate (MIDI → GM soundfont) |
| SFX | Disintesis (whoosh, boom, tick, riser, shimmer), level rendah |
| Ducking | −5 dB pada musik + SFX selama narasi |
| Teks | Playfair Display, Montserrat, Inter (SIL OFL 1.1) |

---

## 6. Kalau mau dipakai di platform lain

- **Instagram Reels / TikTok / YouTube Shorts** — langsung pakai, sudah 9:16 dan < 60 s.
- **Untuk feed 1:1 atau 16:9** — ubah `W`/`H` di `src/brand.ts` dan sesuaikan `objectFit`.
  Perlu penyesuaian tata letak manual, bukan sekadar ganti dimensi.
- **Versi 30 detik** — potong shot 5 (lini varietas) dan shot 7 (brix); sisanya sudah
  membentuk cerita yang utuh.
