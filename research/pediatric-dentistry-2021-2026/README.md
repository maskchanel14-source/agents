# Jurnal Kedokteran Gigi Anak 2021-2026 — 38 Artikel Internasional Open Access

> Daftar kurasi 38 artikel jurnal internasional berbahasa Inggris bidang **kedokteran gigi anak (pediatric dentistry)**, terbit 2021-2026, **semua open access** (full text gratis di PubMed Central). Setiap DOI sudah diverifikasi ke Crossref dan setiap artikel punya PMID/PMCID dari Europe PMC. Disusun: 2026-10-13.

## Cara pakai cepat

- **Cari referensi untuk bab tertentu** → lihat daftar tema di bawah (T1-T11); tiap tabel memuat artikel + link DOI dan PMC.
- **Mau langsung menyitasi di Word/Mendeley/Zotero** → impor file `references.bib` (38 entri, sudah lengkap DOI/PMID/PMCID).
- **Mau tahu cara pencariannya dibuat ulang** → baca `search-log.md` (semua query, tanggal, dan jumlah hasil).
- **Mau versi Excel** → `data/articles.csv`.

## Isi paket

| File | Isi |
|---|---|
| `README.md` | Dokumen ini: metode, tabel tema, tabel jurnal, catatan |
| `references.bib` | 38 entri BibTeX siap impor |
| `search-log.md` | Log pencarian yang bisa direproduksi (query + hitungan hasil) |
| `data/articles.json` | Struktur tema & urutan artikel |
| `data/records.json` | Metadata per artikel (sumber tunggal) |
| `data/articles.csv` | Versi tabel untuk Excel/Sheets |
| `build.py` | Skrip yang membangun README, .bib, dan .csv dari JSON |

## Metode singkat (bisa dikutip di bagian metode)

**Pertanyaan:** artikel jurnal internasional berbahasa Inggris bidang kedokteran gigi anak, 5 tahun terakhir (2021 sampai Oktober 2026), yang bisa diunduh gratis.

**Kriteria inklusi**

1. Bahasa Inggris;
2. Tahun terbit 2021-2026 (lima tahun terakhir per 13 Oktober 2026);
3. Artikel jurnal peer-review dari penerbit internasional (semua terindeks PubMed/MEDLINE, mayoritas Scopus);
4. Open access: full text tersedia gratis di PubMed Central (PMC);
5. Topik termasuk lingkup kedokteran gigi anak (karies anak, MIH, perilaku, trauma, pulpa, anak berkebutuhan khusus, dll).

**Kriteria eksklusi:** preprint (arXiv/medRxiv/bioRxiv), abstrak konferensi, editorial, artikel non-Inggris, artikel berbayar tanpa versi PMC, dan artikel kedokteran umum yang tidak menyentuh aspek gigi-mulut anak.

**Basis data & verifikasi**

- Pencarian utama: **Europe PMC REST API** (korpus MEDLINE/PubMed + PMC) dengan filter `OPEN_ACCESS:Y`, `PUB_YEAR:[2021 TO 2026]`, `LANG:eng`, diurutkan berdasarkan jumlah sitasi; dilengkapi **PubMed E-utilities** untuk hitungan judul.
- Verifikasi sitasi: seluruh **38 DOI** dicek ulang ke **Crossref REST API** (judul, nama jurnal, volume, nomor, halaman) — 38/38 cocok; status open access dan tautan PMC diambil dari Europe PMC.
- Tanggal pencarian: 13 Oktober 2026. Jumlah sitasi adalah angka Europe PMC pada tanggal tersebut.

> Catatan metodologis: skrip `verify_citations.py` dari skill `literature-review` tidak bisa dijalankan karena sandbox ini tidak membuka jaringan untuk perintah shell; fungsi yang sama (cek registrasi DOI + tarik metadata) dilakukan langsung ke endpoint Crossref dan Europe PMC. Ini bukan systematic review — daftar ini kurasi bertema, tanpa penghitungan PRISMA.

## Jurnal-jurnal sumber

