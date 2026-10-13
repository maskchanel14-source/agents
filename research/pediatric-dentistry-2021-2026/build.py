#!/usr/bin/env python3
"""Generate README.md, references.bib, and data/articles.csv from the JSON dataset.

Usage:  python3 build.py
Inputs: data/articles.json (themes + ordering), data/records.json (metadata per article)
Outputs: README.md, references.bib, data/articles.csv
Stdlib only; deterministic output (sorted keys where relevant).
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
README = HERE / "README.md"
BIB = HERE / "references.bib"
CSV = HERE / "data" / "articles.csv"

MAX_DISPLAY_AUTHORS = 3
MAX_BIB_AUTHORS = 12
COMPILED = "2026-10-13"

LATEX_MAP = {
    "\u00e4": '{\\"a}', "\u00f6": '{\\"o}', "\u00fc": '{\\"u}', "\u00df": '{\\ss}',
    "\u00e1": "{\\'a}", "\u00e9": "{\\'e}", "\u00ed": "{\\'i}", "\u00f3": "{\\'o}",
    "\u00fa": "{\\'u}", "\u00e0": "{\\`a}", "\u00e8": "{\\`e}", "\u00ec": "{\\`i}",
    "\u00f1": "{\\~n}", "\u00e7": "{\\c c}", "\u015f": "{\\c s}", "\u0131": "{\\i}",
    "\u2014": "---", "\u2013": "--", "\u2019": "'", "\u201c": "``", "\u201d": "''",
    "&": "\\&", "%": "\\%", "$": "\\$", "#": "\\#", "_": "\\_",
    "{": "\\{", "}": "\\}", "~": "\\textasciitilde{}", "^": "\\textasciicircum{}",
}


def latex(text: str) -> str:
    out = []
    for ch in text:
        out.append(LATEX_MAP.get(ch, ch))
    return "".join(out)


def md_authors(authors: list[str], note: str | None = None) -> str:
    shown = ", ".join(authors[:MAX_DISPLAY_AUTHORS])
    if len(authors) > MAX_DISPLAY_AUTHORS:
        shown += ", et al."
    if note:
        shown += f" ({note})"
    return shown


def bib_author(name: str) -> str:
    parts = name.split()
    if len(parts) >= 2 and parts[-1].isupper() and parts[-1].isalpha():
        family, initials = " ".join(parts[:-1]), parts[-1]
        given = " ".join(f"{i}." for i in initials)
        return f"{latex(family)}, {latex(given)}"
    return latex(name)


def bib_entry(key: str, r: dict) -> str:
    authors = r["authors"]
    if len(authors) > MAX_BIB_AUTHORS:
        author_field = " and ".join(bib_author(a) for a in authors[:MAX_BIB_AUTHORS]) + " and others"
    else:
        author_field = " and ".join(bib_author(a) for a in authors)
    fields = [
        ("author", author_field),
        ("title", latex(r["title"])),
        ("journal", latex(r["journal"])),
        ("year", str(r["year"])),
        ("volume", r["volume"]),
        ("number", r.get("issue", "")),
        ("pages", r["pages"]),
        ("doi", r["doi"]),
        ("pmid", r["pmid"]),
        ("pmcid", r["pmcid"]),
        ("note", f"Open access (PMC): https://pmc.ncbi.nlm.nih.gov/articles/{r['pmcid']}/"),
        ("keywords", "pediatric dentistry, open access"),
    ]
    body = ",\n".join(f"  {k:<8} = {{{v}}}" for k, v in fields if v != "")
    return f"@article{{{key},\n{body}\n}}\n"


VENUES = [
    # (journal name, publisher, ISSN, verified ranking, verified flag)
    ("International Journal of Paediatric Dentistry", "Wiley", "0960-7439 / 1365-263X", "Q1 (SJR 0,687; IF ~2,2)"),
    ("European Archives of Paediatric Dentistry", "Springer", "1818-6300 / 1996-9805", "Q1 (SJR 2025 = 0,812)"),
    ("BMC Oral Health", "BMC / Springer Nature", "1472-6831", "Q1 (SJR 0,936; IF 3,8)"),
    ("International Journal of Oral Science", "Nature Portfolio (Sichuan University)", "1674-2818 / 2049-3169", "Q1 (IF 17,6)"),
    ("JAMA Network Open", "American Medical Association", "2574-3805", "Q1 (kedokteran umum, JCR)"),
    ("Japanese Dental Science Review", "Elsevier", "1882-7616 / 2213-6851", "Terindeks PubMed/MEDLINE"),
    ("International Dental Journal", "Wiley (FDI)", "0020-6539 / 1875-595X", "Terindeks PubMed/MEDLINE"),
    ("Dental Traumatology", "Wiley", "1600-4469 / 1600-9657", "Terindeks PubMed/MEDLINE"),
    ("The Saudi Dental Journal", "Elsevier (Saudi Dental Society)", "1013-9052 / 1658-3558", "Open access penuh"),
    ("Frontiers in Oral Health", "Frontiers", "2673-4842", "Open access penuh"),
    ("Scientific Reports", "Nature Portfolio", "2045-2322", "Terindeks PubMed/MEDLINE"),
    ("npj Biofilms and Microbiomes", "Nature Portfolio", "2055-5008", "Terindeks PubMed/MEDLINE"),
    ("BMJ", "BMJ Publishing Group", "0959-8138 / 1756-1833", "Q1 (kedokteran umum, JCR)"),
    ("Health Expectations", "Wiley", "1369-6513 / 1369-7625", "Terindeks PubMed/MEDLINE"),
    ("Digital Health", "SAGE", "2055-2076", "Open access penuh"),
    ("Dentistry Journal", "MDPI", "2304-6767", "Open access penuh"),
    ("Healthcare", "MDPI", "2227-9032", "Open access penuh"),
    ("Brain and Behavior", "Wiley", "2162-3279", "Open access penuh"),
    ("Dental Research Journal", "Wolters Kluwer (Isfahan Univ.)", "1735-3327 / 2008-0255", "Open access penuh"),
    ("Journal of Oral Rehabilitation", "Wiley", "0305-182X / 1365-2842", "Terindeks PubMed/MEDLINE"),
]


def build_readme(meta: dict, themes: list[dict], rec: dict) -> str:
    total = sum(len(t["articles"]) for t in themes)
    years = sorted({rec[k]["year"] for t in themes for k in t["articles"]})
    lines: list[str] = []
    a = lines.append

    a("# Jurnal Kedokteran Gigi Anak 2021-2026 — 38 Artikel Internasional Open Access")
    a("")
    a(f"> Daftar kurasi {total} artikel jurnal internasional berbahasa Inggris bidang **kedokteran gigi anak (pediatric dentistry)**, "
      f"terbit {years[0]}-{years[-1]}, **semua open access** (full text gratis di PubMed Central). "
      f"Setiap DOI sudah diverifikasi ke Crossref dan setiap artikel punya PMID/PMCID dari Europe PMC. "
      f"Disusun: {meta['compiled']}.")
    a("")
    a("## Cara pakai cepat")
    a("")
    a("- **Cari referensi untuk bab tertentu** → lihat daftar tema di bawah (T1-T11); tiap tabel memuat artikel + link DOI dan PMC.")
    a("- **Mau langsung menyitasi di Word/Mendeley/Zotero** → impor file `references.bib` (38 entri, sudah lengkap DOI/PMID/PMCID).")
    a("- **Mau tahu cara pencariannya dibuat ulang** → baca `search-log.md` (semua query, tanggal, dan jumlah hasil).")
    a("- **Mau versi Excel** → `data/articles.csv`.")
    a("")
    a("## Isi paket")
    a("")
    a("| File | Isi |")
    a("|---|---|")
    a("| `README.md` | Dokumen ini: metode, tabel tema, tabel jurnal, catatan |")
    a("| `references.bib` | 38 entri BibTeX siap impor |")
    a("| `search-log.md` | Log pencarian yang bisa direproduksi (query + hitungan hasil) |")
    a("| `data/articles.json` | Struktur tema & urutan artikel |")
    a("| `data/records.json` | Metadata per artikel (sumber tunggal) |")
    a("| `data/articles.csv` | Versi tabel untuk Excel/Sheets |")
    a("| `build.py` | Skrip yang membangun README, .bib, dan .csv dari JSON |")
    a("")
    a("## Metode singkat (bisa dikutip di bagian metode)")
    a("")
    a("**Pertanyaan:** artikel jurnal internasional berbahasa Inggris bidang kedokteran gigi anak, 5 tahun terakhir "
      "(2021 sampai Oktober 2026), yang bisa diunduh gratis.")
    a("")
    a("**Kriteria inklusi**")
    a("")
    a("1. Bahasa Inggris;")
    a("2. Tahun terbit 2021-2026 (lima tahun terakhir per 13 Oktober 2026);")
    a("3. Artikel jurnal peer-review dari penerbit internasional (semua terindeks PubMed/MEDLINE, mayoritas Scopus);")
    a("4. Open access: full text tersedia gratis di PubMed Central (PMC);")
    a("5. Topik termasuk lingkup kedokteran gigi anak (karies anak, MIH, perilaku, trauma, pulpa, anak berkebutuhan khusus, dll).")
    a("")
    a("**Kriteria eksklusi:** preprint (arXiv/medRxiv/bioRxiv), abstrak konferensi, editorial, artikel non-Inggris, "
      "artikel berbayar tanpa versi PMC, dan artikel kedokteran umum yang tidak menyentuh aspek gigi-mulut anak.")
    a("")
    a("**Basis data & verifikasi**")
    a("")
    a("- Pencarian utama: **Europe PMC REST API** (korpus MEDLINE/PubMed + PMC) dengan filter `OPEN_ACCESS:Y`, "
      "`PUB_YEAR:[2021 TO 2026]`, `LANG:eng`, diurutkan berdasarkan jumlah sitasi; dilengkapi **PubMed E-utilities** untuk hitungan judul.");
    a("- Verifikasi sitasi: seluruh **38 DOI** dicek ulang ke **Crossref REST API** (judul, nama jurnal, volume, nomor, halaman) — "
      "38/38 cocok; status open access dan tautan PMC diambil dari Europe PMC.");
    a("- Tanggal pencarian: 13 Oktober 2026. Jumlah sitasi adalah angka Europe PMC pada tanggal tersebut.")
    a("")
    a("> Catatan metodologis: skrip `verify_citations.py` dari skill `literature-review` tidak bisa dijalankan karena sandbox ini "
      "tidak membuka jaringan untuk perintah shell; fungsi yang sama (cek registrasi DOI + tarik metadata) dilakukan langsung ke "
      "endpoint Crossref dan Europe PMC. Ini bukan systematic review — daftar ini kurasi bertema, tanpa penghitungan PRISMA.")
    a("")
    a("## Jurnal-jurnal sumber")
    a("")
    counts: dict[str, int] = {}
    for t in themes:
        for key in t["articles"]:
            jname = rec[key]["journal"]
            counts[jname] = counts.get(jname, 0) + 1
    a("| Jurnal | Penerbit | ISSN | Peringkat (dicek Okt 2026) | Artikel di daftar ini |")
    a("|---|---|---|---|---|")
    for name, pub, issn, rank in VENUES:
        a(f"| {name} | {pub} | {issn} | {rank} | {counts.get(name, 0)} |")
    a("")
    a("Kuartil/IF dicek dari Scimago dan ringkasan JCR pada Oktober 2026; nilai ini berubah setiap tahun, "
      "sebutkan tahun metrik saat mengutipnya. Semua jurnal di atas terindeks di PubMed/MEDLINE.")
    a("")
    a("Catatan akses: tautan **PMC** selalu menyediakan full text gratis dalam bentuk HTML; sebagian artikel juga "
      "menyediakan PDF penerbit secara gratis (mis. artikel BMC, MDPI, Frontiers, Springer OA).")
    a("")
    a("## Daftar artikel per tema")
    a("")
    for t in themes:
        a(f"### {t['id']}. {t['name']}")
        a("")
        a(f"*{t['why']}*")
        a("")
        a("| # | Artikel | Jurnal (tahun) | Tipe | Sitasi | Akses gratis |")
        a("|---|---|---|---|---|---|")
        for i, key in enumerate(t["articles"], start=1):
            r = rec[key]
            authors = md_authors(r["authors"], r.get("authors_note"))
            title = r["title"].rstrip(".")
            jr = f"{r['journal_short']} {r['volume']}"
            if r.get("issue"):
                jr += f"({r['issue']})"
            jr += f":{r['pages']} ({r['year']})"
            doi = f"[DOI](https://doi.org/{r['doi']})"
            pmc = f"[PMC](https://pmc.ncbi.nlm.nih.gov/articles/{r['pmcid']}/)"
            a(f"| {i} | {authors} — **{title}** | {jr} | {r['type']} | {r['cites']} | {doi} · {pmc} |")
        a("")
        for i, key in enumerate(t["articles"], start=1):
            r = rec[key]
            a(f"{i}. **{r['authors'][0].split()[0]} {r['year']}** — {r['why']}")
        a("")
    a("## Ringkasan angka")
    a("")
    a(f"- Total artikel: **{total}** (semuanya open access, semuanya berbahasa Inggris)")
    a(f"- Rentang terbit: **{years[0]}-{years[-1]}**")
    a(f"- Tema: **{len(themes)}** kelompok")
    a("- Artikel paling banyak dikutip: Lygidakis dkk. 2022, dokumen kebijakan MIH EAPD (**254 sitasi**)")
    a("- Artikel terbaru: Carvalho dkk. 2026, review erosi gigi anak (terbit Agustus 2026)")
    a("")
    a("## Keterbatasan")
    a("")
    a("1. Jumlah sitasi berbeda-beda antar database (Europe PMC vs Scopus vs Google Scholar); angka di sini dari Europe PMC.")
    a("2. Bukan systematic review: tidak ada penyaringan ganda dan hitungan PRISMA; daftar ini kurasi bertema yang mengutamakan kualitas jurnal, relevansi klinis, dan dampak sitasi.")
    a("3. Beberapa isu klinis (misalnya sedasi, trauma) punya pedoman yang lebih spesifik per negara; panduan EAPD/FDI/IADT dipakai sebagai acuan internasional.")
    a("4. Dokumen kebijakan/panduan (bukan penelitian primer) tetap disertakan karena menjadi rujukan standar, dan sudah ditandai pada kolom Tipe.")
    a("")
    a("## Lisensi & atribusi")
    a("")
    a("- Metadata (judul, penulis, DOI, PMID) adalah data publik dari Crossref dan Europe PMC.")
    a("- Teks lengkap setiap artikel mengikuti lisensi masing-masing (umumnya CC BY 4.0 pada jurnal open access); "
      "sertakan atribusi sesuai ketentuan jurnal bila mengutip gambar atau tabel.")
    a("- Daftar ini disusun ulang dari `data/records.json` memakai `build.py`; jangan menyunting README secara manual.")
    a("")
    return "\n".join(lines)


def build_bib(rec: dict, themes: list[dict]) -> str:
    lines = [
        "% references.bib — 38 artikel kedokteran gigi anak (2021-2026), semua open access",
        f"% Dibuat otomatis oleh build.py pada {COMPILED} dari data/records.json.",
        "% Sumber metadata: Europe PMC (PMID/PMCID) + Crossref (verifikasi DOI).",
        "% Kompilasi: pdflatex/bibtex, biber/BibLaTeX, atau impor ke Mendeley/Zotero/EndNote.",
        "",
    ]
    for t in themes:
        lines.append(f"% ==== {t['id']}. {t['name']} ====")
        lines.append("")
        for key in t["articles"]:
            lines.append(bib_entry(key, rec[key]).rstrip("\n"))
            lines.append("")
    return "\n".join(lines).rstrip("\n") + "\n"


def build_csv(themes: list[dict], rec: dict) -> str:
    import io

    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["theme_id", "theme", "no", "authors", "title", "journal", "year",
                "volume", "issue", "pages", "type", "cited_by", "doi", "pmid", "pmcid", "pmc_link"])
    for t in themes:
        for i, key in enumerate(t["articles"], start=1):
            r = rec[key]
            w.writerow([t["id"], t["name"], i, "; ".join(r["authors"]), r["title"], r["journal"],
                        r["year"], r["volume"], r.get("issue", ""), r["pages"], r["type"],
                        r["cites"], r["doi"], r["pmid"], r["pmcid"],
                        f"https://pmc.ncbi.nlm.nih.gov/articles/{r['pmcid']}/"])
    return buf.getvalue()


def main() -> None:
    meta = json.loads((HERE / "data" / "articles.json").read_text(encoding="utf-8"))["meta"]
    themes = json.loads((HERE / "data" / "articles.json").read_text(encoding="utf-8"))["themes"]
    rec = json.loads((HERE / "data" / "records.json").read_text(encoding="utf-8"))
    assigned = [k for t in themes for k in t["articles"]]
    missing = [k for k in assigned if k not in rec]
    unused = [k for k in rec if k not in assigned]
    if missing or unused:
        raise SystemExit(f"dataset mismatch: missing={missing} unused={unused}")
    README.write_text(build_readme(meta, themes, rec), encoding="utf-8")
    BIB.write_text(build_bib(rec, themes), encoding="utf-8")
    CSV.write_text(build_csv(themes, rec), encoding="utf-8")
    print(f"wrote {README.name}, {BIB.name}, {CSV.relative_to(HERE)} ({len(assigned)} articles)")


if __name__ == "__main__":
    main()
