#!/usr/bin/env python3
"""Membangun ssc-pedodonsia.pptx sebagai cadangan statis dari deck HTML.

Deck HTML adalah versi utama karena interaktivitas (langkah bertahap, pop-up,
tab, kasus bercabang, kuis) tidak dapat dibuat andal lewat python-pptx.
PowerPoint di sini memuat hyperlink agenda dan catatan pembicara.
"""
import re
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn

INK = RGBColor(0x15, 0x32, 0x3A)
INK2 = RGBColor(0x47, 0x64, 0x6C)
MUTED = RGBColor(0x7D, 0x8F, 0x93)
PAPER = RGBColor(0xFB, 0xF7, 0xEF)
CARD = RGBColor(0xFF, 0xFD, 0xF8)
LINE = RGBColor(0xE3, 0xD9, 0xC8)
ACCENT = RGBColor(0xC6, 0x5B, 0x45)
TEAL = RGBColor(0x2C, 0x6E, 0x6A)
GOLD = RGBColor(0xBD, 0x94, 0x40)
PALE = RGBColor(0xF7, 0xF0, 0xE0)

SERIF = "Georgia"
SANS = "Calibri"
W, H = 13.333, 7.5
M = 0.62


def add_bg(slide):
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(W), Inches(H))
    bg.fill.solid()
    bg.fill.fore_color.rgb = PAPER
    bg.line.fill.background()
    bg.shadow.inherit = False
    # garis aksen tipis di kiri
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(0.09), Inches(H))
    bar.fill.solid()
    bar.fill.fore_color.rgb = ACCENT
    bar.line.fill.background()
    bar.shadow.inherit = False


def set_spc(run, value):
    rPr = run._r.get_or_add_rPr()
    rPr.set("spc", str(int(value)))


def tx(slide, x, y, w, h, text, size=14, font=SANS, color=INK2, bold=False,
       align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, spacing=1.12, spc=0,
       italic=False, margins=(0, 0, 0, 0)):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left, tf.margin_right, tf.margin_top, tf.margin_bottom = [Inches(m) for m in margins]
    tf.vertical_anchor = anchor
    tf.clear()
    for i, line in enumerate(str(text).split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = spacing
        p.space_after = Pt(0)
        r = p.add_run()
        r.text = line
        r.font.size = Pt(size)
        r.font.name = font
        r.font.bold = bold
        r.font.italic = italic
        r.font.color.rgb = color
        if spc:
            set_spc(r, spc)
    return tb


def card(slide, x, y, w, h, fill=CARD, line=LINE, radius=0.09, line_w=1.0):
    sh = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.adjustments[0] = radius
    sh.fill.solid()
    sh.fill.fore_color.rgb = fill
    if line is None:
        sh.line.fill.background()
    else:
        sh.line.color.rgb = line
        sh.line.width = Pt(line_w)
    sh.shadow.inherit = False
    return sh


def rule(slide, x, y, w, color=LINE, weight=0.75):
    ln = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Pt(weight))
    ln.fill.solid()
    ln.fill.fore_color.rgb = color
    ln.line.fill.background()
    ln.shadow.inherit = False
    return ln


def header(slide, kicker, title, page, title_size=30):
    tx(slide, M, 0.40, 10.5, 0.24, kicker.upper(), size=9.5, color=ACCENT, bold=True, spc=180)
    tx(slide, M, 0.66, 11.6, 1.05, title, size=title_size, font=SERIF, color=INK, bold=False, spacing=1.03)
    tx(slide, 12.35, 0.42, 0.45, 0.22, str(page), size=8.5, color=MUTED, align=PP_ALIGN.RIGHT)
    # tombol agenda
    b = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(11.55), Inches(0.34), Inches(0.78), Inches(0.30))
    b.adjustments[0] = 0.5
    b.fill.background()
    b.line.color.rgb = LINE
    b.line.width = Pt(0.75)
    b.shadow.inherit = False
    tf = b.text_frame
    tf.margin_left = tf.margin_right = 0
    tf.margin_top = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = "Agenda"
    r.font.size = Pt(8)
    r.font.name = SANS
    r.font.color.rgb = INK2
    return b


def footer(slide, cite):
    rule(slide, M, 6.86, W - 2 * M)
    tx(slide, M, 6.95, 10.6, 0.32, cite, size=8, color=MUTED)
    tx(slide, 11.3, 6.95, 1.4, 0.32, "IIK Bhaktiwiyata", size=8, color=MUTED, align=PP_ALIGN.RIGHT)


def placeholder(slide, x, y, w, h, title, sub):
    sh = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.adjustments[0] = 0.08
    sh.fill.solid()
    sh.fill.fore_color.rgb = RGBColor(0xF6, 0xEF, 0xE2)
    sh.line.color.rgb = RGBColor(0xC9, 0xB9, 0xA1)
    sh.line.width = Pt(1)
    sh.line.dash_style = 4  # dash
    sh.shadow.inherit = False
    tx(slide, x + 0.1, y + h / 2 - 0.32, w - 0.2, 0.28, title, size=10.5, color=RGBColor(0x6F, 0x62, 0x4E),
       bold=True, align=PP_ALIGN.CENTER)
    tx(slide, x + 0.12, y + h / 2 - 0.02, w - 0.24, 0.5, sub, size=8.5, color=RGBColor(0x8A, 0x7A, 0x62),
       align=PP_ALIGN.CENTER)


def notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text


def stat(slide, x, y, w, value, unit, label, source):
    card(slide, x, y, w, 1.28)
    tx(slide, x + 0.18, y + 0.13, w - 0.3, 0.52, value, size=30, font=SERIF, color=INK, bold=False)
    if unit:
        tx(slide, x + 0.18 + len(value) * 0.145, y + 0.31, 0.5, 0.28, unit, size=12, color=INK2)
    tx(slide, x + 0.18, y + 0.66, w - 0.34, 0.42, label, size=10.5, color=INK2)
    tx(slide, x + 0.18, y + 1.03, w - 0.34, 0.2, source, size=8, color=MUTED)


def bars(slide, x, y, w, h, data, vmax=100, color=TEAL, label_w=1.0, unit="%"):
    """Bar horizontal sederhana, data = [(label, value)]."""
    n = len(data)
    row = min(0.34, h / max(n, 1))
    for i, (lab, val) in enumerate(data):
        yy = y + i * row
        tx(slide, x, yy, label_w, row, lab, size=9.5, color=INK2, anchor=MSO_ANCHOR.MIDDLE)
        track = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x + label_w), Inches(yy + row * 0.28),
                                       Inches(w - label_w - 0.75), Inches(row * 0.4))
        track.adjustments[0] = 0.5
        track.fill.solid()
        track.fill.fore_color.rgb = RGBColor(0xEE, 0xE3, 0xD2)
        track.line.fill.background()
        track.shadow.inherit = False
        bw = max(0.04, (w - label_w - 0.75) * val / vmax)
        b = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x + label_w), Inches(yy + row * 0.28),
                                   Inches(bw), Inches(row * 0.4))
        b.adjustments[0] = 0.5
        b.fill.solid()
        b.fill.fore_color.rgb = color
        b.line.fill.background()
        b.shadow.inherit = False
        txt = ("%.2f" % val).rstrip("0").rstrip(".") if val % 1 else str(int(val))
        tx(slide, x + label_w + bw - 0.02, yy, 0.72, row, txt + unit, size=9.5, color=INK, bold=True,
           anchor=MSO_ANCHOR.MIDDLE)


