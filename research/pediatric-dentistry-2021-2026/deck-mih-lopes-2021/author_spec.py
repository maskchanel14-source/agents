#!/usr/bin/env python3
"""Author the deck specification (v5) for the MIH journal presentation.

Design system "klinis terang": white paper, deep-teal ink, filled panels and chips
instead of hairlines, large figures, and two real illustrations. Every slide is laid
out from a shared master grid: kicker chip, title, takeaway band, content area,
footer rail.

Every position, size, and style is declared here; build_deck.py only maps the spec
onto the PPTX. Text boxes are sized with the same line estimate the audit uses, so
the deck cannot ship with copy that does not fit.

Usage:  python3 author_spec.py
"""
from __future__ import annotations

import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "spec.json"

SLIDE_W, SLIDE_H = 13.333, 7.5
M = 0.58
W = round(SLIDE_W - 2 * M, 3)          # content width
RIGHT = round(SLIDE_W - M, 3)
BODY_TOP = 2.24
CONTENT_BOTTOM = 6.66
FOOT_RULE_Y = 6.84
FOOT_TEXT_Y = 6.88

# ---- design tokens ---------------------------------------------------------
# v6 chrome: a designed background instead of blank paper
PAPER_A = "#F9F7F3"          # warm paper, top-left of the wash
PAPER_B = "#E6EFF2"          # cool tint, bottom-right of the wash
BAND = "#0B4A5A"             # deep teal header band
BAND2 = "#0F6274"            # its gradient partner
ON_BAND = "#8FD8E4"          # kicker on the dark band
PAPER = "#FFFFFF"
PANEL = "#F2F7F8"
MINT = "#E3F1F3"
INK = "#08262E"
TEAL = "#0E7C8C"
TEAL2 = "#14A0B4"
TEALSOFT = "#BCDCE2"
CREAM = "#FBF2E4"
AMBER = "#B26A14"
AMBERBG = "#FBEBD6"
TEXT = "#102A31"
MUTED = "#5C757C"
LINE = "#D7E3E6"
WHITE = "#FFFFFF"

BODY, DISP, MONO = "Calibri", "Cambria", "Consolas"

CITATION = "Lopes dkk., Sci Rep 2021;11:22405 · DOI 10.1038/s41598-021-01541-7 · CC BY 4.0"


def est_lines(text: str, width_in: float, font_pt: float) -> int:
    """Estimate wrapped line count with a margin over the audit's own estimate.

    The audit uses 0.53 em per character; real Calibri/Carlito metrics plus word
    wrapping need roughly 0.62 em, so authoring to the stricter figure keeps the
    built deck inside every text box the renderer measures.
    """
    usable = max(0.1, width_in - 0.1)
    chars_per_line = max(8, int(usable * 96 / (0.62 * font_pt)))
    return sum(max(1, math.ceil(len(chunk) / chars_per_line)) for chunk in text.split("\n"))


def h_for(text: str, width_in: float, font_pt: float, pad: float = 0.14) -> float:
    return round(est_lines(text, width_in, font_pt) * (font_pt * 1.22 / 72) + pad, 3)


def cols(n: int, gap: float = 0.22, total: float = W, x0: float = M):
    w = round((total - gap * (n - 1)) / n, 3)
    return [(round(x0 + i * (w + gap), 3), w) for i in range(n)]


