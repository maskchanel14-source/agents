# Deck: Presentasi Jurnal — Prevalensi MIH (Lopes dkk., Sci Rep 2021)

Deck PowerPoint **editable** (15 slide, bahasa Indonesia) untuk diskusi jurnal kedokteran
gigi anak, dibangun dari satu artikel dalam daftar `../README.md`.

Versi 2 (revisi): bahasa dan catatan pemateri melewati skill `avoid-ai-writing`, tata visual
dibangun ulang memakai `visual-design-foundations` dan grafik native PowerPoint.

## Berkas hasil

| Berkas | Isi |
|---|---|
| `Presentasi-Jurnal-MIH-Lopes-2021.pptx` | **Deck utama** — 15 slide, 450 objek native, 3 grafik native, catatan pemateri di setiap slide |
| `spec.json` | Kontrak koordinat (source of truth: bbox inci, font, warna, z-index, reading order, rujukan) |
| `author_spec.py` | Naskah spesifikasi — semua koordinat, isi slide, dan catatan pemateri ditulis di sini |
| `build_deck.py` | Pembangun PPTX (termasuk grafik native, transparansi, letter-spacing) |
| `audit_deck.py` | Audit geometri, kolisi, margin, kapasitas teks, type scale, reading order |
| `preview_spec.py` | Renderer perkiraan (Pillow) untuk pemeriksaan visual cepat |
| `audits/` | Laporan audit (`geometry`, `accessibility`, `quality-gates`, `package-report`) + PNG pratinjau |
| `build_record.json` | Rekaman pembangunan (spec → objek per slide) |

## Sumber (source manifest)

| ID | Sitasi | Peran |
|---|---|---|
| S1 | Lopes LB, Machado V, Mascarenhas P, Mendes JJ, Botelho J. *The prevalence of molar-incisor hypomineralization: a systematic review and meta-analysis.* Sci Rep. 2021;11:22405. DOI 10.1038/s41598-021-01541-7 · PMID 34789780 · PMC8599453 · CC BY 4.0 | Artikel utama |
| S2 | Weerheijm KL, dkk. *Judgement criteria for MIH in epidemiologic studies.* Eur J Paediatr Dent. 2003;4:110–113 | Kriteria EAPD (dikutip dalam S1) |
| S3 | Schwendicke F, dkk. *Global burden of molar incisor hypomineralization.* J Dent. 2018;68:10–18 | Pembanding tinjauan sebelumnya |
| S4 | Zhao D, dkk. *The prevalence of MIH: evidence from 70 studies.* Int J Paediatr Dent. 2018;28:170–179 | Pembanding tinjauan sebelumnya |

Semua angka, diagram, dan kesimpulan berasal dari S1 dan dapat dilacak lewat `source_ref`
pada setiap objek di `spec.json`.

## Struktur deck (15 slide)

1. Sampul · 2. Ringkasan · 3. Apa itu MIH · 4. Angka laporan yang tersebar luas
5. Pertanyaan penelitian dan empat luaran · 6. Metode: cara mencari bukti · 7. Metode: cara menyaring bukti
8. Hasil: seleksi studi dan mutu · 9. Hasil: prevalensi global 13,5% · 10. Hasil: keparahan dan gigi terkena
11. Sub-analisis wilayah dan kriteria · 12. Diskusi · 13. Penilaian kritis (kekuatan vs keterbatasan)
14. Implikasi klinis · 15. Kesimpulan dan rujukan

## Sistem desain

| Aspek | Keputusan |
|---|---|
| Profil | `editorial-minimal` (skill `pptx-deck-context`), disesuaikan untuk diskusi jurnal |
| Warna | kertas `#F6F8F9`, tinta `#0B2E36`, aksen teal `#0E7490`/`#155E75`, amber `#B45309` hanya untuk keterbatasan |
| Tipografi | Calibri; judul 24 pt, sampul 36 pt, badan 10,5–12 pt, kaki 9 pt; kicker 10,5 pt dengan letter-spacing |
| Motif | lengkung gigi dari objek native di sampul, batang aksen + garis rambut di kepala slide, nomor halaman di kaki |
| Visual data | 3 grafik native PowerPoint: kolom (NOS), batang mendatar (jumlah molar), donut (porsi kasus); batang proporsional native untuk perbandingan wilayah |
| Aset eksternal | tidak ada, sehingga tidak ada masalah lisensi dan deck tetap dapat diedit |

## Cara membangun ulang

```bash
cd research/pediatric-dentistry-2021-2026/deck-mih-lopes-2021
python3 author_spec.py      # menulis spec.json
python3 build_deck.py       # menulis Presentasi-Jurnal-MIH-Lopes-2021.pptx + build_record.json
python3 audit_deck.py       # menulis audits/*.json; exit 0 bila lulus
python3 preview_spec.py     # opsional: PNG perkiraan untuk pemeriksaan cepat

# integritas paket OOXML memakai skrip skill di repo (dijalankan dari akar repo)
cd /home/user/agents
python3 plugins/pptx-deck-creation/skills/pptx-reference-deck-analysis/scripts/validate_package.py \
  research/pediatric-dentistry-2021-2026/deck-mih-lopes-2021/Presentasi-Jurnal-MIH-Lopes-2021.pptx \
  --output research/pediatric-dentistry-2021-2026/deck-mih-lopes-2021/audits/package-report.json
```

Dependensi: `python-pptx`, `Pillow`, `defusedxml` (untuk skrip validator skill).

## Status audit

| Gerbang | Hasil |
|---|---|
| Geometri, kolisi, margin aman, kapasitas teks, type scale, reading order | **450 objek, 0 error** |
| Integritas paket OOXML (`validate_package.py`) | **ok: true**, 0 error, 0 warning |
| Catatan pemateri | ada di 15 slide (302–484 karakter per slide) |
| Grafis | 3 grafik native, dapat diedit langsung di PowerPoint |

**Pengecualian terdokumentasi:** garis aksen (batang 0,055 in dan garis rambut) dibangun sebagai
persegi panjang native, bukan konektor, sehingga tidak ada normalisasi tinggi OOXML lagi.

## Catatan keterbatasan

1. Deck memakai **Calibri** (bawaan Office). Bila dibuka di perangkat tanpa Calibri,
   PowerPoint mengganti font dan tampilan sedikit berbeda meski tata letak tetap.
2. `preview_spec.py` adalah renderer perkiraan berbasis Pillow dengan font DejaVu yang lebih
   lebar dari Calibri; gambar di `audits/preview/` hanya untuk pemeriksaan tata letak.
3. Dua ketidakkonsistenan pada artikel sumber tetap ditampilkan apa adanya dan diberi catatan:
   angka insisivus berbeda antara abstrak (36,6%) dan Tabel 2 (38,7%), serta penyebutan basis
   data yang tidak seragam (PubMed/MEDLINE dipisah, EMBASE hanya di strategi pencarian).
4. Deck ini menyajikan **1 artikel** dari daftar 38 artikel di `../README.md`.
