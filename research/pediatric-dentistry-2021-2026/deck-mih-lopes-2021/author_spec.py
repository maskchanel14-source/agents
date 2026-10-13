#!/usr/bin/env python3
"""Author spec.json for the MIH / Lopes 2021 journal deck (v3).

Why v3 exists
-------------
v2 fixed the prose mechanically but kept the layout the same on every slide: a title,
a row of rounded cards, each card a bold mini-heading plus two lines of gloss. That
grid is the strongest "generated deck" signal there is, and it also left no room for
the data to lead. v3 changes the shape of the slides, not just their wording:

* Layouts are authored per slide. A cover with a typographic hero and an enamel-rod
  texture; a technical molar diagram instead of three cards; a range bar; a horizon
  timeline; a two-column comparison with a hairline divider; three full-width charts;
  giant numerals separated by hairlines. Card grids survive nowhere.
* Display type is Cambria (serif, ships with Office on Windows and macOS) against
  Calibri body text. Serif titles are the cheapest, most reliable way to stop a deck
  looking machine-made.
* Body copy is cut to the bone. Detail that used to sit on the slide now lives in the
  speaker notes, which is where a presenter actually uses it.

Copy rules applied here (repo skill `avoid-ai-writing`, Indonesian academic register):
no em dashes, no "bukan X melainkan Y", no reader-steering frames ("bacalah begini",
"apa artinya", "catatan pembacaan"), no significance inflation, sentence lengths varied
by hand. Visual rules from `visual-design-foundations` and `design-system-patterns`
(primitive -> semantic -> component tokens), chart choices from `kpi-dashboard-design`.

Every number still traces to S1 (Lopes et al. 2021, CC BY 4.0) through `source_ref`.

Usage:  python3 author_spec.py
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

# ------------------------------------------------------------------ design tokens
# primitive
T = {
    "ink_900": "#08222A", "ink_800": "#0C313C", "ink_700": "#134450",
    "paper": "#FBF9F6", "white": "#FFFFFF",
    "teal_600": "#0E7490", "teal_700": "#155E75", "teal_300": "#7FDCE6", "teal_100": "#E4F3F5",
    "amber_700": "#A16207", "amber_50": "#FDF6E6",
    "slate_900": "#141E24", "slate_700": "#3E4C54", "slate_500": "#6E7C83",
    "slate_200": "#E2DFD9", "slate_100": "#F1EEE9",
}
# semantic
S = {
    "surface": T["paper"], "surface_ink": T["ink_900"], "surface_card": T["white"],
    "surface_tint": T["teal_100"], "surface_warning": T["amber_50"],
    "heading": T["slate_900"], "body": T["slate_700"], "muted": T["slate_500"],
    "on_ink": "#E8F1F2", "on_ink_muted": "#8FAAB0",
    "accent": T["teal_600"], "accent_deep": T["teal_700"], "accent_soft": T["teal_300"],
    "warning": T["amber_700"], "hair": T["slate_200"], "tint_line": "#BFD9DD",
    "white": T["white"], "ink_700": T["ink_700"], "hair_ink": "#1C4C57",
}
# component
DISPLAY, BODY, MONO = "Cambria", "Calibri", "Consolas"
SLIDE_W, SLIDE_H = 13.333, 7.5
SAFE, RIGHT = 0.7, 12.63
FOOTER = "Lopes dkk., Sci Rep 2021;11:22405 · DOI 10.1038/s41598-021-01541-7 · CC BY 4.0"


class Slide:
    def __init__(self, sid: str, kicker: str, title: str, notes: str = "") -> None:
        self.sid, self.kicker, self.title, self.notes = sid, kicker, title, notes
        self.objs: dict[str, dict] = {}
        self.order: list[str] = []
        self.z = 0

    def _put(self, oid, kind, role, x, y, w, h, content, style, classification="content",
             src="", reading=True):
        if oid in self.objs:
            raise SystemExit(f"duplicate object id {oid} on {self.sid}")
        if w <= 0 or h <= 0:
            raise SystemExit(f"non-positive geometry on {oid} ({w}x{h})")
        self.z += 1
        self.objs[oid] = {
            "id": oid, "kind": kind, "role": role, "classification": classification,
            "content": content, "style": style,
            "bbox": {"x": round(x, 3), "y": round(y, 3), "width": round(w, 3), "height": round(h, 3)},
            "z_index": self.z, "source_ref": src, "alt_text": "",
        }
        if reading:
            self.order.append(oid)

    # ---------------------------------------------------------------- primitives
    def shape(self, oid, x, y, w, h, *, fill=None, gradient=None, angle=45.0, line="none",
              line_width=0.0, radius=0.06, kind="rounded_rectangle", role="decoration",
              classification="layout_design", alpha=100, rotation=0.0, reading=False, src=""):
        style = {"fill": fill or T["white"], "line_color": fill or "#FFFFFF",
                 "line_width": line_width, "radius": radius, "shadow": False,
                 "alpha": alpha, "rotation": rotation}
        if gradient:
            style["gradient"] = gradient
            style["gradient_angle"] = angle
        if line != "none":
            style["line_color"] = line
        self._put(oid, "shape", role, x, y, w, h, {"shape": kind}, style,
                  classification=classification, reading=reading, src=src)

    def rect(self, oid, x, y, w, h, color, *, alpha=100, rotation=0.0, role="rule"):
        self.shape(oid, x, y, w, h, fill=color, radius=0.0, kind="rectangle", role=role,
                   alpha=alpha, rotation=rotation)

    def hairline(self, oid, x, y, w, color=None, h=0.012):
        self.rect(oid, x, y, w, h, color or S["hair"])

    def txt(self, oid, x, y, w, h, text, *, size=11.5, color=None, bold=False, italic=False,
            align="left", anchor="top", line_spacing=None, space_after=0, spc=0, font=BODY,
            src="", role="body", classification="content", reading=True):
        style = {"font": font, "font_size": size, "color": color or S["body"], "bold": bold,
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

    def display(self, oid, x, y, w, h, text, *, size=40, color=None, src="", role="title",
                align="left", line_spacing=1.0, reading=True):
        self.txt(oid, x, y, w, h, text, size=size, color=color or S["heading"],
                 font=DISPLAY, bold=False, align=align, src=src, role=role,
                 line_spacing=line_spacing, reading=reading)

    def kicker_line(self, oid, x, y, w, text, color=None, src=""):
        self.txt(oid, x, y, w, 0.26, text, size=9.5, bold=True, color=color or S["accent"],
                 spc=140, role="kicker", src=src)

    def lead(self, oid, x, y, w, h, text, *, size=13, color=None, src="", line_spacing=1.12):
        self.txt(oid, x, y, w, h, text, size=size, color=color or S["body"],
                 line_spacing=line_spacing, src=src, role="callout")

    def bullets(self, oid, x, y, w, h, items, *, size=11, color=None, src="", marker="•  ",
                line_spacing=1.05, space_after=5):
        self.txt(oid, x, y, w, h, "\n".join(f"{marker}{i}" for i in items), size=size,
                 color=color or S["body"], line_spacing=line_spacing, space_after=space_after,
                 src=src)

    def fact(self, tag, x, y, w, headline, note="", *, src="", size=14, rule=True,
             color=None, note_color=None):
        """One typographic fact: value, optional gloss, hairline underneath."""
        self.txt(f"{tag}_v", x, y, w, 0.32, headline, size=size, bold=True,
                 color=color or S["heading"], src=src, font=DISPLAY)
        if note:
            self.txt(f"{tag}_n", x, y + 0.36, w, 0.30, note, size=10.5,
                     color=note_color or S["muted"], src=src)
        if rule:
            self.hairline(f"{tag}_r", x, y + (0.66 if note else 0.42), w)

    def chart(self, oid, x, y, w, h, chart_type, categories, values, *, colors=None,
              gap_width=None, data_labels=False, label_format='0.0"%"', font_size=10.5,
              axis_labels=True, show_value_axis=False, src=""):
        content = {"chart_type": chart_type, "categories": categories, "values": values,
                   "series_name": "nilai", "colors": colors or [S["accent"]],
                   "data_labels": data_labels, "label_format": label_format,
                   "font_size": font_size, "gap_width": gap_width, "axis_labels": axis_labels,
                   "show_value_axis": show_value_axis}
        self._put(oid, "chart", "chart", x, y, w, h, content,
                  {"font": BODY, "font_size": font_size, "color": S["body"]}, src=src)

    def bar_row(self, tag, x, y, w, label, value, fraction, cap_width, value_size=15, src=""):
        self.txt(f"{tag}_lab", x, y, w - 1.9, 0.28, label, size=10.5, color=S["body"], src=src)
        self.txt(f"{tag}_val", x + w - 1.8, y - 0.06, 1.8, 0.36, value, size=value_size,
                 bold=True, color=S["accent_deep"], align="right", font=DISPLAY, src=src)
        self.shape(f"{tag}_track", x, y + 0.36, cap_width, 0.16, fill=S["hair"], radius=0.08,
                   role="bar", classification="content")
        self.shape(f"{tag}_fill", x, y + 0.36, max(0.12, cap_width * fraction), 0.16,
                   fill=S["accent"], radius=0.08, role="bar", classification="content")

    # ------------------------------------------------------------------- chrome
    def footer(self, page: int):
        self.hairline("rail", SAFE, 6.82, RIGHT - SAFE)
        self.txt("footer", SAFE, 6.92, 9.4, 0.28, FOOTER, size=9, color=S["muted"],
                 role="footer", reading=False)
        self.txt("page", 11.0, 6.90, RIGHT - 11.0, 0.30, f"{page:02d}", size=10,
                 color=S["accent"], align="right", role="footer", reading=False)

    def head(self, page: int, y: float = 0.5):
        self.rect("accent_tick", SAFE, y + 0.02, 0.045, 0.26, S["accent"], role="decoration")
        self.kicker_line("kicker", SAFE + 0.16, y, 7.0, self.kicker)
        self.display("title", SAFE, y + 0.36, RIGHT - SAFE, 0.72, self.title, size=27,
                     role="title", line_spacing=0.98)
        self.hairline("rule", SAFE, y + 1.16, RIGHT - SAFE)
        self.footer(page)

    def emit(self):
        return {
            "id": self.sid, "title": self.title, "kicker": self.kicker, "notes": self.notes,
            "layout_tree": {"slide_size": {"width": SLIDE_W, "height": SLIDE_H},
                            "objects": self.objs},
            "accessibility": {"title": self.title, "reading_order": self.order,
                              "language": "id-ID"},
        }


def paper_bg(s: Slide):
    s.shape("bg", 0, 0, SLIDE_W, SLIDE_H, fill=S["surface"], radius=0.0, kind="rectangle")


def enamel_rods(s: Slide, x: float, y: float, count: int = 9, spacing: float = 0.30,
                height: float = 3.6, rotation: float = 24.0, color: str = None):
    """Cover texture: parallel diagonal lines that echo the prisms in enamel."""
    for i in range(count):
        s.rect(f"rod_{i:02d}", x + i * spacing, y, 0.022, height, color or S["accent_soft"],
               alpha=9 + (i % 4) * 5, rotation=rotation, role="decoration")


def arch_diagram(s: Slide, cx: float, cy: float, scale: float = 1.0):
    """Occlusal view of the upper arch, drawn from native shapes.

    Twelve teeth along an arc; the two posterior teeth on each side stand for the first
    permanent molars and the four middle ones for the incisors. Everything is
    layout_design, so the illustration never competes with the content checks.
    """
    import math

    rx, ry = 1.74 * scale, 0.90 * scale
    tw, th = 0.34 * scale, 0.30 * scale
    molar_index = {0, 1, 10, 11}
    incisor_index = {4, 5, 6, 7}
    for i in range(12):
        angle = math.radians(198 + 144 * i / 11)
        x = cx + rx * math.cos(angle)
        y = cy + ry * math.sin(angle)
        if i in molar_index:
            fill, line = S["warning"], S["warning"]
        elif i in incisor_index:
            fill, line = T["teal_100"], S["accent"]
        else:
            fill, line = T["white"], S["hair"]
        s.shape(f"tooth_{i:02d}", x - tw / 2, y - th / 2, tw, th, fill=fill, line=line,
                line_width=0.75, radius=0.05, kind="round2same", role="illustration")


def enamel_swatch(s: Slide, x: float, y: float):
    """Small schematic swatch: normal surface next to a demarcated defect."""
    s.shape("sw_normal", x, y, 1.10, 0.76, fill=T["white"], line=S["hair"], line_width=0.75,
            radius=0.08, role="illustration")
    s.rect("sw_normal_lab", x + 0.06, y + 0.74, 0.98, 0.012, S["hair"], role="illustration")
    s.shape("sw_defect", x + 1.34, y, 1.10, 0.76, fill=T["amber_50"], line="#EFDCB4",
            line_width=0.75, radius=0.08, role="illustration")
    for i, (dx, dy, size) in enumerate(((0.16, 0.16, 0.30), (0.62, 0.40, 0.22))):
        s.shape(f"sw_spot_{i}", x + 1.34 + dx, y + dy, size, size, fill=S["warning"],
                radius=0.5, kind="oval", role="illustration", alpha=100)
    s.rect("sw_defect_lab", x + 1.40, y + 0.74, 0.98, 0.012, S["hair"], role="illustration")


slides: list[Slide] = []

# ============================================================================ 01
s = Slide("s01_cover", "DISKUSI JURNAL · KEDOKTERAN GIGI ANAK",
          "Molar-Incisor Hypomineralization pada anak dan remaja",
          notes="Satu menit untuk sampul. Sebutkan identitas artikelnya: Lopes dkk., Scientific "
                "Reports 2021, akses terbuka. Lalu lempar angka besarnya lebih dulu, 13,5%, "
                "supaya peserta punya pegangan sejak awal. Kalau ada yang bertanya kenapa "
                "artikel ini yang dipilih, jawab: ini meta-analisis terbaru dengan jumlah studi "
                "dan peserta terbesar untuk MIH.")
s.shape("bg", 0, 0, SLIDE_W, SLIDE_H, gradient=[T["ink_900"], T["ink_700"]], angle=35.0,
        radius=0.0, kind="rectangle")
enamel_rods(s, 8.55, -0.6)
s.rect("tick", SAFE, 0.92, 0.045, 0.30, S["accent_soft"], role="decoration")
s.kicker_line("kicker", SAFE + 0.18, 0.90, 7.0, "DISKUSI JURNAL · KEDOKTERAN GIGI ANAK",
              color=S["accent_soft"])
s.display("title", SAFE, 1.30, 7.15, 2.16,
          "Molar-Incisor Hypomineralization pada anak dan remaja", size=38,
          color=S["white"], role="title", line_spacing=1.02)
s.txt("orig", SAFE, 3.52, 6.6, 0.34, "The prevalence of molar-incisor hypomineralization: "
      "a systematic review and meta-analysis", size=10.5, italic=True, color=S["on_ink_muted"],
      src="S1, judul")
s.hairline("meta_rule", SAFE, 3.94, 6.4, color=S["hair_ink"], h=0.014)
s.txt("meta", SAFE, 4.08, 6.5, 1.40,
      "Lopes LB, Machado V, Mascarenhas P, Mendes JJ, Botelho J · Egas Moniz, Portugal\n"
      "Scientific Reports 2021;11:22405 · open access CC BY 4.0\n"
      "PMID 34789780 · PMC8599453 · PROSPERO CRD42021229435",
      size=10, color=S["on_ink_muted"], role="meta", src="S1, halaman judul",
      line_spacing=1.25, space_after=3)
s.display("hero_v", 8.72, 2.62, 3.72, 1.66, "13,5%", size=76, color=S["white"],
          role="metric", align="center", src="S1, Tabel 2")
s.hairline("hero_rule", 9.42, 4.42, 2.32, color=S["hair_ink"], h=0.014)
s.txt("hero_l", 8.72, 4.58, 3.72, 0.62, "prevalensi global MIH\n95% CI 12,0–15,1 · 113.089 anak",
      size=10.5, color=S["on_ink_muted"], align="center", role="caption", src="S1, Tabel 2",
      line_spacing=1.20)
s.hairline("foot_rule", SAFE, 6.62, RIGHT - SAFE, color=S["hair_ink"], h=0.014)
s.txt("presenter", SAFE, 6.78, 11.6, 0.32,
      "Pemateri: ____________________     Tanggal: ____________________     "
      "Program Studi Kedokteran Gigi", size=10, color=S["on_ink_muted"], role="footer",
      reading=False)
slides.append(s)

# ============================================================================ 02
s = Slide("s02_ringkasan", "RINGKASAN", "Ringkasan",
          notes="Kalau waktu terbatas, seluruh presentasi bisa diringkas dari slide ini. Tiga "
                "kartu angka di kiri adalah intinya: 116 studi, 113.089 peserta, 13,5%. Baris "
                "kanan menunjukkan bahwa artikel ini juga mencatat keparahan dan HSPM, dua hal "
                "yang sering dilewatkan tinjauan sebelumnya.")
paper_bg(s)
s.head(2)
s.display("hero_v", SAFE, 1.92, 4.20, 1.90, "13,5%", size=84, color=S["accent_deep"],
          role="metric", src="S1, Tabel 2")
s.txt("hero_l", SAFE, 3.86, 4.20, 0.60, "prevalensi global\n95% CI 12,0–15,1 · n = 113.089",
      size=11, color=S["body"], src="S1, Tabel 2", line_spacing=1.18)
s.hairline("hero_r", SAFE, 4.62, 4.20)
s.txt("hero_n", SAFE, 4.74, 4.20, 1.10,
      "Setara satu dari tujuh sampai delapan anak. Angka ini dihitung dari 98 studi yang "
      "memakai kriteria EAPD 2003.", size=11, color=S["body"], line_spacing=1.12,
      src="S1, Tabel 2")
facts = [
    ("f1", "116 studi · 133.734 peserta", "113.089 di antaranya masuk analisis utama"),
    ("f2", "36,3% kasus sedang sampai berat", "95% CI 29,9–43,2"),
    ("f3", "HSPM menyertai 3,6% kasus", "lihat juga slide 10"),
    ("f4", "Kepastian bukti SORT A", "48 studi berskor NOS 9/9"),
]
for i, (tag, head, note) in enumerate(facts):
    s.fact(tag, 6.10, 1.94 + i * 1.10, 6.53, head, note, src="S1, Tabel 2", size=16)
s.lead("close", SAFE, 6.06, RIGHT - SAFE, 0.44,
       "MIH bukan kelainan langka, dan lebih dari sepertiganya butuh perawatan.", size=12.5,
       src="S1, Conclusion")
slides.append(s)

# ============================================================================ 03
s = Slide("s03_mih", "LATAR BELAKANG", "Apa itu MIH",
          notes="Tunjukkan gambar potongan gigi pelan-pelan, jangan buru-buru. Yang perlu "
                "ditekankan: emailnya memang tidak matang sejak awal, jadi rapuh, dan bercaknya "
                "punya batas yang tegas. Tiga bintik oranye di gambar mewakili area "
                "hipomineralisasi. Kalau ada peserta yang bertanya soal penyebab, jawab terus "
                "terang bahwa sampai artikel ini terbit penyebabnya belum diketahui.")
paper_bg(s)
s.head(3)
s.lead("lead", SAFE, 1.84, 5.60, 1.06,
       "Email pada gigi permanen muda gagal matang. Opasitasnya berbatas tegas, warnanya putih "
       "sampai cokelat, dan jaringan itu lebih rapuh daripada email di sebelahnya sehingga mudah "
       "pecah setelah gigi erupsi (post-eruptive enamel breakdown).", size=13,
       src="S1, Introduction")
arch_diagram(s, SAFE + 2.10, 3.92, scale=0.96)
s.rect("occl_line", SAFE + 0.20, 4.86, 4.30, 0.012, S["hair"], role="illustration")
s.txt("occl_cap", SAFE + 0.20, 4.96, 4.30, 0.54,
      "Rahang atas dari permukaan kunyah. Studi MIH memeriksa molar pertama permanen, kadang "
      "disertai insisivus.", size=10, italic=True, color=S["muted"],
      line_spacing=1.08, src="S1, Introduction")
s.shape("lg_molar", SAFE + 0.20, 5.62, 0.16, 0.16, fill=S["warning"], radius=0.08, kind="oval",
        role="decor")
s.txt("lg_molar_t", SAFE + 0.42, 5.58, 2.10, 0.26, "molar pertama", size=10, color=S["body"])
s.shape("lg_inc", SAFE + 2.60, 5.62, 0.16, 0.16, fill=S["accent"], radius=0.08, kind="oval",
        role="decor")
s.txt("lg_inc_t", SAFE + 2.82, 5.58, 1.70, 0.26, "insisivus", size=10, color=S["body"])
enamel_swatch(s, SAFE + 0.20, 5.98)
s.txt("sw_cap", SAFE + 2.76, 6.02, 2.86, 0.56,
      "Email normal dan email dengan bercak hipomineralisasi.", size=10, italic=True,
      color=S["muted"], line_spacing=1.06, src="S1, Introduction")
right = [
    ("r1", "Definisi resminya", "Defek kualitatif email: kandungan mineralnya berkurang, "
                               "bukan jumlah emailnya."),
    ("r2", "Yang dirasakan anak", "Hipersensitivitas dentin, sulit menyikat, dan restorasi "
                                 "yang sering harus diulang."),
    ("r3", "Yang belum jelas", "Penyebabnya belum diketahui, sehingga pencegahan MIH sendiri "
                              "masih belum bisa dilakukan."),
]
for i, (tag, head, body) in enumerate(right):
    y = 1.94 + i * 1.52
    s.txt(f"{tag}_h", 6.55, y, 6.08, 0.32, head, size=14, bold=True, color=S["heading"],
          font=DISPLAY, src="S1, Introduction")
    s.txt(f"{tag}_b", 6.55, y + 0.38, 6.08, 0.94, body, size=11.5, color=S["body"],
          line_spacing=1.12, src="S1, Introduction")
    s.hairline(f"{tag}_r", 6.55, y + 1.34, 6.08)
slides.append(s)

# ============================================================================ 04
s = Slide("s04_gap", "LATAR BELAKANG", "Angka laporan tersebar dari 2,8% sampai 40,2%",
          notes="Slide ini alasan kenapa artikel ini ditulis. Tunjuk ujung kiri dan ujung "
                "kanan garis. Selisihnya lebih dari empat belas kali lipat, dan itu terjadi "
                "pada penyakit yang sama. Penyebab utamanya bukan perbedaan anak, tetapi "
                "perbedaan cara menegakkan diagnosis. Dua tinjauan sebelumnya berhenti pada "
                "2017 dan hanya melaporkan prevalensi.")
paper_bg(s)
s.head(4)
s.txt("scale_lab", SAFE, 2.16, 6.0, 0.26, "KISARAN YANG DILAPORKAN STUDI", size=9.5, bold=True,
      color=S["muted"], spc=120)
s.shape("track", SAFE, 3.06, 11.83, 0.10, fill=S["hair"], radius=0.05, role="bar")
s.shape("fill", SAFE + 0.79, 3.06, 10.45, 0.10, fill=S["accent"], radius=0.05, role="bar")
for tag, cx, label, align in (("lo", 0.0, "2,8%", "left"), ("hi", 11.83, "40,2%", "right")):
    s.shape(f"{tag}_dot", SAFE + cx - 0.07, 3.03, 0.16, 0.16, fill=S["accent_deep"],
            radius=0.5, kind="oval", role="bar")
    s.txt(f"{tag}_t", SAFE + cx + (0.0 if align == "left" else -1.33), 3.30,
          (1.40 if align == "left" else 1.43), 0.30,
          label, size=13, bold=True, color=S["accent_deep"], align=align, font=DISPLAY,
          src="S1, Introduction")
s.shape("mid_dot", SAFE + 3.70, 3.01, 0.20, 0.20, fill=S["warning"], radius=0.5, kind="oval",
        role="bar")
s.txt("mid_t", SAFE + 2.70, 3.30, 2.30, 0.30, "13,5% di artikel ini", size=11, bold=True,
      color=S["warning"], src="S1, Tabel 2")
s.txt("prev_t", SAFE + 2.72, 2.58, 4.4, 0.30, "Tinjauan 2018: 13,1% dan 14,2%", size=10,
      color=S["muted"], italic=True, src="S3, S4")
cols = [
    ("k1", "Kriteria diagnostik belum seragam, sehingga angka antar studi sulit disandingkan, "
           "padahal penyakitnya sama."),
    ("k2", "Dua tinjauan sebelumnya berhenti pada pertengahan 2017 dan hanya melaporkan "
           "prevalensi, tanpa keparahan kasus."),
    ("k3", "Keparahan, jumlah gigi yang terkena, dan HSPM hampir tidak pernah dilaporkan."),
]
for i, (tag, body) in enumerate(cols):
    x = SAFE + i * 4.06
    s.txt(f"{tag}_t", x, 4.12, 3.72, 1.08, body, size=12, color=S["body"], line_spacing=1.14,
          src="S1, Introduction")
    if i:
        s.rect(f"{tag}_div", x - 0.34, 4.12, 0.012, 1.60, S["hair"], role="rule")
s.hairline("base", SAFE, 5.16, 11.93)
s.txt("closing", SAFE, 5.32, 11.93, 0.60,
      "Artikel ini menjawab dua hal sekaligus: memperbarui estimasi global dengan satu "
      "kriteria diagnostik, lalu mengukur keparahan kasusnya.", size=12, color=S["heading"],
      src="S1, Introduction")
slides.append(s)

# ============================================================================ 05
s = Slide("s05_tujuan", "TUJUAN", "Pertanyaan penelitian dan empat luaran",
          notes="PECO biasanya sudah dikenal peserta, jadi cukup dibaca cepat. Yang layak "
                "ditekankan adalah empat luaran di bawah: artikel ini tidak berhenti pada "
                "prevalensi, tetapi juga menghitung keparahan, jumlah gigi yang terkena, dan "
                "HSPM. Luaran sekunder inilah yang jarang disediakan tinjauan lain.")
paper_bg(s)
s.head(5)
peco = [("P", "Populasi", "studi klinis dan epidemiologis pada manusia"),
        ("E", "Paparan", "diagnosis MIH"),
        ("C", "Pembanding", "anak tanpa MIH"),
        ("O", "Luaran", "prevalensi MIH")]
for i, (letter, label, desc) in enumerate(peco):
    x = SAFE + i * 2.98
    s.display(f"{letter}_l", x, 1.90, 0.62, 0.62, letter, size=30, color=S["accent"],
              role="metric", src="S1, Methods")
    s.txt(f"{letter}_t", x + 0.72, 1.96, 2.04, 0.26, label, size=11, bold=True,
          color=S["heading"], spc=30)
    s.txt(f"{letter}_d", x + 0.72, 2.24, 2.04, 0.62, desc, size=10.5, color=S["muted"],
          line_spacing=1.06, src="S1, Methods")
s.hairline("peco_r", SAFE, 2.96, 11.93)
s.txt("q_t", SAFE, 3.16, 11.93, 0.44,
      "Pertanyaan primernya sederhana: berapa prevalensi MIH di seluruh dunia?",
      size=14, color=S["heading"], font=DISPLAY)
s.txt("out_lab", SAFE, 3.88, 6.0, 0.26, "LUARAN YANG DIUKUR", size=9.5, bold=True,
      color=S["muted"], spc=120)
outs = [
    ("o1", "Prevalensi global MIH", "luaran primer", True),
    ("o2", "Prevalensi kasus sedang sampai berat", "sekunder", False),
    ("o3", "Jumlah molar pertama permanen yang terkena", "sekunder", False),
    ("o4", "Kasus dengan insisivus terkena, dan prevalensi HSPM", "sekunder", False),
]
for i, (tag, label, tier, primary) in enumerate(outs):
    y = 4.26 + i * 0.62
    s.rect(f"{tag}_sq", SAFE, y + 0.07, 0.16, 0.16, S["accent"] if primary else S["tint_line"],
           role="decor")
    s.txt(f"{tag}_t", SAFE + 0.34, y, 6.90, 0.32, label, size=12.5,
          bold=primary, color=S["heading"])
    s.txt(f"{tag}_ty", 8.10, y + 0.02, 2.0, 0.28, tier, size=10, color=S["muted"],
          align="right", italic=True)
    s.txt(f"{tag}_src", 10.30, y + 0.02, 2.33, 0.28, "S1", size=9.5, color=S["muted"],
          align="right")
    if i < len(outs) - 1:
        s.hairline(f"{tag}_r", SAFE, y + 0.46, 11.93)
slides.append(s)

# ============================================================================ 06
s = Slide("s06_metode", "METODE · PENCARIAN", "Cara penulis mengumpulkan bukti",
          notes="Empat simpul di garis waktu ini menunjukkan urutan kerjanya. Protokol "
                "didaftarkan sebelum pencarian dimulai, itu penting untuk menepis tuduhan "
                "memilih hasil. Pencarian berhenti Juli 2021. Soal jumlah basis data, ada "
                "catatan kecil: PubMed dan MEDLINE disebut sebagai dua entri terpisah, dan "
                "EMBASE hanya muncul di strategi. Untuk replikasi, cek lampiran artikelnya.")
paper_bg(s)
s.head(6)
nodes = [("n1", "Protokol didaftarkan", "PROSPERO CRD42021229435, sebelum pencarian dimulai"),
         ("n2", "Pencarian di tujuh basis data", "PubMed, MEDLINE, CENTRAL, Web of Science, "
                                                 "SciELO, LILACS, TRIP"),
         ("n3", "Penyaringan dua peneliti", "seleksi independen, kesepakatan κ = 0,885"),
         ("n4", "Analisis random-effects", "heterogenitas I², bias publikasi uji Egger")]
s.rect("timeline", SAFE, 2.34, 11.93, 0.012, S["hair"], role="rule")
for i, (tag, head, note) in enumerate(nodes):
    x = SAFE + i * 3.00
    s.shape(f"{tag}_dot", x, 2.24, 0.22, 0.22, fill=S["accent"] if i < 3 else S["accent_deep"],
            radius=0.5, kind="oval", role="decor")
    s.txt(f"{tag}_t", x, 1.72, 2.78, 0.44, head, size=12.5, bold=True, color=S["heading"],
          line_spacing=1.02)
    s.txt(f"{tag}_n", x, 2.62, 2.78, 1.20, note, size=10.5, color=S["muted"],
          line_spacing=1.10, src="S1, Methods")
s.hairline("mono_r", SAFE, 4.20, 11.93)
s.txt("mono_lab", SAFE, 4.34, 5.0, 0.26, "ALGORITMA PENCARIAN", size=9.5, bold=True,
      color=S["muted"], spc=120)
s.txt("mono", SAFE, 4.64, 11.93, 0.78,
      "(hypomineralization OR hypomineralisation OR hypomineralized OR hypoplasia OR "
      "demarcated OR opacities OR MIH OR cheese molars) AND (survey OR cross-sectional OR "
      "prevalence) AND (molar OR molars OR incisors)", size=9, color=S["body"], font=MONO,
      line_spacing=1.10, src="S1, Methods")
s.txt("note", SAFE, 5.62, 11.93, 0.66,
      "Pencarian berhenti pada Juli 2021. PubMed dan MEDLINE disebut sebagai dua entri "
      "terpisah, sedangkan EMBASE hanya muncul di bagian strategi; bila hendak direplikasi, "
      "angka tujuh basis data sebaiknya dicek ke lampiran artikel.",
      size=10.5, italic=True, color=S["muted"], line_spacing=1.12, src="S1, Methods")
slides.append(s)

# ============================================================================ 07
s = Slide("s07_penyaringan", "METODE · PENYARINGAN", "Aturan masuk dan keluar",
          notes="Bagian ini yang menentukan apakah hasilnya bisa dipercaya. Kriteria "
                "eksklusinya ketat: populasi khusus, molar sulung saja, dan sampel yang tidak "
                "representatif dikeluarkan. Efeknya, analisis utama hanya memuat 98 dari 116 "
                "studi. Konsekuensinya dibahas lagi di slide keterbatasan.")
paper_bg(s)
s.head(7)
s.txt("inc_h", SAFE, 1.92, 5.6, 0.32, "Masuk", size=17, color=S["accent_deep"], font=DISPLAY,
      src="S1, Methods")
s.bullets("inc_b", SAFE, 2.34, 5.60, 2.60, [
    "Studi observasional yang melaporkan prevalensi MIH",
    "Definisi MIH jelas dan dapat ditelusuri",
    "Subjek tanpa kelainan sistemik",
    "Kedua jenis kelamin diikutsertakan",
], size=11.5, src="S1, Methods")
s.rect("divider", 6.42, 1.92, 0.012, 4.20, S["hair"], role="rule")
s.txt("exc_h", 6.83, 1.92, 5.6, 0.32, "Keluar", size=17, color=S["warning"], font=DISPLAY,
      src="S1, Methods")
s.bullets("exc_b", 6.83, 2.34, 5.80, 2.60, [
    "Populasi khusus, misalnya anak yang lahir prematur",
    "Studi yang hanya melaporkan molar sulung",
    "Sampel non-representatif: pasien satu institusi, kelompok profesi tertentu, atau "
    "kelompok dengan karies tinggi",
], size=11.5, src="S1, Methods")
s.hairline("base", SAFE, 5.24, 11.93)
s.txt("base_t", SAFE, 5.40, 11.93, 0.90,
      "Mutu tiap studi dinilai dengan Newcastle–Ottawa Scale, kepastian bukti dengan SORT, "
      "dan hasilnya digabung memakai model random-effects karena populasi antar studi "
      "beragam.", size=11.5, color=S["body"], line_spacing=1.14, src="S1, Methods")
slides.append(s)

# ============================================================================ 08
s = Slide("s08_hasil_seleksi", "HASIL · 1", "116 studi lolos, dan mutunya tinggi",
          notes="Tiga angka dulu, lalu grafiknya. Sebanyak 48 studi mendapat skor maksimum, "
                "dan hanya satu studi yang berkualitas sedang. Satu hal yang perlu disebut "
                "walau tidak enak: 48,7% studi punya kelemahan pada representativitas sampel, "
                "dan angka itu akan muncul lagi di slide penilaian kritis.")
paper_bg(s)
s.head(8)
s.chart("nos_chart", SAFE, 1.92, 7.55, 3.30, "col", ["9/9", "8/9", "7/9", "6/9"],
        [48, 53, 6, 1], colors=[S["accent"], S["accent"], S["accent"], S["warning"]],
        gap_width=56, data_labels=True, label_format="0", axis_labels=True, src="S1, Tabel 1")
s.txt("nos_cap", SAFE, 5.28, 7.55, 0.30, "Jumlah studi per skor Newcastle–Ottawa", size=10,
      italic=True, color=S["muted"], src="S1, Tabel 1")
facts = [("k1", "116", "studi dimasukkan"),
         ("k2", "133.734", "peserta pada analisis awal"),
         ("k3", "113.089", "peserta pada analisis utama, 98 studi"),
         ("k4", "48,7%", "studi gagal pada representativitas sampel")]
for i, (tag, value, note) in enumerate(facts):
    y = 1.96 + i * 1.16
    s.txt(f"{tag}_v", 8.78, y, 3.85, 0.50, value, size=26, color=S["accent_deep"],
          font=DISPLAY, src="S1, Tabel 2")
    s.txt(f"{tag}_n", 8.78, y + 0.52, 3.85, 0.30, note, size=10.5, color=S["muted"],
          src="S1, Tabel 2")
    s.hairline(f"{tag}_r", 8.78, y + 0.90, 3.85)
slides.append(s)

# ============================================================================ 09
s = Slide("s09_hasil_prevalensi", "HASIL · 2", "Prevalensi global 13,5%",
          notes="Slide inti. Baca angkanya lengkap dengan rentang kepercayaan dan jumlah "
                "peserta. Kalau ditanya soal I² yang 98%, jawab begini: variasi antar studi "
                "memang besar, jadi angka ini paling tepat dibaca sebagai gambaran beban "
                "populasi, bukan angka presisi untuk satu kota. Uji Egger dan leave-one-out "
                "ditampilkan untuk menunjukkan estimasi ini tidak bergantung pada satu studi.")
paper_bg(s)
s.head(9)
s.display("hero_v", SAFE, 1.86, 6.10, 2.30, "13,5%", size=112, color=S["heading"],
          role="metric", src="S1, Tabel 2")
s.txt("hero_ci", SAFE, 4.16, 6.10, 0.34, "95% CI 12,0–15,1 · p < 0,001 · n = 113.089",
      size=13, color=S["body"], font=DISPLAY, src="S1, Tabel 2")
s.hairline("hero_r", SAFE, 4.66, 6.10)
s.txt("hero_n", SAFE, 4.80, 6.10, 0.82,
      "Rata-rata tertimbang dari 98 studi berkriteria EAPD 2003. Angka ini menggambarkan beban "
      "populasi, bukan presisi satu negara.", size=11, color=S["body"],
      line_spacing=1.12, src="S1, Tabel 2")
s.chart("dough", 7.30, 1.98, 3.34, 2.62, "doughnut", ["MIH", "Tanpa MIH"], [13.5, 86.5],
        colors=[S["accent"], S["hair"]], font_size=10, data_labels=False, src="S1, Tabel 2")
s.txt("dough_c", 8.42, 2.92, 1.10, 0.52, "13,5%", size=18, bold=True, color=S["accent_deep"],
      align="center", anchor="middle", role="metric", src="S1, Tabel 2")
s.txt("dough_l", 7.30, 4.72, 3.45, 0.30, "MIH pada 13,5% · tanpa MIH pada 86,5%", size=10,
      color=S["muted"], src="S1, Tabel 2")
for i, (tag, value, label) in enumerate((("b1", "98 studi", "yang memakai kriteria EAPD 2003"),
                                         ("b2", "133.734 peserta", "pada analisis awal"),
                                         ("b3", "kepastian bukti SORT A", "dari penilaian penulis"))):
    x = SAFE + i * 4.06
    s.txt(f"{tag}_v", x, 5.72, 3.72, 0.34, value, size=15, bold=True, color=S["accent_deep"],
          font=DISPLAY, src="S1, Tabel 2")
    s.txt(f"{tag}_l", x, 6.08, 3.72, 0.26, label, size=10, color=S["muted"], src="S1, Tabel 2")
    if i:
        s.rect(f"{tag}_div", x - 0.34, 5.72, 0.012, 0.58, S["hair"], role="rule")
diag = [("d1", "I² = 98,0%", "variasi antar studi tinggi dan nyata"),
        ("d2", "Uji Egger", "p = 0,179, tanpa tanda bias publikasi"),
        ("d3", "Leave-one-out", "estimasi tetap stabil")]
for i, (tag, head, note) in enumerate(diag):
    y = 1.98 + i * 1.02
    s.txt(f"{tag}_h", 10.86, y, 1.77, 0.30, head, size=11.5, bold=True, color=S["heading"],
          align="right")
    s.txt(f"{tag}_n", 10.86, y + 0.30, 1.77, 0.50, note, size=9.5, color=S["muted"],
          align="right", line_spacing=1.06, src="S1, Tabel 2")
s.txt("diag_lab", 10.86, 1.70, 1.77, 0.26, "CARA MEMBACANYA", size=9, bold=True,
      color=S["muted"], align="right", spc=90)
s.hairline("diag_r", 10.86, 4.94, 1.77)
slides.append(s)

# ============================================================================ 10
s = Slide("s10_hasil_keparahan", "HASIL · 3", "Lebih dari sepertiga kasus sudah sedang sampai berat",
          notes="Dua pesan klinis di slide ini. Pertama, 36,3% kasus sudah sedang sampai berat, "
                "artinya lebih dari sepertiga anak perlu perawatan restoratif yang nyata. "
                "Kedua, distribusi molarnya hampir merata, 18% sampai 27% di setiap jumlah "
                "gigi, jadi tidak ada pola tunggal yang bisa diprediksi. Soal angka insisivus, "
                "abstrak menulis 36,6% dan Tabel 2 menulis 38,7%; di deck ini dipakai angka "
                "tabel.")
paper_bg(s)
s.head(10)
s.chart("bar_chart", SAFE, 1.92, 7.65, 3.05, "bar",
        ["4 gigi · 27,4%", "3 gigi · 18,1%", "2 gigi · 26,7%", "1 gigi · 24,3%"],
        [27.4, 18.1, 26.7, 24.3], colors=[S["accent"]], gap_width=46, data_labels=False,
        axis_labels=True, src="S1, Tabel 2")
s.txt("bar_cap", SAFE, 5.02, 7.65, 0.30, "Jumlah molar pertama permanen yang terkena, dalam "
      "persen kasus", size=10, italic=True, color=S["muted"], src="S1, Tabel 2")
stats = [("v1", "36,3%", "sedang sampai berat", "95% CI 29,9–43,2 · 33 studi · I² = 95,2%"),
         ("v2", "38,7%", "insisivus terkena (Tabel 2)",
          "MIH tipe molar-insisivus; abstrak menulis 36,6%"),
         ("v3", "3,6%", "HSPM menyertai MIH", "95% CI 1,9–6,8 · hanya 7 studi")]
for i, (tag, value, label, note) in enumerate(stats):
    y = 1.96 + i * 1.42
    s.txt(f"{tag}_v", 8.86, y, 3.77, 0.56, value, size=28, color=S["accent_deep"],
          font=DISPLAY, src="S1, Tabel 2")
    s.txt(f"{tag}_l", 8.86, y + 0.56, 3.77, 0.28, label, size=11, bold=True, color=S["heading"],
          src="S1, Tabel 2")
    s.txt(f"{tag}_n", 8.86, y + 0.84, 3.77, 0.30, note, size=10, color=S["muted"],
          src="S1, Tabel 2")
    s.hairline(f"{tag}_r", 8.86, y + 1.22, 3.77)
slides.append(s)

# ============================================================================ 11
s = Slide("s11_subanalisis", "SUB-ANALISIS", "Wilayah berbeda, kriteria lebih menentukan",
          notes="Dua temuan yang sifatnya beda. Selisih antar wilayah, Amerika 15,3% dan Asia "
                "10,7%, tidak bermakna secara statistik, dan urutan wilayahnya bergeser "
                "dibanding tinjauan 2018. Sebaliknya, pemakaian kriteria non-EAPD menghasilkan "
                "estimasi yang berbeda bermakna, p sama dengan 0,0061. Kalau presentasi ini "
                "memicu perdebatan, biarkan perdebatannya soal standardisasi diagnosis.")
paper_bg(s)
s.head(11)
s.txt("geo_lab", SAFE, 1.96, 7.4, 0.26, "PREVALENSI MENURUT WILAYAH", size=9.5, bold=True,
      color=S["muted"], spc=120)
s.bar_row("geo1", SAFE, 2.36, 7.40, "Amerika · 95% CI 12,8–18,3 · I² = 96,3%", "15,3%",
          15.3 / 20, 7.40, value_size=17, src="S1, Tabel 2")
s.bar_row("geo2", SAFE, 3.48, 7.40, "Asia · 95% CI 8,5–13,5 · I² = 98,7%", "10,7%",
          10.7 / 20, 7.40, value_size=17, src="S1, Tabel 2")
s.txt("geo_scale", SAFE, 4.22, 7.40, 0.26, "Batang digambar pada skala 0–20%", size=9,
      color=S["muted"], align="right")
s.hairline("geo_r", SAFE, 4.60, 7.40)
s.txt("geo_n", SAFE, 4.74, 7.40, 1.20,
      "Beda antar wilayah tidak bermakna secara statistik. Afrika yang dulu terendah tidak "
      "lagi di posisi itu, dan penulis menyimpulkan wilayah belum cukup menjelaskan variasi "
      "angka.", size=11, color=S["body"], line_spacing=1.12, src="S1, Discussion")
s.shape("crit_block", 8.64, 1.96, 3.99, 2.62, fill=S["surface_warning"], gradient=None,
        line="#EFDCB4", line_width=0.75, radius=0.10, role="panel", classification="content")
s.txt("crit_lab", 8.86, 2.12, 3.55, 0.26, "KRITERIA DIAGNOSTIK", size=9.5, bold=True,
      color=S["warning"], spc=120)
s.display("crit_v", 8.86, 2.42, 3.55, 0.78, "p = 0,0061", size=30, color=S["warning"],
          role="metric", src="S1, Results")
s.txt("crit_n", 8.86, 3.26, 3.55, 1.16,
      "Studi tanpa definisi kasus EAPD 2003 menghasilkan estimasi yang berbeda bermakna, "
      "umumnya lebih rendah. Sub-analisis ini memuat 133.734 peserta.",
      size=10.5, color=S["body"], line_spacing=1.10, src="S1, Results")
s.txt("small_h", 8.64, 4.84, 3.99, 0.30, "Yang pengaruhnya kecil", size=13, color=S["heading"],
      font=DISPLAY, src="S1, Discussion")
s.txt("small_n", 8.64, 5.18, 3.99, 0.86,
      "Ukuran sampel dan tahun publikasi hanya menyumbang sedikit. Meta-regresi lain tidak "
      "menunjukkan faktor metodologis yang menonjol.",
      size=11, color=S["body"], line_spacing=1.12, src="S1, Discussion")
slides.append(s)

# ============================================================================ 12
s = Slide("s12_diskusi", "DISKUSI", "Yang menurut penulis menjelaskan variasi",
          notes="Bagian ini jawaban penulis atas pertanyaan kenapa angkanya berbeda-beda. "
                "Pesan utamanya: variasi wilayah lebih menjelaskan dibanding faktor "
                "metodologis yang mereka uji. Tiga baris di bawah adalah alasannya, dan baris "
                "terakhir memuat permintaan penulis untuk penelitian berikutnya.")
paper_bg(s)
s.head(12)
s.display("quote", SAFE, 2.10, 11.93, 1.60,
          "Variasi antar wilayah lebih menjelaskan perbedaan angka daripada faktor metodologis "
          "yang diuji lewat meta-regresi.", size=23, color=S["heading"], role="takeaway",
          line_spacing=1.10, src="S1, Discussion")
s.hairline("q_r", SAFE, 3.92, 11.93, S["accent"], h=0.022)
rows = [("d1", "Definisi kasus", "klasifikasi non-EAPD cenderung menurunkan estimasi"),
        ("d2", "Makna keparahan", "sepertiga anak dengan MIH perlu perawatan restoratif nyata"),
        ("d3", "Data turunan", "keparahan, gigi terkena, dan HSPM jarang dilaporkan")]
for i, (tag, head, body) in enumerate(rows):
    y = 4.20 + i * 0.80
    s.txt(f"{tag}_h", SAFE, y, 2.9, 0.32, head, size=12.5, bold=True, color=S["heading"],
          font=DISPLAY)
    s.txt(f"{tag}_b", SAFE + 3.10, y + 0.02, 8.83, 0.32, body, size=11.5, color=S["body"],
          src="S1, Discussion")
    if i < 2:
        s.hairline(f"{tag}_r", SAFE, y + 0.68, 11.93)
s.txt("disc_close", SAFE, 6.22, 11.93, 0.28,
      "Artinya, standardisasi kriteria diagnostik lebih mungkin mengubah angka daripada "
      "memperluas sampel.", size=10.5, italic=True, color=S["muted"], src="S1, Discussion")
slides.append(s)

# ============================================================================ 13
s = Slide("s13_appraisal", "PENILAIAN KRITIS", "Yang kuat dan yang perlu dibaca hati-hati",
          notes="Bagian favorit di diskusi jurnal. Sampaikan kekuatannya dengan adil, lalu "
                "keterbatasannya tanpa melemahkan artikelnya. Dua baris terakhir keterbatasan "
                "adalah temuan saya sendiri: angka insisivus berbeda antara abstrak dan tabel, "
                "dan penyebutan basis data tidak seragam.")
paper_bg(s)
s.head(13)
s.txt("str_h", SAFE, 1.92, 5.6, 0.32, "Kuat", size=17, color=S["accent_deep"], font=DISPLAY)
props = ["Protokol terdaftar sebelum pencarian dimulai, laporan mengikuti PRISMA",
         "Tujuh basis data, rentang tahun luas",
         "Penyaringan dan penilaian risiko bias oleh dua peneliti, κ = 0,885",
         "Semua studi analisis utama berkualitas tinggi, NOS 7/9 atau lebih",
         "Uji kestabilan lengkap: Egger, cumulative, leave-one-out",
         "Kriteria EAPD dibandingkan dengan definisi alternatif",
         "113.089 peserta dengan kepastian bukti SORT A"]
s.bullets("str_b", SAFE, 2.32, 5.60, 3.10, props, size=11, src="S1, Strengths and limitations")
s.rect("div", 6.42, 1.92, 0.012, 4.16, S["hair"], role="rule")
s.txt("lim_h", 6.83, 1.92, 5.6, 0.32, "Perlu hati-hati", size=17, color=S["warning"],
      font=DISPLAY)
lims = ["Heterogenitas tinggi, I² 93–98%, sehingga angka tunggal jangan dibaca sebagai "
        "presisi",
        "48,7% studi gagal pada representativitas sampel",
        "Dari 116 studi, hanya 98 masuk analisis utama",
        "Estimasi keparahan dan HSPM hanya dari 7 sampai 33 studi",
        "Faktor medis, sosiodemografis, dan lingkungan tidak bisa dianalisis",
        "Tanpa penilaian GRADE; kepastian bukti memakai SORT"]
s.bullets("lim_b", 6.83, 2.32, 5.60, 3.10, lims, size=11, src="S1, Strengths and limitations")
s.hairline("base", SAFE, 5.52, 11.93)
s.txt("base_t", SAFE, 5.68, 11.93, 0.80,
      "Dua hal kecil yang saya catat sendiri saat membaca: angka insisivus berbeda antara "
      "abstrak (36,6%) dan Tabel 2 (38,7%), dan penyebutan basis data tidak seragam di bagian "
      "metode.", size=11, color=S["body"], line_spacing=1.12, src="S1, Abstract vs Tabel 2")
slides.append(s)

# ============================================================================ 14
s = Slide("s14_implikasi", "IMPLIKASI KLINIS", "Langkah praktis di klinik",
          notes="Turunkan ke praktik. Dua langkah pertama bisa dikerjakan besok pagi: periksa "
                "molar pertama begitu erupsi, dan pakai kriteria EAPD supaya catatan kita bisa "
                "dibandingkan dengan literatur. Kalau audiensnya dari puskesmas atau program "
                "sekolah, bagian bawah slide ini yang paling relevan.")
paper_bg(s)
s.head(14)
steps = [("a1", "Periksa lebih awal", "Molar pertama permanen diperiksa begitu erupsi, "
                                      "sekitar usia 6 sampai 8 tahun."),
         ("a2", "Pakai kriteria EAPD", "Satu kriteria untuk semua pasien, disertai foto "
                                       "klinis, supaya catatan kita sebanding."),
         ("a3", "Catat keparahan", "Keparahan dan jumlah molar yang terkena menentukan "
                                   "intensitas recall."),
         ("a4", "Tangani seminimal mungkin", "Desensitisasi, sealant pada molar berisiko, "
                                             "restorasi atau SSC bila enamel pecah. Hindari "
                                             "preparasi agresif.")]
s.rect("step_line", SAFE, 2.02, 11.93, 0.012, S["hair"], role="rule")
for i, (tag, head, body) in enumerate(steps):
    x = SAFE + i * 3.00
    s.shape(f"{tag}_dot", x, 1.93, 0.20, 0.20, fill=S["accent"], radius=0.5, kind="oval",
            role="decor")
    s.txt(f"{tag}_n", x + 0.32, 1.88, 0.40, 0.30, str(i + 1), size=13, bold=True,
          color=S["accent_deep"], font=DISPLAY)
    s.txt(f"{tag}_h", x, 2.30, 2.78, 0.66, head, size=13.5, color=S["heading"], font=DISPLAY,
          line_spacing=1.04, src="S1, Discussion")
    s.txt(f"{tag}_b", x, 3.04, 2.78, 1.30, body, size=11, color=S["body"], line_spacing=1.12,
          src="S1, Discussion")
    if i:
        s.rect(f"{tag}_div", x - 0.18, 2.30, 0.012, 2.04, S["hair"], role="rule")
s.shape("school", SAFE, 4.78, 11.93, 1.30, fill=S["surface_tint"], line=S["tint_line"],
        line_width=0.75, radius=0.10, role="panel", classification="content")
s.rect("school_tick", SAFE, 4.78, 0.05, 1.30, S["accent"], role="decor")
s.txt("school_t", SAFE + 0.30, 4.98, 11.20, 0.90,
      "Untuk program sekolah: angka 13% sampai 15% cukup tinggi untuk menjadikan pemeriksaan "
      "MIH bagian dari skrining rutin, bukan temuan yang kebetulan terlihat.",
      size=13, color=S["heading"], font=DISPLAY, anchor="middle", src="S1, Discussion")
slides.append(s)

# ============================================================================ 15
s = Slide("s15_kesimpulan", "KESIMPULAN", "Tiga angka, satu pesan",
          notes="Tutup dengan tiga angka, lalu satu kalimat: MIH sering terlewat, dan "
                "pencatatan yang rapi membuat data klinik kita sebanding dengan literatur "
                "internasional. Dua pertanyaan untuk membuka diskusi: apakah angka di "
                "Indonesia mungkin berbeda, dan apakah kriteria EAPD bisa diterapkan di "
                "tempat kerja peserta sehari-hari?")
paper_bg(s)
s.head(15)
final = [("g1", "13,5%", "prevalensi global", "dari 113.089 anak, kepastian bukti SORT A"),
         ("g2", "36,3%", "kasus sedang sampai berat", "artinya butuh perawatan, bukan "
                                                      "pemantauan saja"),
         ("g3", "3,6%", "HSPM menyertai MIH", "molar sulung juga perlu diperiksa")]
for i, (tag, value, label, note) in enumerate(final):
    x = SAFE + i * 4.06
    s.display(f"{tag}_v", x, 2.02, 3.72, 1.20, value, size=52, color=S["accent_deep"],
              role="metric", src="S1, Tabel 2")
    s.txt(f"{tag}_l", x, 3.24, 3.72, 0.32, label, size=13, bold=True, color=S["heading"],
          src="S1, Tabel 2")
    s.txt(f"{tag}_n", x, 3.58, 3.72, 0.72, note, size=11, color=S["body"], line_spacing=1.10,
          src="S1, Tabel 2")
    if i:
        s.rect(f"{tag}_div", x - 0.34, 2.10, 0.012, 2.06, S["hair"], role="rule")
s.hairline("close_r", SAFE, 4.62, 11.93, S["accent"], h=0.022)
s.display("close", SAFE, 4.84, 11.93, 0.80,
          "Dengan kriteria yang sama, catatan klinik kita bisa dibandingkan dengan literatur "
          "internasional.", size=16, color=S["heading"], role="takeaway", line_spacing=1.06,
          src="S1, Conclusion")
refs = ["Lopes LB, dkk. Sci Rep. 2021;11:22405. doi:10.1038/s41598-021-01541-7 (artikel utama)",
        "Weerheijm KL, dkk. Eur J Paediatr Dent. 2003;4:110–113 (kriteria EAPD)",
        "Schwendicke F, dkk. J Dent. 2018;68:10–18 · Zhao D, dkk. Int J Paediatr Dent. "
        "2018;28:170–179 (tinjauan sebelumnya)"]
s.txt("refs", SAFE, 5.82, 11.93, 0.74, "\n".join(refs), size=9.5, color=S["muted"],
      line_spacing=1.18)
slides.append(s)


def main() -> None:
    spec = {
        "summary": {
            "deck_title": "Prevalensi MIH pada Anak dan Remaja (Lopes dkk., 2021)",
            "audience": "Mahasiswa dan dokter gigi pada diskusi jurnal kedokteran gigi anak",
            "decision": "Menilai besaran beban MIH dan menetapkan langkah skrining serta tatalaksana",
            "language": "id-ID",
            "narrative_framework": "custom, struktur pembacaan jurnal dengan judul pendek dan "
                                   "satu gagasan per slide",
            "slide_count": len(slides),
            "layout_policy": {"safe_margin": SAFE, "content_bottom": 6.6, "footer_top": 6.82,
                              "minimum_gap": 0.12},
            "design_context": {
                "profile": "editorial-minimal dengan aksen ilmiah, disesuaikan untuk diskusi jurnal",
                "typography": {"display": "Cambria (serif, Office di Windows dan macOS)",
                               "body": "Calibri", "mono": "Consolas",
                               "cover_pt": 38, "title_pt": 27, "metric_pt": "26–96",
                               "lead_pt": 13, "body_pt": "10–12", "footer_pt": 9},
                "palette": {"surface": S["surface"], "surface_ink": S["surface_ink"],
                            "accent": S["accent"], "accent_deep": S["accent_deep"],
                            "warning": S["warning"], "hairline": S["hair"]},
                "composition": "tata letak disusun per slide, tanpa grid kartu berulang: "
                               "sampul tipografis dengan tekstur batang email, diagram molar "
                               "teknis, batang rentang, garis waktu horizontal, dua kolom "
                               "dengan pembatas garis rambut, tiga grafik native, dan deret "
                               "angka besar yang dipisah garis rambut",
                "viz": "grafik native PowerPoint (kolom, batang mendatar, donut) dan batang "
                       "proporsional native; pilihan grafik mengikuti kpi-dashboard-design",
                "evidence": "pptx-deck-context (profil editorial-minimal), visual-design-"
                            "foundations (skala tipe, grid, kontras), design-system-patterns "
                            "(token primitif ke semantik), data-storytelling (insight dulu), "
                            "avoid-ai-writing (bahasa)",
            },
            "accessibility": {"presentation_title": "Prevalensi MIH pada Anak dan Remaja",
                              "language": "id-ID", "min_text_pt": 9,
                              "notes": "catatan pemateri di setiap slide memuat detail yang "
                                       "tidak lagi ditulis di slide"},
            "sources": [
                {"id": "S1", "citation": "Lopes LB, Machado V, Mascarenhas P, Mendes JJ, "
                                         "Botelho J. The prevalence of molar-incisor "
                                         "hypomineralization: a systematic review and "
                                         "meta-analysis. Sci Rep. 2021;11:22405.",
                 "doi": "10.1038/s41598-021-01541-7", "pmcid": "PMC8599453",
                 "license": "CC BY 4.0", "role": "artikel utama, seluruh angka di deck"},
                {"id": "S2", "citation": "Weerheijm KL, dkk. Judgement criteria for molar "
                                         "incisor hypomineralisation in epidemiologic studies. "
                                         "Eur J Paediatr Dent. 2003;4:110–113.",
                 "role": "kriteria EAPD, dikutip dalam S1"},
                {"id": "S3", "citation": "Schwendicke F, dkk. Global burden of molar incisor "
                                         "hypomineralization. J Dent. 2018;68:10–18.",
                 "role": "pembanding tinjauan sebelumnya (13,1%)"},
                {"id": "S4", "citation": "Zhao D, dkk. The prevalence of molar incisor "
                                         "hypomineralization: evidence from 70 studies. "
                                         "Int J Paediatr Dent. 2018;28:170–179.",
                 "role": "pembanding tinjauan sebelumnya (14,2%)"},
            ],
            "visual_assets": "tanpa aset eksternal dan tanpa gambar hasil generasi; tekstur "
                             "batang email dan diagram molar digambar sebagai objek native "
                             "PowerPoint sehingga tetap dapat diedit",
            "copy_pass": "avoid-ai-writing, register akademik Indonesia: tanpa tanda pisah "
                         "panjang, tanpa kerangka penuntun pembaca, tanpa inflasi makna; "
                         "panjang kalimat divariasikan",
        },
        "slides": [s.emit() for s in slides],
    }
    (HERE / "spec.json").write_text(json.dumps(spec, indent=2, ensure_ascii=False) + "\n",
                                    encoding="utf-8")
    total = sum(len(x["layout_tree"]["objects"]) for x in spec["slides"])
    words = 0
    for x in spec["slides"]:
        for o in x["layout_tree"]["objects"].values():
            if o["kind"] == "text" and o["role"] not in ("footer", "kicker", "metric", "title"):
                words += len(o["content"]["text"].split())
    print(f"spec.json written: {len(spec['slides'])} slides, {total} objects, "
          f"~{words} kata isi")


if __name__ == "__main__":
    main()