class Slide:
    def __init__(self, deck: "Deck", sid: str, kicker: str, title: str, notes: str = "") -> None:
        self.deck = deck
        self.id = sid
        self.kicker = kicker
        self.title = title
        self.notes = notes
        self.objects: dict[str, dict] = {}
        self.reading: list[str] = []
        self.z = 0
        deck.slides.append(self)

    # -- internals ----------------------------------------------------------
    def _add(self, oid, kind, role, classification, content, style, x, y, w, h,
             source_ref="", alt_text=""):
        if oid in self.objects:
            raise SystemExit(f"duplicate object id: {self.id}/{oid}")
        if w <= 0 or h <= 0:
            raise SystemExit(f"non-positive geometry: {self.id}/{oid} {w}x{h}")
        self.z += 1
        self.objects[oid] = {
            "id": oid, "kind": kind, "role": role, "classification": classification,
            "content": content, "style": style,
            "bbox": {"x": round(x, 3), "y": round(y, 3), "width": round(w, 3), "height": round(h, 3)},
            "z_index": self.z, "source_ref": source_ref, "alt_text": alt_text,
        }
        return oid

    # -- primitives ---------------------------------------------------------
    def bg(self, fill: str = PAPER) -> None:
        """A graded paper wash plus two soft shapes, so no slide is blank white."""
        if fill != PAPER:
            self._add("bg", "shape", "background", "layout_design", {"shape": "rectangle"},
                      {"fill": fill, "line_color": fill, "line_width": 0.0}, 0, 0, SLIDE_W, SLIDE_H)
            return
        self.bar("bg", 0, 0, SLIDE_W, SLIDE_H, PAPER_A, role="background",
                 gradient=[PAPER_A, PAPER_B], gradient_angle=40.0)
        self._add("bg_orb1", "shape", "background", "layout_design", {"shape": "oval"},
                  {"fill": "#E4EFF1", "line_color": "#E4EFF1", "line_width": 0.0},
                  9.95, -2.45, 4.90, 4.90)
        self._add("bg_orb2", "shape", "background", "layout_design", {"shape": "oval"},
                  {"fill": "#EAF3F4", "line_color": "#EAF3F4", "line_width": 0.0},
                  -1.75, 4.55, 4.30, 4.30)
        self.bar("bg_foot", 0, 7.06, SLIDE_W, 0.44, "#DCE7EA", role="background", alpha=85.0)

    def pic(self, oid, path: str, x, y, w, h, alt: str = "") -> None:
        self._add(oid, "picture", "decoration", "layout_design", {"path": path},
                  {"alpha": 100}, x, y, w, h, alt_text=alt)

    def bar(self, oid, x, y, w, h, fill: str, radius: float = 0.0, role: str = "bar",
            alpha: float = 100.0, line_color: str | None = None, line_width: float = 0.0,
            gradient: list[str] | None = None, gradient_angle: float = 0.0,
            gradient_alpha: list[float] | None = None) -> None:
        style = {"fill": fill, "radius": radius, "alpha": alpha, "rotation": 0.0,
                 "line_width": line_width if line_color else 0.0,
                 "line_color": line_color or fill}
        if gradient:
            style["gradient"] = gradient
            style["gradient_angle"] = gradient_angle
            if gradient_alpha:
                style["gradient_alpha"] = gradient_alpha
        self._add(oid, "shape", role, "layout_design",
                  {"shape": "rounded_rectangle" if radius else "rectangle"}, style, x, y, w, h)

    def card(self, oid, x, y, w, h, fill: str = PANEL, radius: float = 0.10,
             edge: str | None = None, role: str = "panel") -> None:
        self.bar(oid, x, y, w, h, fill, radius=radius, role=role,
                 line_color=edge, line_width=0.75 if edge else 0.0)

    def add_chart(self, oid, content: dict, x, y, w, h, source_ref: str = "") -> None:
        style = {"font": BODY, "font_size": content.get("font_size", 10.5), "color": MUTED}
        self._add(oid, "chart", "chart", "content", content, style, x, y, w, h,
                  source_ref=source_ref)

    def rule(self, oid, x, y, w, color: str = LINE, h: float = 0.014) -> None:
        self._add(oid, "shape", "rule", "layout_design", {"shape": "rectangle"},
                  {"fill": color, "line_color": color, "line_width": 0.0}, x, y, w, h)

    def txt(self, oid, x, y, w, h, text: str, size: float = 12.0, font: str = BODY,
            bold: bool = False, italic: bool = False, color: str = TEXT,
            align: str = "left", anchor: str = "top", role: str = "body",
            ls: float | None = None, sa: float = 0.0, spc: int | None = None,
            source_ref: str = "") -> None:
        style = {"font": font, "font_size": size, "bold": bold, "italic": italic,
                 "color": color, "align": align, "anchor": anchor,
                 "inset_left": 0.0, "inset_right": 0.0, "inset_top": 0.0, "inset_bottom": 0.0,
                 "space_after_pt": sa}
        if ls:
            style["line_spacing"] = ls
        if spc:
            style["spc"] = spc
        self._add(oid, "text", role, "content", {"text": text}, style, x, y, w, h,
                  source_ref=source_ref, alt_text="")
        self.reading.append(oid)

    def chip(self, oid, x, y, text: str, fill: str = INK, color: str = WHITE,
             size: float = 9.5, spc: int = 60) -> None:
        w = round(len(text) * size * 0.60 / 72 + 0.34, 3)
        self.bar(oid + "_bg", x, y, w, 0.30, fill, radius=0.06, role="bar")
        self.txt(oid, x + 0.17, y + 0.068, w - 0.34, 0.18, text, size=size, bold=True,
                 color=color, role="kicker", spc=spc)

    # -- master blocks -------------------------------------------------------
    def header(self, action: str = "", action_fill: str = MINT, action_color: str = TEAL,
               title_size: float = 26.0) -> None:
        """Deep-teal band carrying the kicker and title, then a carded lead line."""
        title_h = h_for(self.title, W, title_size, pad=0.10)
        band_h = round(0.56 + title_h + 0.18, 3)
        self.bar("hdr", 0, 0, SLIDE_W, band_h, BAND, role="background",
                 gradient=[BAND, BAND2], gradient_angle=0.0)
        self.bar("hdr_edge", 0, band_h, SLIDE_W, 0.05, TEAL2, role="background")
        self.txt("kicker", M, 0.28, W, 0.24, self.kicker, size=9.5, bold=True,
                 color=ON_BAND, role="kicker", spc=110)
        self.txt("title", M, 0.56, W, title_h, self.title, size=title_size, bold=True,
                 color=WHITE, role="title")
        if action:
            ay = round(band_h + 0.14, 3)
            width = W - 0.88
            lines = est_lines(action, width, 12.5)
            ah = round(lines * (12.5 * 1.24 / 72) + 0.30, 3)
            self.card("action_bg", M, ay, W, ah, WHITE, radius=0.08, edge=LINE)
            self.bar("action_edge", M, ay, 0.06, ah, action_color, role="bar")
            self.txt("action", M + 0.32, round(ay + 0.15, 3), width, round(ah - 0.30, 3),
                     action, size=12.5, bold=True, color=action_color, role="takeaway")

    def footer(self, page: str) -> None:
        self.rule("foot_rule", M, FOOT_RULE_Y, W)
        self.txt("footer", M, FOOT_TEXT_Y, 9.4, 0.28, CITATION, size=9, color=MUTED, role="footer")
        self.bar("page_chip", round(RIGHT - 0.44, 3), round(FOOT_RULE_Y - 0.03, 3), 0.44, 0.28,
                 BAND, radius=0.05, role="bar")
        self.txt("page", round(RIGHT - 0.44, 3), round(FOOT_RULE_Y + 0.035, 3), 0.44, 0.20,
                 page, size=9.5, bold=True, color=WHITE, align="center", role="footer")

    def kpi_rail(self, oid_prefix: str, x, y, w, rows, row_h: float = 0.78,
                 num_size: float = 24.0, num_w: float = 2.05) -> None:
        """Number on the left, label and note on the right, ruled rows."""
        for i, (number, label, note) in enumerate(rows):
            top = round(y + i * row_h, 3)
            if i:
                self.rule(f"{oid_prefix}_r{i}", x, top - 0.06, w)
            self.txt(f"{oid_prefix}_v{i}", x, top + 0.06, num_w,
                     h_for(number, num_w, num_size, pad=0.08), number, size=num_size,
                     bold=True, font=DISP, color=TEAL, role="metric")
            tx = round(x + num_w + 0.16, 3)
            tw = round(w - num_w - 0.16, 3)
            self.txt(f"{oid_prefix}_l{i}", tx, top + 0.04, tw,
                     h_for(label, tw, 11.5, pad=0.06), label, size=11.5, bold=True,
                     color=INK, role="panel_text")
            if note:
                self.txt(f"{oid_prefix}_n{i}", tx, top + 0.36, tw,
                         h_for(note, tw, 9.5, pad=0.06), note, size=9.5, color=MUTED,
                         role="panel_text")

    def bullets(self, oid_prefix: str, x, y, w, items, size: float = 11.5,
                row_h: float = 0.48, dot: str = TEAL, color: str = TEXT) -> float:
        tw = round(w - 0.30, 3)
        for i, item in enumerate(items):
            top = round(y + i * row_h, 3)
            self.bar(f"{oid_prefix}_d{i}", x, top + 0.075, 0.13, 0.13, dot, radius=0.5, role="bar")
            self.txt(f"{oid_prefix}_t{i}", round(x + 0.30, 3), top, tw,
                     h_for(item, tw, size, pad=0.06), item, size=size, color=color,
                     role="panel_text")
        return round(y + len(items) * row_h, 3)

    def step_card(self, oid, x, y, w, h, number: str, head: str, body: str,
                  accent: str = TEAL, badge_fill: str = TEAL) -> None:
        self.card(oid + "_bg", x, y, w, h)
        self.bar(oid + "_badge", round(x + 0.28, 3), round(y + 0.26, 3), 0.46, 0.46,
                 badge_fill, radius=0.5, role="bar")
        self.txt(oid + "_n", round(x + 0.28, 3), round(y + 0.345, 3), 0.46, 0.26, number,
                 size=15, bold=True, font=DISP, color=WHITE, align="center", role="metric")
        tw = round(w - 1.06, 3)
        self.txt(oid + "_h", round(x + 0.88, 3), round(y + 0.32, 3), tw,
                 h_for(head, tw, 13, pad=0.10), head, size=13, bold=True, color=accent,
                 role="panel_text")
        bw = round(w - 0.56, 3)
        self.txt(oid + "_b", round(x + 0.28, 3), round(y + 0.90, 3), bw,
                 h_for(body, bw, 10, pad=0.10), body, size=10, color=TEXT,
                 role="panel_text")

    def big_stat(self, oid, x, y, w, number: str, label: str, note: str = "",
                 num_size: float = 44.0, num_color: str = TEAL) -> None:
        self.txt(oid + "_v", x, y, w, h_for(number, w, num_size, pad=0.12), number,
                 size=num_size, bold=True, font=DISP, color=num_color, role="metric")
        ly = round(y + h_for(number, w, num_size, pad=0.12) + 0.04, 3)
        self.txt(oid + "_l", x, ly, w, h_for(label, w, 12.5, pad=0.08), label, size=12.5,
                 bold=True, color=INK, role="panel_text")
        if note:
            self.txt(oid + "_n", x, round(ly + h_for(label, w, 12.5, pad=0.08) + 0.02, 3),
                     w, h_for(note, w, 10.5, pad=0.08), note, size=10.5, color=MUTED,
                     role="panel_text")

    def spec(self) -> dict:
        return {"id": self.id, "title": self.title, "kicker": self.kicker, "notes": self.notes,
                "layout_tree": {"slide_size": {"width": SLIDE_W, "height": SLIDE_H},
                                "objects": self.objects},
                "accessibility": {"title": self.title, "reading_order": self.reading,
                                  "language": "id-ID"}}


class Deck:
    def __init__(self) -> None:
        self.slides: list[Slide] = []

    def add(self, sid, kicker, title, notes="") -> Slide:
        s = Slide(self, sid, kicker, title, notes)
        self.slides.append(s)
        return s


deck = Deck()

# ===========================================================================
# 01 — cover
# ===========================================================================
s = Slide(deck, "s01_cover", "DISKUSI JURNAL · KEDOKTERAN GIGI ANAK",
          "Molar-Incisor Hypomineralization pada anak dan remaja",
          notes="Satu menit untuk sampul. Sebutkan identitas artikelnya: Lopes dkk., Scientific "
                "Reports 2021, akses terbuka. Lalu lempar angka besarnya lebih dulu, 13,5%, supaya "
                "peserta punya pegangan sejak awal. Kalau ada yang bertanya kenapa artikel ini "
                "yang dipilih, jawab: ini meta-analisis terbaru dengan jumlah studi dan peserta "
                "terbesar untuk MIH.")
s.pic("cover_img", "assets/cover-enamel.png", 0, 0, SLIDE_W, SLIDE_H,
      alt="Tekstur batang email gigi, tampilan dekat")
s.bar("scrim", 0, 0, 9.95, SLIDE_H, INK, role="background",
      gradient=[INK, INK], gradient_alpha=[93.0, 0.0], gradient_angle=0.0)
