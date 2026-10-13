# Deck: Presentasi Jurnal — Prevalensi MIH (Lopes dkk., Sci Rep 2021)

Deck PowerPoint **editable** (15 slide, bahasa Indonesia) untuk diskusi jurnal kedokteran
gigi anak, dibangun dari satu artikel dalam daftar `../README.md`.

Versi 5. Alasan versi 4 dibuang: hasil rendernya memperlihatkan slide yang kosong, garis
rambut tipis, dan "diagram gigi" yang sebenarnya cuma tangga kotak tanpa makna. Itu
wireframe, bukan desain. Versi 5 dibangun ulang dari nol dengan bahasa desain baru.

## Yang berubah di versi 5

1. **Latar putih, blok warna terisi.** Panel mint, krem, dan amber menggantikan latar
   beige dan garis rambut. Setiap slide punya chip bagian, judul, banner inti, isi, dan
   rel footer yang konsisten.
2. **Dua ilustrasi nyata** di folder `assets/`: tekstur batang email untuk sampul
   (ditimpa panel tinta semi-transparan supaya teks terbaca) dan potongan molar
   berlesi hipomineralisasi untuk slide "Apa itu MIH", lengkap dengan legenda warna.
   Keduanya ditanam sebagai gambar biasa, jadi bisa diganti tanpa membongkar tata letak.
3. **Isi dipadatkan dan diperbesar.** Badan teks 10–15 pt, angka kunci 20–62 pt,
   dan tidak ada slide yang separuh kosong. Empat grafik native: kolom (sebaran NOS),
   donat (proporsi 13,5%), dua grafik batang mendatar.
4. **Naskah medis dipertahankan** dari versi 4 (`post-eruptive enamel breakdown`,
   hipersensitivitas dentin, opasitas berbatas tegas, MIH tipe molar-insisivus, HSPM)
   beserta seluruh angka dan rujukannya.
5. **Renderer dipakai sebagai alat kontrol mutu.** `render_deck.py` menggambar ulang
   setiap objek dengan font bermetrik sama, melaporkan teks yang meluber, dan sekarang
   juga menempatkan gambar. Deck hanya dianggap selesai kalau audit 0 error dan render
   tidak melaporkan luberan.

## Sumber desain eksternal (design evidence, bukan aset)

