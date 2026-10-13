#!/usr/bin/env python3
"""Author spec.json for the MIH / Lopes 2021 journal deck (v2).

What changed from v1, and why
-----------------------------
* Copy rewritten with the repo skill `avoid-ai-writing` (rewrite mode, Indonesian
  academic register): clauses joined with punctuation instead of dashes, no
  significance inflation, no "bukan X melainkan Y" cadence, sentence length varied by
  hand, speaker notes rewritten as spoken cues instead of a uniform template.
* Visual system rebuilt (repo skill `visual-design-foundations` + the `editorial-minimal`
  profile in `pptx-deck-context`): dark ink surfaces for the cover, the hero metric and
  the closing strips; a three-step type scale with 10.5 pt tracked kickers; native
  PowerPoint charts (column, horizontal bar, doughnut) so the data carries the layout;
  an arch motif drawn from native shapes; consistent footer rail with page numbers.

Everything factual still comes from S1 (Lopes et al. 2021, CC BY 4.0); every content
object carries a `source_ref` locator. No external assets, no invented numbers.

Usage:  python3 author_spec.py
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

# --------------------------------------------------------------------------- tokens
T = {
    "ink": "#0B2E36",
    "ink_2": "#123F4A",
    "ink_3": "#1B5361",
    "paper": "#F6F8F9",
    "surface": "#FFFFFF",
    "tint": "#E9F5F6",
    "tint_2": "#D2E9EB",
    "accent": "#0E7490",
    "accent_deep": "#155E75",
    "accent_soft": "#7FDCE6",
    "accent_mid": "#8FC6CE",
    "amber": "#B45309",
    "amber_tint": "#FCF6EA",
    "amber_edge": "#EBD8B4",
    "heading": "#0F172A",
    "body": "#3C4A55",
    "muted": "#6B7B87",
    "hairline": "#DCE3E8",
    "track": "#E4EBEE",
    "chip": "#EFF4F6",
    "white": "#FFFFFF",
    "on_ink_body": "#BCD0D5",
    "on_ink_muted": "#8AA6AC",
}
FONT = "Calibri"
MONO = "Consolas"
SLIDE_W, SLIDE_H = 13.333, 7.5
SAFE = 0.6
RIGHT = 12.73  # right edge of the content column
W2 = 5.9       # half column
W3 = 3.856     # third column
W4 = 2.845     # quarter column
FOOTER = "Lopes dkk., Sci Rep 2021;11:22405 · DOI 10.1038/s41598-021-01541-7 · CC BY 4.0"


class Slide:
    """Coordinate-explicit slide builder. Every object gets an id, a role, a bbox."""

    def __init__(self, sid: str, kicker: str, title: str, notes: str = "") -> None:
        self.sid, self.kicker, self.title, self.notes = sid, kicker, title, notes
        self.objs: dict[str, dict] = {}
        self.order: list[str] = []
        self.z = 0

    def _put(self, oid, kind, role, x, y, w, h, content, style, classification="content",
             src="", alt="", reading=True):
        if oid in self.objs:
            raise SystemExit(f"duplicate object id {oid} on {self.sid}")
        if w <= 0 or h <= 0:
            raise SystemExit(f"non-positive geometry on {oid} ({w}x{h})")
        self.z += 1
        self.objs[oid] = {
            "id": oid, "kind": kind, "role": role, "classification": classification,
            "content": content, "style": style,
            "bbox": {"x": round(x, 3), "y": round(y, 3), "width": round(w, 3), "height": round(h, 3)},
            "z_index": self.z, "source_ref": src, "alt_text": alt,
        }
        if reading:
            self.order.append(oid)

    # -- primitives --------------------------------------------------------------
    def shape(self, oid, x, y, w, h, *, fill, line="none", line_width=0.0, radius=0.06,
              kind="rounded_rectangle", role="decoration", classification="layout_design",
              alpha=100, reading=False):
        style = {"fill": fill, "line_color": fill if line == "none" else line,
                 "line_width": line_width, "radius": radius, "shadow": False, "alpha": alpha}
        self._put(oid, "shape", role, x, y, w, h, {"shape": kind}, style,
                  classification=classification, reading=reading)

    def rule(self, oid, x, y, w, color, *, h=0.022):
        self.shape(oid, x, y, w, h, fill=color, radius=0.011)

    def txt(self, oid, x, y, w, h, text, *, size=12, color=None, bold=False, italic=False,
            align="left", anchor="top", line_spacing=None, space_after=0, spc=0,
            font=FONT, src="", role="body", classification="content", reading=True):
        style = {"font": font, "font_size": size, "color": color or T["body"], "bold": bold,
                 "italic": italic, "align": align, "anchor": anchor,
                 "inset_left": 0.02, "inset_right": 0.02, "inset_top": 0.0, "inset_bottom": 0.0}
        if line_spacing:
            style["line_spacing"] = line_spacing
        if space_after:
            style["space_after_pt"] = space_after
        if spc:
            style["spc"] = spc
        self._put(oid, "text", role, x, y, w, h, {"text": text}, style,
                  classification=classification, src=src, reading=reading)

    def card(self, oid, x, y, w, h, *, fill=None, line=None, radius=0.09, src=""):
        self.shape(oid, x, y, w, h, fill=fill or T["surface"], line=line or T["hairline"],
                   line_width=0.75, radius=radius, kind="rounded_rectangle",
                   role="card", classification="content", reading=False)
        self.objs[oid]["source_ref"] = src

    def head(self, oid, x, y, w, text, *, size=12, color=None, src="", spc=0):
        self.txt(oid, x, y, w, 0.28, text, size=size, bold=True, color=color or T["accent"],
                 spc=spc, role="panel_text", src=src)

    def bullets(self, oid, x, y, w, h, items, *, size=11, color=None, src="", marker="•  "):
        body = "\n".join(f"{marker}{item}" for item in items)
        self.txt(oid, x, y, w, h, body, size=size, color=color or T["body"],
                 line_spacing=0.96, space_after=5, src=src)

    def chart(self, oid, x, y, w, h, chart_type, categories, values, *, colors=None,
              gap_width=None, data_labels=False, label_format='0.0"%"', font_size=10.5,
              axis_labels=True, show_value_axis=True, src=""):
        content = {"chart_type": chart_type, "categories": categories, "values": values,
                   "series_name": "nilai", "colors": colors or [T["accent"]],
                   "data_labels": data_labels, "label_format": label_format,
                   "font_size": font_size, "gap_width": gap_width,
                   "axis_labels": axis_labels, "show_value_axis": show_value_axis}
        style = {"font": FONT, "font_size": font_size, "color": T["body"]}
        self._put(oid, "chart", "chart", x, y, w, h, content, style, src=src)

    def bar_row(self, tag, x, y, w, label, value, fraction, cap_width, source=""):
        """Proportional bar row: caption, value, track and filled portain."""
        self.txt(f"{tag}_lab", x, y, w - 1.62, 0.26, label, size=11, color=T["body"],
                 src=source)
        self.txt(f"{tag}_val", x + w - 1.34, y - 0.02, 1.34, 0.3, value, size=13, bold=True,
                 color=T["accent_deep"], align="right", src=source)
        self.shape(f"{tag}_track", x, y + 0.34, cap_width, 0.22, fill=T["track"], radius=0.11,
                   role="bar", classification="content")
        self.shape(f"{tag}_fill", x, y + 0.34, max(0.12, cap_width * fraction), 0.22,
                   fill=T["accent"], radius=0.11, role="bar", classification="content")

    def tile(self, tag, x, y, w, h, value, label, note, *, value_size=34, src="", value_color=None):
        self.card(f"{tag}_card", x, y, w, h, src=src)
        self.txt(f"{tag}_v", x + 0.18, y + 0.14, w - 0.36, 0.60, value, size=value_size,
                 bold=True, color=value_color or T["accent_deep"], src=src, role="metric")
        self.txt(f"{tag}_l", x + 0.18, y + 0.76, w - 0.36, 0.26, label, size=11.5, bold=True,
                 color=T["heading"], src=src, role="panel_text")
        self.txt(f"{tag}_n", x + 0.18, y + 1.04, w - 0.36, h - 1.22, note, size=10,
                 color=T["muted"], line_spacing=1.0, src=src)

    def footer_rail(self, page: int):
        self.rule("rail", SAFE, 6.78, RIGHT - SAFE, T["hairline"], h=0.014)
        self.txt("footer", SAFE, 6.88, 9.6, 0.3, FOOTER, size=9, color=T["muted"],
                 role="footer", reading=False)
        self.txt("page", 11.1, 6.86, RIGHT - 11.1, 0.32, f"{page:02d}", size=10.5, bold=True,
                 color=T["accent"], align="right", role="footer", reading=False)

    def header(self, page: int):
        self.shape("accent_bar", SAFE, 0.45, 0.055, 0.32, fill=T["accent"], radius=0.02)
        self.txt("kicker", SAFE + 0.18, 0.43, 6.6, 0.3, self.kicker, size=10.5, bold=True,
                 color=T["accent"], spc=130, role="kicker")
        self.txt("title", SAFE, 0.80, RIGHT - SAFE, 0.62, self.title, size=24, bold=True,
                 color=T["heading"], role="title", line_spacing=0.98)
        self.rule("rule_teal", SAFE, 1.52, 1.30, T["accent"], h=0.026)
        self.rule("rule_hair", SAFE + 1.40, 1.525, RIGHT - SAFE - 1.40, T["hairline"], h=0.014)
        self.footer_rail(page)

    def emit(self):
        return {
            "id": self.sid, "title": self.title, "kicker": self.kicker,
            "notes": self.notes,
            "layout_tree": {
                "slide_size": {"width": SLIDE_W, "height": SLIDE_H},
                "objects": self.objs,
            },
            "accessibility": {
                "title": self.title,
                "reading_order": self.order,
                "language": "id-ID",
            },
        }


def background_and_frame(s: Slide, page_light=True):
    s.shape("bg", 0, 0, SLIDE_W, SLIDE_H, fill=T["paper"] if page_light else T["ink"],
            radius=0.0, kind="rectangle")


def arch_motif(s: Slide, cx: float, cy: float, radius: float, count: int = 13,
               tint: str = "soft", prefix: str = "ring"):
    """Arch motif: an arrangement of dots along a semicircle, drawn from native shapes.

    Reads as a stylised tooth arch and stays decorative (layout_design, out of the
    reading order and out of collision checks).
    """
    import math

    color = T["accent_soft"] if tint == "soft" else T["accent_mid"]
    for i in range(count):
        angle = math.radians(180 + 180 * i / (count - 1))
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle) * 0.72
        size = 0.30
        s.shape(f"{prefix}_{i:02d}", x - size / 2, y - size / 2, size, size, fill=color,
                radius=0.10, alpha=34 if i % 2 == 0 else 60)
    for ring, alpha in ((1.0, 26), (0.72, 16), (0.46, 26)):
        s.shape(f"{prefix}_arc_{int(ring*100)}", cx - radius * ring, cy - radius * ring * 0.72,
                radius * ring * 2, radius * ring * 1.44, fill=T["ink"], line=T["accent_soft"],
                line_width=1.0, radius=0.5, kind="oval", alpha=alpha)


# ======================================================================= slide list
slides: list[Slide] = []

# ------------------------------------------------------------------------ 01 cover
s = Slide("s01_cover", "DISKUSI JURNAL · KEDOKTERAN GIGI ANAK",
          "Prevalensi Molar-Incisor Hypomineralization pada Anak dan Remaja",
          notes="Buka dengan satu kalimat saja: ini meta-analisis tentang seberapa sering MIH "
                "muncul pada anak, terbit di Scientific Reports 2021 dan aksesnya terbuka. "
                "Sebutkan bahwa angka besarnya 13,5% akan dibahas di slide 9. Karena ini "
                "diskusi jurnal, tawarkan sejak awal bahwa peserta boleh menyela untuk "
                "bertanya.")
s.shape("bg", 0, 0, SLIDE_W, SLIDE_H, fill=T["ink"], radius=0.0, kind="rectangle")
arch_motif(s, 10.45, 3.62, 3.35)
s.shape("accent_bar", 0.9, 0.88, 0.055, 0.34, fill=T["accent_soft"], radius=0.02)
s.txt("kicker", 1.08, 0.86, 7.0, 0.32, "DISKUSI JURNAL · KEDOKTERAN GIGI ANAK", size=10.5,
      bold=True, color=T["accent_soft"], spc=150, role="kicker")
s.txt("title", 0.9, 1.34, 7.3, 1.62, "Prevalensi Molar-Incisor Hypomineralization pada Anak "
      "dan Remaja", size=36, bold=True, color=T["white"], role="title", line_spacing=0.95)
s.txt("subtitle", 0.9, 3.02, 7.3, 0.36, "Tinjauan sistematis dan meta-analisis 116 studi",
      size=14, color=T["accent_mid"], src="S1, judul")
s.txt("orig", 0.9, 3.44, 7.3, 0.56, "The prevalence of molar-incisor hypomineralization: "
      "a systematic review and meta-analysis", size=11, italic=True, color=T["on_ink_muted"],
      src="S1, judul", line_spacing=1.05)
s.txt("meta", 0.9, 4.22, 7.3, 1.35,
      "Lopes LB, Machado V, Mascarenhas P, Mendes JJ, Botelho J · Egas Moniz, Portugal\n"
      "Scientific Reports 2021;11:22405 · akses terbuka CC BY 4.0\n"
      "DOI 10.1038/s41598-021-01541-7 · PMID 34789780 · PMC8599453\n"
      "PROSPERO CRD42021229435 · systematic review dan meta-analisis",
      size=10.5, color=T["on_ink_body"], role="meta", src="S1, halaman judul", line_spacing=1.22,
      space_after=2)
s.txt("hero_v", 8.30, 2.30, 4.40, 1.45, "13,5%", size=60, bold=True, color=T["white"],
      align="center", role="metric", src="S1, Tabel 2")
s.txt("hero_l", 8.30, 3.80, 4.40, 0.62, "prevalensi global MIH\n95% CI 12,0–15,1", size=12,
      color=T["on_ink_body"], align="center", role="callout", src="S1, Tabel 2",
      line_spacing=1.15)
s.card("hero_chip", 9.35, 4.52, 2.55, 0.52, fill=T["ink_2"], line=T["ink_3"], radius=0.26)
s.txt("hero_chip_t", 9.49, 4.65, 2.27, 0.24, "n = 113.089 anak dan remaja", size=10.5,
      color=T["accent_mid"], align="center", src="S1, Tabel 2")
s.rule("rail", 0.9, 6.52, RIGHT - 0.9, T["ink_3"], h=0.014)
s.txt("presenter", 0.9, 6.68, 11.6, 0.34,
      "Pemateri: ____________________     Tanggal: ____________________     "
      "Program Studi Kedokteran Gigi", size=11, color=T["on_ink_muted"], role="footer",
      reading=False)
slides.append(s)

# --------------------------------------------------------------------- 02 ringkasan
s = Slide("s02_ringkasan", "RINGKASAN", "Inti artikel dalam satu slide",
          notes="Enam kartu ini bisa dibaca dalam satu menit. Kalau waktu terbatas, cukup tiga "
                "angka di baris atas: 116 studi, 113.089 peserta, dan 13,5%. Sebutkan juga "
                "sejak awal bahwa kepastian buktinya SORT A, karena itu akan jadi bahan "
                "perdebatan di bagian penilaian kritis nanti.")
background_and_frame(s)
s.header(2)
s.tile("t1", SAFE, 1.72, W3, 1.50, "13,5%", "Prevalensi global MIH",
       "95% CI 12,0–15,1 · dari 98 studi berkriteria EAPD 2003", src="S1, Tabel 2")
s.tile("t2", 4.736, 1.72, W3, 1.50, "116", "Studi observasional",
       "133.734 peserta pada analisis awal, semua klasifikasi", src="S1, Results")
s.tile("t3", 8.872, 1.72, W3, 1.50, "113.089", "Peserta analisis utama",
       "SORT A untuk kepastian bukti; 48 studi berskor NOS 9/9", src="S1, Tabel 2")
cards = [
    ("c1", "Desain", "Systematic review dan meta-analisis, laporan mengikuti PRISMA, "
                     "protokol terdaftar di PROSPERO."),
    ("c2", "Kriteria utama", "Analisis utama memakai definisi kasus EAPD 2003, "
                             "sehingga 98 studi yang dihitung."),
    ("c3", "Heterogenitas", "I² = 98,0%. Angka global dibaca sebagai beban populasi, "
                            "bukan angka presisi satu negara."),
    ("c4", "Keparahan", "36,3% kasus tergolong sedang sampai berat (95% CI 29,9–43,2)."),
    ("c5", "Gigi terkena", "Insisivus terlibat pada 36–39% kasus; HSPM menyertai 3,6% kasus."),
    ("c6", "Sumber", "Sci Rep 2021;11:22405, akses terbuka CC BY 4.0.")
    ]
for i, (tag, head, body) in enumerate(cards):
    x = SAFE + (i % 3) * (W3 + 0.28)
    y = 3.46 + (i // 3) * 1.18
    s.card(f"{tag}_card", x, y, W3, 1.05)
    s.head(f"{tag}_h", x + 0.17, y + 0.15, W3 - 0.34, head, size=11.5, color=T["heading"])
    s.txt(f"{tag}_b", x + 0.17, y + 0.46, W3 - 0.34, 0.44, body, size=10.5, line_spacing=1.0)
s.card("take_card", SAFE, 5.80, RIGHT - SAFE, 0.70, fill=T["tint"], line=T["tint_2"])
s.shape("take_tick", SAFE, 5.80, 0.06, 0.70, fill=T["accent"], radius=0.03)
s.txt("take_t", SAFE + 0.26, 5.93, RIGHT - SAFE - 0.5, 0.44,
      "Kesimpulan penulis: prevalensi 13,5%, kasus sedang sampai berat 36,3%, insisivus "
      "terlibat pada 36–39% kasus, dan HSPM 3,6%. Seluruh kesimpulan diberi peringkat SORT A.",
      size=11.5, color=T["heading"], anchor="middle", role="takeaway", src="S1, Abstract")
slides.append(s)

# ---------------------------------------------------------------- 03 apa itu MIH
s = Slide("s03_mih", "LATAR BELAKANG · 1", "Apa itu MIH",
          notes="Mulai dari pengalaman klinis peserta: pernah melihat molar muda dengan bercak "
                "putih yang emailnya mudah terkelupas? Dari situ masuk ke definisi MIH. Tiga "
                "tahap di kanan bawah menjelaskan kenapa ini bukan persoalan estetika saja: "
                "emailnya memang tidak matang, jadi rapuh sejak awal.")
background_and_frame(s)
s.header(3)
left = [
    ("a", "Definisi", "Defek kualitatif email, disebut hipomineralisasi, pada satu molar pertama "
                      "permanen atau lebih dan kadang disertai insisivus. Penyebabnya belum "
                      "diketahui. Istilah ini dipakai EAPD sejak 2003."),
    ("b", "Yang terlihat di kursi gigi", "Opasitas putih, kuning, sampai cokelat dengan batas "
                                         "yang tegas. Emailnya lebih lunak, sehingga mudah pecah "
                                         "setelah gigi erupsi."),
    ("c", "Yang dialami anak", "Gigi sensitif, karies lebih mudah terjadi, restorasi sering "
                               "berulang, dan penampilan gigi depan menambah beban psikologis."),
]
for i, (tag, head, body) in enumerate(left):
    y = 1.72 + i * 1.63
    s.card(f"{tag}_card", SAFE, y, W2, 1.48)
    s.head(f"{tag}_h", SAFE + 0.18, y + 0.15, W2 - 0.36, head, size=12)
    s.txt(f"{tag}_b", SAFE + 0.18, y + 0.50, W2 - 0.36, 0.82, body, size=11, line_spacing=1.05,
          src="S1, Introduction")
s.card("why_card", 6.83, 1.72, W2, 2.35, fill=T["tint"], line=T["tint_2"])
s.head("why_h", 7.01, 1.88, W2 - 0.36, "Kenapa angkanya diperdebatkan", size=12)
s.txt("why_b", 7.01, 2.22, W2 - 0.36, 1.70,
      "Angka prevalensi menentukan besar beban penyakit, dan dari situ disusun perencanaan "
      "skrining, kebutuhan tenaga, serta edukasi orang tua.\n"
      "Laporan yang ada tersebar dari 2,8% sampai 40,2%, sehingga perencanaan kehilangan "
      "pijakan.", size=11, line_spacing=1.06, space_after=6, src="S1, Introduction")
s.txt("steps_lab", 6.83, 4.24, W2, 0.28, "Tiga tahap kerusakan email", size=11, bold=True,
      color=T["heading"])
steps = [("s1", "Email gagal matang"), ("s2", "Enamel lunak"), ("s3", "Pecah setelah erupsi")]
for i, (tag, label) in enumerate(steps):
    x = 6.83 + i * 2.02
    s.card(f"{tag}_card", x, 4.58, 1.80, 1.10, fill=T["surface"])
    s.txt(f"{tag}_t", x + 0.15, 4.72, 1.50, 0.82, label, size=11.5, bold=True,
          color=T["heading"], align="center", anchor="middle", src="S1, Introduction")
for i, tag in enumerate(("ar1", "ar2")):
    x = 8.66 + i * 2.02
    s.shape(tag, x, 4.98, 0.18, 0.26, fill=T["accent_mid"], kind="right_arrow", radius=0.0)
s.txt("steps_note", 6.83, 5.82, W2, 0.62, "Pecahnya email terjadi setelah gigi muncul, jadi "
      "kerusakan sering belum terlihat saat anak masih kecil.", size=10.5, italic=True,
      color=T["muted"], src="S1, Introduction")
slides.append(s)

# ------------------------------------------------------------- 04 sebaran angka
s = Slide("s04_gap", "LATAR BELAKANG · 2", "Angka laporan yang tersebar luas",
          notes="Slide ini menjelaskan kenapa artikel ini diperlukan. Tunjuk garis rentangnya: "
                "terendah 2,8%, tertinggi 40,2%. Lalu tanyakan: kalau dua studi memberi angka "
                "sejauh itu, angka mana yang dipakai untuk menyusun program? Di situ celahnya, "
                "kriteria diagnostik belum seragam.")
background_and_frame(s)
s.header(4)
s.card("range_card", SAFE, 1.72, RIGHT - SAFE, 2.42)
s.head("range_h", SAFE + 0.22, 1.88, 8.0, "Rentang prevalensi yang dilaporkan studi",
       size=11.5, src="S1, Introduction")
s.txt("anno_prev", 2.40, 2.78, 3.0, 0.28, "SR 2018 · 13,1% dan 14,2%", size=10, bold=True,
      color=T["muted"], src="S3, S4")
s.rule("anno_bracket", 4.52, 3.10, 0.30, T["muted"], h=0.02)
s.shape("track", 1.20, 3.52, 10.60, 0.12, fill=T["track"], radius=0.06, role="bar",
        classification="content")
s.shape("range_fill", 1.91, 3.52, 9.44, 0.12, fill=T["accent_mid"], radius=0.06, role="bar",
        classification="content")
for tag, pos, label, align in (("m_lo", 1.83, "2,8%", "left"), ("m_hi", 11.28, "40,2%", "right")):
    s.shape(f"{tag}_dot", pos, 3.49, 0.18, 0.18, fill=T["accent"], radius=0.09, kind="oval",
            role="bar", classification="content")
    s.txt(f"{tag}_lab", pos - (0.06 if align == "left" else 1.14), 3.72, 1.20, 0.28, label,
          size=12, bold=True, color=T["accent_deep"], align=align, src="S1, Introduction")
s.shape("m_mid_dot", 4.53, 3.47, 0.22, 0.22, fill=T["accent_deep"], radius=0.11, kind="oval",
        role="bar", classification="content")
s.txt("anno_this", 3.60, 3.72, 2.4, 0.28, "Artikel ini · 13,5%", size=10, bold=True,
      color=T["accent_deep"], src="S1, Tabel 2")
s.txt("scale", 11.40, 3.32, 1.18, 0.26, "skala 0–42%", size=9, color=T["muted"], align="right")
gaps = [
    ("g1", "Akar masalahnya", "Kriteria diagnostik belum seragam. Selisih angka antar studi "
                              "tidak selalu mencerminkan perbedaan penyakit yang sebenarnya."),
    ("g2", "Bukti sebelumnya", "Dua tinjauan tahun 2018 melaporkan 13,1% dan 14,2%, dengan "
                               "pencarian yang berhenti pada pertengahan 2017."),
    ("g3", "Yang belum terjawab", "Keparahan kasus, jumlah gigi yang terkena, dan HSPM "
                                  "jarang dilaporkan."),
]
for i, (tag, head, body) in enumerate(gaps):
    x = SAFE + i * (W3 + 0.28)
    s.card(f"{tag}_card", x, 4.38, W3, 2.12)
    s.head(f"{tag}_h", x + 0.18, 4.54, W3 - 0.36, head, size=12, color=T["heading"])
    s.txt(f"{tag}_b", x + 0.18, 4.92, W3 - 0.36, 1.40, body, size=11, line_spacing=1.06,
          src="S1, Introduction")
slides.append(s)

# ------------------------------------------------------------------- 05 tujuan
s = Slide("s05_tujuan", "TUJUAN", "Pertanyaan penelitian dan empat luaran",
          notes="Bacakan pertanyaan PECO satu kali saja, peserta sudah paham istilahnya. Yang "
                "layak ditekankan adalah empat luaran di bawah: artikel ini tidak berhenti pada "
                "prevalensi, tetapi juga mengukur keparahan, jumlah gigi yang terkena, dan "
                "HSPM. Luaran sekunder inilah yang biasanya tidak disediakan tinjauan lain.")
background_and_frame(s)
s.header(5)
s.card("q_card", SAFE, 1.72, RIGHT - SAFE, 0.76, fill=T["ink"], line=T["ink_2"])
s.txt("q_t", SAFE + 0.26, 1.86, RIGHT - SAFE - 0.5, 0.48,
      "Berapa prevalensi MIH global pada anak dan remaja?", size=15, bold=True,
      color=T["white"], anchor="middle", role="callout", src="S1, Methods")
peco = [
    ("p", "P", "Populasi", "studi klinis dan epidemiologis pada manusia"),
    ("e", "E", "Paparan", "diagnosis MIH ditegakkan"),
    ("c", "C", "Pembanding", "anak tanpa MIH"),
    ("o", "O", "Luaran", "prevalensi MIH"),
]
for i, (tag, letter, label, desc) in enumerate(peco):
    x = SAFE + i * (W4 + 0.25)
    s.card(f"{tag}_card", x, 2.66, W4, 1.12)
    s.txt(f"{tag}_l", x + 0.16, 2.80, 0.55, 0.5, letter, size=22, bold=True, color=T["accent"],
          role="metric")
    s.txt(f"{tag}_t", x + 0.74, 2.80, W4 - 0.9, 0.84, f"{label}\n{desc}", size=10.5,
          color=T["body"], line_spacing=1.05)
s.card("out_card", SAFE, 3.98, RIGHT - SAFE, 2.52)
s.head("out_h", SAFE + 0.22, 4.10, 6.0, "Luaran yang diukur", size=12, src="S1, Methods")
rows = [
    ("PRIMER", "Prevalensi global MIH", "diperkirakan dari seluruh studi yang memenuhi kriteria"),
    ("SEKUNDER 1", "Prevalensi kasus MIH sedang sampai berat", "dengan ambang keparahan yang dilaporkan penulis"),
    ("SEKUNDER 2", "Jumlah molar pertama permanen yang terkena", "dihitung untuk 1 sampai 4 gigi"),
    ("SEKUNDER 3 & 4", "Kasus dengan insisivus terkena dan prevalensi HSPM", "molar kedua sulung yang juga hipomineralisasi"),
]
for i, (tier, label, desc) in enumerate(rows):
    y = 4.42 + i * 0.48
    s.shape(f"r{i}_chip", SAFE + 0.22, y + 0.03, 0.30, 0.30, fill=T["accent"] if i == 0 else T["tint_2"],
            radius=0.15, role="chip", classification="content")
    s.txt(f"r{i}_n", SAFE + 0.24, y + 0.06, 0.26, 0.26, str(i + 1), size=11, bold=True,
          color=T["white"] if i == 0 else T["accent_deep"], align="center")
    s.txt(f"r{i}_t", SAFE + 0.66, y - 0.02, 2.2, 0.42, tier, size=9, bold=True, color=T["muted"],
          anchor="middle", spc=60)
    s.txt(f"r{i}_l", SAFE + 2.90, y - 0.02, 4.2, 0.42, label, size=11.5, bold=True,
          color=T["heading"], anchor="middle")
    s.txt(f"r{i}_d", SAFE + 7.20, y - 0.02, 4.72, 0.42, desc, size=10.5, color=T["muted"],
          anchor="middle")
slides.append(s)

# ------------------------------------------------------------------- 06 metode 1
s = Slide("s06_metode1", "METODE · 1", "Cara penulis mencari bukti",
          notes="Tiga hal yang perlu ditunjuk: protokol didaftarkan sebelum pencarian dimulai, "
                "tujuh basis data, dan pencarian berhenti pada Juli 2021. Catatan kuning adalah "
                "temuan saya sendiri saat membaca: PubMed dan MEDLINE disebut terpisah, dan "
                "EMBASE hanya muncul di strategi. Untuk keperluan replikasi, cek lampiran "
                "artikelnya.")
background_and_frame(s)
s.header(6)
s.card("d_card", SAFE, 1.72, W2, 1.52)
s.head("d_h", SAFE + 0.18, 1.87, W2 - 0.36, "Desain dan registrasi", size=12)
s.txt("d_b", SAFE + 0.18, 2.22, W2 - 0.36, 0.86,
      "Systematic review dan meta-analisis, dilaporkan mengikuti pedoman PRISMA. Protokolnya "
      "didaftarkan lebih dulu di PROSPERO, nomor CRD42021229435.", size=11, line_spacing=1.06,
      src="S1, Methods")
s.card("note_card", SAFE, 3.40, W2, 3.10, fill=T["amber_tint"], line=T["amber_edge"])
s.head("note_h", SAFE + 0.18, 3.56, W2 - 0.36, "Catatan pembacaan", size=12, color=T["amber"])
s.txt("note_b", SAFE + 0.18, 3.92, W2 - 0.36, 2.36,
      "PubMed dan MEDLINE disebut sebagai dua entri terpisah, sedangkan EMBASE hanya muncul "
      "pada bagian strategi pencarian.\n"
      "Keduanya lazim dalam praktik systematic review, tetapi angka tujuh basis data sebaiknya "
      "tidak dikutip tanpa catatan ini. Untuk replikasi, periksa lampiran artikel.",
      size=11, line_spacing=1.06, space_after=6, src="S1, Methods")
s.card("db_card", SAFE + W2 + 0.33, 1.72, W2, 2.78)
dbx = SAFE + W2 + 0.51
s.head("db_h", dbx, 1.87, W2 - 0.36, "Basis data dan tanggal", size=12)
chips = ["PubMed", "MEDLINE", "CENTRAL", "Web of Science", "SciELO", "LILACS", "TRIP",
         "EMBASE (strategi)"]
for i, label in enumerate(chips):
    x = dbx + (i % 2) * 2.55
    y = 2.20 + (i // 2) * 0.48
    s.card(f"db{i}", x, y, 2.38, 0.46, fill=T["chip"], line=T["track"], radius=0.23)
    s.txt(f"db{i}_t", x + 0.15, y + 0.13, 2.08, 0.18, label, size=10, color=T["body"],
          align="center")
s.txt("db_date", dbx, 4.14, W2 - 0.36, 0.20, "Pencarian sampai Juli 2021", size=10.5, bold=True,
      color=T["accent_deep"], src="S1, Methods")
s.card("qry_card", SAFE + W2 + 0.33, 4.72, W2, 1.78)
s.head("qry_h", dbx, 4.86, W2 - 0.36, "Algoritma pencarian", size=12)
s.txt("qry_b", dbx, 5.22, W2 - 0.36, 1.12,
      "(hypomineralization OR hypomineralisation OR hypomineralized OR hypoplasia OR "
      "demarcated OR opacities OR MIH OR cheese molars) AND (survey OR cross-sectional OR "
      "prevalence) AND (molar OR molars OR incisors)", size=9.5, font=MONO, color=T["body"],
      line_spacing=1.05, src="S1, Methods")
slides.append(s)

# ------------------------------------------------------------------- 07 metode 2
s = Slide("s07_metode2", "METODE · 2", "Cara penulis menyaring dan menimbang bukti",
          notes="Yang membuat hasil ini layak dipercaya ada dua: penyaringan oleh dua peneliti "
                "independen dengan kesepakatan hampir sempurna, kappa 0,885, dan model "
                "random-effects yang memang diperlukan karena populasi antar studi beragam. "
                "Kalau ada pertanyaan soal mutu studi, jawabannya ada di slide berikutnya.")
background_and_frame(s)
s.header(7)
quad = [
    ("i1", "Kriteria inklusi", [
        "Studi observasional yang melaporkan prevalensi MIH",
        "Definisi MIH dijelaskan dengan jelas",
        "Subjek tanpa kelainan sistemik",
        "Kedua jenis kelamin diikutsertakan"]),
    ("i2", "Kriteria eksklusi", [
        "Populasi khusus, misalnya anak yang lahir prematur",
        "Studi yang hanya melaporkan molar sulung",
        "Sampel non-representatif, misalnya pasien satu institusi atau kelompok dengan karies "
        "tinggi"]),
    ("i3", "Seleksi dan risiko bias", [
        "Penyaringan oleh dua peneliti independen",
        "Kesepakatan antar-penilai κ = 0,885",
        "Mutu dinilai dengan Newcastle–Ottawa Scale"]),
    ("i4", "Analisis", [
        "Model random-effects untuk prevalensi",
        "Heterogenitas diuji dengan I², bias publikasi dengan uji Egger",
        "Kepastian bukti dinilai memakai SORT"]),
]
for i, (tag, head, items) in enumerate(quad):
    x = SAFE + (i % 2) * (W2 + 0.33)
    y = 1.72 + (i // 2) * 2.42
    s.card(f"{tag}_card", x, y, W2, 2.24)
    s.head(f"{tag}_h", x + 0.18, y + 0.15, W2 - 0.36, head, size=12)
    s.bullets(f"{tag}_b", x + 0.18, y + 0.52, W2 - 0.36, 1.58, items, size=11,
              src="S1, Methods")
slides.append(s)

# -------------------------------------------------------------------- 08 hasil 1
s = Slide("s08_hasil1", "HASIL · 1", "116 studi lolos seleksi, dan mutunya tinggi",
          notes="Mulai dari tiga angka di atas: 116 studi, 133.734 peserta, dan 113.089 peserta "
                "yang akhirnya dianalisis. Grafik batang menunjukkan mutunya: 48 studi dengan "
                "skor maksimum dan hanya satu studi berkualitas sedang. Sebutkan angka 48,7% di "
                "kartu kanan, karena angka itu akan muncul lagi di slide keterbatasan.")
background_and_frame(s)
s.header(8)
s.tile("k1", SAFE, 1.72, W3, 1.42, "116", "Studi dimasukkan",
       "studi observasional memenuhi kriteria", src="S1, Results")
s.tile("k2", 4.736, 1.72, W3, 1.42, "133.734", "Peserta analisis awal",
       "semua jenis klasifikasi diagnostik", src="S1, Results")
s.tile("k3", 8.872, 1.72, W3, 1.42, "113.089", "Peserta analisis utama",
       "dari 98 studi berkriteria EAPD 2003", src="S1, Tabel 2")
s.card("nos_card", SAFE, 3.34, 7.60, 3.16)
s.head("nos_h", SAFE + 0.22, 3.50, 6.8, "Distribusi skor Newcastle–Ottawa Scale", size=12,
       src="S1, Results")
s.chart("nos_chart", SAFE + 0.30, 3.88, 7.00, 2.42, "col", ["9/9", "8/9", "7/9", "6/9"],
        [48, 53, 6, 1], colors=[T["accent"], T["accent"], T["accent"], T["amber"]],
        gap_width=58, data_labels=True, label_format="0", axis_labels=True,
        show_value_axis=False, src="S1, Tabel 1")
s.card("q_card", 8.48, 3.34, 4.25, 3.16)
s.head("q_h", 8.68, 3.50, 3.85, "Catatan mutu", size=12)
s.txt("q_b", 8.68, 3.86, 3.85, 2.42,
      "Analisis utama hanya memuat studi dengan NOS 7/9 atau lebih.\n"
      "Kelemahan yang paling sering muncul adalah representativitas sampel: 48,7% studi tidak "
      "memenuhinya.\n"
      "Domain lain dinilai memadai.", size=11, line_spacing=1.06, space_after=6,
      src="S1, Results")
slides.append(s)

# -------------------------------------------------------------------- 09 hasil 2
s = Slide("s09_hasil2", "HASIL · 2", "Prevalensi global 13,5%",
          notes="Ini slide intinya. Tiga angka: 13,5% dengan rentang kepercayaan 12,0 sampai "
                "15,1, dari 113.089 anak. Kalau ditanya soal I² 98%, jawab begini: rata-rata ini "
                "menggambarkan beban populasi, bukan angka presisi untuk satu kota. Uji Egger "
                "dan leave-one-out ada untuk menunjukkan estimasi tidak bergantung pada satu "
                "studi tertentu.")
background_and_frame(s)
s.header(9)
s.card("hero_card", SAFE, 1.72, 6.40, 3.36, fill=T["ink"], line=T["ink_2"])
s.txt("hero_lab", SAFE + 0.30, 1.96, 5.8, 0.28, "Prevalensi MIH global", size=10.5, bold=True,
      color=T["accent_mid"], spc=60)
s.txt("hero_v", SAFE + 0.30, 2.26, 5.8, 1.28, "13,5%", size=64, bold=True, color=T["white"],
      role="metric", src="S1, Tabel 2")
s.txt("hero_ci", SAFE + 0.30, 3.66, 5.8, 0.30, "95% CI 12,0–15,1 · p < 0,001 · n = 113.089",
      size=12, color=T["on_ink_body"], src="S1, Tabel 2")
s.txt("hero_note", SAFE + 0.30, 4.06, 5.8, 0.80,
      "Rata-rata tertimbang dari 98 studi berkriteria EAPD 2003. Bacalah sebagai gambaran "
      "beban populasi, bukan angka presisi untuk satu negara.", size=10.5,
      color=T["on_ink_muted"], line_spacing=1.05, src="S1, Tabel 2")
s.card("dough_card", 7.30, 1.72, 5.43, 3.36)
s.head("dough_h", 7.52, 1.90, 5.0, "Porsi anak dengan MIH", size=12, src="S1, Tabel 2")
s.chart("dough_chart", 7.72, 2.22, 4.60, 1.94, "doughnut", ["MIH", "Tanpa MIH"], [13.5, 86.5],
        colors=[T["accent"], T["track"]], font_size=10, data_labels=False, src="S1, Tabel 2")
s.txt("dough_center", 9.52, 2.96, 1.00, 0.44, "13,5%", size=16, bold=True,
      color=T["accent_deep"], align="center", anchor="middle", role="metric", src="S1, Tabel 2")
s.shape("lg1_dot", 8.32, 4.34, 0.16, 0.16, fill=T["accent"], radius=0.08, kind="oval",
        role="decoration")
s.txt("lg1_t", 8.54, 4.29, 1.70, 0.26, "MIH · 13,5%", size=10.5, color=T["heading"],
      src="S1, Tabel 2")
s.shape("lg2_dot", 10.56, 4.34, 0.16, 0.16, fill=T["track"], radius=0.08, kind="oval",
        role="decoration")
s.txt("lg2_t", 10.78, 4.29, 1.80, 0.26, "Tanpa MIH · 86,5%", size=10.5, color=T["muted"],
      src="S1, Tabel 2")
chips9 = [
    ("h1", "I² = 98,0%", "Variasi antar studi sangat tinggi dan nyata, bukan kebetulan acak."),
    ("h2", "Uji Egger p = 0,179", "Tidak ada tanda bias publikasi yang berarti."),
    ("h3", "Leave-one-out", "Estimasi tetap stabil; tidak ditentukan oleh satu studi saja."),
]
for i, (tag, head, body) in enumerate(chips9):
    x = SAFE + i * (W3 + 0.28)
    s.card(f"{tag}_card", x, 5.32, W3, 1.18)
    s.head(f"{tag}_h", x + 0.18, 5.46, W3 - 0.36, head, size=12, color=T["accent_deep"])
    s.txt(f"{tag}_b", x + 0.18, 5.78, W3 - 0.36, 0.58, body, size=10.5, line_spacing=1.04,
          src="S1, Tabel 2")
slides.append(s)

# -------------------------------------------------------------------- 10 hasil 3
s = Slide("s10_hasil3", "HASIL · 3", "Keparahan dan gigi yang terkena",
          notes="Dua pesan klinis. Pertama, 36,3% kasus tergolong sedang sampai berat, jadi "
                "lebih dari sepertiga anak membutuhkan perawatan nyata. Kedua, empat pola molar "
                "hampir merata, 18% sampai 27%, jadi tidak ada pola tunggal yang bisa "
                "diprediksi. Kalau ada yang bertanya soal insisivus, jawab terus terang: abstrak "
                "menulis 36,6% dan Tabel 2 menulis 38,7%; saya memakai angka tabel.")
background_and_frame(s)
s.header(10)
s.tile("v1", SAFE, 1.72, W3, 1.42, "36,3%", "Kasus sedang sampai berat",
       "95% CI 29,9–43,2 · 33 studi · I² = 95,2%", src="S1, Tabel 2")
s.tile("v2", 4.736, 1.72, W3, 1.42, "36–39%", "Insisivus terkena",
       "Tabel 2: 38,7% · abstrak: 36,6%", src="S1, Tabel 2", value_size=30)
s.tile("v3", 8.872, 1.72, W3, 1.42, "3,6%", "HSPM menyertai MIH",
       "95% CI 1,9–6,8 · hanya 7 studi · I² = 95,9%", src="S1, Tabel 2")
s.card("bar_card", SAFE, 3.34, 7.60, 3.16)
s.head("bar_h", SAFE + 0.22, 3.50, 6.9,
       "Jumlah molar pertama permanen yang terkena, dalam persen kasus", size=12,
       src="S1, Tabel 2")
s.chart("bar_chart", SAFE + 0.30, 3.84, 7.00, 2.46, "bar",
        ["4 gigi · 27,4%", "3 gigi · 18,1%", "2 gigi · 26,7%", "1 gigi · 24,3%"],
        [27.4, 18.1, 26.7, 24.3], colors=[T["accent"]], gap_width=48, data_labels=False,
        axis_labels=True, show_value_axis=False, src="S1, Tabel 2")
s.card("read_card", 8.48, 3.34, 4.25, 3.16)
s.head("read_h", 8.68, 3.50, 3.85, "Apa artinya", size=12)
s.txt("read_b", 8.68, 3.86, 3.85, 1.70,
      "Empat pola hampir merata, 18% sampai 27%. Tidak ada satu pola yang dominan, sehingga "
      "berat ringannya beban per anak sulit diperkirakan hanya dari diagnosis MIH.",
      size=11, line_spacing=1.06, src="S1, Tabel 2")
s.rule("read_rule", 8.68, 5.62, 3.85, T["hairline"], h=0.014)
s.txt("read_note", 8.68, 5.78, 3.85, 0.58,
      "Angka insisivus pada abstrak dan Tabel 2 berbeda; Tabel 2 dipakai sebagai rujukan.",
      size=10, italic=True, color=T["muted"], line_spacing=1.04, src="S1, Abstract vs Tabel 2")
slides.append(s)

# --------------------------------------------------------------- 11 sub-analisis
s = Slide("s11_subanalisis", "SUB-ANALISIS", "Wilayah dan kriteria diagnostik",
          notes="Dua temuan yang sifatnya berbeda. Selisih antar wilayah, Amerika 15,3% dan "
                "Asia 10,7%, tidak bermakna secara statistik, dan urutan wilayahnya bergeser "
                "dibanding tinjauan 2018. Sebaliknya, pemakaian kriteria non-EAPD menghasilkan "
                "estimasi yang berbeda bermakna dengan p 0,0061. Kalau presentasi ini memicu "
                "satu debat, biarkan debatnya soal standardisasi kriteria diagnostik.")
background_and_frame(s)
s.header(11)
s.card("geo_card", SAFE, 1.72, 6.40, 4.78)
s.head("geo_h", SAFE + 0.22, 1.88, 5.9, "Prevalensi menurut wilayah", size=12, src="S1, Tabel 2")
s.bar_row("geo1", SAFE + 0.30, 2.34, 5.80, "Amerika · 95% CI 12,8–18,3 · I² = 96,3%",
          "15,3%", 15.3 / 20, 5.80, source="S1, Tabel 2")
s.bar_row("geo2", SAFE + 0.30, 3.32, 5.80, "Asia · 95% CI 8,5–13,5 · I² = 98,7%",
          "10,7%", 10.7 / 20, 5.80, source="S1, Tabel 2")
s.txt("geo_scale", SAFE + 0.30, 4.06, 5.80, 0.24, "Batang digambar pada skala 0–20%",
      size=9, color=T["muted"], align="right")
s.rule("geo_rule", SAFE + 0.30, 4.42, 5.80, T["hairline"], h=0.014)
s.txt("geo_note", SAFE + 0.30, 4.60, 5.80, 1.70,
      "Selisih antar wilayah tidak bermakna secara statistik.\n"
      "Urutan wilayah bergeser dibanding tinjauan 2018: Afrika yang dulu berada di posisi "
      "terendah tidak lagi memegang posisi itu.\n"
      "Penulis menyimpulkan perbedaan wilayah belum cukup menjelaskan variasi angka.",
      size=11, line_spacing=1.06, space_after=6, src="S1, Discussion")
s.card("crit_card", 7.30, 1.72, 5.43, 2.30, fill=T["amber_tint"], line=T["amber_edge"])
s.head("crit_h", 7.52, 1.88, 5.0, "Kriteria diagnostik berpengaruh", size=12, color=T["amber"])
s.txt("crit_v", 7.52, 2.18, 4.99, 0.52, "p = 0,0061", size=26, bold=True, color=T["amber"],
      role="metric", src="S1, Results")
s.txt("crit_b", 7.52, 2.76, 4.99, 1.10,
      "Studi yang tidak memakai definisi kasus EAPD 2003 menghasilkan estimasi berbeda secara "
      "bermakna, umumnya lebih rendah. Sub-analisis ini mencakup 133.734 peserta.",
      size=10.5, line_spacing=1.05, src="S1, Results")
s.card("small_card", 7.30, 4.20, 5.43, 2.30)
s.head("small_h", 7.52, 4.36, 5.0, "Yang pengaruhnya kecil", size=12)
s.txt("small_b", 7.52, 4.72, 4.99, 1.60,
      "Ukuran sampel dan tahun publikasi hanya menyumbang sebagian kecil heterogenitas.\n"
      "Meta-regresi lain tidak menunjukkan faktor metodologis yang menonjol, sehingga penulis "
      "mengarah pada perbedaan wilayah sebagai penjelasan yang lebih besar.",
      size=11, line_spacing=1.06, space_after=6, src="S1, Discussion")
slides.append(s)

# ------------------------------------------------------------------- 12 diskusi
s = Slide("s12_diskusi", "DISKUSI", "Apa yang menurut penulis menjelaskan variasi ini",
          notes="Bagian ini jawaban penulis atas pertanyaan kenapa angkanya berbeda-beda. Pesan "
                "utamanya: variasi wilayah lebih menjelaskan daripada faktor metodologis yang "
                "mereka uji. Tiga kartu di bawah adalah alasannya, dan yang terakhir memuat "
                "permintaan penulis untuk studi berikutnya.")
background_and_frame(s)
s.header(12)
s.card("main_card", SAFE, 1.72, RIGHT - SAFE, 1.50, fill=T["ink"], line=T["ink_2"])
s.txt("main_lab", SAFE + 0.30, 1.88, 8.0, 0.26, "PESAN UTAMA", size=10, bold=True,
      color=T["accent_mid"], spc=90)
s.txt("main_t", SAFE + 0.30, 2.16, RIGHT - SAFE - 0.6, 0.90,
      "Variasi antar wilayah lebih menjelaskan perbedaan angka daripada faktor metodologis "
      "yang diuji penulis lewat meta-regresi.", size=16, bold=True, color=T["white"],
      role="takeaway", line_spacing=1.02, src="S1, Discussion")
disc = [
    ("d1", "Definisi kasus", "Klasifikasi non-EAPD cenderung menurunkan estimasi. Ini alasan "
                             "praktis untuk menyeragamkan kriteria diagnostik."),
    ("d2", "Makna keparahan", "36,3% kasus sedang sampai berat, sehingga sekitar sepertiga anak "
                              "dengan MIH memerlukan perawatan restoratif yang nyata."),
    ("d3", "Data turunan", "Hanya sebagian studi melaporkan keparahan, gigi yang terkena, dan "
                           "HSPM. Penulis meminta studi berikutnya melaporkan lebih lengkap."),
]
for i, (tag, head, body) in enumerate(disc):
    x = SAFE + i * (W3 + 0.28)
    s.card(f"{tag}_card", x, 3.42, W3, 3.08)
    s.head(f"{tag}_h", x + 0.18, 3.60, W3 - 0.36, head, size=12, color=T["heading"])
    s.txt(f"{tag}_b", x + 0.18, 3.98, W3 - 0.36, 2.38, body, size=11, line_spacing=1.07,
          src="S1, Discussion")
slides.append(s)

# ------------------------------------------------------------- 13 penilaian kritis
s = Slide("s13_appraisal", "PENILAIAN KRITIS", "Kekuatan dan keterbatasan artikel ini",
          notes="Bagian ini biasanya paling hidup di diskusi jurnal. Sampaikan kekuatannya "
                "dengan adil, lalu kelemahannya tanpa melemahkan artikelnya: heterogenitas "
                "tinggi, hampir separuh studi gagal pada representativitas sampel, dan tidak "
                "ada penilaian GRADE. Saya juga mencatat dua ketidakkonsistenan kecil: angka "
                "insisivus berbeda antara abstrak dan tabel, dan penyebutan basis data tidak "
                "seragam.")
background_and_frame(s)
s.header(13)
strength = [
    "Protokol terdaftar sebelum pencarian dimulai, laporan mengikuti PRISMA",
    "Tujuh basis data dengan rentang tahun yang luas",
    "Penyaringan dan penilaian risiko bias oleh dua peneliti independen, κ = 0,885",
    "Semua studi pada analisis utama dinilai berkualitas tinggi, NOS 7/9 atau lebih",
    "Definisi kasus EAPD dibandingkan dengan definisi alternatif",
    "Uji kestabilan lengkap: Egger, cumulative, dan leave-one-out",
    "113.089 peserta dengan kepastian bukti SORT A",
]
limits = [
    "Heterogenitas sangat tinggi, I² 93–98%, sehingga angka tunggal perlu dibaca hati-hati",
    "48,7% studi tidak memenuhi representativitas sampel",
    "Studi tanpa definisi EAPD dikeluarkan dari analisis utama, jumlahnya turun dari 116 ke 98",
    "Data keparahan, gigi terkena, dan HSPM langka; sebagian estimasi hanya dari 7 studi",
    "Faktor medis, sosiodemografis, dan lingkungan tidak dapat dianalisis karena pelaporannya "
    "tidak seragam",
    "Tidak ada penilaian GRADE, kepastian bukti memakai SORT. Angka insisivus pada abstrak "
    "(36,6%) juga berbeda dari Tabel 2 (38,7%)",
]
s.card("str_card", SAFE, 1.72, W2, 4.78, fill=T["tint"], line=T["tint_2"])
s.head("str_h", SAFE + 0.22, 1.88, W2 - 0.44, "Kekuatan", size=13)
s.bullets("str_b", SAFE + 0.22, 2.28, W2 - 0.44, 4.06, strength, size=10.5,
          src="S1, Strengths and limitations")
s.card("lim_card", 6.83, 1.72, W2, 4.78, fill=T["amber_tint"], line=T["amber_edge"])
s.head("lim_h", 7.05, 1.88, W2 - 0.44, "Keterbatasan", size=13, color=T["amber"])
s.bullets("lim_b", 7.05, 2.28, W2 - 0.44, 4.06, limits, size=10.5,
          src="S1, Strengths and limitations")
slides.append(s)

# --------------------------------------------------------------- 14 implikasi
s = Slide("s14_implikasi", "IMPLIKASI KLINIS", "Apa yang bisa dilakukan di klinik",
          notes="Turunkan ke praktik. Dua langkah pertama paling mudah dilakukan besok pagi: "
                "periksa molar pertama segera setelah erupsi, dan pakai kriteria EAPD supaya "
                "catatan kita sebanding dengan literatur. Dua langkah berikutnya soal "
                "tatalaksana minimal invasif. Kalau audiensnya dari puskesmas atau program "
                "sekolah, bagian bawah slide ini yang paling relevan.")
background_and_frame(s)
s.header(14)
steps14 = [
    ("a1", "Periksa lebih awal", "Molar pertama permanen diperiksa begitu erupsi, sekitar usia "
                                 "6 sampai 8 tahun. Cari opasitas berbatas tegas dan catat "
                                 "gigi yang terkena."),
    ("a2", "Pakai kriteria yang sama", "Kriteria EAPD 2003 dipakai konsisten, disertai foto "
                                       "klinis, supaya data pasien kita dapat dibandingkan "
                                       "dengan literatur."),
    ("a3", "Catat keparahan", "Keparahan dan jumlah molar yang terkena menentukan intensitas "
                              "recall dan pilihan perawatan."),
    ("a4", "Tangani secara minimal invasif", "Desensitisasi, sealant pada molar berisiko, "
                                             "restorasi atau SSC bila enamel pecah. Hindari "
                                             "preparasi agresif, dan ingat bahwa pencegahan "
                                             "karies lebih menentukan pada enamel yang lemah."),
]
for i, (tag, head, body) in enumerate(steps14):
    x = SAFE + i * (W4 + 0.25)
    s.card(f"{tag}_card", x, 1.80, W4, 3.06)
    s.shape(f"{tag}_chip", x + 0.18, 1.98, 0.42, 0.42, fill=T["accent"], radius=0.21,
            role="chip", classification="content")
    s.txt(f"{tag}_n", x + 0.18, 2.06, 0.42, 0.28, str(i + 1), size=13, bold=True,
          color=T["white"], align="center")
    s.txt(f"{tag}_h", x + 0.18, 2.54, W4 - 0.36, 0.62, head, size=12, bold=True,
          color=T["heading"], line_spacing=1.0, src="S1, Discussion")
    s.txt(f"{tag}_b", x + 0.18, 3.20, W4 - 0.36, 1.50, body, size=10.5, line_spacing=1.06,
          src="S1, Discussion")
for i, tag in enumerate(("ar14a", "ar14b", "ar14c")):
    s.shape(tag, 3.52 + i * (W4 + 0.25), 3.16, 0.19, 0.26, fill=T["accent_mid"],
            kind="right_arrow", radius=0.0)
s.card("school_card", SAFE, 5.06, RIGHT - SAFE, 1.44, fill=T["ink"], line=T["ink_2"])
s.txt("school_lab", SAFE + 0.30, 5.22, 8.0, 0.26, "UNTUK PROGRAM SEKOLAH", size=10, bold=True,
      color=T["accent_mid"], spc=90)
s.txt("school_t", SAFE + 0.30, 5.50, RIGHT - SAFE - 0.6, 0.84,
      "Angka 13% sampai 15% cukup tinggi untuk menjadikan pemeriksaan MIH bagian dari "
      "skrining rutin, bukan temuan yang kebetulan terlihat.", size=13, color=T["white"],
      line_spacing=1.04, src="S1, Discussion")
slides.append(s)

# -------------------------------------------------------------- 15 kesimpulan
s = Slide("s15_kesimpulan", "KESIMPULAN", "Tiga angka, satu pesan",
          notes="Tutup dengan tiga angka dan satu kalimat: MIH sering terlewat, dan pencatatan "
                "yang rapi membuat data klinik kita sebanding dengan literatur internasional. "
                "Siapkan dua pertanyaan untuk membuka diskusi. Pertama, apakah angka di "
                "Indonesia mungkin berbeda dari 13,5%? Kedua, apakah kriteria EAPD bisa "
                "diterapkan di tempat kerja peserta sehari-hari?")
background_and_frame(s)
s.header(15)
final = [
    ("f1", "13,5%", "12,0–15,1", "Prevalensi global dari 113.089 peserta, dengan kepastian "
                                 "bukti SORT A."),
    ("f2", "36,3%", "29,9–43,2", "Kasus sedang sampai berat, sehingga beban perawatan nyata "
                                 "dirasakan sekitar sepertiga anak dengan MIH."),
    ("f3", "36–39%", "HSPM 3,6%", "Insisivus terlibat pada 36–39% kasus, dan HSPM menyertai "
                                 "3,6% kasus."),
]
for i, (tag, value, sub, body) in enumerate(final):
    x = SAFE + i * (W3 + 0.28)
    s.card(f"{tag}_card", x, 1.72, W3, 1.86)
    s.txt(f"{tag}_v", x + 0.18, 1.86, W3 - 0.36, 0.50, value, size=24, bold=True,
          color=T["accent_deep"], role="metric", src="S1, Tabel 2")
    s.txt(f"{tag}_s", x + 0.18, 2.36, W3 - 0.36, 0.26, sub, size=10.5, color=T["muted"],
          src="S1, Tabel 2")
    s.txt(f"{tag}_b", x + 0.18, 2.66, W3 - 0.36, 0.76, body, size=10.5, line_spacing=1.05,
          src="S1, Tabel 2")
s.card("close_card", SAFE, 3.72, RIGHT - SAFE, 1.06, fill=T["tint"], line=T["tint_2"])
s.shape("close_tick", SAFE, 3.72, 0.06, 1.06, fill=T["accent"], radius=0.03)
s.txt("close_t", SAFE + 0.26, 3.86, RIGHT - SAFE - 0.5, 0.78,
      "Angka 13,5% menempatkan MIH sebagai kelainan yang sering dijumpai. Dengan kriteria "
      "EAPD yang sama, catatan klinik kita dapat dibandingkan dengan literatur internasional.",
      size=12, color=T["heading"], anchor="middle", role="takeaway", src="S1, Conclusion")
s.card("ref_card", SAFE, 4.92, RIGHT - SAFE, 1.58)
s.head("ref_h", SAFE + 0.22, 5.04, 4.0, "Rujukan", size=10.5, color=T["muted"], spc=60)
refs = [
    "1.  Lopes LB, dkk. Sci Rep. 2021;11:22405. doi:10.1038/s41598-021-01541-7 (artikel utama)",
    "2.  Weerheijm KL, dkk. Eur J Paediatr Dent. 2003;4:110–113 (kriteria EAPD)",
    "3.  Schwendicke F, dkk. J Dent. 2018;68:10–18 (tinjauan sebelumnya)",
    "4.  Zhao D, dkk. Int J Paediatr Dent. 2018;28:170–179 (tinjauan sebelumnya)",
]
s.txt("ref_b", SAFE + 0.22, 5.34, RIGHT - SAFE - 0.44, 1.00, "\n".join(refs), size=9.5,
      color=T["body"], line_spacing=1.16)
slides.append(s)


# ------------------------------------------------------------------- write spec
def main() -> None:
    spec = {
        "summary": {
            "deck_title": "Presentasi Jurnal: Prevalensi MIH pada Anak dan Remaja (Lopes dkk., 2021)",
            "audience": "Mahasiswa dan dokter gigi pada diskusi jurnal kedokteran gigi anak",
            "decision": "Menilai besaran beban MIH dan menetapkan langkah skrining serta tatalaksana",
            "language": "id-ID",
            "narrative_framework": "custom, struktur pembacaan jurnal (latar belakang, tujuan, "
                                   "metode, hasil, diskusi, penilaian kritis, implikasi, kesimpulan)",
            "slide_count": len(slides),
            "layout_policy": {"safe_margin": SAFE, "content_bottom": 6.6, "footer_top": 6.78,
                              "minimum_gap": 0.12},
            "design_context": {
                "profile": "editorial-minimal, disesuaikan untuk diskusi jurnal akademik",
                "adaptation": "permukaan gelap tinta untuk sampul, angka utama, dan strip "
                              "penutup; sisanya kertas terang; satu aksen teal, amber hanya "
                              "untuk keterbatasan dan peringatan",
                "motif": "lengkung gigi dari objek native pada sampul, batang aksen dan garis "
                         "rambut pada kepala slide, nomor halaman di kaki",
                "palette": {"ink": T["ink"], "paper": T["paper"], "surface": T["surface"],
                            "tint": T["tint"], "accent": T["accent"], "amber": T["amber"],
                            "heading": T["heading"], "body": T["body"], "muted": T["muted"]},
                "typography": {"font": FONT, "cover_pt": 36, "title_pt": 24, "kicker_pt": 10.5,
                               "metric_pt": "24–64", "body_pt": "10.5–12", "caption_pt": "9–10",
                               "floor_pt": 9},
                "viz": "grafik native PowerPoint (kolom, batang mendatar, donut) untuk data "
                       "yang memang punya empat kategori; batang proporsional native untuk "
                       "perbandingan wilayah",
                "evidence": "skill pptx-deck-context (profil editorial-minimal), skill "
                            "visual-design-foundations (skala tipe, grid 8 pt, kontras), skill "
                            "data-storytelling (insight lebih dulu, metodenya menyusul)",
            },
            "accessibility": {
                "presentation_title": "Presentasi Jurnal: Prevalensi MIH pada Anak dan Remaja",
                "language": "id-ID", "min_text_pt": 9,
                "notes": "setiap slide punya catatan pemateri berisi konteks lisan",
            },
            "sources": [
                {"id": "S1", "citation": "Lopes LB, Machado V, Mascarenhas P, Mendes JJ, "
                                         "Botelho J. The prevalence of molar-incisor "
                                         "hypomineralization: a systematic review and "
                                         "meta-analysis. Sci Rep. 2021;11:22405.",
                 "doi": "10.1038/s41598-021-01541-7", "pmcid": "PMC8599453", "license": "CC BY 4.0",
                 "role": "artikel utama, seluruh angka di deck"},
                {"id": "S2", "citation": "Weerheijm KL, dkk. Judgement criteria for molar "
                                         "incisor hypomineralisation in epidemiologic studies. "
                                         "Eur J Paediatr Dent. 2003;4:110–113.",
                 "role": "definisi kriteria EAPD, dikutip dalam S1"},
                {"id": "S3", "citation": "Schwendicke F, dkk. Global burden of molar incisor "
                                         "hypomineralization. J Dent. 2018;68:10–18.",
                 "role": "pembanding tinjauan sebelumnya (13,1%)"},
                {"id": "S4", "citation": "Zhao D, dkk. The prevalence of molar incisor "
                                         "hypomineralization: evidence from 70 studies. "
                                         "Int J Paediatr Dent. 2018;28:170–179.",
                 "role": "pembanding tinjauan sebelumnya (14,2%)"},
            ],
            "visual_assets": "tidak ada aset eksternal; seluruh visual dibuat sebagai objek "
                             "native PowerPoint sehingga deck tetap dapat diedit",
            "copy_pass": "teks dan catatan pemateri melewati skill avoid-ai-writing (mode "
                         "rewrite, register akademik Indonesia): tanpa tanda pisah panjang, "
                         "tanpa kalimat inflasi makna, panjang kalimat divariasikan",
        },
        "slides": [s.emit() for s in slides],
    }
    (HERE / "spec.json").write_text(json.dumps(spec, indent=2, ensure_ascii=False) + "\n",
                                    encoding="utf-8")
    total = sum(len(s["layout_tree"]["objects"]) for s in spec["slides"])
    print(f"spec.json written: {len(spec['slides'])} slides, {total} objects")


if __name__ == "__main__":
    main()