s.chip("kicker", 0.62, 0.62, "DISKUSI JURNAL · KEDOKTERAN GIGI ANAK", fill=TEAL, size=9.5)
title = "Molar-Incisor Hypomineralization pada anak dan remaja"
s.txt("title", 0.62, 1.06, 6.62, 1.80, title, size=31,
      bold=True, font=DISP, color=WHITE, role="title", ls=1.02)
s.bar("accent", 0.62, 2.98, 0.92, 0.055, TEAL2, role="bar")
sub = "The prevalence of molar-incisor hypomineralization: a systematic review and meta-analysis"
s.txt("orig", 0.62, 3.14, 6.45, 0.52, sub, size=12, italic=True,
      color=TEALSOFT, role="callout")
meta = ("Lopes LB, Machado V, Mascarenhas P, Mendes JJ, Botelho J · Egas Moniz, Portugal\n"
        "Scientific Reports 2021;11:22405 · akses terbuka CC BY 4.0\n"
        "PMID 34789780 · PMC8599453 · PROSPERO CRD42021229435")
s.txt("meta", 0.62, 3.74, 6.55, 0.70, meta, size=10.5,
      color="#9FC3CA", role="callout", ls=1.15)
s.txt("hero_v", 8.06, 2.62, 4.60, h_for("13,5%", 4.60, 62, pad=0.26), "13,5%", size=62,
      bold=True, font=DISP, color=WHITE, role="metric")
s.txt("hero_l", 8.12, 3.98, 4.20, h_for("prevalensi global MIH", 4.20, 13, pad=0.10),
      "prevalensi global MIH", size=13, color="#DCEFF1", role="callout")
s.txt("hero_n", 8.12, 4.30, 4.30, h_for("95% CI 12,0–15,1 · 113.089 anak", 4.30, 10.5, pad=0.08),
      "95% CI 12,0–15,1 · 113.089 anak", size=10.5, color="#9FC3CA", role="callout")
s.rule("cover_rule", 0.62, FOOT_RULE_Y, W)
s.txt("presenter", 0.62, FOOT_TEXT_Y, 7.55, 0.28,
      "Pemateri: ____________________     Tanggal: ____________________", size=9.5,
      color="#9FC3CA", role="footer")
s.txt("program", 8.32, FOOT_TEXT_Y, 4.42, 0.28, "Program Studi Kedokteran Gigi",
      size=9.5, color="#9FC3CA", align="right", role="footer")

# ===========================================================================
# 02 — summary
# ===========================================================================
s = Slide(deck, "s02_ringkasan", "RINGKASAN", "13,5% anak dan remaja mengalami MIH",
          notes="Kalau waktu terbatas, seluruh presentasi bisa diringkas dari slide ini. Empat "
                "baris angka di kanan adalah intinya: 116 studi, 133.734 peserta, 36,3% kasus "
                "berat, dan kepastian bukti SORT A. Artikel ini juga mencatat keparahan dan HSPM, "
                "dua hal yang sering dilewatkan tinjauan sebelumnya.")
s.bg()
s.header("Satu dari tujuh sampai delapan anak, dan lebih dari sepertiganya sudah butuh perawatan.")
s.card("sum_bg", M, BODY_TOP, 4.35, 3.10, MINT)
s.big_stat("sum", M + 0.30, BODY_TOP + 0.24, 3.75, "13,5%", "prevalensi global MIH",
           "95% CI 12,0–15,1 · p < 0,001\nRata-rata tertimbang 98 studi · 113.089 anak",
           num_size=60)
s.kpi_rail("sumk", 5.15, BODY_TOP, 7.60, [
    ("116", "studi masuk ke tinjauan", "48 di antaranya berskor NOS 9/9"),
    ("133.734", "peserta pada analisis awal", "113.089 di antaranya masuk analisis utama"),
    ("36,3%", "kasus sedang sampai berat", "95% CI 29,9–43,2 · 33 studi"),
    ("SORT A", "kepastian bukti tertinggi", "tanpa penilaian GRADE"),
], row_h=0.78)
s.bar("sum_band", M, 5.50, W, 1.16, INK, radius=0.10, role="bar")
s.txt("sum_band_t", M + 0.34, 5.66, W - 0.68, 0.44,
      "MIH bukan kelainan langka, dan lebih dari sepertiganya butuh perawatan restoratif.",
      size=15, bold=True, color=WHITE, font=DISP, role="takeaway")
s.txt("sum_band_n", M + 0.34, 6.12, W - 0.68, 0.30,
      "Kriteria diagnostik yang seragam membuat angka ini bisa dibandingkan antar negara.",
      size=11, color="#A9CFD6", role="panel_text")
s.footer("02")

# ===========================================================================
# 03 — what MIH is
# ===========================================================================
s = Slide(deck, "s03_mih", "LATAR BELAKANG", "Apa itu MIH",
          notes="Tunjukkan gambar potongan gigi pelan-pelan, jangan buru-buru. Yang perlu "
                "ditekankan: emailnya memang tidak matang sejak awal, jadi rapuh, dan bercaknya "
                "punya batas yang tegas. Lesi pada gambar mewakili area hipomineralisasi. Kalau "
                "ada peserta yang bertanya soal penyebab, jawab terus terang bahwa sampai artikel "
                "ini terbit penyebabnya belum diketahui.")
s.bg()
s.header("Email gigi permanen muda gagal matang: opasitas berbatas tegas, dan jaringan yang "
         "lebih rapuh daripada email di sebelahnya.")
rows = [
    ("Definisi resmi", "Defek kualitatif email: kandungan mineralnya berkurang, bukan jumlah emailnya."),
    ("Yang dirasakan anak", "Hipersensitivitas dentin, sulit menyikat, dan restorasi yang sering "
                            "harus diulang."),
    ("Yang belum jelas", "Penyebabnya belum diketahui, sehingga pencegahan MIH sendiri masih belum "
                         "bisa dilakukan."),
]
y = BODY_TOP
for i, (head, body) in enumerate(rows):
    s.card(f"m{i}_bg", M, y, 6.05, 1.32)
    s.txt(f"m{i}_h", M + 0.30, round(y + 0.18, 3), 5.45, 0.26, head.upper(), size=10.5,
          bold=True, color=TEAL, role="panel_text", spc=40)
    s.txt(f"m{i}_t", M + 0.30, round(y + 0.50, 3), 5.45, h_for(body, 5.45, 11.5, pad=0.10),
          body, size=11.5, color=TEXT, role="panel_text", ls=1.12)
    y = round(y + 1.48, 3)
s.card("fig_bg", 6.95, BODY_TOP, 5.80, 4.28, CREAM)
s.card("fig_plate", 7.21, 2.32, 2.38, 3.54, WHITE, radius=0.05, edge=LINE)
s.pic("fig_molar", "assets/molar-mih-crop.png", 7.33, 2.44, 2.14, 3.30,
      alt="Potongan molar pertama permanen dengan lesi hipomineralisasi pada email")
legend = [("#A8D8DC", "email sehat"), ("#D9A566", "dentin"), ("#2E8B8B", "pulpa"),
          ("#C98F4A", "lesi hipomineralisasi")]
for i, (dot, label) in enumerate(legend):
    ly = round(2.72 + i * 0.38, 3)
    s.bar(f"lg{i}_d", 9.85, ly, 0.14, 0.14, dot, radius=0.5, role="bar")
    s.txt(f"lg{i}_t", 10.09, round(ly - 0.045, 3), 2.36, 0.30, label, size=10.5, color=TEXT,
          role="panel_text")
s.txt("fig_cap", 9.85, 4.32, 2.60, h_for("Sumber: artikel S1, gambar skematik", 2.60, 9.5, pad=0.08),
      "Sumber: artikel S1, gambar skematik", size=9.5, italic=True, color=MUTED, role="body")
s.txt("fig_note", 7.33, 5.92, 5.10, h_for("Skema, bukan gambaran klinis pasien.", 5.10, 9.5, pad=0.08),
      "Skema, bukan gambaran klinis pasien.", size=9.5, italic=True, color=MUTED, role="body")
s.footer("03")

