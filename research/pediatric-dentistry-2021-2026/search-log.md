# Search log — literatur kedokteran gigi anak 2021-2026

Log ini membuat pencarian bisa diulang (reproducible). Semua pencarian dijalankan **13 Oktober 2026**.
Angka "hasil" adalah `hitCount` yang dilaporkan basis data pada tanggal tersebut dan akan berubah seiring waktu.

## Skill & tool dari repo yang dipakai

| Skill / tool | Peran dalam tugas ini |
|---|---|
| `tools/skill_router.py plan/search` | Merutekan tugas: memilih skill riset, verifikasi, dan domain (output: `citation-management`, `literature-review`, `paper-lookup`) |
| `literature-review` (`.agents/skills/literature-review/`) | Kerangka 7 fase: scoping → pencarian sistematis → penyaringan → ekstraksi → sintesis → verifikasi sitasi → dokumen |
| `paper-lookup` (`.agents/skills/paper-lookup/`) | Kontrak endpoint tiap basis data + catatan mode gagal senyap (Europe PMC `errCode` di body 200, dsb.) |
| `citation-management` (`.agents/skills/citation-management/`) | Format BibTeX + validasi metadata |
| `scientific-writing` (pendamping) | Struktur penulisan daftar pustaka & catatan keterbatasan |

Catatan: `npx skills experimental_install` sudah menyiapkan `.agents/skills/` (256 paket) sesuai `AGENTS.md`.

## Basis data

| Basis data | Endpoint | Peran |
|---|---|---|
| Europe PMC REST | `https://www.ebi.ac.uk/europepmc/webservices/rest/search` | Pencarian utama (korpus MEDLINE + PMC), filter open access |
| PubMed E-utilities | `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi` | Hitungan judul pembanding |
| Crossref REST | `https://api.crossref.org/works` | Verifikasi 38 DOI (judul, jurnal, volume, nomor, halaman) |

## Query yang dijalankan (Europe PMC)

Semua query memakai pola: `(topik) AND (OPEN_ACCESS:Y) AND (PUB_YEAR:[2021 TO 2026]) AND (LANG:eng)`, urut `sort=CITED desc`.

| # | Query (inti) | Hasil |
|---|---|---|
| 1 | `TITLE:"early childhood caries"` | 459 |
| 2 | `TITLE:"silver diamine fluoride"` | 297 |
| 3 | `TITLE:"molar incisor hypomineralisation" OR TITLE:"...hypomineralization"` | 234 |
| 4 | `(TITLE:"dental anxiety" OR TITLE:"behaviour management" OR TITLE:"behavior management") AND (TITLE:children OR TITLE:child)` | 92 |
| 5 | `TITLE:"traumatic dental injuries" OR TITLE:"dental trauma"` | 208 |
| 6 | `(TITLE:"caries prevention" OR TITLE:"fluoride varnish") AND (TITLE:children OR TITLE:child OR TITLE:preschool)` | 38 |
| 7 | `TITLE:"pulpotomy" OR TITLE:"vital pulp therapy"` | 325 |
| 8 | `TITLE:"Hall technique" OR TITLE:"preformed metal crown" OR TITLE:"stainless steel crown"` | 44 |
| 9 | `TITLE:"oral health-related quality of life" AND (TITLE:children OR TITLE:child OR TITLE:adolescents)` | 172 |
| 10 | `TITLE:"special health care needs" OR TITLE:"children with disabilities" OR TITLE:"special needs"` | 535 (banyak hasil non-gigi; disaring manual) |
| 11 | `(TITLE:teledentistry OR TITLE:mhealth OR TITLE:"digital health") AND (TITLE:children OR TITLE:dental OR TITLE:oral)` | 188 (banyak hasil non-gigi; disaring manual) |
| 12 | `TITLE:autism OR TITLE:autistic OR TITLE:"cerebral palsy" OR TITLE:"down syndrome"` + `(TITLE:dental OR TITLE:oral OR TITLE:caries)` | 216 |
| 13 | `TITLE:probiotics AND (TITLE:caries OR TITLE:dental OR TITLE:oral)` | 155 |
| 14 | `TITLE:malocclusion OR TITLE:"interceptive orthodontics" OR TITLE:"early orthodontic treatment"` + anak | 124 |
| 15 | `(TITLE:"sugar-sweetened beverages" OR TITLE:"free sugars" OR TITLE:"added sugar" OR TITLE:"sugar consumption")` + karies/anak | 53 |
| 16 | `(TITLE:"artificial intelligence" OR TITLE:"deep learning" OR TITLE:"machine learning")` + dental/pediatric + tahun 2023-2026 | 1589 (banyak hasil non-gigi; disaring manual) |
| 17 | `ISSN:"0960-7439" OR ISSN:"1365-263X" OR ISSN:"1818-6300" OR ISSN:"1996-9805"` (IJPD + EAPD) + OA + 2021-2026 | 300 |
| 18 | `ISSN:"0960-7439" OR ISSN:"1365-263X"` (IJPD) + OA + 2024-2026 | 69 |
| 19 | `ISSN:"1472-6831" OR ISSN:"1818-6300"` + OA + 2024-2026 | 5639 |
| 20 | `ISSN:"0960-7439" OR ISSN:"1365-263X" OR ISSN:"1818-6300" OR ISSN:"1996-9805" OR ISSN:"0974-7052" OR ISSN:"1591-996X"` + OA + 2025-2026, urut tanggal | 599 |