| Jurnal | Penerbit | ISSN | Peringkat (dicek Okt 2026) | Artikel di daftar ini |
|---|---|---|---|---|
| International Journal of Paediatric Dentistry | Wiley | 0960-7439 / 1365-263X | Q1 (SJR 0,687; IF ~2,2) | 5 |
| European Archives of Paediatric Dentistry | Springer | 1818-6300 / 1996-9805 | Q1 (SJR 2025 = 0,812) | 9 |
| BMC Oral Health | BMC / Springer Nature | 1472-6831 | Q1 (SJR 0,936; IF 3,8) | 5 |
| International Journal of Oral Science | Nature Portfolio (Sichuan University) | 1674-2818 / 2049-3169 | Q1 (IF 17,6) | 1 |
| JAMA Network Open | American Medical Association | 2574-3805 | Q1 (kedokteran umum, JCR) | 1 |
| Japanese Dental Science Review | Elsevier | 1882-7616 / 2213-6851 | Terindeks PubMed/MEDLINE | 2 |
| International Dental Journal | Wiley (FDI) | 0020-6539 / 1875-595X | Terindeks PubMed/MEDLINE | 1 |
| Dental Traumatology | Wiley | 1600-4469 / 1600-9657 | Terindeks PubMed/MEDLINE | 1 |
| The Saudi Dental Journal | Elsevier (Saudi Dental Society) | 1013-9052 / 1658-3558 | Open access penuh | 1 |
| Frontiers in Oral Health | Frontiers | 2673-4842 | Open access penuh | 2 |
| Scientific Reports | Nature Portfolio | 2045-2322 | Terindeks PubMed/MEDLINE | 1 |
| npj Biofilms and Microbiomes | Nature Portfolio | 2055-5008 | Terindeks PubMed/MEDLINE | 1 |
| BMJ | BMJ Publishing Group | 0959-8138 / 1756-1833 | Q1 (kedokteran umum, JCR) | 1 |
| Health Expectations | Wiley | 1369-6513 / 1369-7625 | Terindeks PubMed/MEDLINE | 1 |
| Digital Health | SAGE | 2055-2076 | Open access penuh | 1 |
| Dentistry Journal | MDPI | 2304-6767 | Open access penuh | 1 |
| Healthcare | MDPI | 2227-9032 | Open access penuh | 1 |
| Brain and Behavior | Wiley | 2162-3279 | Open access penuh | 1 |
| Dental Research Journal | Wolters Kluwer (Isfahan Univ.) | 1735-3327 / 2008-0255 | Open access penuh | 1 |
| Journal of Oral Rehabilitation | Wiley | 0305-182X / 1365-2842 | Terindeks PubMed/MEDLINE | 1 |

Kuartil/IF dicek dari Scimago dan ringkasan JCR pada Oktober 2026; nilai ini berubah setiap tahun, sebutkan tahun metrik saat mengutipnya. Semua jurnal di atas terindeks di PubMed/MEDLINE.

Catatan akses: tautan **PMC** selalu menyediakan full text gratis dalam bentuk HTML; sebagian artikel juga menyediakan PDF penerbit secara gratis (mis. artikel BMC, MDPI, Frontiers, Springer OA).

## Daftar artikel per tema

### T1. Beban penyakit & kebijakan karies anak usia dini (Early Childhood Caries/ECC)

*Tema inti kedokteran gigi anak: definisi, angka prevalensi global, dan kebijakan pencegahan. Pijakan untuk latar belakang (bab 1) dan argumen promotif.*