# ===========================================================================
# 04 — the reported range
# ===========================================================================
s = Slide(deck, "s04_gap", "LATAR BELAKANG", "Angka laporan tersebar dari 2,8% sampai 40,2%",
          notes="Slide ini alasan kenapa artikel ini ditulis. Tunjuk ujung kiri dan ujung kanan "
                "garis. Selisihnya lebih dari empat belas kali lipat, dan itu terjadi pada "
                "penyakit yang sama. Penyebab utamanya bukan perbedaan anak, tetapi perbedaan "
                "cara menegakkan diagnosis. Dua tinjauan sebelumnya berhenti pada 2017 dan hanya "
                "melaporkan prevalensi.")
s.bg()
s.header("Selisihnya lebih dari empat belas kali lipat, pada penyakit yang sama.")
s.card("range_bg", M, BODY_TOP, W, 1.72)
s.txt("range_lab", M + 0.32, 2.40, 6.0, 0.22, "PREVALENSI YANG DILAPORKAN 116 STUDI", size=9.5,
      bold=True, color=MUTED, role="panel_text", spc=40)
s.bar("track", 1.60, 3.28, 10.20, 0.16, "#DCE9EB", radius=0.08, role="bar")
t = (13.5 - 2.8) / (40.2 - 2.8)
dot_x = round(1.60 + t * 10.20, 3)
s.bar("track_stem", round(dot_x - 0.011, 3), 3.00, 0.022, 0.24, TEAL, role="bar")
s.bar("track_dot", round(dot_x - 0.14, 3), 3.22, 0.28, 0.28, TEAL, radius=0.5, role="bar")
s.txt("track_lab", round(dot_x - 0.60, 3), 2.66, 3.40, 0.32, "13,5% (95% CI 12,0–15,1)", size=12,
      bold=True, color=TEAL, role="metric")
s.txt("r_lo", 1.52, 3.54, 0.90, 0.26, "2,8%", size=11, color=MUTED, role="panel_text")
s.txt("r_hi", 10.95, 3.54, 1.00, 0.26, "40,2%", size=11, color=MUTED, align="right",
      role="panel_text")
cards = [
    ("Definisi kasus belum seragam", "Kriteria diagnostik berbeda antar studi, sehingga angka "
                                     "sulit disandingkan meski penyakitnya sama.", "14× selisih"),
    ("Tinjauan sebelumnya berhenti 2017", "Dua tinjauan sebelumnya hanya melaporkan prevalensi, "
                                          "tanpa keparahan kasus.", "2017"),
    ("Keparahan hampir tak dilaporkan", "Keparahan, jumlah gigi yang terkena, dan HSPM hampir "
                                        "tidak pernah dilaporkan.", "3 luaran"),
]
for i, (x, w) in enumerate(cols(3)):
    head, body, tag = cards[i]
    s.card(f"g{i}_bg", x, 4.16, w, 2.00)
    s.bar(f"g{i}_tag", x + 0.30, 4.44, 0.62, 0.055, TEAL, role="bar")
    s.txt(f"g{i}_h", x + 0.30, 4.60, w - 0.60, h_for(head, w - 0.60, 12.5, pad=0.08), head,
          size=12.5, bold=True, color=INK, role="panel_text")
    s.txt(f"g{i}_t", x + 0.30, 5.05, w - 0.60, h_for(body, w - 0.60, 11, pad=0.08), body,
          size=11, color=TEXT, role="panel_text", ls=1.12)
    s.txt(f"g{i}_m", x + 0.30, 5.70, w - 0.60, 0.28, tag, size=10.5, bold=True, color=TEAL,
          role="panel_text")
s.bar("gap_band", M, 6.16, W, 0.50, MINT, radius=0.08, role="bar")
s.txt("gap_band_t", M + 0.30, 6.27, W - 0.60, 0.30,
      "Artikel ini menjawab dua hal sekaligus: memperbarui estimasi global dengan satu kriteria "
      "diagnostik, lalu mengukur keparahan kasusnya.", size=12, bold=True, color=TEAL,
      role="takeaway")
s.footer("04")

# ===========================================================================
# 05 — question and outcomes
# ===========================================================================
s = Slide(deck, "s05_tujuan", "TUJUAN", "Pertanyaan penelitian dan empat luaran",
          notes="PECO biasanya sudah dikenal peserta, jadi cukup dibaca cepat. Yang layak "
                "ditekankan adalah empat luaran di bawah: artikel ini tidak berhenti pada "
                "prevalensi, tetapi juga menghitung keparahan, jumlah gigi yang terkena, dan "
                "HSPM. Luaran sekunder inilah yang jarang disediakan tinjauan lain.")
s.bg()
s.header("Berapa prevalensi MIH pada anak dan remaja di seluruh dunia?", action_fill=INK,
         action_color=WHITE)
peco = [
    ("P", "POPULASI", "Anak dan remaja 0–19 tahun dengan gigi permanen muda."),
    ("E", "PAPARAN", "Pemeriksaan klinis MIH memakai kriteria EAPD 2003."),
    ("C", "PEMBANDING", "Tanpa kelompok pembanding; ini studi prevalensi."),
    ("O", "LUARAN", "Prevalensi, keparahan, gigi terkena, dan HSPM."),
]
for i, (x, w) in enumerate(cols(4, gap=0.22)):
    letter, label, body = peco[i]
    s.card(f"p{i}_bg", x, BODY_TOP, w, 1.78)
    s.txt(f"p{i}_v", x + 0.28, round(BODY_TOP + 0.24, 3), 0.90, 0.62, letter, size=34, bold=True,
          font=DISP, color=TEAL, role="metric")
    s.txt(f"p{i}_l", x + 1.30, round(BODY_TOP + 0.32, 3), w - 1.54, 0.24, label, size=9.5,
          bold=True, color=MUTED, role="panel_text", spc=40)
    s.txt(f"p{i}_t", x + 0.28, round(BODY_TOP + 0.98, 3), w - 0.56,
          h_for(body, w - 0.56, 11, pad=0.10), body, size=11, color=TEXT, role="panel_text",
          ls=1.12)
s.card("out_bg", M, 4.22, W, 2.44)
s.txt("out_lab", M + 0.32, 4.40, 8.0, 0.24, "EMPAT LUARAN YANG DILAPORKAN", size=9.5, bold=True,
      color=MUTED, role="panel_text", spc=40)
outcomes = ["Prevalensi global MIH",
            "Prevalensi kasus sedang sampai berat",
            "Jumlah molar pertama permanen yang terkena",
            "Kasus dengan insisivus terkena, dan prevalensi HSPM"]
for i, item in enumerate(outcomes):
    oy = round(4.78 + i * 0.44, 3)
    s.bar(f"o{i}_d", M + 0.34, oy + 0.05, 0.22, 0.22, TEAL, radius=0.5, role="bar")
    s.txt(f"o{i}_n", M + 0.34, round(oy + 0.055, 3), 0.22, 0.20, str(i + 1), size=9.5, bold=True,
          color=WHITE, align="center", role="metric")
    s.txt(f"o{i}_t", M + 0.74, oy, W - 1.10, 0.30, item, size=12, color=TEXT, role="panel_text")
s.footer("05")

# ===========================================================================
# 06 — how the evidence was collected
# ===========================================================================
s = Slide(deck, "s06_metode", "METODE · PENCARIAN", "Cara penulis mengumpulkan bukti",
          notes="Empat kartu ini menunjukkan urutan kerjanya. Protokol didaftarkan sebelum "
                "pencarian dimulai, itu penting untuk menepis tuduhan memilih hasil. Pencarian "
                "berhenti Juli 2021. Soal jumlah basis data, ada catatan kecil: PubMed dan "
                "MEDLINE disebut sebagai dua entri terpisah, dan EMBASE hanya muncul di strategi. "
                "Untuk replikasi, cek lampiran artikelnya.")
s.bg()
s.header("Protokol didaftarkan sebelum pencarian dimulai, dan pencarian berhenti Juli 2021.")
steps = [
    ("1", "Protokol", "PROSPERO CRD42021229435, didaftarkan sebelum pencarian."),
    ("2", "Pencarian", "Tujuh basis data: PubMed, MEDLINE, CENTRAL, Web of Science, SciELO, "
                       "LILACS, TRIP."),
    ("3", "Penyaringan", "Seleksi independen oleh dua peneliti, kesepakatan κ = 0,885."),
    ("4", "Analisis", "Model random-effects; heterogenitas I²; bias publikasi diuji dengan Egger."),
]
for i, (x, w) in enumerate(cols(4, gap=0.22)):
    n, head, body = steps[i]
    s.step_card(f"st{i}", x, BODY_TOP, w, 2.30, n, head, body)