Pembanding di PubMed (E-utilities):
`"pediatric dentistry"[jour] AND 2021:2026[dp]` → **350** judul.

## Verifikasi DOI (Crossref)

Dijalankan dalam 4 panggilan batch dengan pemilihan field
`select=DOI,title,container-title,volume,issue,page,issued`:

1. Batch 1: 12 DOI → 12/12 ditemukan
2. Batch 2: 10 DOI → 10/10 ditemukan
3. Batch 3: 11 DOI → 11/11 ditemukan
4. Batch 4: 3 DOI (IJPD) → 3/3 ditemukan
5. Batch 5: 2 DOI (IJPD) → 2/2 ditemukan

Total **38/38 DOI valid** dan metadata (nama jurnal, volume, nomor, halaman) cocok dengan Europe PMC.
Status open access + PMCID diambil dari field `isOpenAccess`, `inPMC`, `hasPDF`, `pmcid` Europe PMC.

Contoh query verifikasi (dapat diulang):

```text
https://api.crossref.org/works?filter=doi:10.1038/s41368-022-00186-0,doi:10.1186/s12903-024-04605-y
  &select=DOI,title,container-title,volume,issue,page,issued
  &mailto=alamat-email-anda@contoh.org
```

## Alur penyaringan

1. **Kandidat** dikumpulkan dari 20 query di atas (ratusan hingga ribuan hasil per query).
2. **Saring otomatis**: hanya `isOpenAccess = Y` dan `inPMC = Y` (punya full text gratis).
3. **Saring judul/abstrak**: dibuang yang bukan lingkup gigi-mulut anak (contoh hasil yang dibuang: manajemen berat badan digital, sepsis pediatrik, tumor otak pediatrik, terapi wicara COVID, kesehatan mental orang tua).
4. **Prioritas jurnal**: jurnal kedokteran gigi/pediatric dentistry didahulukan; jurnal umum (BMJ, JAMA Netw Open) hanya dipakai bila artikelnya benar-benar relevan dan berdampak besar.
5. **Batas akhir**: 38 artikel dalam 11 tema; setiap tema 2-5 artikel.

## Batasan teknis yang perlu diketahui

- Sandbox kerja tidak memberi akses jaringan untuk perintah shell (`curl` gagal), sehingga
  `scripts/verify_citations.py` dari skill `literature-review` tidak dapat dijalankan.
  Verifikasi setara dilakukan lewat endpoint Crossref/Europe PMC memakai kanal pengambilan halaman.
- Europe PMC bisa mengembalikan HTTP 200 dengan isi `errCode` saat query salah; pemeriksaan bentuk
  respons dilakukan manual (sesuai peringatan di skill `paper-lookup`).
- Jumlah sitasi adalah metrik Europe PMC, bukan Scopus/Google Scholar, dan akan berbeda antar basis data.
