# Deck: Presentasi Jurnal — Prevalensi MIH (Lopes dkk., Sci Rep 2021)

Deck PowerPoint **editable** (15 slide, bahasa Indonesia) untuk diskusi jurnal kedokteran
gigi anak, dibangun dari satu artikel dalam daftar `../README.md`.

## Berkas hasil

| Berkas | Isi |
|---|---|
| `Presentasi-Jurnal-MIH-Lopes-2021.pptx` | **Deck utama** — 15 slide, 289 objek native, catatan pemateri di setiap slide |
| `spec.json` | Kontrak koordinat (source of truth: bbox inci, font, warna, z-index, reading order, rujukan) |
| `author_spec.py` | Naskah spesifikasi — semua koordinat & isi slide ditulis eksplisit di sini |
| `build_deck.py` | Pembangun PPTX; murni memetakan spec → objek PowerPoint, tanpa keputusan tata letak |
| `audit_deck.py` | Audit geometri, kolisi, margin, kapasitas teks, type scale, reading order |
| `preview_spec.py` | Renderer perkiraan (Pillow) untuk pemeriksaan visual cepat |
| `audits/package-report.json` | Laporan integritas paket OOXML dari `validate_package.py` milik skill repo |
| `audits/geometry-audit.json`, `audits/accessibility-audit.json`, `audits/quality-gates.json` | Hasil audit |
| `audits/preview/` | PNG tiap slide + contact sheet (perkiraan tata letak, bukan render PowerPoint) |
| `build_record.json` | Rekaman pembangunan (spec → objek per slide) |

## Sumber (source manifest)

| ID | Sitasi | Peran | Verifikasi |
|---|---|---|---|
| S1 | Lopes LB, Machado V, Mascarenhas P, Mendes JJ, Botelho J. *The prevalence of molar-incisor hypomineralization: a systematic review and meta-analysis.* Sci Rep. 2021;11:22405. DOI 10.1038/s41598-021-01541-7 · PMID 34789780 · PMC8599453 | Artikel utama | Europe PMC full text (CC BY 4.0) + Crossref, 2026-10-13 |
| S2 | Weerheijm KL, dkk. *Judgement criteria for MIH in epidemiologic studies.* Eur J Paediatr Dent. 2003;4:110–113 | Definisi kriteria EAPD | dikutip dalam S1 |
| S3 | Schwendicke F, dkk. *Global burden of molar incisor hypomineralization.* J Dent. 2018;68:10–18 | Pembanding SR sebelumnya | dikutip dalam S1 |
| S4 | Zhao D, dkk. *The prevalence of MIH: evidence from 70 studies.* Int J Paediatr Dent. 2018;28:170–179 | Pembanding SR sebelumnya | dikutip dalam S1 |

Semua angka, tabel, dan kesimpulan di deck berasal dari S1 dan dapat dilacak lewat locator
pada setiap objek (`source_ref`) di `spec.json`.

## Struktur deck (15 slide)

1. Sampul · 2. Ringkasan cepat · 3. Latar belakang: apa itu MIH · 4. Latar belakang: celah penelitian
5. Tujuan (PECO + luaran) · 6. Metode: desain & pencarian · 7. Metode: kriteria, RoB, analisis
8. Hasil: alur seleksi & kualitas studi · 9. Hasil: prevalensi global 13,5% · 10. Hasil: keparahan & molar
11. Sub-analisis wilayah & kriteria diagnostik · 12. Diskusi · 13. Critical appraisal (kekuatan vs keterbatasan)
14. Implikasi klinis · 15. Kesimpulan & rujukan

Catatan pemateri (speaker notes) tersedia di setiap slide dalam PowerPoint, lengkap dengan
locator sumber dan pertanyaan pemicu diskusi.

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

Dependensi: `python-pptx`, `Pillow`, dan `defusedxml` (khusus skrip validator skill).

## Status audit

| Gerbang | Hasil |
|---|---|
| Audit geometri & layout (289 objek, 15 slide) | **0 error** — tidak ada kolisi, semua konten di dalam margin aman dan di atas footer |
| Type scale & kapasitas teks | Lulus; teks terkecil 9 pt (footer), isi ≥ 10 pt |
| Reading order, judul slide, header tabel | Lulus (lihat `audits/accessibility-audit.json`) |
| Integritas paket OOXML (`validate_package.py`) | **ok: true**, 0 error, 0 warning |

**Pengecualian terdokumentasi:** objek `rule` (garis teal 1,5 pt) dideklarasikan setinggi 0,028 in,
tetapi PowerPoint menormalkan konektor lurus ke tinggi 0 — stroke dirender dari lebar garis.
Tercatat di `audits/quality-gates.json` pada `accepted_exceptions`.

## Catatan keterbatasan

1. Font deck memakai **Calibri** (bawaan PowerPoint/Office). Bila dibuka di perangkat tanpa
   Calibri, PowerPoint akan mengganti font (mis. Carlito) — tata letak tetap, tampilan sedikit berbeda.
2. `preview_spec.py` adalah renderer perkiraan berbasis Pillow dengan font DejaVu; gambar
   `audits/preview/` hanya untuk pemeriksaan tata letak, bukan representasi persis hasil PowerPoint.
3. Tidak ada aset visual eksternal (tanpa logo/gambar pihak ketiga), sehingga tidak ada risiko
   lisensi; seluruh kartu, bar, dan tabel dibuat sebagai objek native PowerPoint.
4. Deck ini menyajikan **1 artikel** dari daftar 38 artikel di `../README.md`. Artikel lain dapat
   dibuatkan dengan pola yang sama (`author_spec.py` → `build_deck.py` → `audit_deck.py`).