s.card("q_bg", M, 4.74, W, 1.42)
s.txt("q_lab", M + 0.32, 4.90, 8.0, 0.24, "STRATEGI PENCARIAN", size=9.5, bold=True, color=MUTED,
      role="panel_text", spc=40)
q = ("(hypomineralization OR hypomineralisation OR hypomineralized OR hypoplasia OR demarcated "
     "OR opacities OR MIH OR cheese molars) AND (survey OR cross-sectional OR prevalence) AND "
     "(molar OR molars OR incisors)")
s.txt("q_t", M + 0.32, 5.22, W - 0.64, h_for(q, W - 0.64, 9.5, pad=0.10), q, size=9.5,
      font=MONO, color=INK, role="body", ls=1.15, source_ref="S1, strategi pencarian")
s.txt("q_note", M, 6.24, W, h_for(
    "PubMed dan MEDLINE disebut sebagai dua entri terpisah, sedangkan EMBASE hanya muncul di "
    "bagian strategi; untuk replikasi, cek lampiran artikelnya.", W, 9.5, pad=0.06),
      "PubMed dan MEDLINE disebut sebagai dua entri terpisah, sedangkan EMBASE hanya muncul di "
      "bagian strategi; untuk replikasi, cek lampiran artikelnya.", size=9.5, italic=True,
      color=MUTED, role="body")
s.footer("06")

# ===========================================================================
# 07 — inclusion and exclusion
# ===========================================================================
s = Slide(deck, "s07_penyaringan", "METODE · PENYARINGAN", "Aturan masuk dan keluar",
          notes="Bagian ini yang menentukan apakah hasilnya bisa dipercaya. Kriteria eksklusinya "
                "ketat: populasi khusus, molar sulung saja, dan sampel yang tidak representatif "
                "dikeluarkan. Efeknya, analisis utama hanya memuat 98 dari 116 studi. "
                "Konsekuensinya dibahas lagi di slide keterbatasan.")
s.bg()
s.header("Analisis utama hanya memuat 98 dari 116 studi, karena kriterianya ketat.")
s.card("in_bg", M, BODY_TOP, 5.93, 3.90, MINT)
s.txt("in_h", M + 0.34, round(BODY_TOP + 0.26, 3), 4.0, 0.44, "Masuk", size=20, bold=True,
      font=DISP, color=TEAL, role="panel_text")
s.bullets("in", M + 0.34, round(BODY_TOP + 0.92, 3), 5.25, [
    "Studi observasional yang melaporkan prevalensi MIH",
    "Definisi MIH jelas dan dapat ditelusuri",
    "Subjek tanpa kelainan sistemik",
    "Kedua jenis kelamin diikutsertakan",
], row_h=0.52)
s.card("ex_bg", 6.82, BODY_TOP, 5.93, 3.90, AMBERBG)
s.txt("ex_h", 6.82 + 0.34, round(BODY_TOP + 0.26, 3), 4.0, 0.44, "Keluar", size=20, bold=True,
      font=DISP, color=AMBER, role="panel_text")
s.bullets("ex", 6.82 + 0.34, round(BODY_TOP + 0.92, 3), 5.25, [
    "Populasi khusus, misalnya anak yang lahir prematur",
    "Studi yang hanya melaporkan molar sulung",
    "Sampel non-representatif: satu institusi atau kelompok profesi tertentu",
], row_h=0.52, dot=AMBER)
s.txt("ex_note", 6.82 + 0.34, 4.72, 5.25, h_for(
    "Efeknya, 18 dari 116 studi tidak masuk analisis utama.", 5.25, 11, pad=0.08),
      "Efeknya, 18 dari 116 studi tidak masuk analisis utama.", size=11, bold=True, color=AMBER,
      role="panel_text")
s.txt("base_t", M, 6.28, W, h_for(
    "Mutu tiap studi dinilai dengan Newcastle–Ottawa Scale, dan kepastian bukti dengan SORT.",
    W, 10, pad=0.06),
      "Mutu tiap studi dinilai dengan Newcastle–Ottawa Scale, dan kepastian bukti dengan SORT.",
      size=10, italic=True, color=MUTED, role="body")
s.footer("07")

# ===========================================================================
# 08 — selection results
# ===========================================================================
s = Slide(deck, "s08_hasil_seleksi", "HASIL · 1", "116 studi lolos, dan mutunya tinggi",
          notes="Tiga angka dulu, lalu grafiknya. Sebanyak 48 studi mendapat skor maksimum, dan "
                "hanya satu studi yang berkualitas sedang. Satu hal yang perlu disebut walau "
                "tidak enak: 48,7% studi punya kelemahan pada representativitas sampel, dan "
                "angka itu akan muncul lagi di slide penilaian kritis.")
s.bg()
s.header("Semua studi yang masuk analisis utama berskor NOS 7/9 atau lebih tinggi.")
s.card("nos_bg", M, BODY_TOP, 7.30, 3.60)
s.add_chart("nos_chart", {
    "chart_type": "col", "categories": ["9/9", "8/9", "7/9", "6/9"], "values": [48, 53, 6, 1],
    "series_name": "studi", "colors": [TEAL, TEAL, TEAL, AMBER], "data_labels": True,
    "label_format": "0", "font_size": 10.5, "gap_width": 52, "axis_labels": True,
    "show_value_axis": False}, M + 0.28, 2.46, 6.74, 2.80, source_ref="S1, Tabel 1")
s.txt("nos_cap", M + 0.28, 5.36, 6.74, 0.28,
      "Jumlah studi per skor Newcastle–Ottawa (9 = mutu tertinggi)", size=9.5, color=MUTED,
      role="body")
s.card("sel_bg", 8.12, BODY_TOP, 4.63, 3.60)
s.txt("sel_lab", 8.42, 2.44, 4.0, 0.24, "ANGKA KUNCI", size=9.5, bold=True, color=MUTED,
      role="panel_text", spc=40)
s.big_stat("v1", 8.42, 2.78, 4.03, "116", "studi dimasukkan", num_size=30)
s.big_stat("v2", 8.42, 3.72, 4.03, "133.734", "peserta pada analisis awal", num_size=30)
s.big_stat("v3", 8.42, 4.66, 4.03, "113.089", "peserta pada analisis utama, 98 studi", num_size=30)
s.bar("sel_band", M, 6.00, W, 0.66, AMBERBG, radius=0.08, role="bar")
s.txt("sel_band_t", M + 0.30, 6.18, W - 0.60, 0.32,
      "Yang perlu dicatat: 48,7% studi gagal pada butir representativitas sampel.", size=12,
      bold=True, color=AMBER, role="takeaway")
s.footer("08")

# ===========================================================================
# 09 — pooled prevalence
# ===========================================================================
s = Slide(deck, "s09_hasil_prevalensi", "HASIL · 2", "Prevalensi global 13,5%",
          notes="Slide inti. Baca angkanya lengkap dengan rentang kepercayaan dan jumlah "
                "peserta. Kalau ditanya soal I² yang 98%, jawab begini: variasi antar studi "
                "memang besar, jadi angka ini paling tepat dibaca sebagai gambaran beban "
                "populasi, bukan angka presisi untuk satu kota. Uji Egger dan leave-one-out "
                "ditampilkan untuk menunjukkan estimasi ini tidak bergantung pada satu studi.")
s.bg()
s.header("Rata-rata tertimbang dari 98 studi berkriteria EAPD 2003, mencakup 113.089 anak.")
s.card("dough_bg", M, BODY_TOP, 5.00, 3.40, MINT)
s.add_chart("dough_chart", {
    "chart_type": "doughnut", "categories": ["MIH", "Tanpa MIH"], "values": [13.5, 86.5],
    "series_name": "prevalensi", "colors": [TEAL, "#D5E5E8"], "data_labels": False,
    "font_size": 10, "axis_labels": False}, 0.98, 2.46, 4.20, 2.60)
s.txt("dough_c", 2.30, 3.50, 1.56, 0.42, "13,5%", size=22, bold=True, font=DISP, color=TEAL,
      align="center", role="metric")
s.txt("dough_l", 0.98, 5.16, 4.20, 0.30, "MIH pada 13,5% anak · tanpa MIH pada 86,5%", size=10,
      color=MUTED, align="center", role="body")
