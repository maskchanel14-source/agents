#!/usr/bin/env python3
"""Author the coordinate-explicit deck specification for the Lopes 2021 MIH deck.

This file is the AUTHOR, not a renderer: every inch coordinate, font size, and
z-index below is written out explicitly. It materializes `spec.json`, which is the
contract that `build_deck.py` consumes and `audit_deck.py` verifies.

Design lock: profile `editorial-minimal` (research/exec narrative) adapted to a
medical-academic palette. One motif: teal rule under every action title.
Sources: S1 = Lopes et al. 2021 (main article), S2 = Weerheijm et al. 2003 (EAPD
criteria, cited inside S1), S3 = Schwendicke et al. 2018, S4 = Zhao et al. 2018.
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

# ---------------------------------------------------------------- design tokens
PAGE = "#F8FAFC"
SURFACE = "#FFFFFF"
TINT = "#F0FDFA"
INK = "#0F172A"
BODY = "#334155"
MUTED = "#64748B"
TEAL = "#0E7490"
TEAL_DEEP = "#155E75"
TEAL_EDGE = "#99F6E4"
AMBER = "#B45309"
AMBER_TINT = "#FFFBEB"
LINE = "#CBD5E1"
FONT = "Calibri"

SLIDE_W, SLIDE_H = 13.333, 7.5
X0, CONTENT_W = 0.6, 12.13
CONTENT_TOP, CONTENT_BOTTOM = 1.66, 6.6
FOOTER_TOP = 6.85
RULE_Y = 1.5

FOOTER_SRC = ("Sumber utama: Lopes LB, Machado V, Mascarenhas P, Mendes JJ, Botelho J. "
              "Sci Rep 2021;11:22405 (CC BY 4.0)")

slides: list[dict] = []
_slide_no = 0

# --------------------------------------------------------------------- helpers
def _obj(oid, kind, role, content, bbox, z, style=None, classification="content",
         source_ref=None, alt=None):
    o = {
        "id": oid,
        "kind": kind,
        "role": role,
        "classification": classification,
        "content": content,
        "style": style or {},
        "bbox": {"x": bbox[0], "y": bbox[1], "width": bbox[2], "height": bbox[3]},
        "z_index": z,
    }
    if source_ref:
        o["source_ref"] = source_ref
    if alt:
        o["alt_text"] = alt
    return o


def text(oid, bbox, s, size, color=BODY, bold=False, italic=False, align="left",
         anchor="top", z=3, spacing=None, source_ref=None, role="body"):
    style = {"font": FONT, "font_size": size, "bold": bold, "italic": italic,
             "color": color, "align": align, "anchor": anchor,
             "inset_left": 0.0, "inset_right": 0.0}
    if spacing:
        style["line_spacing"] = spacing
    return _obj(oid, "text", role, {"text": s}, bbox, z, style, source_ref=source_ref)


def card(oid, bbox, fill=SURFACE, line_color=LINE, z=2, radius=0.06, role="card"):
    return _obj(oid, "shape", role, {"shape": "rounded_rectangle"},
                bbox, z, {"fill": fill, "line_color": line_color, "line_width": 1.0,
                          "radius": radius, "shadow": False})


def panel(oid, bbox, fill=TINT, line_color=TEAL_EDGE, z=2):
    return _obj(oid, "shape", "panel", {"shape": "rounded_rectangle"},
                bbox, z, {"fill": fill, "line_color": line_color, "line_width": 1.25,
                          "radius": 0.08, "shadow": False})


def bar(oid, bbox, fill, z=2):
    return _obj(oid, "shape", "bar", {"shape": "rounded_rectangle"},
                bbox, z, {"fill": fill, "line_color": fill, "line_width": 0.5,
                          "radius": 0.5, "shadow": False})


def rule(oid, y, x=X0, w=CONTENT_W, color=TEAL, h=0.028, z=2, classification="layout_design"):
    return _obj(oid, "line", "rule", {"x1": x, "y1": y, "x2": x + w, "y2": y},
                (x, y, w, h), z, {"color": color, "width": 1.5}, classification=classification)


def new_slide(sid, kicker, headline, reading_order, source_locator="Abstract"):
    global _slide_no
    _slide_no += 1
    objs = [
        _obj("bg", "shape", "background", {"shape": "rectangle"},
             (0, 0, SLIDE_W, SLIDE_H), 0,
             {"fill": PAGE, "line_color": PAGE, "line_width": 0, "shadow": False},
             classification="layout_design"),
        rule("rule", RULE_Y),
        text("kicker", (X0, 0.3, 9.0, 0.26), kicker.upper(), 10, TEAL, True, z=3, role="kicker"),
        text("title", (X0, 0.58, CONTENT_W, 0.86), headline, 25, INK, True, z=3,
             role="title", spacing=0.95),
        text("footer_src", (X0, FOOTER_TOP + 0.03, 10.6, 0.3), FOOTER_SRC, 9, MUTED, z=4,
             role="footer"),
        text("page_no", (11.7, FOOTER_TOP + 0.03, 1.03, 0.3), f"{_slide_no}", 9, MUTED,
             align="right", z=4, role="footer"),
    ]
    slide = {
        "id": sid,
        "title": headline,
        "kicker": kicker,
        "notes": "",
        "accessibility": {"reading_order": reading_order + ["footer_src", "page_no"],
                          "title": headline, "source_locator": source_locator},
        "layout_tree": {
            "slide_size": {"width": SLIDE_W, "height": SLIDE_H},
            "root_group_id": "root",
            "groups": {"root": {"id": "root", "role": "slide", "layout_mode": "absolute",
                                "object_ids": [], "group_ids": [],
                                "bbox": {"x": 0, "y": 0, "width": SLIDE_W, "height": SLIDE_H}}},
            "objects": {o["id"]: o for o in objs},
        },
    }
    slides.append(slide)
    return slide


def add(slide, *objs):
    tree = slide["layout_tree"]
    for o in objs:
        if o["id"] in tree["objects"]:
            raise SystemExit(f"duplicate object id {o['id']} on {slide['id']}")
        tree["objects"][o["id"]] = o
        tree["groups"]["root"]["object_ids"].append(o["id"])


def bullet(slide, oid, y, s, size=14, x=X0, w=CONTENT_W, h=0.42, color=BODY,
           marker=True, locator="Abstract", bold_prefix=None):
    """One bullet = one marker glyph object + one text object with hanging offset."""
    prefix = "\u25aa  " if marker else ""
    style = {"font": FONT, "font_size": size, "bold": False, "italic": False,
             "color": color, "align": "left", "anchor": "top",
             "inset_left": 0.0, "inset_right": 0.0, "line_spacing": 0.95}
    o = _obj(oid, "text", "body", {"text": prefix + s}, (x, y, w, h), 3, style,
             source_ref={"source_id": "S1", "locator": locator} if locator else None)
    add(slide, o)
    return o


# =============================================================== S01 — cover
s = new_slide("s01_cover", "Presentasi jurnal \u00b7 Kedokteran gigi anak",
              "Prevalensi Molar-Incisor Hypomineralization (MIH) pada Anak dan Remaja",
              ["kicker", "title", "subtitle", "meta_card", "meta", "presenter"],
              source_locator="Title page")
add(s,
    text("subtitle", (X0, 1.5, CONTENT_W, 0.5),
         "The prevalence of molar-incisor hypomineralization: a systematic review and meta-analysis",
         15, MUTED, italic=True, z=3, role="subtitle"),
    panel("meta_card", (X0, 2.15, CONTENT_W, 2.15), z=2),
    text("meta", (X0 + 0.3, 2.35, CONTENT_W - 0.6, 1.75),
         "Naskah asli: Lopes LB, Machado V, Mascarenhas P, Mendes JJ, Botelho J \u2014 "
         "Egas Moniz, Portugal\n"
         "Jurnal: Scientific Reports (Nature Portfolio), 2021;11:22405 \u00b7 Open access CC BY 4.0\n"
         "DOI: 10.1038/s41598-021-01541-7 \u00b7 PMID 34789780 \u00b7 PMC8599453\n"
         "Desain: systematic review & meta-analisis (PRISMA) \u00b7 "
         "Registrasi PROSPERO CRD42021229435",
         13, BODY, z=3, role="meta", spacing=1.05),
    text("presenter", (X0, 4.6, CONTENT_W, 0.4),
         "Pemateri: ______________________   \u00b7   Tanggal: ______________________   \u00b7   "
         "Program Studi Kedokteran Gigi",
         12, INK, z=3, role="presenter"),
    text("cta", (X0, 5.25, CONTENT_W, 1.0),
         "\u201cMIH bukan kelainan langka: sekitar 1 dari 7\u20138 anak mengalaminya, dan lebih dari "
         "sepertiga kasusnya tergolong sedang\u2013berat.\u201d",
         16, TEAL_DEEP, bold=True, z=3, role="callout"),
)

# =============================================================== S02 — ringkasan
s = new_slide("s02_ringkasan", "Ringkasan cepat",
              "Satu meta-analisis, 116 studi, 113.089 peserta \u2014 prevalensi global 13,5%",
              ["kicker", "title", "c1", "c2", "c3", "c4", "c5", "c6", "takeaway"],
              source_locator="Abstract; Table 2")
for i, (head, val, sub) in enumerate([
    ("Desain", "SR + meta-analisis", "PRISMA; protokol PROSPERO CRD42021229435"),
    ("Studi", "116 studi observasional", "98 studi masuk analisis utama (kriteria EAPD 2003)"),
    ("Peserta", "113.089 anak & remaja", "133.734 peserta pada analisis awal semua klasifikasi"),
    ("Temuan utama", "13,5% (95% CI 12,0\u201315,1)", "I\u00b2 = 98,0% \u2192 heterogenitas tinggi"),
    ("Kualitas bukti", "SORT A", "48 studi skor NOS 9/9; hanya 1 studi kualitas sedang"),
    ("Registrasi", "PROSPERO", "CRD42021229435 \u00b7 Sci Rep 2021;11:22405"),
]):
    y = 1.72 + (i // 3) * 1.62
    x = X0 + (i % 3) * (3.87 + 0.16)
    add(s,
        card(f"c{i+1}", (x, y, 3.87, 1.46)),
        text(f"c{i+1}h", (x + 0.22, y + 0.16, 3.43, 0.24), head.upper(), 10, TEAL, True, z=3),
        text(f"c{i+1}v", (x + 0.22, y + 0.44, 3.43, 0.42), val, 15, INK, True, z=3),
        text(f"c{i+1}s", (x + 0.22, y + 0.88, 3.43, 0.44), sub, 10.5, MUTED, z=3, spacing=0.95),
        )
add(s, text("takeaway", (X0, 5.05, CONTENT_W, 1.3),
            "Kesimpulan penulis: prevalensi MIH 13,5%; kasus sedang\u2013berat 36,3%; insisivus terkena "
            "pada \u00b136% kasus; hipomineralisasi molar kedua sulung (HSPM) 3,6% \u2014 seluruh hasil "
            "diberi rekomendasi SORT A.",
            13, BODY, z=3, role="takeaway", spacing=0.98))

# =============================================================== S03 — apa itu MIH
s = new_slide("s03_mih", "Latar belakang (1/2)",
              "MIH: defek kualitatif email pada gigi permanen muda, etiologi belum diketahui",
              ["kicker", "title", "d1", "d1t", "d2", "d2t", "d3", "d3t", "impact"],
              source_locator="Introduction")
add(s,
    card("d1", (X0, 1.72, 3.87, 2.3)),
    text("d1t", (X0 + 0.22, 1.9, 3.43, 1.95),
         "APA ITU MIH\nDefek kualitatif (hipomineralisasi) email dengan etiologi yang belum "
         "diketahui. Menyerang satu atau lebih molar pertama permanen, dapat disertai insisivus "
         "permanen. Nomenklatur EAPD sejak 2003.",
         12, BODY, z=3, spacing=1.0),
    card("d2", (X0 + 4.03, 1.72, 3.87, 2.3)),
    text("d2t", (X0 + 4.25, 1.9, 3.43, 1.95),
         "GAMBARAN KLINIS\nOpasitas putih\u2013kuning\u2013cokelat berbatas tegas; email lebih lunak dan "
         "rapuh, sehingga mudah pecah setelah erupsi (post-eruptive breakdown).",
         12, BODY, z=3, spacing=1.0),
    card("d3", (X0 + 8.06, 1.72, 4.07, 2.3)),
    text("d3t", (X0 + 8.28, 1.9, 3.63, 1.95),
         "DAMPAK PADA ANAK\nHipersensitivitas, risiko karies tinggi, restorasi berulang dan "
         "kompleks, serta beban estetik dan psikososial.",
         12, BODY, z=3, spacing=1.0),
    panel("impact", (X0, 4.2, CONTENT_W, 1.6)),
    text("impact_t", (X0 + 0.3, 4.4, CONTENT_W - 0.6, 1.2),
         "Mengapa prevalensi penting bagi klinisi dan program kesehatan?\n"
         "\u2022  Angka prevalensi menentukan besar beban penyakit \u2192 dasar perencanaan skrining, "
         "alokasi tenaga, dan edukasi orang tua.\n"
         "\u2022  Rentang laporan yang lebar (2,8%\u201340,2%) membuat perencanaan sulit \u2014 "
         "diperlukan estimasi global yang terstandar.",
         12.5, INK, z=3, spacing=1.0, source_ref={"source_id": "S1", "locator": "Introduction"},
         role="panel_text"))

# =============================================================== S04 — masalah
s = new_slide("s04_gap", "Latar belakang (2/2)",
              "Rentang 2,8%\u201340,2% menunjukkan masalah standardisasi, bukan sekadar variasi nyata",
              ["kicker", "title", "b1", "b2", "b3", "b4", "gap"],
              source_locator="Introduction")
for i, (label, value, note) in enumerate([
    ("Rentang laporan prevalensi", "2,8% \u2013 40,2%",
     "Selisih >14 kali antar studi sulit ditafsirkan"),
    ("Akar masalah", "Kriteria diagnostik belum seragam",
     "Perbedaan definisi antar peneliti/klinisi"),
    ("Bukti sebelumnya", "SR 2018: 13,1% dan 14,2%",
     "Pencarian hanya sampai pertengahan 2017"),
    ("Belum tergali", "Keparahan, gigi terkena, HSPM",
     "Data karakteristik klinis masih sangat sedikit"),
]):
    x = X0 if i % 2 == 0 else X0 + 6.22
    y = 1.72 + (i // 2) * 1.28
    add(s,
        card(f"b{i+1}", (x, y, 5.91, 1.16)),
        text(f"b{i+1}l", (x + 0.24, y + 0.14, 5.43, 0.24), label.upper(), 10, TEAL, True, z=3),
        text(f"b{i+1}v", (x + 0.24, y + 0.4, 5.43, 0.34), value, 15, INK, True, z=3),
        text(f"b{i+1}n", (x + 0.24, y + 0.74, 5.43, 0.28), note, 11, MUTED, z=3))
add(s, panel("gap", (X0, 4.3, CONTENT_W, 1.5)),
    text("gap_t", (X0 + 0.3, 4.5, CONTENT_W - 0.6, 1.1),
         "Celah penelitian yang diisi artikel ini\n"
         "Belum ada estimasi global terbaru yang (a) memakai kriteria EAPD 2003 secara konsisten, "
         "dan (b) sekaligus menjawab pertanyaan klinis turunan: berapa proporsi kasus sedang\u2013berat, "
         "berapa banyak molar/insisivus yang terkena, dan seberapa sering HSPM menyertai MIH.",
         12.5, INK, z=3, spacing=1.0, source_ref={"source_id": "S1", "locator": "Introduction"}))

# =============================================================== S05 — tujuan
s = new_slide("s05_tujuan", "Tujuan",
              "Satu pertanyaan primer (PECO) dan empat luaran sekunder yang diukur serentak",
              ["kicker", "title", "peco", "o1", "o2", "o3", "o4"],
              source_locator="Methods \u2014 Focused question")
add(s, panel("peco", (X0, 1.72, CONTENT_W, 1.55)),
    text("peco_t", (X0 + 0.3, 1.9, CONTENT_W - 0.6, 1.2),
         "PERTANYAAN PENELITIAN (PECO)  \u201cBerapa prevalensi global MIH?\u201d\n"
         "P (Population): studi klinis/epidemiologis pada manusia   \u00b7   "
         "E (Exposure): diagnosis MIH   \u00b7   C (Comparison): tanpa MIH   \u00b7   "
         "O (Outcome): prevalensi MIH",
         13, INK, z=3, spacing=1.05,
         source_ref={"source_id": "S1", "locator": "Methods, focused question"}))
for i, (t, d) in enumerate([
    ("Luaran primer", "Prevalensi global MIH"),
    ("Sekunder 1", "Prevalensi kasus MIH sedang\u2013berat"),
    ("Sekunder 2", "Jumlah molar pertama permanen yang terkena (1\u20134 gigi)"),
    ("Sekunder 3 & 4", "Kasus dengan insisivus terkena; prevalensi HSPM (molar kedua sulung)"),
]):
    y = 3.5 + i * 0.72
    add(s,
        card(f"o{i+1}", (X0, y, CONTENT_W, 0.62)),
        bar(f"o{i+1}bar", (X0, y + 0.1, 0.07, 0.42), TEAL if i == 0 else TEAL_EDGE),
        text(f"o{i+1}t", (X0 + 0.28, y + 0.14, 2.6, 0.34), t.upper(), 11, TEAL, True, z=3),
        text(f"o{i+1}d", (X0 + 2.95, y + 0.12, 8.9, 0.36), d, 13, BODY, z=3))

# =============================================================== S06 — metode 1
s = new_slide("s06_metode1", "Metode (1/2)",
              "Protokol PRISMA terdaftar, tujuh basis data, pencarian sampai Juli 2021",
              ["kicker", "title", "m1", "m1t", "m2", "m2t", "m3", "m3t"],
              source_locator="Methods \u2014 Protocol, search strategy")
add(s,
    card("m1", (X0, 1.72, 3.87, 2.6)),
    text("m1t", (X0 + 0.24, 1.9, 3.39, 2.25),
         "DESAIN & REGISTRASI\n\u2022  Systematic review + meta-analisis\n"
         "\u2022  Dilaporkan mengikuti pedoman PRISMA\n"
         "\u2022  Protokol terdaftar di PROSPERO: CRD42021229435",
         12, BODY, z=3, spacing=1.0),
    card("m2", (X0 + 4.03, 1.72, 3.87, 2.6)),
    text("m2t", (X0 + 4.27, 1.9, 3.39, 2.25),
         "BASIS DATA & TANGGAL\n\u2022  PubMed, MEDLINE, CENTRAL, Web of Science, SciELO, "
         "LILACS, TRIP\n\u2022  EMBASE ikut pada strategi pencarian\n"
         "\u2022  Pencarian sampai Juli 2021",
         12, BODY, z=3, spacing=1.0),
    card("m3", (X0 + 8.06, 1.72, 4.07, 2.6)),
    text("m3t", (X0 + 8.3, 1.9, 3.59, 2.25),
         "ALGORITMA PENCARIAN\n(hypomineralization OR hypomineralisation OR hypomineralized OR "
         "hypoplasia OR demarcated OR opacities OR MIH OR cheese molars) AND (survey OR "
         "cross-sectional OR prevalence OR \u2026) AND (molar OR molars OR incisors)",
         11.5, BODY, z=3, spacing=0.96),
    )
add(s, text("m_note", (X0, 4.5, CONTENT_W, 1.2),
            "Catatan pembacaan kritis: artikel menyebut PubMed dan MEDLINE sebagai dua entri "
            "terpisah, dan EMBASE hanya muncul pada bagian strategi pencarian \u2014 keduanya wajar "
            "dalam praktik SR, namun jumlah basis data efektif perlu ditelusuri pada lampiran "
            "bila ingin direplikasi.",
            11.5, MUTED, italic=True, z=3, spacing=1.0,
            source_ref={"source_id": "S1", "locator": "Methods, search strategy"}))

# =============================================================== S07 — metode 2
s = new_slide("s07_metode2", "Metode (2/2)",
              "Kriteria ketat, penilaian risiko bias oleh dua peneliti, analisis random-effects",
              ["kicker", "title", "i1", "i1t", "i2", "i2t", "q1", "q1t", "s1", "s1t"],
              source_locator="Methods \u2014 Eligibility, RoB, statistics")
add(s,
    card("i1", (X0, 1.72, 5.91, 2.2)),
    text("i1t", (X0 + 0.24, 1.9, 5.43, 1.85),
         "KRITERIA INKLUSI\n\u2022  Studi observasional yang melaporkan prevalensi MIH\n"
         "\u2022  Definisi MIH dilaporkan dengan jelas\n"
         "\u2022  Subjek tanpa kelainan sistemik; kedua jenis kelamin",
         12, BODY, z=3, spacing=1.0),
    card("i2", (X0 + 6.22, 1.72, 5.91, 2.2)),
    text("i2t", (X0 + 6.46, 1.9, 5.43, 1.85),
         "KRITERIA EKSKLUSI\n\u2022  Populasi khusus (mis. anak lahir prematur)\n"
         "\u2022  Studi yang hanya melaporkan molar sulung\n"
         "\u2022  Sampel non-representatif (institusi, profesi tertentu, karies tinggi)",
         12, BODY, z=3, spacing=1.0),
    card("q1", (X0, 4.1, 5.91, 1.75)),
    text("q1t", (X0 + 0.24, 4.28, 5.43, 1.4),
         "SELEKSI & RISIKO BIAS\n\u2022  Seleksi oleh dua peneliti independen\n"
         "\u2022  Kesepakatan antar-penilai \u03ba = 0,885\n"
         "\u2022  Kualitas dinilai dengan Newcastle\u2013Ottawa Scale (NOS)",
         12, BODY, z=3, spacing=1.0),
    card("s1", (X0 + 6.22, 4.1, 5.91, 1.75)),
    text("s1t", (X0 + 6.46, 4.28, 5.43, 1.4),
         "ANALISIS\n\u2022  Meta-analisis prevalensi model random-effects\n"
         "\u2022  Heterogenitas uji I\u00b2 \u00b7 bias publikasi uji Egger\n"
         "\u2022  Kepastian bukti dinilai dengan SORT",
         12, BODY, z=3, spacing=1.0))

# =============================================================== S08 — hasil 1
s = new_slide("s08_hasil1", "Hasil (1/3)",
              "116 studi lolos seleksi; mutu metodologis hampir seluruhnya tinggi",
              ["kicker", "title", "k1", "k1v", "k2", "k2v", "k3", "k3v", "nos_t", "nos"],
              source_locator="Results; Table 1")
for i, (t, v, n) in enumerate([
    ("Studi dimasukkan", "116", "studi observasional memenuhi kriteria"),
    ("Analisis awal", "133.734", "peserta (semua jenis klasifikasi diagnostik)"),
    ("Analisis utama", "113.089", "peserta dari 98 studi (kriteria EAPD 2003)"),
]):
    x = X0 + i * (3.87 + 0.16)
    add(s,
        card(f"k{i+1}", (x, 1.72, 3.87, 1.5)),
        text(f"k{i+1}l", (x + 0.24, 1.86, 3.39, 0.24), t.upper(), 10, TEAL, True, z=3),
        text(f"k{i+1}v", (x + 0.24, 2.1, 3.39, 0.55), v, 30, TEAL_DEEP, True, z=3),
        text(f"k{i+1}n", (x + 0.24, 2.68, 3.39, 0.4), n, 10.5, MUTED, z=3, spacing=0.95))
add(s, text("nos_t", (X0, 3.45, 6.0, 0.34),
            "Distribusi skor Newcastle\u2013Ottawa Scale", 13, INK, True, z=3),
    text("nos", (X0, 3.85, 6.0, 1.0),
         "\u2022  Sumber inkonsistensi utama: representativitas sampel \u2014 48,7% studi tidak memenuhi "
         "kriteria ini.\n\u2022  Semua studi lain dinilai memadai pada definisi kasus, pemilihan kontrol, "
         "dan penilaian luaran.",
         11.5, BODY, z=3, spacing=1.0, source_ref={"source_id": "S1", "locator": "Results, RoB"}),
    card("nos_card", (X0 + 6.4, 3.4, 5.73, 2.15)),
    text("nos_head", (X0 + 6.62, 3.56, 5.29, 0.3), "Kualitas metodologis (NOS)", 12, INK, True, z=4),
    )

# table object for NOS distribution
add(s, _obj("nos_table", "table", "data_table",
            {"header": ["Skor NOS", "Jumlah studi", "Interpretasi"],
             "rows": [["9/9", "48", "Kualitas tinggi (skor maksimum)"],
                      ["8/9", "53", "Kualitas tinggi"],
                      ["7/9", "6", "Kualitas tinggi"],
                      ["6/9", "1", "Kualitas sedang"]]},
            (X0 + 6.62, 3.9, 5.3, 1.5), 4,
            {"header_fill": TEAL, "header_color": "#FFFFFF", "header_size": 11,
             "body_size": 11, "col_widths": [1.05, 1.15, 3.10],
             "row_height": 0.3, "band_fill": "#F1F5F9", "line_color": LINE},
            source_ref={"source_id": "S1", "locator": "Results, RoB"}))

# =============================================================== S09 — hasil 2
s = new_slide("s09_hasil2", "Hasil (2/3)",
              "Prevalensi global MIH 13,5% \u2014 setara sekitar 1 dari 7\u20138 anak",
              ["kicker", "title", "hero", "hero_v", "hero_l", "r1", "r1t", "r2", "r2t",
               "r3", "r3t", "note"],
              source_locator="Table 2; Results, global prevalence")
add(s,
    panel("hero", (X0, 1.72, 5.5, 3.0)),
    text("hero_v", (X0 + 0.3, 2.05, 4.9, 1.35), "13,5%", 66, TEAL_DEEP, True,
         align="center", z=3, role="metric"),
    text("hero_l", (X0 + 0.3, 3.45, 4.9, 1.1),
         "prevalensi MIH global\n95% CI 12,0\u201315,1   \u00b7   p < 0,001   \u00b7   n = 113.089",
         13, INK, align="center", z=3, spacing=1.05),
    card("r1", (X0 + 5.9, 1.72, 6.23, 0.92)),
    text("r1t", (X0 + 6.14, 1.86, 5.75, 0.66),
         "I\u00b2 = 98,0% \u2014 heterogenitas sangat tinggi antar studi (variasi nyata, bukan acak).",
         12.5, BODY, z=4, spacing=0.98),
    card("r2", (X0 + 5.9, 2.78, 6.23, 0.92)),
    text("r2t", (X0 + 6.14, 2.92, 5.75, 0.66),
         "Uji Egger p = 0,179 \u2014 tidak ada indikasi bias publikasi yang bermakna.",
         12.5, BODY, z=4, spacing=0.98),
    card("r3", (X0 + 5.9, 3.84, 6.23, 0.88)),
    text("r3t", (X0 + 6.14, 3.98, 5.75, 0.62),
         "Cumulative & leave-one-out meta-analisis: estimasi stabil, tidak didorong satu studi.",
         12.5, BODY, z=4, spacing=0.98),
    text("note", (X0, 4.95, CONTENT_W, 1.4),
         "Cara membaca angkanya: 13,5% adalah rata-rata tertimbang dari 98 studi yang memakai "
         "kriteria EAPD 2003. Karena heterogenitas 98%, angka ini paling tepat dibaca sebagai "
         "\u201cbesaran beban populasi\u201d, bukan angka presisi untuk satu negara tertentu.",
         12, MUTED, italic=True, z=3, spacing=1.0,
         source_ref={"source_id": "S1", "locator": "Results, global prevalence"}))

# =============================================================== S10 — hasil 3
s = new_slide("s10_hasil3", "Hasil (3/3)",
              "Lebih dari sepertiga kasus tergolong sedang\u2013berat; pola molar bervariasi",
              ["kicker", "title", "v1", "v1t", "v2", "v2t", "v3", "v3t",
               "bar_t", "m1", "m1v", "m2", "m2v", "m3", "m3v", "m4", "m4v", "barsrc"],
              source_locator="Table 2; Results")
for i, (t, v, n) in enumerate([
    ("Kasus sedang\u2013berat", "36,3%", "95% CI 29,9\u201343,2  \u00b7  33 studi  \u00b7  I\u00b2 = 95,2%"),
    ("Insisivus terkena", "\u00b136\u201339%", "Tabel 2: 38,7% (32,1\u201345,8); abstrak: 36,6%"),
    ("HSPM menyertai MIH", "3,6%", "95% CI 1,9\u20136,8  \u00b7  hanya 7 studi  \u00b7  I\u00b2 = 95,9%"),
]):
    x = X0 + i * (3.87 + 0.16)
    add(s,
        card(f"v{i+1}", (x, 1.72, 3.87, 1.42)),
        text(f"v{i+1}t", (x + 0.22, 1.86, 3.43, 0.24), t.upper(), 10, TEAL, True, z=3),
        text(f"v{i+1}v", (x + 0.22, 2.1, 3.43, 0.5), v, 26, TEAL_DEEP, True, z=3),
        text(f"v{i+1}n", (x + 0.22, 2.6, 3.43, 0.4), n, 10, MUTED, z=3, spacing=0.95))
add(s, text("bar_t", (X0, 3.35, 7.5, 0.32),
            "Distribusi jumlah molar pertama permanen yang terkena (% kasus)",
            13, INK, True, z=3))
molar = [("1 molar", 24.3, "18,9\u201330,7"), ("2 molar", 26.7, "23,9\u201329,7"),
         ("3 molar", 18.1, "13,8\u201323,3"), ("4 molar", 27.4, "21,1\u201334,7")]
for i, (label, val, ci) in enumerate(molar):
    y = 3.78 + i * 0.62
    w = round(val / 30.0 * 4.3, 3)
    add(s,
        text(f"m{i+1}", (X0, y + 0.04, 1.25, 0.34), label, 12, BODY, z=3),
        _obj(f"m{i+1}v", "shape", "bar", {"shape": "rounded_rectangle"},
             (X0 + 1.3, y + 0.03, 4.3, 0.36), 2,
             {"fill": "#E2E8F0", "line_color": "#E2E8F0", "line_width": 0, "radius": 0.5,
              "shadow": False}),
        bar(f"m{i+1}x", (X0 + 1.3, y + 0.03, w, 0.36), TEAL),
        text(f"m{i+1}l", (X0 + 5.72, y + 0.03, 0.84, 0.34), f"{val:.1f}%".replace(".", ","),
             12, INK, True, z=3),
        text(f"m{i+1}c", (X0 + 6.65, y + 0.06, 2.4, 0.3), f"CI {ci}", 10, MUTED, z=3))
add(s, panel("barsrc", (X0 + 9.3, 3.72, 2.83, 2.6)),
    text("barsrc_t", (X0 + 9.52, 3.9, 2.39, 2.24),
         "BACALAH BEGINI\nEmpat pola hampir merata (18\u201327%) \u2014 tidak ada satu pola dominan "
         "jumlah molar yang terkena.\n\nIni menyulitkan prediksi klinis: berat ringannya beban "
         "per anak sangat bervariasi.",
         11, BODY, z=3, spacing=1.0,
         source_ref={"source_id": "S1", "locator": "Table 2"}))

# =============================================================== S11 — sub-analisis
s = new_slide("s11_subanalisis", "Sub-analisis",
              "Amerika tertinggi (15,3%) dan Asia terendah (10,7%), namun bedanya tidak bermakna",
              ["kicker", "title", "g1", "g1v", "g1l", "g2", "g2v", "g2l", "g_note",
               "crit", "crit_t"],
              source_locator="Abstract; Results, subgroup analyses")
add(s,
    card("g1", (X0, 1.72, 6.0, 1.6)),
    text("g1v", (X0 + 0.28, 1.86, 5.44, 0.6), "15,3%", 30, TEAL_DEEP, True, z=3),
    text("g1l", (X0 + 0.28, 2.52, 5.44, 0.66),
         "Amerika \u2014 tertinggi  \u00b7  95% CI 12,8\u201318,3  \u00b7  I\u00b2 = 96,3%", 11.5, BODY, z=3),
    card("g2", (X0 + 6.13, 1.72, 6.0, 1.6)),
    text("g2v", (X0 + 6.41, 1.86, 5.44, 0.6), "10,7%", 30, TEAL_DEEP, True, z=3),
    text("g2l", (X0 + 6.41, 2.52, 5.44, 0.66),
         "Asia \u2014 terendah  \u00b7  95% CI 8,5\u201313,5  \u00b7  I\u00b2 = 98,7%", 11.5, BODY, z=3),
    text("g_note", (X0, 3.45, CONTENT_W, 0.7),
         "Penulis menyimpulkan tidak ada perbedaan prevalensi antar benua yang bermakna. "
         "Peringkat benua juga bergeser dibanding tinjauan sebelumnya (dulu Afrika terendah).",
         12.5, BODY, z=3, spacing=1.0,
         source_ref={"source_id": "S1", "locator": "Discussion"}),
    panel("crit", (X0, 4.25, CONTENT_W, 1.55)),
    text("crit_t", (X0 + 0.3, 4.44, CONTENT_W - 0.6, 1.2),
         "Faktor yang terbukti memengaruhi angka: kriteria diagnostik\n"
         "\u2022  Studi yang tidak memakai definisi kasus EAPD 2003 menghasilkan estimasi berbeda "
         "secara bermakna (p = 0,0061; sub-analisis 133.734 peserta) \u2014 umumnya lebih rendah.\n"
         "\u2022  Ukuran sampel dan tahun publikasi hanya penyumbang kecil heterogenitas.",
         12, INK, z=3, spacing=1.0,
         source_ref={"source_id": "S1", "locator": "Results, subgroup analyses"}))

# =============================================================== S12 — diskusi
s = new_slide("s12_diskusi", "Diskusi",
              "Heterogenitas berasal dari variasi wilayah, bukan dari definisi keparahan saja",
              ["kicker", "title", "p1", "p1t", "p2", "p2t", "p3", "p3t", "p4", "p4t"],
              source_locator="Discussion")
for i, (t, d) in enumerate([
    ("Sumber heterogenitas",
     "Analisis penulis: variasi antar wilayah lebih menjelaskan heterogenitas dibanding faktor "
     "metodologis yang diuji lewat meta-regresi."),
    ("Definisi kasus",
     "Pemakaian klasifikasi non-EAPD \u201cmenurunkan\u201d estimasi prevalensi \u2014 alasan kuat untuk "
     "menyeragamkan kriteria diagnostik."),
    ("Makna klinis keparahan",
     "36,3% kasus sedang\u2013berat berarti sekitar sepertiga anak dengan MIH memerlukan perawatan "
     "restoratif nyata, bukan sekadar pemantauan."),
    ("Keterbatasan data turunan",
     "Hanya sebagian studi melaporkan keparahan, gigi terkena, dan HSPM; penulis menyerukan "
     "pelaporan yang lebih lengkap pada studi epidemiologi berikutnya."),
]):
    x = X0 if i % 2 == 0 else X0 + 6.22
    y = 1.72 + (i // 2) * 2.15
    add(s,
        card(f"p{i+1}", (x, y, 5.91, 1.95)),
        text(f"p{i+1}t", (x + 0.24, y + 0.2, 5.43, 0.34), t.upper(), 11, TEAL, True, z=3),
        text(f"p{i+1}d", (x + 0.24, y + 0.58, 5.43, 1.25), d, 12, BODY, z=3, spacing=1.0,
             source_ref={"source_id": "S1", "locator": "Discussion/Conclusion"}))

# =============================================================== S13 — appraisal
s = new_slide("s13_appraisal", "Critical appraisal",
              "Kekuatan pada desain dan mutu studi; kelemahan pada heterogenitas dan representativitas",
              ["kicker", "title", "st", "str_t", "wt", "wk_t"],
              source_locator="Strengths and potential limitations")
add(s,
    card("st", (X0, 1.72, 5.91, 4.6), fill="#FFFFFF"),
    text("str_t", (X0 + 0.28, 1.9, 5.35, 4.25),
         "KEKUATAN\n"
         "\u2022  Dilaporkan mengikuti PRISMA dengan protokol yang terdaftar lebih dulu.\n"
         "\u2022  Pencarian tujuh basis data + rentang tahun luas.\n"
         "\u2022  Seleksi dan penilaian risiko bias oleh dua peneliti independen "
         "(\u03ba = 0,885) \u2014 mengurangi bias seleksi.\n"
         "\u2022  Semua studi pada analisis utama berkualitas tinggi (NOS \u2265 7/9).\n"
         "\u2022  Membandingkan definisi kasus EAPD vs alternatif sebelum analisis utama.\n"
         "\u2022  Uji Egger, cumulative, dan leave-one-out untuk menguji kestabilan estimasi.\n"
         "\u2022  Jumlah peserta besar dan kepastian bukti dinilai SORT A.",
         12, BODY, z=3, spacing=1.0),
    card("wt", (X0 + 6.22, 1.72, 5.91, 4.6), fill=AMBER_TINT, line_color="#FCD34D"),
    text("wk_t", (X0 + 6.5, 1.9, 5.35, 4.25),
         "KETERBATASAN\n"
         "\u2022  Heterogenitas sangat tinggi (I\u00b2 93\u201398%) \u2192 angka tunggal harus dibaca hati-hati.\n"
         "\u2022  Hampir separuh studi (48,7%) gagal memenuhi representativitas sampel.\n"
         "\u2022  Studi tanpa definisi EAPD 2003 dikeluarkan dari analisis utama \u2192 sebagian data "
         "hilang, dan masih ada 116 vs 98 studi yang tidak seluruhnya terpakai.\n"
         "\u2022  Data keparahan, gigi terkena, dan HSPM langka \u2192 estimasi sekunder kurang stabil "
         "(beberapa hanya dari 7 studi).\n"
         "\u2022  Faktor medis, sosiodemografis, dan lingkungan tidak dapat dianalisis karena "
         "pelaporan studi yang tidak seragam.\n"
         "\u2022  Tidak ada penilaian GRADE; kepastian bukti memakai SORT. Selain itu, angka "
         "insisivus berbeda antara abstrak (36,6%) dan Tabel 2 (38,7%).",
         12, BODY, z=3, spacing=1.0))

# =============================================================== S14 — implikasi
s = new_slide("s14_implikasi", "Implikasi klinis",
              "Protokol praktis: skrining usia 6\u20138 tahun, catat keparahan, tatalaksana minimal invasif",
              ["kicker", "title", "a1", "a1t", "a2", "a2t", "a3", "a3t", "a4", "a4t", "imp"],
              source_locator="Discussion; Conclusion")
for i, (t, d) in enumerate([
    ("1. Deteksi dini",
     "Periksa molar pertama permanen segera setelah erupsi (sekitar usia 6\u20138 tahun). Cari "
     "opasitas berbatas tegas; catat gigi yang terkena."),
    ("2. Dokumentasi terstandar",
     "Gunakan kriteria EAPD 2003 secara konsisten + foto klinis, agar data pasien kita dapat "
     "dibandingkan dengan literatur dan antar-klinisi."),
    ("3. Stratifikasi risiko",
     "Catat keparahan (sedang/berat) dan jumlah molar yang terkena \u2014 dua hal ini menentukan "
     "intensitas recall dan pilihan perawatan."),
    ("4. Tatalaksana & pencegahan",
     "Desensitisasi, sealant pada molar berisiko, restorasi/SSC bila enamel pecah; hindari "
     "preparasi agresif. Pencegahan karies lebih krusial pada enamel yang sudah lemah."),
]):
    x = X0 if i % 2 == 0 else X0 + 6.22
    y = 1.72 + (i // 2) * 1.75
    add(s,
        card(f"a{i+1}", (x, y, 5.91, 1.58)),
        text(f"a{i+1}t", (x + 0.24, y + 0.16, 5.43, 0.3), t.upper(), 11, TEAL, True, z=3),
        text(f"a{i+1}d", (x + 0.24, y + 0.5, 5.43, 0.94), d, 11.5, BODY, z=3, spacing=1.0))
add(s, panel("imp", (X0, 5.35, CONTENT_W, 0.95)),
    text("imp_t", (X0 + 0.3, 5.48, CONTENT_W - 0.6, 0.62),
         "Untuk program kesehatan gigi sekolah: prevalensi \u00b1 13\u201315% cukup tinggi untuk "
         "menjadikan pemeriksaan MIH bagian rutin skrining UKS, bukan temuan insidental.",
         12.5, INK, z=3, spacing=1.0,
         source_ref={"source_id": "S1", "locator": "Discussion, future directions"}))

# =============================================================== S15 — kesimpulan
s = new_slide("s15_kesimpulan", "Kesimpulan & rujukan",
              "MIH menyerang sekitar 1 dari 7\u20138 anak \u2014 siapkan skrining dan tatalaksananya",
              ["kicker", "title", "c1", "c2", "c3", "ref_t", "ref", "closing"],
              source_locator="Conclusion")
add(s,
    card("c1", (X0, 1.72, 3.87, 1.35)),
    text("c1t", (X0 + 0.22, 1.84, 3.43, 1.08),
         "13,5% (12,0\u201315,1)\nPrevalensi global MIH dari 113.089 peserta, SORT A.",
         12, BODY, z=3, spacing=1.0),
    card("c2", (X0 + 4.03, 1.72, 3.87, 1.35)),
    text("c2t", (X0 + 4.25, 1.84, 3.43, 1.08),
         "36,3% kasus sedang\u2013berat\nBeban perawatan nyata pada lebih dari sepertiga anak "
         "dengan MIH.",
         12, BODY, z=3, spacing=1.0),
    card("c3", (X0 + 8.06, 1.72, 4.07, 1.35)),
    text("c3t", (X0 + 8.28, 1.84, 3.63, 1.08),
         "\u00b136\u201339% disertai insisivus; HSPM 3,6%\nDampak estetik dan riwayat molar sulung "
         "perlu ditanyakan.",
         12, BODY, z=3, spacing=1.0))
add(s, text("ref_t", (X0, 3.3, CONTENT_W, 0.3), "Rujukan", 13, INK, True, z=3),
    text("ref", (X0, 3.66, CONTENT_W, 1.75),
         "1.  Lopes LB, Machado V, Mascarenhas P, Mendes JJ, Botelho J. The prevalence of "
         "molar-incisor hypomineralization: a systematic review and meta-analysis. Sci Rep. "
         "2021;11:22405. doi:10.1038/s41598-021-01541-7  \u2190 artikel utama\n"
         "2.  Weerheijm KL, dkk. Judgement criteria for molar incisor hypomineralisation (MIH) in "
         "epidemiologic studies (European meeting on MIH, Athens 2003). Eur J Paediatr Dent. "
         "2003;4:110\u2013113.\n"
         "3.  Schwendicke F, dkk. Global burden of molar incisor hypomineralization. J Dent. "
         "2018;68:10\u201318.\n"
         "4.  Zhao D, dkk. The prevalence of molar incisor hypomineralization: evidence from 70 "
         "studies. Int J Paediatr Dent. 2018;28:170\u2013179.",
         11.5, BODY, z=3, spacing=1.0),
    text("closing", (X0, 5.6, CONTENT_W, 0.7),
         "Take-home: MIH bukan kelainan langka. Dengan kriteria EAPD yang sama, data klinik kita "
         "dapat dibandingkan dengan literatur internasional \u2014 mulai dari pencatatan yang rapi.",
         13, TEAL_DEEP, bold=True, z=3, spacing=1.0))

# ------------------------------------------------------------------ speaker notes
NOTES = {
    "s01_cover": "Buka dengan satu kalimat: ini presentasi jurnal dari artikel meta-analisis "
                 "Lopes dkk. (Scientific Reports, 2021) tentang seberapa sering MIH terjadi pada "
                 "anak. Sebutkan identitas naskah dan bahwa artikelnya open access (CC BY 4.0). "
                 "Sumber: S1, halaman judul.",
    "s02_ringkasan": "Ringkas angka kunci 1 menit: 116 studi, 113.089 peserta, prevalensi 13,5% "
                     "(95% CI 12,0-15,1), kasus sedang-berat 36,3%, kepastian bukti SORT A. "
                     "Ingatkan bahwa ini bukan angka presisi untuk satu negara, melainkan besaran "
                     "beban global. Sumber: S1 Abstract dan Tabel 2.",
    "s03_mih": "Jelaskan definisi MIH dengan bahasa klinis: email berbercak putih-kuning-cokelat "
               "berbatas tegas, lebih lunak, mudah pecah setelah erupsi. Tunjukkan kenapa hal ini "
               "penting: hipersensitivitas, risiko karies, restorasi berulang, dampak estetik. "
               "Sumber: S1 Introduction.",
    "s04_gap": "Sampaikan masalahnya: rentang laporan 2,8%-40,2% membuat perencanaan sulit, dan "
               "dua SR sebelumnya (13,1% dan 14,2%) pencariannya berhenti pada 2017. Di sini kita "
               "bisa memancing diskusi: apakah rentang lebar itu karena definisi, atau karena "
               "perbedaan populasi? Sumber: S1 Introduction.",
    "s05_tujuan": "Bacakan pertanyaan PECO sekali saja, lalu fokus ke empat luaran. Poin yang "
                  "ingin saya tekankan: artikel ini tidak hanya menghitung prevalensi, tetapi juga "
                  "keparahan, jumlah molar terkena, dan HSPM. Sumber: S1 Methods bagian focused "
                  "question.",
    "s06_metode1": "Tunjukkan bahwa protokol terdaftar lebih dulu di PROSPERO (mengurangi risiko "
                   "cherry-picking). Sebutkan tujuh basis data dan batas pencarian Juli 2021. "
                   "Catatan jujur: penyebutan PubMed dan MEDLINE sebagai dua entri terpisah, serta "
                   "EMBASE yang hanya muncul di strategi, perlu ditelusuri bila kita ingin "
                   "mereplikasi pencariannya. Sumber: S1 Methods.",
    "s07_metode2": "Tiga hal yang membuat hasil ini layak dipercaya: kriteria ketat, seleksi "
                   "independen oleh dua peneliti (kappa 0,885), dan analisis random-effects. "
                   "Jelaskan singkat kenapa random-effects dipilih: karena populasi dan metode "
                   "antar studi sangat beragam. Sumber: S1 Methods.",
    "s08_hasil1": "Mulai dari alur seleksi. Tekankan bahwa 48 dari 116 studi mendapat skor NOS "
                  "maksimum 9/9, dan hanya satu studi berkualitas sedang. Ini menjawab pertanyaan "
                  "yang biasanya muncul lebih dulu di diskusi jurnal: seberapa bagus kualitas "
                  "studinya? Sumber: S1 Results dan Tabel 1.",
    "s09_hasil2": "Slide inti. Bacakan 13,5% dengan interval kepercayaan dan n-nya, lalu jelaskan "
                  "I-squared 98% dengan analogi sederhana: rata-rata ini menggambarkan beban "
                  "populasi, bukan angka presisi untuk satu kota atau satu sekolah. Sebutkan juga "
                  "uji Egger dan leave-one-out sebagai pemeriksaan kestabilan. Sumber: S1 Tabel 2.",
    "s10_hasil3": "Fokus pesan klinis: sepertiga lebih kasus tergolong sedang-berat, sehingga "
                  "banyak anak butuh perawatan nyata. Untuk distribusi molar, tunjukkan bahwa "
                  "polanya hampir merata (18-27%), artinya berat ringannya beban per anak sangat "
                  "bervariasi. Sebut singkat perbedaan angka insisivus antara abstrak (36,6%) dan "
                  "Tabel 2 (38,7%) sebagai contoh pentingnya cek tabel. Sumber: S1 Tabel 2.",
    "s11_subanalisis": "Jelaskan dua temuan: peringkat benua (Amerika 15,3%; Asia 10,7%) tidak "
                       "menghasilkan perbedaan bermakna, dan pemakaian klasifikasi non-EAPD 2003 "
                       "menghasilkan estimasi yang berbeda bermakna (p = 0,0061). Implikasinya: "
                       "standardisasi kriteria diagnostik bukan sekadar soal akademik, tetapi "
                       "memengaruhi angka yang kita laporkan. Sumber: S1 Results dan Discussion.",
    "s12_diskusi": "Empat kartu ini adalah penjelasan penulis. Tekankan bahwa heterogenitas lebih "
                   "menjelaskan variasi wilayah daripada faktor metodologis yang diuji, dan bahwa "
                   "data keparahan serta HSPM masih langka sehingga penulis menyerukan pelaporan "
                   "yang lebih lengkap. Sumber: S1 Discussion.",
    "s13_appraisal": "Ini bagian penilaian kritis - penting untuk diskusi jurnal. Sebut kekuatan "
                     "secara adil, lalu keterbatasan tanpa melemahkan artikelnya: heterogenitas "
                     "tinggi, representativitas sampel yang sering gagal, sebagian data dikeluarkan "
                     "dari analisis utama, dan tidak ada penilaian GRADE. Sebutkan juga dua "
                     "ketidakkonsistenan kecil yang saya temukan sendiri: angka insisivus berbeda "
                     "antara abstrak dan tabel, serta penyebutan basis data yang tidak seragam. "
                     "Sumber: S1 Strengths and limitations.",
    "s14_implikasi": "Tutup bagian klinis dengan empat langkah praktis. Paling penting dua hal: "
                     "periksa molar pertama permanen segera setelah erupsi (sekitar usia 6-8 "
                     "tahun), dan dokumentasikan keparahan dengan kriteria EAPD supaya data kita "
                     "bisa dibandingkan dengan literatur. Sumber: S1 Discussion dan Conclusion.",
    "s15_kesimpulan": "Ulangi tiga angka kunci, tunjukkan rujukan utama, lalu tutup dengan "
                      "take-home: MIH bukan kelainan langka, dan pencatatan yang rapi membuat data "
                      "klinik kita sebanding dengan literatur internasional. Siapkan dua pertanyaan "
                      "pemicu diskusi: (1) apakah prevalensi di Indonesia mungkin berbeda? "
                      "(2) bagaimana kriteria EAPD diterapkan di klinik kita sehari-hari?",
}
for slide in slides:
    slide["notes"] = NOTES.get(slide["id"], "")

# ----------------------------------------------------------------- output spec
spec = {
    "summary": {
        "deck_title": "Presentasi Jurnal \u2014 Prevalensi MIH (Lopes dkk., Sci Rep 2021)",
        "audience": "Mahasiswa/dokter gigi pada diskusi jurnal kedokteran gigi anak",
        "decision": "Memahami besaran beban MIH dan menetapkan langkah skrining serta tatalaksana",
        "language": "id-ID",
        "narrative_framework": "custom \u2014 struktur academic journal reading (IMRaD: latar belakang \u2192 "
                               "tujuan \u2192 metode \u2192 hasil \u2192 diskusi \u2192 implikasi \u2192 kesimpulan)",
        "slide_count": len(slides),
        "layout_policy": {"safe_margin": 0.55, "content_bottom": CONTENT_BOTTOM,
                          "footer_top": FOOTER_TOP, "minimum_gap": 0.12},
        "design_context": {
            "profile": "editorial-minimal",
            "adaptation": "palet akademik kedokteran: teal sebagai aksen tunggal, amber khusus kartu keterbatasan",
            "motif": "garis teal di bawah setiap judul + label kicker huruf kapital",
            "palette": {"page": PAGE, "surface": SURFACE, "tint": TINT, "ink": INK, "body": BODY,
                        "muted": MUTED, "accent": TEAL, "accent_deep": TEAL_DEEP,
                        "accent_edge": TEAL_EDGE, "warn": AMBER, "warn_tint": AMBER_TINT,
                        "line": LINE},
            "typography": {"font": FONT, "title_pt": 25, "section_pt": 13, "body_pt": 12,
                           "caption_pt": 10, "footer_pt": 9, "min_pt": 9},
            "spacing": {"margin_in": 0.55, "gutter_in": 0.16, "card_radius_in": 0.06},
            "signature_element": "hero metric card dengan angka teal besar pada slide hasil"
        },
        "accessibility": {"language": "id-ID",
                          "presentation_title": "Presentasi Jurnal \u2014 Prevalensi Molar-Incisor "
                                                "Hypomineralization (Lopes dkk. 2021)",
                          "reading_order": "per slide, atas\u2013bawah lalu kiri\u2013kanan (lihat tiap slide)",
                          "min_font_pt": 9},
        "sources": [
            {"source_id": "S1", "type": "artikel utama",
             "citation": "Lopes LB, Machado V, Mascarenhas P, Mendes JJ, Botelho J. Sci Rep. 2021;11:22405",
             "locator": "DOI 10.1038/s41598-021-01541-7; PMID 34789780; PMC8599453",
             "verified": "2026-10-13 via Europe PMC + Crossref", "license": "CC BY 4.0"},
            {"source_id": "S2", "type": "definisi kriteria (dikutip dalam S1)",
             "citation": "Weerheijm KL, dkk. Eur J Paediatr Dent. 2003;4:110\u2013113", "verified": "via S1"},
            {"source_id": "S3", "type": "pembanding (dikutip dalam S1)",
             "citation": "Schwendicke F, dkk. J Dent. 2018;68:10\u201318", "verified": "via S1"},
            {"source_id": "S4", "type": "pembanding (dikutip dalam S1)",
             "citation": "Zhao D, dkk. Int J Paediatr Dent. 2018;28:170\u2013179", "verified": "via S1"},
        ],
        "visual_assets": "tidak ada aset eksternal; seluruh visual (kartu, bar, tabel) dibuat sebagai "
                         "objek native PowerPoint",
    },
    "slides": slides,
}

(HERE / "spec.json").write_text(json.dumps(spec, indent=2, ensure_ascii=False) + "\n",
                                encoding="utf-8")
print(f"spec.json written: {len(slides)} slides, "
      f"{sum(len(s['layout_tree']['objects']) for s in slides)} objects")