def crown_shape(slide, x, y, scale=1.0):
    pts = [(0.00, 0.95), (0.00, 0.30), (0.13, 0.10), (0.32, 0.16), (0.46, 0.02),
           (0.62, 0.16), (0.80, 0.02), (0.96, 0.16), (1.16, 0.10), (1.30, 0.30),
           (1.30, 0.95), (1.22, 1.03), (1.10, 0.98), (1.10, 1.13), (0.96, 1.13),
           (0.96, 0.98), (0.34, 0.98), (0.34, 1.13), (0.20, 1.13), (0.20, 0.98),
           (0.08, 1.03)]
    fb = slide.shapes.build_freeform(Inches(x), Inches(y), scale=1.0)
    fb.add_line_segments([(Inches(x + px * scale), Inches(y + py * scale)) for px, py in pts[1:]], close=True)
    shp = fb.convert_to_shape()
    shp.fill.solid()
    shp.fill.fore_color.rgb = RGBColor(0xF6, 0xDF, 0xD7)
    shp.line.color.rgb = INK
    shp.line.width = Pt(2.0)
    shp.shadow.inherit = False
    return shp


def new_deck():
    prs = Presentation()
    prs.slide_width = Inches(W)
    prs.slide_height = Inches(H)
    return prs


def blank(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(s)
    return s


def build(path, notes_map):
    prs = new_deck()
    slides = []
    agenda_links = []

    # 1 COVER
    s = blank(prs); slides.append(s)
    tx(s, M, 0.95, 7.0, 0.25, "IIK BHAKTIWIYATA  ·  PROGRAM STUDI KEDOKTERAN GIGI", size=9.5,
       color=TEAL, bold=True, spc=200)
    rule(s, M, 1.32, 0.9, ACCENT, 2.5)
    tx(s, M, 1.55, 8.1, 2.1, "Stainless steel crown pada gigi desidui dan gigi permanen muda",
       size=38, font=SERIF, color=INK, spacing=1.02)
    tx(s, M, 3.72, 7.4, 0.75, "Indikasi, preparasi, Hall Technique, dan bukti klinis dalam sepuluh menit",
       size=15, color=INK2)
    for i, (label, w) in enumerate([("10 menit", 1.05), ("Pemateri: [nama]", 1.75), ("[tanggal]", 1.1)]):
        x = M + sum([1.05, 1.75, 1.1][:i]) + 0.12 * i
        b = card(s, x, 4.62, w, 0.34, fill=RGBColor(0xFD, 0xF1, 0xEC), line=RGBColor(0xE7, 0xC3, 0xB8), radius=0.5)
        tx(s, x, 4.66, w, 0.26, label, size=9.5, color=RGBColor(0xA3, 0x46, 0x2F), align=PP_ALIGN.CENTER)
    tx(s, M, 5.18, 7.2, 0.5, "Materi edukasi. Bukan pengganti pertimbangan klinis pada pasien tertentu.",
       size=9.5, color=MUTED)
    crown_shape(s, 9.55, 1.25, 2.05)
    tx(s, 9.9, 4.1, 3.0, 0.3, "SSC: coverage koronal penuh", size=9.5, color=MUTED, align=PP_ALIGN.CENTER)
    footer(s, "Sumber angka dan sitasi ada di tiap slide serta di research_notes.md")
    notes(s, notes_map[0])

    # 2 AGENDA
    s = blank(prs); slides.append(s)
    header(s, "Agenda", "Sembilan bagian, sepuluh menit", 2)
    items = [("1", "Restorasi yang gagal berulang", "0:45", 2),
             ("2", "Mengapa SSC", "0:45", 3),
             ("3", "Indikasi dan batas", "1:00", 4),
             ("4", "Gigi desidui dan preparasi", "0:45", 5),
             ("5", "Sepuluh langkah konvensional", "1:45", 6),
             ("6", "Hall Technique", "1:00", 7),
             ("7", "Perbandingan dan penyulit", "1:00", 8),
             ("8", "Bukti dan alternatif", "1:30", 10),
             ("9", "Kasus, kuis, penutup", "0:45", 12)]
    for i, (n, label, dur, target) in enumerate(items):
        col = 0 if i < 5 else 1
        row = i if i < 5 else i - 5
        x = M + col * 6.1
        y = 1.85 + row * 0.86
        b = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(5.75), Inches(0.74))
        b.fill.background()
        b.line.fill.background()
        agenda_links.append((b, target))
        tx(s, x, y + 0.06, 0.4, 0.4, n, size=17, font=SERIF, color=ACCENT)
        tx(s, x + 0.42, y + 0.06, 4.3, 0.4, label, size=13.5, color=INK)
        tx(s, x + 4.7, y + 0.08, 0.9, 0.3, dur, size=9, color=MUTED, align=PP_ALIGN.RIGHT)
        rule(s, x, y + 0.72, 5.75)
    tx(s, M, 6.25, 11.5, 0.6, "Klik bagian mana pun untuk melompat. Tombol Agenda di kanan atas mengembalikan ke halaman ini. Bagian kasus dan kuis dapat dilewati bila waktu tersisa kurang dari dua menit.",
       size=9, color=MUTED)
    footer(s, "Total 9 menit 15 detik konten, sekitar 10 menit dengan perpindahan")
    notes(s, notes_map[1])

    # 3 PROBLEM
    s = blank(prs); slides.append(s)
    header(s, "Masalah klinis", "Tambalan berulang gagal pada gigi yang sama", 3)
    fails = [("Tambalan pertama", "Tepi terbuka, karies kembali"),
             ("Tambalan kedua", "Karies sekunder"),
             ("Tambalan ketiga", "Nyeri, pulpa terlibat")]
    for i, (a, b) in enumerate(fails):
        y = 1.95 + i * 1.05
        card(s, M, y, 5.9, 0.86)
        dot = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(M + 0.28), Inches(y + 0.36), Inches(0.13), Inches(0.13))
        dot.fill.solid(); dot.fill.fore_color.rgb = ACCENT; dot.line.fill.background(); dot.shadow.inherit = False
        tx(s, M + 0.58, y + 0.14, 2.1, 0.3, a, size=13, color=INK, bold=True)
        tx(s, M + 0.58, y + 0.45, 4.9, 0.3, b, size=11.5, color=INK2)
    tx(s, M, 5.25, 5.6, 0.3, "Kasus ilustratif, bukan data penelitian.", size=8.5, color=MUTED)
    tx(s, 6.95, 1.75, 5.7, 1.3, "Setiap pengulangan menghilangkan lebih banyak dentin.", size=25, font=SERIF, color=INK, spacing=1.05)
    tx(s, 6.95, 3.25, 5.55, 1.2, "Enamel gigi desidui sekitar 1 mm, dentin tipis, tanduk pulpa tinggi. Kapan berhenti menambal dan menutup seluruh gigi?",
       size=13, color=INK2)
    b = card(s, 6.95, 4.68, 3.85, 0.44, fill=RGBColor(0xEE, 0xF6, 0xF4), line=RGBColor(0xBC, 0xD4, 0xD0), radius=0.5)
    tx(s, 7.05, 4.76, 3.7, 0.3, "Karies usia 5–6 tahun: 93%", size=10, color=RGBColor(0x22, 0x60, 0x5C))
    footer(s, "Kindelan 2008 · AAPD 2025 · Cochrane 2015 · Innes 2011 · Riskesdas 2018")
    notes(s, notes_map[2])

    # 4 WHY
    s = blank(prs); slides.append(s)
    header(s, "Prinsip", "SSC menutup seluruh mahkota dan tidak bergantung pada dinding yang tersisa", 4, 28)
    stat(s, M, 1.95, 3.85, "96,1%", "", "success SSC pada 12 bulan, 31 studi", "Chisini 2018 · SR/MA, I")
    stat(s, M + 4.12, 1.95, 3.85, "0,18", "", "RR kegagalan mayor vs tambalan (95% CI 0,06–0,56)", "Cochrane 2015 · I")
    stat(s, M + 8.24, 1.95, 3.85, "92%", "", "success Hall vs 52% kontrol pada 60 bulan", "Innes 2011 · RCT, II")
    cards = [("Menutup seluruh korona", "Tidak ada tepi restorasi."),
             ("Tahan fraktur", "Logam menahan gaya oklusal pada dinding tipis."),
             ("Lebih sedikit pengulangan", "Biaya awal lebih tinggi, retreatment lebih rendah.")]
    for i, (a, b) in enumerate(cards):
        x = M + i * 4.12
        card(s, x, 3.55, 3.85, 1.28)
        tx(s, x + 0.2, 3.72, 3.45, 0.3, a, size=12, color=INK, bold=True)
        tx(s, x + 0.2, 4.06, 3.45, 0.62, b, size=10.5, color=INK2)
    tx(s, M, 5.15, 11.8, 0.7, "Retensi berasal dari undercut servikal dan adaptasi margin. Semen membantu seal, bukan menggantikan adaptasi.",
       size=12, color=INK2)
    footer(s, "Chisini 2018 · Innes 2015 Cochrane · Innes 2011 · AAPD 2025")
    notes(s, notes_map[3])

    # 5 INDICATION
    s = blank(prs); slides.append(s)
    header(s, "Seleksi kasus", "SSC dipilih saat karies melewati line angle atau pulpa sudah diterapi", 5, 28)
    card(s, M, 1.9, 6.2, 2.2)
    tx(s, M + 0.22, 2.03, 5.7, 0.3, "Pilih SSC", size=12, color=ACCENT, bold=True)
    tx(s, M + 0.22, 2.38, 5.75, 1.6,
       "•  Lebih dari 2 permukaan, atau melewati line angle\n"
       "•  Setelah pulpotomi atau pulpektomi\n"
       "•  Hipoplasia, MIH, fraktur, atrisi\n"
       "•  Abutment space maintainer, risiko karies tinggi", size=10.5, color=INK2, spacing=1.2)
    card(s, M, 4.25, 6.2, 1.55)
    tx(s, M + 0.22, 4.38, 5.7, 0.3, "Batas dan kontraindikasi", size=12, color=TEAL, bold=True)
    tx(s, M + 0.22, 4.72, 5.75, 1.0,
       "•  Lebih dari setengah akar teresorpsi, alergi nikel\n"
       "•  Gigi tidak restorable\n"
       "•  Hall: nyeri spontan, abses, fistula, tanpa dentine bridge", size=10.5, color=INK2, spacing=1.2)
    # alur keputusan sederhana
    tx(s, 7.35, 1.86, 5.0, 0.3, "ALUR KEPUTUSAN", size=8.5, color=ACCENT, bold=True, spc=80)
    bands = [
        ("Karies luas, lebih dari 2 permukaan, atau melewati line angle?", CARD, LINE, INK),
        ("Tanda pulpa ireversibel?  Ya: pulpotomi atau pulpektomi, lalu SSC konvensional.", PALE, RGBColor(0xDD, 0xC9, 0xA4), INK),
        ("Tidak: Hall bila dentine bridge jelas, atau SSC konvensional.", RGBColor(0xEE, 0xF6, 0xF4), RGBColor(0xBC, 0xD4, 0xD0), INK),
        ("Bukan kandidat SSC: gigi tidak restorable, akar teresorpsi, alergi nikel.", CARD, LINE, INK),
    ]
    ys5 = [2.2, 3.05, 3.9, 4.75]
    for (label, fill, ln, col), y in zip(bands, ys5):
        card(s, 7.35, y, 5.35, 0.68, fill=fill, line=ln)
        tx(s, 7.48, y + 0.1, 5.1, 0.5, label, size=8.4, color=col, spacing=1.05)
        if y < 4.7:
            ar = s.shapes.add_shape(MSO_SHAPE.DOWN_ARROW, Inches(9.92), Inches(y + 0.7), Inches(0.18), Inches(0.14))
            ar.fill.solid(); ar.fill.fore_color.rgb = RGBColor(0x8F, 0xA3, 0xA0)
            ar.line.fill.background(); ar.shadow.inherit = False
    footer(s, "Kindelan 2008 · AAPD 2025 · SDCEP 2025 · Hall Technique Guide 2015")
    notes(s, notes_map[4])

    # 6 PREP
    s = blank(prs); slides.append(s)
    header(s, "Anatomi dan preparasi", "Bentuk gigi desidui menentukan arah preparasi", 6, 28)
    rules = [("Retensi ada di servikal", "Undercut di bawah bulbositas menahan crown."),
             ("Bukal dan lingual tidak rutin", "Hanya bila kontur menghalangi seating."),
             ("Enamel 1 mm", "Reduksi oklusal 1,0–1,5 mm, atau 1,5–2,0 mm menurut sumber lain."),
             ("Kontak harus putus", "Probe melewati kontak mesial dan distal.")]
    for i, (a, b) in enumerate(rules):
        y = 1.95 + i * 1.12
        card(s, M, y, 5.95, 0.98)
        tx(s, M + 0.2, y + 0.12, 5.5, 0.3, a, size=12.5, color=INK, bold=True)
        tx(s, M + 0.2, y + 0.44, 5.55, 0.5, b, size=10, color=INK2)
    # skema sederhana
    card(s, 6.95, 1.9, 5.75, 4.4, fill=RGBColor(0xFD, 0xFA, 0xF4))
    tooth = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.55), Inches(2.55), Inches(2.5), Inches(2.9))
    tooth.adjustments[0] = 0.16
    tooth.fill.solid(); tooth.fill.fore_color.rgb = RGBColor(0xFA, 0xF1, 0xDE)
    tooth.line.color.rgb = RGBColor(0xD8, 0xC6, 0xA8); tooth.line.width = Pt(1.2); tooth.shadow.inherit = False
    prep = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.78), Inches(2.85), Inches(2.04), Inches(2.3))
    prep.adjustments[0] = 0.16
    prep.fill.solid(); prep.fill.fore_color.rgb = RGBColor(0xF3, 0xCD, 0xC1)
    prep.line.color.rgb = ACCENT; prep.line.width = Pt(1.4); prep.line.dash_style = 4; prep.shadow.inherit = False
    crown_shape(s, 8.76, 2.2, 1.6)
    tx(s, 6.98, 2.42, 1.5, 0.5, "1,0–1,5 mm\nreduksi oklusal", size=8.5, color=INK)
    tx(s, 6.98, 4.2, 1.45, 0.5, "bulbositas\nservikal", size=8.5, color=INK)
    tx(s, 10.82, 4.55, 1.7, 0.5, "margin 1 mm\nsubgingiva", size=8.5, color=INK)
    tx(s, 10.82, 3.9, 1.7, 0.5, "feather edge,\ntanpa ledge", size=8.5, color=INK)
    tx(s, 6.98, 5.9, 5.0, 0.3, "Skema: garis putus-putus adalah permukaan setelah preparasi.", size=8, color=MUTED)
    footer(s, "Kindelan 2008 · Randall 2002 · Amlani & Brizuela 2023")
    notes(s, notes_map[5])

    # 7 STEPS
    s = blank(prs); slides.append(s)
    header(s, "SSC konvensional", "Sepuluh langkah, satu per satu", 7, 28)
    step_names = [
        ("1", "Anestesi dan isolasi"), ("2", "Ukur dan pilih ukuran"),
        ("3", "Ekskavasi dan pulp therapy"), ("4", "Reduksi oklusal"),
        ("5", "Reduksi proksimal"), ("6", "Haluskan line angle"),
        ("7", "Try-in"), ("8", "Trim, crimp, contour"),
        ("9", "Sementasi"), ("10", "Cek akhir dan instruksi")]
    for i, (n, name) in enumerate(step_names):
        col = 0 if i < 5 else 1
        row = i if i < 5 else i - 5
        x = M + col * 6.05
        y = 1.95 + row * 0.82
        card(s, x, y, 5.7, 0.7)
        tx(s, x + 0.2, y + 0.16, 0.42, 0.36, n, size=14, color=ACCENT, bold=True)
        tx(s, x + 0.6, y + 0.18, 4.9, 0.34, name, size=12, color=INK)
    tx(s, M, 6.15, 11.9, 0.4, "Rincian tujuan, cara, instrumen, kesalahan, dan tanda benar ada di versi HTML dan protokol_klinis.md.",
       size=9, color=MUTED)
    footer(s, "Kindelan 2008 · Randall 2002 · AAPD VPT 2024 · AAPD 2023 anestesi")
    notes(s, notes_map[6])

    # 8 HALL
    s = blank(prs); slides.append(s)
    header(s, "Hall Technique", "Hall menutup karies tanpa anestesi dan tanpa preparasi", 8, 28)
    hall_steps = [("1", "Nilai dan radiograf", "Vital, dentine bridge jelas. Karies tidak dibuang."),
                  ("2", "Separator bila kontak ketat", "Mesial dan distal, 3–5 hari."),
                  ("3", "Pilih crown", "Terkecil, menutup seluruh gigi, spring-back."),
                  ("4", "Isi semen dua pertiga", "GIC atau RMGIC, semua dinding terlapisi."),
                  ("5", "Seating dan bite", "Lindungi airway, gigit 2–3 menit.")]
    for i, (n, a, b) in enumerate(hall_steps):
        y = 1.9 + i * 0.9
        tx(s, M, y, 0.4, 0.35, n, size=15, font=SERIF, color=ACCENT)
        tx(s, M + 0.38, y, 5.5, 0.3, a, size=12.5, color=INK, bold=True)
        tx(s, M + 0.38, y + 0.32, 5.5, 0.4, b, size=9.8, color=INK2)
        rule(s, M, y + 0.82, 5.9)
    card(s, M, 6.05, 5.9, 0.62, fill=PALE, line=RGBColor(0xE8, 0xD9, 0xC2))
    tx(s, M + 0.14, 6.14, 5.6, 0.45, "Batas Hall: bukan untuk pulpitis ireversibel, abses, fistula, atau tanpa dentine bridge.",
       size=8.8, color=RGBColor(0x6B, 0x5A, 0x3E))
    card(s, 6.95, 1.9, 5.75, 4.2, fill=RGBColor(0xFD, 0xFA, 0xF4))
    # dua gigi + crown
    for gx in [7.6, 9.2]:
        g = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(gx), Inches(3.0), Inches(1.25), Inches(2.1))
        g.adjustments[0] = 0.18
        g.fill.solid(); g.fill.fore_color.rgb = RGBColor(0xFA, 0xF1, 0xDE)
        g.line.color.rgb = RGBColor(0xD8, 0xC6, 0xA8); g.line.width = Pt(1); g.shadow.inherit = False
    cr = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.45), Inches(2.55), Inches(1.55), Inches(1.0))
    cr.adjustments[0] = 0.12
    cr.fill.solid(); cr.fill.fore_color.rgb = RGBColor(0xF6, 0xDF, 0xD7)
    cr.line.color.rgb = INK; cr.line.width = Pt(1.6); cr.shadow.inherit = False
    tx(s, 7.55, 2.78, 1.35, 0.4, "crown", size=9, color=INK, align=PP_ALIGN.CENTER)
    tx(s, 8.95, 3.5, 1.3, 0.4, "separator", size=7.5, color=RGBColor(0x6F, 0x5B, 0x3F), align=PP_ALIGN.CENTER)
    tx(s, 7.2, 5.3, 5.2, 0.55, "Karies tetap di tempatnya dan tertutup dari substrat oral.", size=9.5, color=INK2, align=PP_ALIGN.CENTER)
    footer(s, "Innes 2007 · Hall Technique Guide 2015 · SDCEP 2025")
    notes(s, notes_map[7])

    # 9 COMPARE
    s = blank(prs); slides.append(s)
    header(s, "Dua teknik", "Hall lebih cepat, konvensional lebih terkontrol", 9, 28)
    for i, (title, sub, wakt, anes, prep, kar, color) in enumerate([
            ("SSC konvensional", "Anestesi, preparasi, ekskavasi", "17,4 ± 2,9", "Ya", "Ya", "Dibuang", TEAL),
            ("Hall Technique", "Tanpa anestesi, tanpa preparasi", "7,1 ± 2,8", "Tidak", "Tidak", "Disegel", GOLD)]):
        x = M + i * 6.1
        card(s, x, 1.9, 5.8, 4.0)
        tx(s, x + 0.24, 2.05, 5.2, 0.4, title, size=16, font=SERIF, color=INK)
        tx(s, x + 0.24, 2.5, 5.2, 0.3, sub, size=9.5, color=MUTED)
        rows = [("Waktu kursi", wakt + " menit"), ("Anestesi", anes), ("Preparasi", prep), ("Karies", kar)]
        for j, (k, v) in enumerate(rows):
            yy = 2.95 + j * 0.58
            tx(s, x + 0.24, yy, 1.7, 0.3, k.upper(), size=8, color=MUTED, bold=True)
            tx(s, x + 1.95, yy - 0.04, 3.6, 0.36, v, size=12, color=INK)
        barw = 4.8 * (17.4 if i == 0 else 7.1) / 17.4
        track = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x + 0.24), Inches(5.3), Inches(4.8), Inches(0.16))
        track.adjustments[0] = 0.5; track.fill.solid(); track.fill.fore_color.rgb = RGBColor(0xEE, 0xE3, 0xD2)
        track.line.fill.background(); track.shadow.inherit = False
        b = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x + 0.24), Inches(5.3), Inches(barw), Inches(0.16))
        b.adjustments[0] = 0.5; b.fill.solid(); b.fill.fore_color.rgb = color
        b.line.fill.background(); b.shadow.inherit = False
        tx(s, x + 0.24, 5.55, 5.2, 0.3, "Waktu prosedur (Mohamed 2026)", size=8, color=MUTED)
    tx(s, M, 6.12, 11.9, 0.6, "Tidak ada RCT yang membandingkan Hall dengan SSC konvensional (Cochrane 2015). Penerimaan anak dan orang tua lebih baik pada Hall (Innes 2007).",
       size=10, color=INK2)
    footer(s, "Mohamed 2026 · Innes 2007 · Innes 2015 Cochrane")
    notes(s, notes_map[8])

    # 10 COMPLICATIONS
    s = blank(prs); slides.append(s)
    header(s, "Penyulit", "Penyulit SSC bisa dicegah di langkah preparasi", 10, 28)
    comps = [("Crown longgar", "Ukuran terlalu besar atau crimping kurang."),
             ("Crown tidak duduk", "Ledge atau kontak belum putus."),
             ("Perdarahan gingiva", "Margin terlalu panjang atau tepi tajam."),
             ("Perforasi crown", "Trimming berlebihan atau wear oklusal."),
             ("Crown lepas", "Retensi buruk atau karies sekunder."),
             ("Anak tidak kooperatif", "Cemas atau pengalaman buruk.")]
    for i, (a, b) in enumerate(comps):
        x = M + (i % 3) * 4.05
        y = 1.9 + (i // 3) * 1.5
        card(s, x, y, 3.85, 1.3)
        tx(s, x + 0.18, y + 0.14, 3.5, 0.3, a, size=12, color=INK, bold=True)
        tx(s, x + 0.18, y + 0.5, 3.5, 0.6, b, size=10, color=INK2)
    strip = [("Alergi nikel", "Kontraindikasi. Pilih zirkonia atau komposit."),
             ("MIH", "Survival 94,4% vs komposit 49,2% pada 24 bulan."),
             ("Berkebutuhan khusus", "Lebih sedikit kunjungan.")]
    for i, (a, b) in enumerate(strip):
        x = M + i * 4.05
        card(s, x, 5.05, 3.85, 1.1, fill=RGBColor(0xFD, 0xF8, 0xEF))
        tx(s, x + 0.18, 5.16, 3.5, 0.3, a, size=10.5, color=ACCENT, bold=True)
        tx(s, x + 0.18, 5.46, 3.5, 0.6, b, size=9.5, color=INK2)
    footer(s, "Kindelan 2008 · Randall 2002 · Farias 2022 · Ahlström 2019")
    notes(s, notes_map[9])

    # 11 EVIDENCE
    s = blank(prs); slides.append(s)
    header(s, "Bukti", "Bukti terkuat ada pada kegagalan mayor, bukan pada estetika", 11, 28)
    card(s, M, 1.9, 5.85, 3.7)
    tx(s, M + 0.22, 2.02, 5.4, 0.3, "Hall vs restorasi rutin, 60 bulan", size=11.5, color=INK, bold=True)
    tx(s, M + 0.22, 2.32, 5.4, 0.3, "RCT split-mouth, 132 anak (Innes 2011)", size=8.5, color=MUTED)
    bars(s, M + 0.22, 2.72, 5.3, 1.2, [("Hall", 92), ("Kontrol", 52)], color=TEAL)
    tx(s, M + 0.22, 4.65, 5.3, 0.5, "Kegagalan mayor 3% vs 16,5%. NNT 8.", size=9, color=INK2)
    card(s, M + 6.05, 1.9, 5.85, 3.7)
    tx(s, M + 6.27, 2.02, 5.4, 0.3, "Retensi 5 tahun per material", size=11.5, color=INK, bold=True)
    tx(s, M + 6.27, 2.32, 5.4, 0.3, "SR/MA 13 RCT + 5 studi klinis (Lampl 2025). Sumbu 80–100%.", size=8.5, color=MUTED)
    bars(s, M + 6.27, 2.68, 5.35, 2.4,
         [("SSC", 97.88), ("Zirkonia", 97.09), ("Komposit", 92.18), ("RMGIC", 90.30),
          ("Compomer", 88.90), ("Strip", 83.48)], vmax=100, color=TEAL, label_w=1.05)
    tx(s, M, 5.78, 11.9, 0.4, "Angka retensi dan success tidak boleh dibandingkan langsung. Definisi kegagalan berbeda antar studi.",
       size=9.5, color=INK2)
    footer(s, "Innes 2011 · Lampl 2025 · Chisini 2018 · Innes 2015 Cochrane")
    notes(s, notes_map[10])

    # 12 ALTERNATIVES
    s = blank(prs); slides.append(s)
    header(s, "Alternatif estetik", "Zirkonia lebih baik pada gingiva, belum pada retensi jangka panjang", 12, 27)
    cols = [("Zirkonia", ["Kegagalan: RR 0,48 (0,15–1,52)", "Gingiva: MD −0,32 (−0,42 sampai −0,23)", "Biaya, wear antagonis, sulit direparasi"]),
            ("Pre-veneered SSC", ["Retensi 6 bulan: 95% (Walia 2014)", "Veneer bisa fraktur", "Bukti belum cukup menggantikan SSC"]),
            ("Strip crown", ["Retensi 6 bulan: 78% (Walia 2014)", "Sensitif kelembapan", "Bukan pilihan utama molar posterior"])]
    for i, (title, lines) in enumerate(cols):
        x = M + i * 3.92
        card(s, x, 1.9, 3.72, 2.55)
        tx(s, x + 0.18, 2.02, 3.4, 0.3, title, size=12.5, color=INK, bold=True)
        ty = 2.42
        for ln in lines:
            tx(s, x + 0.18, ty, 3.4, 0.42, "•  " + ln, size=9.3, color=INK2)
            ty += 0.52
    card(s, M, 4.65, 11.55, 1.55)
    tx(s, M + 0.2, 4.75, 5.0, 0.3, "Retensi 6 bulan", size=10.5, color=INK, bold=True)
    tx(s, M + 0.2, 5.02, 6.0, 0.3, "RCT 129 gigi insisivus desidui (Walia 2014)", size=8.5, color=MUTED)
    bars(s, M + 0.2, 5.28, 6.2, 0.85, [("Zirkonia", 100), ("PVSSC", 95), ("Strip", 78)], color=TEAL, label_w=0.9)
    tx(s, M + 6.65, 5.0, 4.7, 0.9, "Untuk molar posterior desidui, SSC tetap menjadi pembanding utama dalam SR dan meta-analisis.",
       size=9.5, color=INK2)
    footer(s, "Patnana 2022 · Pei & Chen 2023 · Aiem 2017 · Walia 2014")
    notes(s, notes_map[11])

    # 13 CASE
    s = blank(prs); slides.append(s)
    header(s, "Kasus ilustratif", "Kasus: molar kedua desidui bawah kanan, karies oklusal-distal", 13, 26)
    card(s, M, 1.85, 6.0, 1.95)
    tx(s, M + 0.2, 1.98, 5.6, 1.7,
       "Anak laki-laki, 7 tahun. Gigi 85, karies oklusal-distal luas.\n"
       "Tidak ada nyeri spontan, swelling, atau fistula. Vital, perkusi negatif.\n"
       "Radiograf: lesi mendekati pulpa dengan dentine bridge terlihat.", size=10.2, color=INK2, spacing=1.25)
    placeholder(s, M, 3.98, 2.9, 1.45, "Foto klinis", "Okusal gigi 85. Ganti dengan foto Anda.")
    placeholder(s, M + 3.1, 3.98, 2.9, 1.45, "Radiograf", "Bitewing gigi 85. Ganti dengan radiograf Anda.")
    tx(s, M, 5.55, 5.9, 0.3, "Data fiktif untuk latihan keputusan.", size=8, color=MUTED)
    tx(s, 6.95, 1.85, 5.7, 0.3, "1. Apa keputusan Anda?", size=13, color=INK, bold=True)
    opts = ["Hall Technique tanpa anestesi", "SSC konvensional dengan anestesi", "Komposit dua permukaan"]
    for i, o in enumerate(opts):
        y = 2.22 + i * 0.5
        card(s, 6.95, y, 5.7, 0.4, radius=0.5)
        tx(s, 7.1, y + 0.08, 5.4, 0.28, o, size=10.5, color=INK2)
    tx(s, 6.95, 3.8, 5.7, 0.3, "2. Crown belum duduk merata saat try-in", size=13, color=INK, bold=True)
    tx(s, 6.95, 4.12, 5.7, 0.3, "Tepi servikal terangkat di distal. Apa langkah berikutnya?", size=9.5, color=INK2)
    opts2 = ["Tekan dengan bite stick sampai duduk", "Periksa ledge dan sisa kontak distal", "Ganti crown satu ukuran lebih besar"]
    for i, o in enumerate(opts2):
        y = 4.45 + i * 0.5
        card(s, 6.95, y, 5.7, 0.4, radius=0.5)
        tx(s, 7.1, y + 0.08, 5.4, 0.28, o, size=10.5, color=INK2)
    tx(s, 6.95, 6.05, 5.7, 0.5, "Jawaban dan alasan ada di catatan pembicara versi ini.", size=8, color=MUTED)
    footer(s, "Kindelan 2008 · SDCEP 2025 · Randall 2002")
    notes(s, notes_map[12] + " Kunci: Hall atau SSC konvensional sama-sama dapat diterima. Bila crown tidak duduk, periksa ledge dan sisa kontak, jangan memaksa.")

    # 14 QUIZ
    s = blank(prs); slides.append(s)
    header(s, "Kuis", "Lima pertanyaan untuk diskusi", 14, 28)
    qs = ["1. Nyeri spontan malam, molar desidui. Hall atau konvensional?",
          "2. Berapa reduksi oklusal yang paling banyak dipakai?",
          "3. Crown tidak duduk, ada ledge. Apa langkah berikutnya?",
          "4. Apa yang paling menentukan retensi jangka panjang?",
          "5. MIH berat pada molar permanen. Pilihan dengan bukti terkuat?"]
    for i, q in enumerate(qs):
        y = 1.9 + i * 0.86
        card(s, M, y, 11.55, 0.7)
        tx(s, M + 0.2, y + 0.2, 11.1, 0.34, q, size=11.5, color=INK)
    tx(s, M, 6.2, 11.5, 0.3, "Jawaban: 1 konvensional, 2 1,0–1,5 mm, 3 periksa ledge, 4 kontur dan crimping, 5 SSC.",
       size=8.5, color=MUTED)
    footer(s, "Kindelan 2008 · AAPD 2024 · Farias 2022 · Randall 2002")
    notes(s, notes_map[13] + " Kunci jawaban: 1 SSC konvensional setelah pulpotomi; 2 1,0–1,5 mm; 3 periksa ledge dan sisa kontak; 4 kontur dan crimping margin; 5 SSC.")

    # 15 RECAP
    s = blank(prs); slides.append(s)
    header(s, "Penutup", "Tiga hal yang harus diingat", 15)
    recap = [("1", "SSC menutup seluruh mahkota", "Retensi dari margin dan undercut servikal. Crimping lebih menentukan daripada semen."),
             ("2", "Hall hanya untuk gigi vital dengan dentine bridge jelas", "Nyeri spontan atau abses mengubah rencana. Pilih konvensional setelah pulp therapy."),
             ("3", "Baca angka sesuai definisinya", "Success, survival, dan retention bukan hal yang sama.")]
    for i, (n, a, b) in enumerate(recap):
        y = 1.9 + i * 1.42
        card(s, M, y, 11.55, 1.24)
        tx(s, M + 0.25, y + 0.2, 0.7, 0.8, n, size=32, font=SERIF, color=ACCENT)
        tx(s, M + 0.95, y + 0.15, 10.3, 0.4, a, size=15, font=SERIF, color=INK)
        tx(s, M + 0.95, y + 0.62, 10.3, 0.5, b, size=10.5, color=INK2)
    tx(s, M, 6.2, 11.5, 0.4, "Materi edukasi. Keputusan klinis tetap mempertimbangkan kondisi pasien dan fasilitas.",
       size=9, color=MUTED)
    footer(s, "Kindelan 2008 · AAPD 2025 · Innes 2015 Cochrane · Lampl 2025")
    notes(s, notes_map[14])

    # 16-17 REFERENCES
    refs = [
        "1. American Academy of Pediatric Dentistry. Pediatric restorative dentistry. Reference Manual. Chicago: AAPD; 2025. p. 473-486.",
        "2. Kindelan SA, Day P, Nichol R, Willmott N, Fayle SA. UK National Clinical Guidelines: stainless steel preformed crowns for primary molars. Int J Paediatr Dent. 2008;18(Suppl 1):20-28. doi:10.1111/j.1365-263X.2008.00935.x",
        "3. Innes NPT, Ricketts D, Chong LY, Keightley AJ, Lamont T, Santamaria RM. Preformed crowns for decayed primary molar teeth. Cochrane Database Syst Rev. 2015;(12):CD005512. doi:10.1002/14651858.CD005512.pub3",
        "4. Innes NPT, Evans DJP, Stirrups DR. Sealing caries in primary molars: randomized control trial, 5-year results. J Dent Res. 2011;90(12):1405-1410. doi:10.1177/0022034511422064",
        "5. Innes NPT, Evans DJP, Stirrups DR. The Hall Technique: acceptability and outcomes at 23 months. BMC Oral Health. 2007;7:18. doi:10.1186/1472-6831-7-18",
        "6. Tedesco TK, Innes NP, Gallegos CL, et al. Success rate of Hall Technique for restoring carious primary molars: systematic review and meta-analysis. Evid Based Dent. 2025;26(1):65-66. doi:10.1038/s41432-024-01044-0",
        "7. Mohamed HA, Abdalla EM, HagOmer NA, Philip N. Conventional versus Hall technique for preformed metal crown restorations of carious primary molars: a randomised controlled trial. Eur Arch Paediatr Dent. 2026;27(2):599-606. doi:10.1007/s40368-025-01128-0",
        "8. Chisini LA, Collares K, Cademartori MG, et al. Restorations in primary teeth: a systematic review on survival and reasons for failures. Int J Paediatr Dent. 2018;28(2):123-139. doi:10.1111/ipd.12346",
        "9. Joshi RS, Gokhale NS, Hugar SM, et al. Longevity of stainless steel crowns on primary molars: systematic review and meta-analysis. J Sci Soc. 2023;50(1):28-38. doi:10.4103/jss.jss_164_22",
        "10. Lampl S, Gurunathan D, Mehta D, Jogikalmat K. Reasons for crown failures in primary teeth: systematic review and meta-analysis. Interact J Med Res. 2025;14:e57958. doi:10.2196/57958",
        "11. Randall RC. Preformed metal crowns for primary and permanent molar teeth: review of the literature. Pediatr Dent. 2002;24(5):489-500. PMID 12412964.",
        "12. Amlani DV, Brizuela M. Stainless steel crowns in primary dentition. StatPearls. Treasure Island: StatPearls Publishing; 2023. PMID 34662061.",
        "13. AAPD. Use of vital pulp therapies in primary teeth with deep caries lesions. Reference Manual. Chicago: AAPD; 2025.",
        "14. AAPD. Molar-incisor hypomineralization. Reference Manual. Chicago: AAPD; 2025.",
        "15. Farias L, Campos MS, Dantas L, et al. Survival of stainless-steel crowns and composite resin restorations in molars affected by MIH. Int J Paediatr Dent. 2022;32(2):240-250. doi:10.1111/ipd.12849",
        "16. Chaipattanawan N, et al. Longevity of stainless steel crowns as interim restorations on young permanent first molars after vital pulp therapy. Int J Paediatr Dent. 2022. doi:10.1111/ipd.12971",
        "17. Patnana AK, Chugh VK, Chugh A, Vanga NRV, Kumar P. Effectiveness of zirconia crowns compared with stainless steel crowns in primary posterior teeth: systematic review and meta-analysis. J Am Dent Assoc. 2022;153(2):158-166.e5. doi:10.1016/j.adaj.2021.08.005",
        "18. Pei SL, Chen MH. Comparison of periodontal health of primary teeth restored with zirconia and stainless steel crowns: systematic review and meta-analysis. J Formos Med Assoc. 2023;122(2):148-156. doi:10.1016/j.jfma.2022.08.015",
        "19. Aiem E, Smaïl-Faugeron V, Muller-Bolla M. Aesthetic preformed paediatric crowns: systematic review. Int J Paediatr Dent. 2017;27(4):273-282. doi:10.1111/ipd.12260",
        "20. Walia T, Salami AA, Bashiri R, Hamoodi OM, Rashid F. A randomised controlled trial of three aesthetic full-coronal restorations in primary maxillary teeth. Eur J Paediatr Dent. 2014;15(2):113-118. PMID 25102458.",
        "21. Virupaxi S, Pai R, Mandroli P. Retentive strength of luting cements for stainless steel crowns: a systematic review. J Indian Soc Pedod Prev Dent. 2020;38(1):2-7. doi:10.4103/JISPPD.JISPPD_313_19",
        "22. Scottish Dental Clinical Effectiveness Programme. Prevention and management of dental caries in children. 3rd ed. Dundee: SDCEP; 2025.",
        "23. Innes N, Evans D, Hall N. The Hall Technique. 4th ed. Dundee: University of Dundee; 2015.",
        "24. AAPD. Behavior guidance for the pediatric dental patient. Reference Manual. Chicago: AAPD; 2025.",
        "25. AAPD. Use of local anesthesia for pediatric dental patients. Reference Manual. Chicago: AAPD; 2025.",
        "26. AAPD. Informed consent. Reference Manual. Chicago: AAPD; 2025.",
        "27. Ahlström MG, Thyssen JP, Wennervaldt M, Menné T, Johansen JD. Nickel allergy and allergic contact dermatitis. Contact Dermatitis. 2019;81(4):227-241. doi:10.1111/cod.13327",
        "28. Kementerian Kesehatan RI. Laporan Nasional Riskesdas 2018. Jakarta: Badan Litbangkes; 2019.",
        "29. Kementerian Kesehatan RI. Survei Kesehatan Indonesia 2023. Jakarta: Kemenkes RI; 2024.",
        "30. Miao C, Yang J, Zhu H, et al. Rubber dam isolation for restorative treatment in dental patients. Cochrane Database Syst Rev. 2021;5:CD009858. doi:10.1002/14651858.CD009858.pub3",
        "31. Seale NS. The use of stainless steel crowns. Pediatr Dent. 2002;24(5):501-505. PMID 12412965.",
        "32. Seale NS, Randall R. The use of stainless steel crowns: a systematic literature review. Pediatr Dent. 2015;37(2):145-160. PMID 25905656.",
        "33. American Academy of Pediatric Dentistry. Caries-risk assessment and management for infants, children, and adolescents. Reference Manual. Chicago: AAPD; 2025.",
    ]
    for part, (label, chunk) in enumerate([("Sumber 1–15", refs[:15]), ("Sumber 16–33", refs[15:])]):
        s = blank(prs); slides.append(s)
        header(s, "Daftar pustaka", label + " (Vancouver)", 16 + part, 26)
        if part == 0:
            groups = [chunk[:8], chunk[8:]]
            xs = [M, M + 6.05]
            cw = 5.9
        else:
            per = 8
            groups = [chunk[:per], chunk[per:2 * per], chunk[2 * per:]]
            xs = [M, M + 4.05, M + 8.1]
            cw = 3.85
        for ci, colrefs in enumerate(groups):
            tb = s.shapes.add_textbox(Inches(xs[ci]), Inches(1.78), Inches(cw), Inches(4.9))
            tf = tb.text_frame
            tf.word_wrap = True
            tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
            tf.clear()
            for ri, ref in enumerate(colrefs):
                par = tf.paragraphs[0] if ri == 0 else tf.add_paragraph()
                par.line_spacing = 1.0
                par.space_after = Pt(9)
                run = par.add_run()
                run.text = ref
                run.font.size = Pt(9)
                run.font.name = SANS
                run.font.color.rgb = INK2
        footer(s, "Daftar lengkap dengan DOI dan PMID: research_notes.md")
        notes(s, notes_map[15 + part])

    # 18 APPENDIX
    s = blank(prs); slides.append(s)
    header(s, "Lampiran", "Protokol satu halaman untuk dibawa ke klinik", 18, 26)
    cols = [
        ("Sebelum tindakan", ["Riwayat nyeri, swelling, fistula", "Riwayat medis dan alergi nikel", "Karies, pulpa, gingiva, oklusi", "Radiograf dan dentine bridge", "Pilih teknik dan ukuran", "Informed consent", "Rencana behavior guidance"]),
        ("Konvensional 1–5", ["1 Anestesi dan isolasi", "2 Ukur dan pilih crown", "3 Ekskavasi, pulp therapy", "4 Reduksi oklusal 1,0–1,5 mm", "5 Reduksi proksimal, feather edge"]),
        ("Konvensional 6–10", ["6 Haluskan line angle", "7 Try-in", "8 Trim, crimp, contour", "9 Sementasi", "10 Cek akhir dan instruksi"]),
        ("Hall, kontrol, kegagalan", ["Vital, dentine bridge jelas", "Separator 3–5 hari", "GIC dua pertiga, bite 2–3 menit", "Kontrol 6 bulan", "Radiograf 6–12 bulan", "Sukses, gagal minor, gagal mayor"]),
    ]
    for i, (title, lines) in enumerate(cols):
        x = M + i * 3.05
        tx(s, x, 1.82, 2.9, 0.3, title.upper(), size=8.2, color=ACCENT, bold=True, spc=50)
        ty = 2.2
        for ln in lines:
            tx(s, x, ty, 2.9, 0.30, "□  " + ln, size=8.6, color=INK2)
            ty += 0.52 if len(ln) > 33 else 0.40
    fills = [
        ("Angka kunci", ["Success SSC 96,1% (Chisini 2018)", "Gagal mayor RR 0,18 (Cochrane 2015)", "Hall 92% vs 52% (Innes 2011)", "Retensi 5 tahun 97,88% (Lampl 2025)"]),
        ("Penyulit dan tindakan", ["Longgar: ukuran lebih kecil, crimp ulang", "Tidak duduk: periksa ledge dan kontak", "Perforasi: ganti crown", "Lepas: recement bila crown intak"]),
    ]
    for i, (title, lines) in enumerate(fills):
        x = M + i * 6.1
        card(s, x, 4.85, 5.8, 1.28, fill=RGBColor(0xFD, 0xF8, 0xEF))
        tx(s, x + 0.2, 4.95, 5.4, 0.28, title.upper(), size=8.2, color=ACCENT, bold=True, spc=50)
        ty = 5.26
        for ln in lines:
            tx(s, x + 0.2, ty, 5.4, 0.22, "•  " + ln, size=8.6, color=INK2)
            ty += 0.2
    tx(s, M, 6.3, 11.6, 0.35, "Protokol lengkap: protokol_klinis.md. Angka dan DOI: research_notes.md.",
       size=8, color=MUTED)
    footer(s, "Kindelan 2008 · Randall 2002 · Hall Technique Guide 2015 · AAPD 2025 · SDCEP 2025")
    notes(s, notes_map[17])

    for b, target in agenda_links:
        b.click_action.target_slide = prs.slides[target]
    for sl in prs.slides:
        for shp in sl.shapes:
            if shp.has_text_frame and shp.text_frame.text.strip() == "Agenda":
                shp.click_action.target_slide = prs.slides[1]

    prs.save(path)
    return len(prs.slides._sldIdLst)


def extract_notes(html_path):
    s = open(html_path, encoding="utf-8").read()
    out = []
    for m in re.finditer(r'<section class="slide[^>]*>(.*?)</section>', s, re.S):
        body = m.group(1)
        n = re.search(r'<template class="notes">(.*?)</template>', body, re.S)
        if n:
            raw = re.sub(r'<[^>]+>', ' ', n.group(1))
            raw = re.sub(r'\s+', ' ', raw).strip()
            raw = (raw.replace("&amp;", "&").replace("&nbsp;", " ")
                      .replace("&lt;", "<").replace("&gt;", ">"))
            out.append(raw)
        else:
            out.append("")
    return out


if __name__ == "__main__":
    nm = extract_notes("ssc-pedodonsia.html")
    assert len(nm) == 18, len(nm)
    n = build("ssc-pedodonsia.pptx", nm)
    print("slides:", n)