stats = [("98 studi", "memakai kriteria EAPD 2003"), ("133.734", "peserta pada analisis awal"),
         ("SORT A", "kepastian bukti")]
for i, (x, w) in enumerate(cols(3, gap=0.20, total=6.97, x0=5.78)):
    number, label = stats[i]
    s.card(f"k{i}_bg", x, BODY_TOP, w, 1.55)
    s.big_stat(f"k{i}", round(x + 0.26, 3), round(BODY_TOP + 0.20, 3), round(w - 0.52, 3),
               number, label, num_size=24)
s.card("sens_bg", 5.78, 3.99, 6.97, 1.65)
s.txt("sens_lab", 6.08, 4.14, 6.0, 0.24, "UJI KESTABILAN", size=9.5, bold=True, color=MUTED,
      role="panel_text", spc=40)
sens = [("I² = 98,0%", "variasi antar studi tinggi dan nyata"),
        ("Uji Egger", "p = 0,179, tanpa tanda bias publikasi"),
        ("Leave-one-out", "estimasi tetap stabil")]
for i, (head, note) in enumerate(sens):
    iy = round(4.50 + i * 0.36, 3)
    s.txt(f"s{i}_h", 6.08, iy, 1.85, 0.28, head, size=11, bold=True, color=INK, role="panel_text")
    s.txt(f"s{i}_n", 8.05, iy, 4.40, 0.28, note, size=10.5, color=MUTED, role="panel_text")
s.bar("prev_band", M, 5.84, W, 0.82, INK, radius=0.10, role="bar")
s.txt("prev_band_t", M + 0.34, 5.99, W - 0.68, 0.52,
      "Setara satu dari tujuh sampai delapan anak. Angka ini menggambarkan beban populasi, bukan "
      "presisi satu kota.", size=14, bold=True, color=WHITE, font=DISP, role="takeaway")
s.footer("09")

# ===========================================================================
# 10 — severity
# ===========================================================================
s = Slide(deck, "s10_hasil_keparahan", "HASIL · 3",
          "Lebih dari sepertiga kasus sudah sedang sampai berat",
          notes="Dua pesan klinis di slide ini. Pertama, 36,3% kasus sudah sedang sampai berat, "
                "artinya lebih dari sepertiga anak perlu perawatan restoratif yang nyata. Kedua, "
                "distribusi molarnya hampir merata, 18% sampai 27% di setiap jumlah gigi, jadi "
                "tidak ada pola tunggal yang bisa diprediksi. Soal angka insisivus, abstrak "
                "menulis 36,6% dan Tabel 2 menulis 38,7%; di deck ini dipakai angka tabel.")
s.bg()
s.header("Sebaran gigi yang terkena hampir merata, jadi tidak ada pola tunggal yang bisa "
         "diprediksi.")
s.card("sev_bg", M, BODY_TOP, 7.30, 3.40)
s.add_chart("sev_chart", {
    "chart_type": "bar", "categories": ["4 gigi · 27,4%", "3 gigi · 18,1%", "2 gigi · 26,7%",
                                        "1 gigi · 24,3%"],
    "values": [27.4, 18.1, 26.7, 24.3], "series_name": "persen kasus", "colors": [TEAL],
    "data_labels": False, "font_size": 10.5, "axis_labels": True,
    "show_value_axis": False}, M + 0.28, 2.46, 6.74, 2.58)
s.txt("sev_cap", M + 0.28, 5.14, 6.74, 0.28,
      "Jumlah molar pertama permanen yang terkena, dalam persen kasus", size=9.5, color=MUTED,
      role="body")
sev = [("36,3%", "sedang sampai berat", "95% CI 29,9–43,2 · 33 studi · I² = 95,2%", TEAL),
       ("38,7%", "insisivus terkena (Tabel 2)", "MIH tipe molar-insisivus; abstrak menulis 36,6%",
        TEAL),
       ("3,6%", "HSPM menyertai MIH", "95% CI 1,9–6,8 · hanya 7 studi", AMBER)]
for i, (number, label, note, color) in enumerate(sev):
    iy = round(2.20 + i * 1.20, 3)
    s.big_stat(f"sv{i}", 8.12, iy, 4.63, number, label, note, num_size=28, num_color=color)
s.bar("sev_band", M, 5.84, W, 0.82, MINT, radius=0.10, role="bar")
s.txt("sev_band_t", M + 0.34, 5.99, W - 0.68, 0.52,
      "36,3% kasus berarti lebih dari sepertiga anak perlu perawatan restoratif yang nyata.",
      size=14, bold=True, color=TEAL, font=DISP, role="takeaway")
s.footer("10")

# ===========================================================================
# 11 — regions and criteria
# ===========================================================================
s = Slide(deck, "s11_subanalisis", "SUB-ANALISIS", "Wilayah berbeda, kriteria lebih menentukan",
          notes="Dua temuan yang sifatnya beda. Selisih antar wilayah, Amerika 15,3% dan Asia "
                "10,7%, tidak bermakna secara statistik, dan urutan wilayahnya bergeser "
                "dibanding tinjauan 2018. Sebaliknya, pemakaian kriteria non-EAPD menghasilkan "
                "estimasi yang berbeda bermakna, p sama dengan 0,0061. Kalau presentasi ini "
                "memicu perdebatan, biarkan perdebatannya soal standardisasi diagnosis.")
s.bg()
s.header("Beda antar wilayah tidak bermakna; pemakaian kriteria non-EAPD bermakna, p = 0,0061.")
s.card("geo_bg", M, BODY_TOP, 7.30, 3.40)
s.txt("geo_lab", M + 0.28, 2.42, 6.0, 0.24, "PREVALENSI MENURUT WILAYAH", size=9.5, bold=True,
      color=MUTED, role="panel_text", spc=40)
s.add_chart("geo_chart", {
    "chart_type": "bar", "categories": ["Amerika · 15,3%", "Asia · 10,7%"],
    "values": [15.3, 10.7], "series_name": "persen", "colors": [TEAL, TEAL2],
    "data_labels": False, "font_size": 11, "axis_labels": True,
    "show_value_axis": False}, M + 0.28, 2.72, 6.74, 2.10)
s.txt("geo_cap", M + 0.28, 4.90, 6.74, h_for(
    "Amerika · 95% CI 12,8–18,3 · I² = 96,3%   |   Asia · 95% CI 8,5–13,5 · I² = 98,7%",
    6.74, 9.5, pad=0.08),
      "Amerika · 95% CI 12,8–18,3 · I² = 96,3%   |   Asia · 95% CI 8,5–13,5 · I² = 98,7%",
      size=9.5, color=MUTED, role="body")
s.card("crit_bg", 8.12, BODY_TOP, 4.63, 3.40, AMBERBG)
s.txt("crit_lab", 8.42, 2.46, 4.0, 0.24, "KRITERIA DIAGNOSTIK", size=9.5, bold=True, color=AMBER,
      role="panel_text", spc=40)
s.txt("crit_v", 8.42, 2.76, 4.03, 0.70, "p = 0,0061", size=30, bold=True, font=DISP, color=AMBER,
      role="metric")
s.txt("crit_t", 8.42, 3.56, 4.03, h_for(
    "Studi tanpa definisi kasus EAPD 2003 menghasilkan estimasi yang berbeda bermakna, umumnya "
    "lebih rendah.", 4.03, 10.5, pad=0.10),
      "Studi tanpa definisi kasus EAPD 2003 menghasilkan estimasi yang berbeda bermakna, umumnya "
      "lebih rendah.", size=10.5, color=TEXT, role="panel_text", ls=1.12)
s.rule("crit_rule", 8.42, 4.62, 4.03)
s.txt("crit_n", 8.42, 4.74, 4.03, 0.32, "Sub-analisis ini memuat 133.734 peserta.", size=10.5,
      color=MUTED, role="panel_text")
s.bar("reg_band", M, 5.84, W, 0.82, MINT, radius=0.10, role="bar")
s.txt("reg_t1", M + 0.34, 5.96, 5.60, 0.56,
      "Afrika yang dulu terendah tidak lagi di posisi itu; wilayah belum cukup menjelaskan "
      "variasi angka.", size=10.5, color=TEXT, role="panel_text", ls=1.12)
s.txt("reg_t2", 6.70, 5.96, 5.80, 0.56,
      "Ukuran sampel dan tahun publikasi hanya menyumbang sedikit pada variasi.", size=10.5,
      color=TEXT, role="panel_text", ls=1.12)