| Repo | Lisensi | Yang diambil | Yang tidak diambil |
|---|---|---|---|
| [GordenSun/GordenPPTSkill](https://github.com/GordenSun/GordenPPTSkill) | MIT (keterangan repo: personal/research use only) | Rujukan kepadatan dan keberanian warna: 17 template menunjukkan bahwa deck yang terlihat mahal selalu mengisi slide dengan panel, kartu angka, dan diagram informasi | Tidak ada berkas template, tata letak, atau teksnya yang dipakai; deck ini tetap dibangun dari nol dengan python-pptx |
| [Noi1r/powerpoint-skill](https://github.com/Noi1r/powerpoint-skill) | MIT | Aturan deck akademik: hierarki tipe, batas bawah 9–10 pt, warna aman buta warna, dan larangan garis dekoratif di bawah judul (aturan #11) | Tidak ada skrip PptxGenJS/LaTeX-nya yang dipakai |
| [microsoft/dstoolkit-DiscoveryEnvisioning](https://github.com/microsoft/dstoolkit-DiscoveryEnvisioning) | MIT | Tema dan ritme tata letak, diekstrak read-only lewat skill `pptx-reference-deck-analysis` (39 slide; tema `dk2 #081F2B`, `lt2 #E8E6DF`, `accent1 #0078D3`) | Tidak ada slide, gambar, ikon, atau teks Microsoft yang disalin |
| [SorkinType/Gelasio](https://github.com/SorkinType/Gelasio) | SIL OFL 1.1 | Font pratinjau metrik-sama dengan Cambria untuk renderer | Tidak disematkan ke deck; deck memakai Cambria/Calibri/Consolas bawaan Office |
| [cssobral2013/LC-Sans](https://github.com/cssobral2013/LC-Sans) | SIL OFL 1.1 | Font pratinjau metrik-sama dengan Calibri untuk renderer | Tidak disematkan ke deck |

## Berkas hasil

| Berkas | Isi |
|---|---|
| `Presentasi-Jurnal-MIH-Lopes-2021.pptx` | **Deck utama** — 15 slide, 384 objek native, 3 grafik native, catatan pemateri di setiap slide |
| `spec.json` | Kontrak koordinat (bbox inci, font, warna, gradien, z-index, reading order, rujukan) |
| `author_spec.py` | Naskah spesifikasi — tiap slide disusun eksplisit di sini |
| `build_deck.py` | Pembangun PPTX: bentuk native, gradien, rotasi, grafik, transparansi, letter-spacing |
| `audit_deck.py` | Audit geometri, kolisi, margin, kapasitas teks, type scale, reading order |
| `preview_spec.py` | Sketsa cepat berbasis spec (Pillow); perkiraan kasar, tidak lagi dipakai |
| `render_deck.py` | **Renderer sungguhan**: PPTX → PDF (ReportLab, font metrik-sama) → PNG (PyMuPDF). Ini acuan untuk menilai desain |
| `audits/render/` | Hasil render 15 slide + contact sheet + PDF |
| `assets/` | Dua ilustrasi yang ditanam ke deck (tekstur email, potongan molar berlesi) |
| `audits/` | Laporan audit + PNG pratinjau tiap slide dan contact sheet |
| `build_record.json` | Rekaman pembangunan (spec → objek per slide) |

## Sumber (source manifest)

| ID | Sitasi | Peran |
|---|---|---|
| S1 | Lopes LB, Machado V, Mascarenhas P, Mendes JJ, Botelho J. *The prevalence of molar-incisor hypomineralization: a systematic review and meta-analysis.* Sci Rep. 2021;11:22405. DOI 10.1038/s41598-021-01541-7 · PMID 34789780 · PMC8599453 · CC BY 4.0 | Artikel utama |
| S2 | Weerheijm KL, dkk. *Judgement criteria for MIH in epidemiologic studies.* Eur J Paediatr Dent. 2003;4:110–113 | Kriteria EAPD (dikutip dalam S1) |
| S3 | Schwendicke F, dkk. *Global burden of molar incisor hypomineralization.* J Dent. 2018;68:10–18 | Pembanding tinjauan sebelumnya |
| S4 | Zhao D, dkk. *The prevalence of MIH: evidence from 70 studies.* Int J Paediatr Dent. 2018;28:170–179 | Pembanding tinjauan sebelumnya |

Semua angka dapat dilacak lewat `source_ref` pada setiap objek di `spec.json`.

## Struktur deck (15 slide)

1. Sampul · 2. Ringkasan · 3. Apa itu MIH · 4. Angka laporan tersebar 2,8%–40,2%
5. Pertanyaan penelitian dan empat luaran · 6. Metode: cara mengumpulkan bukti
7. Metode: aturan masuk dan keluar · 8. Hasil: seleksi studi dan mutu
9. Hasil: prevalensi global 13,5% · 10. Hasil: keparahan dan gigi terkena
11. Sub-analisis wilayah dan kriteria · 12. Diskusi · 13. Penilaian kritis
14. Implikasi klinis · 15. Kesimpulan dan rujukan

## Sistem desain (v3)

| Aspek | Keputusan |
|---|---|
| Profil | `editorial-minimal` (skill `pptx-deck-context`) |
| Tipografi | Cambria untuk display, Calibri untuk teks, Consolas untuk algoritma pencarian |
| Warna | kertas `#FBF9F6`, tinta `#08222A` dengan gradien pada sampul, aksen teal `#0E7490`/`#155E75`, amber `#A16207` hanya untuk keterbatasan dan peringatan |
| Token | dipisah menjadi primitif, semantik, dan komponen mengikuti skill `design-system-patterns` |
| Tekstur | batang email diagonal (rotasi 24°, opasitas 9–24%) hanya pada sampul |
| Diagram | lengkung gigi oklusal dan swatch email, semuanya objek native |
| Grafik | kolom (skor NOS), batang mendatar (jumlah molar), donut (porsi kasus) — semua native dan dapat diedit |
| Aset eksternal | tidak ada; tidak ada gambar hasil generasi, sehingga tidak ada masalah lisensi |

Skill yang dipakai: `pptx-deck-creation` (5 skill + agent), `avoid-ai-writing` (bahasa),
`visual-design-foundations` (skala tipe, grid, kontras), `design-system-patterns` (hierarki
token), `data-storytelling` (insight lebih dulu), `kpi-dashboard-design` (pemilihan grafik).

## Cara membangun ulang

```bash
cd research/pediatric-dentistry-2021-2026/deck-mih-lopes-2021
python3 author_spec.py      # menulis spec.json
python3 build_deck.py       # menulis Presentasi-Jurnal-MIH-Lopes-2021.pptx + build_record.json
python3 audit_deck.py       # menulis audits/*.json; exit 0 bila lulus
python3 preview_spec.py     # opsional: sketsa cepat dari spec

# render sungguhan (butuh reportlab + pymupdf, dan sekali saja: klon font pratinjau)
python3 render_deck.py --fetch-fonts      # sekaligus: Gelasio + LC-Sans (SIL OFL)
python3 render_deck.py                    # -> audits/render/*.png + PDF

# integritas paket OOXML memakai skrip skill di repo (dijalankan dari akar repo)
cd /home/user/agents
python3 plugins/pptx-deck-creation/skills/pptx-reference-deck-analysis/scripts/validate_package.py \
  research/pediatric-dentistry-2021-2026/deck-mih-lopes-2021/Presentasi-Jurnal-MIH-Lopes-2021.pptx \
  --output research/pediatric-dentistry-2021-2026/deck-mih-lopes-2021/audits/package-report.json
```

Dependensi: `python-pptx`, `Pillow`, `defusedxml`, `reportlab`, `pymupdf`
(`pip install --break-system-packages reportlab pymupdf`).

## Status audit

| Gerbang | Hasil |
|---|---|
| Geometri, kolisi, margin aman, kapasitas teks, type scale, reading order | **384 objek, 0 error** |
| Integritas paket OOXML (`validate_package.py`) | **ok: true**, 0 error, 0 warning |
| Bahasa | 0 tanda pisah panjang, 0 kerangka penuntun pembaca |
| Catatan pemateri | ada di 15 slide |

## Catatan keterbatasan

1. **Font Cambria dan Calibri** adalah font bawaan Office untuk Windows dan macOS. Di
   lingkungan Linux tanpa font tersebut, PowerPoint atau LibreOffice akan mengganti font
   dan tampilan berubah. Tata letak tetap utuh.
2. **Rendering sebenarnya belum diverifikasi.** Sandbox ini tidak punya LibreOffice atau
   PowerPoint, sehingga verifikasi visual memakai renderer perkiraan (`preview_spec.py`,
   font DejaVu yang lebih lebar dari Calibri). Ada dua risiko sisa: posisi label data pada
   grafik native ditentukan PowerPoint, dan tinggi baris teks di PowerPoint berbeda sedikit
   dari perkiraan. Buka deck sekali di PowerPoint sebelum dipakai presentasi.
3. Dua ketidakkonsistenan pada artikel sumber tetap ditampilkan apa adanya dan diberi
   catatan: insisivus 36,6% di abstrak versus 38,7% di Tabel 2, serta penyebutan basis data
   yang tidak seragam (PubMed/MEDLINE dipisah, EMBASE hanya di strategi pencarian).
4. Deck ini menyajikan **1 artikel** dari daftar 38 artikel di `../README.md`.