| # | Artikel | Jurnal (tahun) | Tipe | Sitasi | Akses gratis |
|---|---|---|---|---|---|
| 1 | Zou J, Du Q, Ge L, et al. — **Expert consensus on early childhood caries management** | Int J Oral Sci 14(1):35 (2022) | Expert consensus | 112 | [DOI](https://doi.org/10.1038/s41368-022-00186-0) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC9283525/) |
| 2 | Maklennan A, Borg-Bartolo R, Wierichs RJ, et al. — **A systematic review and meta-analysis on early-childhood-caries global data** | BMC Oral Health 24(1):835 (2024) | Systematic review + meta-analysis | 34 | [DOI](https://doi.org/10.1186/s12903-024-04605-y) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC11267837/) |
| 3 | Chen J, Duangthip D, Gao SS, et al. (22 penulis; daftar lengkap di DOI) — **Oral Health Policies to Tackle the Burden of Early Childhood Caries: A Review of 14 Countries/Regions** | Front Oral Health 2:670154 (2021) | Policy review | 51 | [DOI](https://doi.org/10.3389/froh.2021.670154) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC8757786/) |
| 4 | Vukovic A, Schmutz KA, Borg-Bartolo R, et al. — **Caries status in 12-year-old children, geographical location and socioeconomic conditions across European countries: A systematic review and meta-analysis** | Int J Paediatr Dent 35(1):201-215 (2025) | Systematic review + meta-analysis | 21 | [DOI](https://doi.org/10.1111/ipd.13224) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC11626496/) |

1. **Zou 2022** — Konsensus ahli terbaru soal etiologi, penilaian risiko, pencegahan, dan tata laksana ECC; sering dipakai sebagai rujukan utama definisi ECC.
2. **Maklennan 2024** — Angka prevalensi ECC global terbaru (dengan analisis subkelompok); sumber data kuat untuk bab pendahuluan.
3. **Chen 2021** — Perbandingan kebijakan ECC di 14 negara/region (termasuk Asia); berguna untuk argumen kebijakan kesehatan gigi anak di Indonesia.
4. **Vukovic 2025** — Menghubungkan status karies anak 12 tahun dengan letak geografis dan kondisi sosial-ekonomi; model analisis yang bisa ditiru untuk data Indonesia.

### T2. Silver diamine fluoride (SDF) & pencegahan karies

*Intervensi non-invasif paling cepat berkembang; ada RCT dan kebijakan global yang bisa dikutip.*

| # | Artikel | Jurnal (tahun) | Tipe | Sitasi | Akses gratis |
|---|---|---|---|---|---|
| 1 | Gao SS, Amarquaye G, Arrow P, et al. (30 penulis; daftar lengkap di DOI) — **Global Oral Health Policies and Guidelines: Using Silver Diamine Fluoride for Caries Control** | Front Oral Health 2:685557 (2021) | Policy/guideline review | 50 | [DOI](https://doi.org/10.3389/froh.2021.685557) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC8757897/) |
| 2 | Ruff RR, Barry-Godín T, Niederman R — **Effect of Silver Diamine Fluoride on Caries Arrest and Prevention: The CariedAway School-Based Randomized Clinical Trial** | JAMA Netw Open 6(2):e2255458 (2023) | Randomized clinical trial | 47 | [DOI](https://doi.org/10.1001/jamanetworkopen.2022.55458) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC9912124/) |
| 3 | Zheng FM, Yan IG, Duangthip D, et al. — **Silver diamine fluoride therapy for dental care** | Jpn Dent Sci Rev 58:249-257 (2022) | Narrative review | 68 | [DOI](https://doi.org/10.1016/j.jdsr.2022.08.001) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC9463534/) |
| 4 | Timms L, Choi S, Marshman Z, et al. — **Parental acceptability of silver diamine fluoride: The UK and US experiences** | Int J Paediatr Dent 35(1):13-21 (2025) | Cross-sectional study | 8 | [DOI](https://doi.org/10.1111/ipd.13195) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC11626544/) |

1. **Gao 2021** — Peta kebijakan pemakaian SDF di berbagai negara; menjawab 'apakah SDF sudah masuk pedoman resmi?'.
2. **Ruff 2023** — RCT besar berbasis sekolah: SDF menahan dan mencegah karies pada anak; bukti level tertinggi untuk efikasi SDF.
3. **Zheng 2022** — Ringkasan mekanisme, indikasi, efek samping (diskolorasi), dan protokol aplikasi SDF; pegangan praktis klinisi.
4. **Timms 2025** — Faktor penerimaan orang tua terhadap SDF (termasuk kekhawatiran diskolorasi); penting untuk konseling sebelum aplikasi SDF.

### T3. Minimal intervention & restorasi gigi sulung

*Perubahan paradigma: dari 'bor semua' ke ART/Hall technique/lesi dalam tanpa tumpatan.*

| # | Artikel | Jurnal (tahun) | Tipe | Sitasi | Akses gratis |
|---|---|---|---|---|---|
| 1 | BaniHani A, Santamaría RM, Hu S, et al. — **Minimal intervention dentistry for managing carious lesions into dentine in primary teeth: an umbrella review** | Eur Arch Paediatr Dent 23(5):667-693 (2022) | Umbrella review | 59 | [DOI](https://doi.org/10.1007/s40368-021-00675-6) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC9637620/) |
| 2 | Duggal M, Gizani S, Albadri S, et al. (23 penulis; daftar lengkap di DOI) — **Best clinical practice guidance for treating deep carious lesions in primary teeth: an EAPD policy document** | Eur Arch Paediatr Dent 23(5):659-666 (2022) | Clinical practice guideline (EAPD) | 56 | [DOI](https://doi.org/10.1007/s40368-022-00718-6) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC9637614/) |
| 3 | Hu S, BaniHani A, Nevitt S, et al. — **Hall technique for primary teeth: A systematic review and meta-analysis** | Jpn Dent Sci Rev 58:286-297 (2022) | Systematic review + meta-analysis | 21 | [DOI](https://doi.org/10.1016/j.jdsr.2022.09.003) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC9520271/) |

1. **BaniHani 2022** — Payung dari banyak systematic review: membandingkan tumpatan konvensional vs teknik minimally invasive pada gigi sulung.
2. **Duggal 2022** — Panduan resmi EAPD untuk lesi karies dalam pada gigi sulung: kapan selective removal, kapan pulpotomi, kapan ekstraksi.
3. **Hu 2022** — Bukti tingkat tinggi bahwa Hall technique (SSC tanpa preparasi) efektif menahan karies gigi sulung.

### T4. Molar incisor hypomineralisation (MIH)

*Menyumbang beban karies pada gigi molar pertama permanen; sudah ada panduan EAPD terbaru.*

| # | Artikel | Jurnal (tahun) | Tipe | Sitasi | Akses gratis |
|---|---|---|---|---|---|
| 1 | Lygidakis NA, Garot E, Somani C, et al. — **Best clinical practice guidance for clinicians dealing with children presenting with molar-incisor-hypomineralisation (MIH): an updated European Academy of Paediatric Dentistry policy document** | Eur Arch Paediatr Dent 23(1):3-21 (2022) | Clinical practice guideline (EAPD) | 254 | [DOI](https://doi.org/10.1007/s40368-021-00668-5) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC8926988/) |
| 2 | Lopes LB, Machado V, Mascarenhas P, et al. — **The prevalence of molar-incisor hypomineralization: a systematic review and meta-analysis** | Sci Rep 11(1):22405 (2021) | Systematic review + meta-analysis | 94 | [DOI](https://doi.org/10.1038/s41598-021-01541-7) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC8599453/) |
| 3 | Somani C, Taylor GD, Garot E, et al. — **An update of treatment modalities in children and adolescents with teeth affected by molar incisor hypomineralisation (MIH): a systematic review** | Eur Arch Paediatr Dent 23(1):39-64 (2022) | Systematic review | 73 | [DOI](https://doi.org/10.1007/s40368-021-00635-0) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC8927013/) |

1. **Lygidakis 2022** — Dokumen paling banyak dikutip di seluruh daftar ini (254 sitasi); panduan MIH resmi EAPD versi terbaru.
2. **Lopes 2021** — Angka prevalensi MIH dunia + faktor geografis; data dasar untuk rumusan masalah prevalensi.
3. **Somani 2022** — Komparasi modalitas terapi MIH (desensitisasi, sealant, restorasi, SSC, sampai ekstraksi) beserta kekuatan buktinya.

### T5. Manajemen perilaku, kecemasan dental & sedasi

*Dasar non-farmakologis pengelolaan anak; banyak RCT distraksi (VR, musik, aromaterapi).*

| # | Artikel | Jurnal (tahun) | Tipe | Sitasi | Akses gratis |
|---|---|---|---|---|---|
| 1 | Shekhar S, Suprabha BS, Shenoy R, et al. — **Effect of active and passive distraction techniques while administering local anaesthesia on the dental anxiety, behaviour and pain levels of children: a randomised controlled trial** | Eur Arch Paediatr Dent 23(3):417-427 (2022) | Randomized clinical trial | 24 | [DOI](https://doi.org/10.1007/s40368-022-00698-7) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC9167192/) |
| 2 | Kohli N, Hugar SM, Soneta SP, et al. — **Psychological behavior management techniques to alleviate dental fear and anxiety in 4-14-year-old children in pediatric dentistry: A systematic review and meta-analysis** | Dent Res J (Isfahan) 19(1):47 (2022) | Systematic review + meta-analysis | 16 | [DOI](https://doi.org/10.4103/1735-3327.346405) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC9338387/) |
| 3 | Du Q, Ma X, Wang S, et al. — **A digital intervention using virtual reality helmets to reduce dental anxiety of children under local anesthesia and primary teeth extraction: A randomized clinical trial** | Brain Behav 12(6):e2600 (2022) | Randomized clinical trial | 24 | [DOI](https://doi.org/10.1002/brb3.2600) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC9226823/) |
| 4 | Ashley P, Anand P, Andersson K — **Best clinical practice guidance for conscious sedation of children undergoing dental treatment: an EAPD policy document** | Eur Arch Paediatr Dent 22(6):989-1002 (2021) | Clinical practice guideline (EAPD) | 43 | [DOI](https://doi.org/10.1007/s40368-021-00660-z) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC8629790/) |

1. **Shekhar 2022** — RCT distraksi aktif vs pasif saat anestesi lokal; desain mudah direplikasi untuk skripsi klinis.
2. **Kohli 2022** — Meta-analisis teknik psikologis (tell-show-do, modeling, distraksi) penurun kecemasan anak usia 4-14 tahun.
3. **Du 2022** — RCT distraksi VR (headset) pada ekstraksi gigi sulung; topik teknologi yang sedang naik.
4. **Ashley 2021** — Standar EAPD untuk sedasi sadar: pemilihan obat, monitoring, dan aspek safety pada anak.

### T6. Pulpa, endodontik & trauma gigi anak

*Topik kasus harian; mencakup gigi imatur nekrosis, epidemiologi trauma, dan mekanisme resorpsi.*

| # | Artikel | Jurnal (tahun) | Tipe | Sitasi | Akses gratis |
|---|---|---|---|---|---|
| 1 | Wikström A, Brundin M, Lopes MF, et al. — **What is the best long-term treatment modality for immature permanent teeth with pulp necrosis and apical periodontitis?** | Eur Arch Paediatr Dent 22(3):311-340 (2021) | Systematic review | 49 | [DOI](https://doi.org/10.1007/s40368-020-00575-1) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC8213569/) |
| 2 | Laforgia A, Inchingolo AM, Inchingolo F, et al. — **Paediatric dental trauma: insights from epidemiological studies and management recommendations** | BMC Oral Health 25(1):6 (2025) | Systematic review | 23 | [DOI](https://doi.org/10.1186/s12903-024-05222-5) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC11697964/) |
| 3 | Galler KM, Grätz EM, Widbiller M, et al. — **Pathophysiological mechanisms of root resorption after dental trauma: a systematic scoping review** | BMC Oral Health 21(1):163 (2021) | Systematic scoping review | 70 | [DOI](https://doi.org/10.1186/s12903-021-01510-6) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC7995728/) |

1. **Wikström 2021** — Perbandingan apexifikasi, revaskularisasi, dan MTA apical plug untuk gigi imatur nekrosis; sering jadi rujukan kasus endo anak.
2. **Laforgia 2025** — Epidemiologi trauma gigi anak plus rekomendasi tata laksana terkini; terbit 2025, datanya segar.
3. **Galler 2021** — Mekanisme patofisiologi resorpsi akar pasca trauma (permukaan, inflamasi, penggantian); dasar prognosis kasus trauma.

### T7. Kualitas hidup terkait kesehatan gigi-mulut (OHRQoL)

*Kerangka outcome pasien yang makin wajib di skripsi/tesis klinis anak.*

| # | Artikel | Jurnal (tahun) | Tipe | Sitasi | Akses gratis |
|---|---|---|---|---|---|
| 1 | Pakkhesal M, Riyahi E, Naghavi Alhosseini A, et al. — **Impact of dental caries on oral health related quality of life among preschool children: perceptions of parents** | BMC Oral Health 21(1):68 (2021) | Cross-sectional study | 46 | [DOI](https://doi.org/10.1186/s12903-021-01396-4) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC7885600/) |
| 2 | Omara M, Stamm T, Bekes K — **Four-dimensional oral health-related quality of life impact in children: A systematic review** | J Oral Rehabil 48(3):293-304 (2021) | Systematic review | 40 | [DOI](https://doi.org/10.1111/joor.13066) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC7984176/) |
| 3 | Jälevik B, Sabel N, Robertson A — **Can molar incisor hypomineralization cause dental fear and anxiety or influence the oral health-related quality of life in children and adolescents?—a systematic review** | Eur Arch Paediatr Dent 23(1):65-78 (2022) | Systematic review | 52 | [DOI](https://doi.org/10.1007/s40368-021-00631-4) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC8927003/) |

1. **Pakkhesal 2021** — Menghubungkan skor karies dengan OHRQoL anak prasekolah menurut persepsi orang tua; instrumennya bisa ditiru.
2. **Omara 2021** — Kerangka 4 dimensi OHRQoL anak (gejala, fungsi, psikologis, sosial) + instrumen pengukurannya.
3. **Jälevik 2022** — Jembatan antara MIH (T4) dan kecemasan dental/OHRQoL (T5, T7); bukti bahwa MIH berdampak psikososial.

### T8. Anak berkebutuhan khusus & disabilitas

*Bukti ketimpangan (inequity) dan hambatan akses layanan; kuat untuk argumen kebijakan.*

| # | Artikel | Jurnal (tahun) | Tipe | Sitasi | Akses gratis |
|---|---|---|---|---|---|
| 1 | Ningrum V, Bakar A, Shieh TM, et al. — **The Oral Health Inequities between Special Needs Children and Normal Children in Asia: A Systematic Review and Meta-Analysis** | Healthcare (Basel) 9(4):410 (2021) | Systematic review + meta-analysis | 29 | [DOI](https://doi.org/10.3390/healthcare9040410) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC8065439/) |
| 2 | Khan AJ, Md Sabri BA, Ahmad MS — **Factors affecting provision of oral health care for people with special health care needs: A systematic review** | Saudi Dent J 34(7):527-537 (2022) | Systematic review | 33 | [DOI](https://doi.org/10.1016/j.sdentj.2022.08.008) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC9577340/) |
| 3 | Erwin J, Paisi M, Neill S, et al. — **Factors influencing oral health behaviours, access and delivery of dental care for autistic children and adolescents: A mixed-methods systematic review** | Health Expect 25(4):1269-1318 (2022) | Mixed-methods systematic review | 44 | [DOI](https://doi.org/10.1111/hex.13544) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC9327820/) |

1. **Ningrum 2021** — Data kuantitatif kesenjangan kesehatan gigi anak berkebutuhan khusus vs anak reguler di Asia (termasuk Asia Tenggara).
2. **Khan 2022** — Faktor pasien, keluarga, klinisi, dan sistem yang menghambat pemberian layanan gigi-mulut pada pasien berkebutuhan khusus.
3. **Erwin 2022** — Sintesis kualitatif + kuantitatif khusus anak autistik; memperkaya bagian 'anak berkebutuhan khusus' dengan perspektif orang tua.

### T9. Teledentistry, AI & teknologi digital

*Topik terhangat 2024-2026; siap dipakai sebagai novelty/kerangka penelitian baru.*

| # | Artikel | Jurnal (tahun) | Tipe | Sitasi | Akses gratis |
|---|---|---|---|---|---|
| 1 | AlShaya M, Farsi D, Farsi N, et al. — **The accuracy of teledentistry in caries detection in children - A diagnostic study** | Digit Health 8:20552076221109075 (2022) | Diagnostic accuracy study | 32 | [DOI](https://doi.org/10.1177/20552076221109075) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC9237921/) |
| 2 | Kuru HE, Aşık A, Demir DM — **Can Artificial Intelligence Language Models Effectively Address Dental Trauma Questions?** | Dent Traumatol 41(5):567-580 (2025) | Cross-sectional evaluation study | 20 | [DOI](https://doi.org/10.1111/edt.13063) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12424120/) |
| 3 | Tuygunov N, Samaranayake L, Khurshid Z, et al. — **The Transformative Role of Artificial Intelligence in Dentistry: A Comprehensive Overview Part 2: The Promise and Perils, and the International Dental Federation Communique** | Int Dent J 75(2):397-404 (2025) | Review / FDI communique | 156 | [DOI](https://doi.org/10.1016/j.identj.2025.02.006) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC11976557/) |
| 4 | Elsonbaty S, Elgarba BM, Fontenele RC, et al. — **Novel AI-based tool for primary tooth segmentation on CBCT using convolutional neural networks: A validation study** | Int J Paediatr Dent 35(1):97-107 (2025) | Validation study (AI) | 12 | [DOI](https://doi.org/10.1111/ipd.13204) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC11626492/) |

1. **AlShaya 2022** — Validitas deteksi karies anak lewat foto/teleconsultation vs pemeriksaan klinis; referensi utama teledentistry anak.
2. **Kuru 2025** — Menguji jawaban ChatGPT dkk untuk pertanyaan trauma gigi anak; topik AI + kedokteran gigi anak, sangat fresh.
3. **Tuygunov 2025** — Pernyataan resmi FDI (Federation Dentaire Internationale) soal AI di kedokteran gigi, termasuk janji dan risikonya pada pasien anak.
4. **Elsonbaty 2025** — Segmentasi otomatis gigi sulung pada CBCT dengan CNN; contoh riset AI yang benar-benar spesifik kedokteran gigi anak.

### T10. Diet gula, menyusui, mikrobioma & pencegahan karies

*Menghubungkan faktor risiko diet dengan biome mulut; bagus untuk kerangka teori etiologi.*

| # | Artikel | Jurnal (tahun) | Tipe | Sitasi | Akses gratis |
|---|---|---|---|---|---|
| 1 | Cheever VJ, Mohajeri A, Patel K, et al. — **Impact of Free Sugar Consumption on Dental Caries: A Cross-Sectional Analysis of Children in the United States** | Dent J (Basel) 13(2):48 (2025) | Cross-sectional study | 21 | [DOI](https://doi.org/10.3390/dj13020048) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC11854531/) |
| 2 | Lara-Castor L, Micha R, Cudhea F, et al. — **Intake of sugar sweetened beverages among children and adolescents in 185 countries between 1990 and 2018: population based study** | BMJ 386:e079234 (2024) | Population-based study | 42 | [DOI](https://doi.org/10.1136/bmj-2024-079234) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC11305379/) |
| 3 | Luo SC, Wei SM, Luo XT, et al. — **How probiotics, prebiotics, synbiotics, and postbiotics prevent dental caries: an oral microbiota perspective** | npj Biofilms Microbiomes 10(1):14 (2024) | Review | 96 | [DOI](https://doi.org/10.1038/s41522-024-00488-7) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC10894247/) |
| 4 | Li K, Wang J, Du N, et al. — **Salivary microbiome and metabolome analysis of severe early childhood caries** | BMC Oral Health 23(1):30 (2023) | Laboratory / cross-sectional study | 38 | [DOI](https://doi.org/10.1186/s12903-023-02722-8) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC9850820/) |
| 5 | Lustosa K, Rodrigues LRS, Rocha RM, et al. — **Risk of Early Childhood Dental Caries Associated With Prolonged Breastfeeding: A Systematic Review and Meta-Analysis** | Int J Paediatr Dent 35(5):964-985 (2025) | Systematic review + meta-analysis | 9 | [DOI](https://doi.org/10.1111/ipd.13313) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12332104/) |

1. **Cheever 2025** — Analisis data survei nasional: asupan gula bebas vs karies anak; angka aktual pembanding untuk data Indonesia.
2. **Lara-Castor 2024** — Data konsumsi minuman manis anak di 185 negara; konteks global (dan regional) untuk faktor risiko karies.
3. **Luo 2024** — Mekanisme probiotik/prebiotik/postbiotik mencegah karies (termasuk pada anak); alternatif pencegahan non-fluorida.
4. **Li 2023** — Profil mikrobioma dan metabolom saliva pada severe ECC; basis biologis untuk penanda risiko karies.
5. **Lustosa 2025** — Menjawab pertanyaan klasik klinisi: kapan menyusui berisiko terhadap karies anak; berguna untuk edukasi orang tua.

### T11. Erosi gigi & tooth wear

*Tema pelengkap karies: etiologinya berbeda (asam, bukan bakteri), dan dua artikel terbaru membahas diagnosis sampai pencegahan.*

| # | Artikel | Jurnal (tahun) | Tipe | Sitasi | Akses gratis |
|---|---|---|---|---|---|
| 1 | Carvalho TS, Baumann T, Niemeyer SH, et al. — **Dental erosion and erosive tooth wear in childhood and adolescence: from diagnosis to prevention** | Eur Arch Paediatr Dent 27(5):1317-1333 (2026) | Review | 0 | [DOI](https://doi.org/10.1007/s40368-026-01233-8) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC13593698/) |
| 2 | Marschner F, Kanzow P, Wiegand A — **Systematic review and meta-analysis on prevalence and anamnestic risk factors for erosive tooth wear in the primary dentition** | Int J Paediatr Dent 35(2):389-404 (2025) | Systematic review + meta-analysis | 7 | [DOI](https://doi.org/10.1111/ipd.13250) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC11788517/) |

1. **Carvalho 2026** — Terbit Agustus 2026 (paling baru di daftar ini): diagnosis sampai pencegahan erosi gigi anak; pelengkap tema karies.
2. **Marschner 2025** — Prevalensi dan faktor risiko tooth wear erosif pada gigi sulung; melengkapi tema erosi (T11) dengan angka kuantitatif.

## Ringkasan angka

- Total artikel: **38** (semuanya open access, semuanya berbahasa Inggris)
- Rentang terbit: **2021-2026**
- Tema: **11** kelompok
- Artikel paling banyak dikutip: Lygidakis dkk. 2022, dokumen kebijakan MIH EAPD (**254 sitasi**)
- Artikel terbaru: Carvalho dkk. 2026, review erosi gigi anak (terbit Agustus 2026)

## Keterbatasan

1. Jumlah sitasi berbeda-beda antar database (Europe PMC vs Scopus vs Google Scholar); angka di sini dari Europe PMC.
2. Bukan systematic review: tidak ada penyaringan ganda dan hitungan PRISMA; daftar ini kurasi bertema yang mengutamakan kualitas jurnal, relevansi klinis, dan dampak sitasi.
3. Beberapa isu klinis (misalnya sedasi, trauma) punya pedoman yang lebih spesifik per negara; panduan EAPD/FDI/IADT dipakai sebagai acuan internasional.
4. Dokumen kebijakan/panduan (bukan penelitian primer) tetap disertakan karena menjadi rujukan standar, dan sudah ditandai pada kolom Tipe.

## Lisensi & atribusi

- Metadata (judul, penulis, DOI, PMID) adalah data publik dari Crossref dan Europe PMC.
- Teks lengkap setiap artikel mengikuti lisensi masing-masing (umumnya CC BY 4.0 pada jurnal open access); sertakan atribusi sesuai ketentuan jurnal bila mengutip gambar atau tabel.
- Daftar ini disusun ulang dari `data/records.json` memakai `build.py`; jangan menyunting README secara manual.