s.footer("11")

# ===========================================================================
# 12 — what explains the variation
# ===========================================================================
s = Slide(deck, "s12_diskusi", "DISKUSI · 1", "Yang menurut penulis menjelaskan variasi",
          notes="Bagian ini jawaban penulis atas pertanyaan kenapa angkanya berbeda-beda. Pesan "
                "utamanya: variasi wilayah lebih menjelaskan dibanding faktor metodologis yang "
                "mereka uji. Tiga kolom di bawah adalah alasannya.")
s.bg()
s.header("Variasi wilayah lebih menjelaskan perbedaan angka daripada faktor metodologis yang "
         "diuji lewat meta-regresi.", action_fill=INK, action_color=WHITE)
expl = [("Kriteria diagnostik", "Klasifikasi non-EAPD cenderung menurunkan estimasi prevalensi.",
         "p = 0,0061", TEAL),
        ("Beban perawatan", "Sepertiga anak dengan MIH perlu perawatan restoratif yang nyata.",
         "36,3% kasus", TEAL),
        ("Pelaporan yang belum lengkap", "Keparahan, gigi terkena, dan HSPM jarang dilaporkan.",
         "7–33 studi", AMBER)]
for i, (x, w) in enumerate(cols(3)):
    head, body, tag, accent = expl[i]
    s.card(f"e{i}_bg", x, BODY_TOP, w, 2.45)
    s.bar(f"e{i}_bar", x + 0.30, round(BODY_TOP + 0.30, 3), 0.62, 0.055, accent, role="bar")
    s.txt(f"e{i}_h", x + 0.30, round(BODY_TOP + 0.46, 3), w - 0.60,
          h_for(head, w - 0.60, 12.5, pad=0.08), head, size=12.5, bold=True, color=INK,
          role="panel_text")
    s.txt(f"e{i}_t", x + 0.30, round(BODY_TOP + 0.86, 3), w - 0.60,
          h_for(body, w - 0.60, 11, pad=0.08), body, size=11, color=TEXT, role="panel_text",
          ls=1.12)
    s.txt(f"e{i}_m", x + 0.30, round(BODY_TOP + 1.92, 3), w - 0.60, 0.28, tag, size=10.5,
          bold=True, color=accent, role="panel_text")
s.card("imp_bg", M, 4.89, W, 1.77, MINT)
s.txt("imp_lab", M + 0.32, 5.06, 8.0, 0.24, "IMPLIKASINYA", size=9.5, bold=True, color=TEAL,
      role="panel_text", spc=40)
s.txt("imp_t", M + 0.32, 5.36, W - 0.64, h_for(
    "Standardisasi kriteria diagnostik lebih mungkin mengubah angka daripada memperluas sampel.",
    W - 0.64, 13, pad=0.10),
      "Standardisasi kriteria diagnostik lebih mungkin mengubah angka daripada memperluas sampel.",
      size=13, bold=True, color=INK, role="takeaway")
s.txt("imp_n", M + 0.32, 5.82, W - 0.64, h_for(
    "Penulis meminta studi berikutnya melaporkan keparahan dan HSPM, tidak hanya prevalensi.",
    W - 0.64, 11, pad=0.08),
      "Penulis meminta studi berikutnya melaporkan keparahan dan HSPM, tidak hanya prevalensi.",
      size=11, color=TEXT, role="panel_text")
s.footer("12")

# ===========================================================================
# 13 — appraisal
# ===========================================================================
s = Slide(deck, "s13_appraisal", "DISKUSI · 2",
          "Yang kuat dan yang perlu dibaca hati-hati",
          notes="Bagian favorit di diskusi jurnal. Sampaikan kekuatannya dengan adil, lalu "
                "keterbatasannya tanpa melemahkan artikelnya. Catatan terakhir adalah temuan "
                "saya sendiri: angka insisivus berbeda antara abstrak dan tabel, dan penyebutan "
                "basis data tidak seragam.")
s.bg()
s.header("Kekuatan metodologisnya nyata, dan keterbatasannya perlu disebut apa adanya.")
s.card("pro_bg", M, BODY_TOP, 5.93, 4.42, MINT)
s.txt("pro_h", M + 0.34, round(BODY_TOP + 0.26, 3), 4.0, 0.44, "Yang kuat", size=20, bold=True,
      font=DISP, color=TEAL, role="panel_text")
s.bullets("pro", M + 0.34, round(BODY_TOP + 0.92, 3), 5.25, [
    "Protokol terdaftar sebelum pencarian dimulai, laporan mengikuti PRISMA",
    "Tujuh basis data, rentang tahun luas",
    "Penyaringan dan penilaian risiko bias oleh dua peneliti, κ = 0,885",
    "Semua studi analisis utama berkualitas tinggi, NOS 7/9 atau lebih",
    "Uji kestabilan lengkap: Egger, cumulative, leave-one-out",
    "Kriteria EAPD dibandingkan dengan definisi alternatif",
    "113.089 peserta dengan kepastian bukti SORT A",
], row_h=0.48)
s.card("con_bg", 6.82, BODY_TOP, 5.93, 4.42, AMBERBG)
s.txt("con_h", 6.82 + 0.34, round(BODY_TOP + 0.26, 3), 4.4, 0.44, "Perlu dibaca hati-hati",
      size=20, bold=True, font=DISP, color=AMBER, role="panel_text")
s.bullets("con", 6.82 + 0.34, round(BODY_TOP + 0.92, 3), 5.25, [
    "Heterogenitas tinggi, I² 93–98%, sehingga angka tunggal bukan angka pasti",
    "48,7% studi gagal pada representativitas sampel",
    "Dari 116 studi, hanya 98 masuk analisis utama",
    "Estimasi keparahan dan HSPM hanya dari 7 sampai 33 studi",
    "Faktor medis, sosiodemografis, dan lingkungan tidak bisa dianalisis",
    "Tanpa penilaian GRADE; kepastian bukti memakai SORT",
], row_h=0.48, dot=AMBER)
s.rule("cat_rule", 6.82 + 0.34, 5.78, 5.25, color="#E4CBA6")
s.txt("cat_n", 6.82 + 0.34, 5.88, 5.25, h_for(
    "Catatan pembaca: angka insisivus berbeda antara abstrak (36,6%) dan Tabel 2 (38,7%).",
    5.25, 9.5, pad=0.08),
      "Catatan pembaca: angka insisivus berbeda antara abstrak (36,6%) dan Tabel 2 (38,7%).",
      size=9.5, italic=True, color=MUTED, role="panel_text")
s.footer("13")

# ===========================================================================
# 14 — clinical steps
# ===========================================================================
s = Slide(deck, "s14_implikasi", "IMPLIKASI", "Langkah praktis di klinik",
          notes="Turunkan ke praktik. Dua langkah pertama bisa dikerjakan besok pagi: periksa "
                "molar pertama begitu erupsi, dan pakai kriteria EAPD supaya catatan kita bisa "
                "dibandingkan dengan literatur. Kalau audiensnya dari puskesmas atau program "
                "sekolah, bagian bawah slide ini yang paling relevan.")
s.bg()
s.header("Dua langkah pertama bisa dikerjakan besok: periksa lebih awal, dan pakai kriteria "
         "yang sama.")
steps = [
    ("1", "Periksa lebih awal", "Molar pertama permanen diperiksa begitu erupsi, sekitar usia 6 "
                               "sampai 8 tahun."),
    ("2", "Pakai kriteria EAPD", "Satu kriteria untuk semua pasien, disertai foto klinis, supaya "
                                 "catatan kita sebanding."),
    ("3", "Catat keparahan", "Keparahan dan jumlah molar yang terkena menentukan intensitas "
                             "recall."),
    ("4", "Tangani seminimal mungkin", "Desensitisasi, sealant pada molar berisiko, restorasi "
                                       "atau SSC bila enamel pecah. Hindari preparasi agresif."),
]
for i, (x, w) in enumerate(cols(4, gap=0.22)):
    n, head, body = steps[i]
    s.step_card(f"cx{i}", x, BODY_TOP, w, 2.60, n, head, body)
s.bar("school_band", M, 5.04, W, 1.62, INK, radius=0.10, role="bar")
s.txt("school_lab", M + 0.36, 5.22, 8.0, 0.24, "UNTUK PROGRAM SEKOLAH", size=9.5, bold=True,
      color=TEALSOFT, role="panel_text", spc=40)
s.txt("school_t", M + 0.36, 5.52, W - 0.72, h_for(
    "Angka 13% sampai 15% cukup tinggi untuk menjadikan pemeriksaan MIH bagian dari skrining "
    "rutin, bukan temuan yang kebetulan terlihat.", W - 0.72, 14, pad=0.12),
      "Angka 13% sampai 15% cukup tinggi untuk menjadikan pemeriksaan MIH bagian dari skrining "
      "rutin, bukan temuan yang kebetulan terlihat.", size=14, bold=True, color=WHITE, font=DISP,
      role="takeaway", ls=1.12)
s.footer("14")

# ===========================================================================
# 15 — conclusion
# ===========================================================================
s = Slide(deck, "s15_kesimpulan", "KESIMPULAN", "Tiga angka, satu pesan",
          notes="Tutup dengan tiga angka, lalu satu kalimat: MIH sering terlewat, dan pencatatan "
                "yang rapi membuat data klinik kita sebanding dengan literatur internasional. "
                "Dua pertanyaan untuk membuka diskusi: apakah angka di Indonesia mungkin berbeda, "
                "dan apakah kriteria EAPD bisa diterapkan di tempat kerja peserta sehari-hari?")
s.bg()
s.header("MIH sering terlewat, dan pencatatan yang rapi membuat data kita sebanding.")
concl = [("13,5%", "prevalensi global", "95% CI 12,0–15,1 · 113.089 anak · SORT A"),
         ("36,3%", "kasus sedang sampai berat", "artinya butuh perawatan, bukan hanya pemantauan"),
         ("3,6%", "HSPM menyertai MIH", "molar sulung juga perlu diperiksa")]
for i, (x, w) in enumerate(cols(3)):
    number, label, note = concl[i]
    s.card(f"z{i}_bg", x, BODY_TOP, w, 2.50, MINT)
    s.big_stat(f"z{i}", round(x + 0.30, 3), round(BODY_TOP + 0.28, 3), round(w - 0.60, 3),
               number, label, note, num_size=46)
s.card("ref_bg", M, 4.94, W, 1.72)
s.txt("ref_lab", M + 0.32, 5.10, 8.0, 0.24, "SUMBER", size=9.5, bold=True, color=MUTED,
      role="panel_text", spc=40)
refs = ["Lopes LB, dkk. Sci Rep. 2021;11:22405. doi:10.1038/s41598-021-01541-7 (artikel utama)",
        "Weerheijm KL, dkk. Eur J Paediatr Dent. 2003;4:110–113 (kriteria EAPD)",
        "Schwendicke F, dkk. J Dent. 2018;68:10–18 · pembanding tinjauan sebelumnya (13,1%)",
        "Zhao D, dkk. Int J Paediatr Dent. 2018;28:170–179 · pembanding tinjauan (14,2%)"]
for i, ref in enumerate(refs):
    s.txt(f"ref{i}", M + 0.32, round(5.38 + i * 0.30, 3), W - 0.64, 0.26, ref, size=9,
          color=TEXT, role="body")
s.footer("15")

# ===========================================================================
# summary + self-check + write
# ===========================================================================
slides = [s.spec() for s in deck.slides]
total_objects = sum(len(s["layout_tree"]["objects"]) for s in slides)

for slide in slides:
    declared = slide["layout_tree"]["objects"]
    if "title" not in declared:
        raise SystemExit(f"slide {slide['id']} has no title object")
    for oid in slide["accessibility"]["reading_order"]:
        if oid not in declared:
            raise SystemExit(f"slide {slide['id']}: reading order id {oid} missing")
    for oid, o in declared.items():
        if o["kind"] != "text":
            continue
        b, size = o["bbox"], float(o["style"]["font_size"])
        needed = est_lines(o["content"]["text"], b["width"], size) * (size * 1.22 / 72) + 0.04
        if needed > b["height"] + 0.06:
            raise SystemExit(f"slide {slide['id']}/{oid}: needs {needed:.2f}in, box {b['height']}in")
        if o["classification"] == "content" and o["role"] != "footer" and size < 9:
            raise SystemExit(f"slide {slide['id']}/{oid}: {size}pt below the 9pt floor")

spec = {
    "summary": {
        "deck_title": "Prevalensi MIH pada Anak dan Remaja (Lopes dkk., 2021)",
        "audience": "Mahasiswa dan dokter gigi pada diskusi jurnal kedokteran gigi anak",
        "decision": "Menilai besaran beban MIH dan menetapkan langkah skrining serta tatalaksana",
        "language": "id-ID",
        "narrative_framework": "custom, struktur pembacaan jurnal; setiap slide memuat satu gagasan "
                               "dengan banner inti di bawah judul",
        "slide_count": len(slides),
        "layout_policy": {"safe_margin": M, "content_bottom": CONTENT_BOTTOM,
                          "footer_top": FOOT_RULE_Y, "minimum_gap": 0.12},
        "design_context": {
            "profile": "klinis terang: kertas putih, panel terisi warna, chip bagian, angka besar",
            "typography": {"display": "Cambria (judul, angka besar)", "body": "Calibri",
                           "mono": "Consolas (kutipan pencarian)",
                           "cover_pt": 31, "title_pt": 27, "metric_pt": "20–62",
                           "body_pt": "10–15", "footer_pt": 9},
            "palette": {"surface": PAPER, "panel": PANEL, "mint": MINT, "ink": INK,
                        "accent": TEAL, "accent_bright": TEAL2, "warning": AMBER,
                        "warning_bg": AMBERBG, "cream": CREAM, "hairline": LINE},
            "composition": "master grid tetap (chip bagian, judul, banner inti, isi, rel footer) "
                           "dengan badan yang beragam: rel angka bergaris, kartu langkah bernomor, "
                           "papan kriteria, grafik kolom, donat, dua grafik batang, dan ilustrasi "
                           "molar berwarna",
            "viz": "grafik native PowerPoint: kolom (sebaran NOS), donat (proporsi 13,5%), "
                   "batang mendatar (gigi terkena, wilayah)",
            "assets": "dua ilustrasi hasil generasi di folder assets/ (tekstur email untuk sampul, "
                      "potongan molar berlesi), ditanam sebagai gambar biasa sehingga bisa diganti",
            "evidence": "Noi1r/powerpoint-skill (aturan deck akademik, tanpa garis dekoratif di "
                        "bawah judul), microsoft/dstoolkit-DiscoveryEnvisioning (tema read-only), "
                        "kpi-dashboard-design, visual-design-foundations, avoid-ai-writing",
        },
        "accessibility": {"presentation_title": "Prevalensi MIH pada Anak dan Remaja",
                          "language": "id-ID", "min_text_pt": 9,
                          "notes": "catatan pemateri di setiap slide memuat detail yang tidak "
                                   "ditulis di slide"},
        "sources": [
            {"id": "S1", "citation": "Lopes LB, Machado V, Mascarenhas P, Mendes JJ, Botelho J. "
                                     "The prevalence of molar-incisor hypomineralization: a "
                                     "systematic review and meta-analysis. Sci Rep. 2021;11:22405.",
             "doi": "10.1038/s41598-021-01541-7", "pmcid": "PMC8599453", "license": "CC BY 4.0",
             "role": "artikel utama, seluruh angka di deck"},
            {"id": "S2", "citation": "Weerheijm KL, dkk. Judgement criteria for molar incisor "
                                     "hypomineralisation in epidemiologic studies. Eur J Paediatr "
                                     "Dent. 2003;4:110–113.", "role": "kriteria EAPD, dikutip dalam S1"},
            {"id": "S3", "citation": "Schwendicke F, dkk. Global burden of molar incisor "
                                     "hypomineralization. J Dent. 2018;68:10–18.",
             "role": "pembanding tinjauan sebelumnya (13,1%)"},
            {"id": "S4", "citation": "Zhao D, dkk. The prevalence of molar incisor "
                                     "hypomineralization: evidence from 70 studies. Int J Paediatr "
                                     "Dent. 2018;28:170–179.",
             "role": "pembanding tinjauan sebelumnya (14,2%)"},
        ],
    },
    "slides": slides,
}

OUT.write_text(json.dumps(spec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"spec.json written: {len(slides)} slides, {total_objects} objects")
