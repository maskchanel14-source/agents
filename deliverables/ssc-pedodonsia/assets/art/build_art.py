#!/usr/bin/env python3
"""Bangun ilustrasi deck: foto anatomi + kolom anotasi vektor.

Foto anatomi (photo-*.jpg) diberi anotasi vektor di sini dan ditulis sebagai
fig-*.svg. tools/render_svg.js mengubahnya menjadi JPEG 2x yang dipakai deck
HTML dan PPTX.

Jalankan:
  python3 assets/art/build_art.py
  NODE_PATH=<node_modules> node tools/render_svg.js 2
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
INK = "#15323a"
INK2 = "#5b7378"
MUTED = "#7d8f93"
ACCENT = "#c65b45"
LINE = "#9aa9a8"
TEAL = "#2c6e6a"
PAPER = "#fbf7ef"

# photo-*.jpg adalah potongan foto anatomi yang dipakai sebagai dasar ilustrasi.
# Berkas asli hasil generasi disimpan di assets/src/*.jpg (tidak dipakai langsung
# oleh deck, hanya arsip bila potongan perlu dibuat ulang).


def img(name, x, y, w, h, rx=12):
    p = "photo-%s.jpg" % name.split(".")[0]
    cid = "cl%d" % (abs(hash((p, x, y, w, h))) % 1000000)
    return (
        '<defs><clipPath id="%s"><rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%s"/></clipPath></defs>'
        '<image href="%s" x="%.1f" y="%.1f" width="%.1f" height="%.1f" '
        'preserveAspectRatio="xMidYMid slice" clip-path="url(#%s)"/>'
        '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%s" fill="none" '
        'stroke="#15323a" stroke-opacity=".10" stroke-width="1"/>'
        % (cid, x, y, w, h, rx, p, x, y, w, h, cid, x, y, w, h, rx)
    )


def label(x, y, main, sub=None, anchor="start", size=17):
    out = ('<text x="%.1f" y="%.1f" font-family="Inter" font-size="%s" font-weight="600" fill="%s" '
           'text-anchor="%s">%s</text>' % (x, y, size, INK, anchor, main))
    if sub:
        out += ('<text x="%.1f" y="%.1f" font-family="Inter" font-size="14.5" fill="%s" '
                'text-anchor="%s">%s</text>' % (x, y + 20, INK2, anchor, sub))
    return out


def callout(ax, ay, tx, ty, main, sub=None, anchor="start", edge=None, size=17):
    """Leader from anatomy point (ax,ay) to a label anchored at (tx,ty).

    edge: x of the photo border the leader must cross; the segment runs from
    the anatomy point straight to (edge ± 10, ty - 5) and then flat to the text.
    """
    if edge is None:
        elb_x, elb_y = tx - 12, ty - 5
    else:
        elb_x = edge + 12 if anchor == "start" else edge - 12
        elb_y = ty - 5
    d = "%.1f,%.1f %.1f,%.1f %.1f,%.1f" % (ax, ay, elb_x, elb_y, elb_x + (10 if anchor == "start" else -10), elb_y)
    out = ('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.2" stroke-linecap="round" '
           'stroke-linejoin="round"/>' % (d, LINE))
    out += '<circle cx="%.1f" cy="%.1f" r="3.4" fill="%s" stroke="%s" stroke-width="1.6"/>' % (ax, ay, "#fffdf8", LINE)
    return out + label(tx, ty, main, sub, anchor, size)


def svg(w, h, body, title):
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" '
            'role="img" aria-label="%s">\n<rect width="%d" height="%d" fill="%s"/>\n%s\n</svg>\n'
            % (w, h, w, h, title, w, h, PAPER, body))


arts = {}

# ------------------------------------------------------------------ COVER
w, h = 486, 552
body = [img("hero.png", 8, 6, 470, 470, rx=24)]
body.append('<text x="243" y="510" font-family="Inter" font-size="13" letter-spacing="2" '
            'fill="%s" text-anchor="middle">PREFORMED METAL CROWN</text>' % MUTED)
body.append('<text x="243" y="532" font-family="Inter" font-size="14" fill="%s" '
            'text-anchor="middle">mahkota molar desidui, pandangan okusal-bukal</text>' % INK2)
arts["cover"] = (w, h, "".join(body), "Mahkota stainless steel untuk molar desidui")

# ------------------------------------------------------------------ WHY
# photo-why.png 620x840 -> 310x420 di (24,26)
PW, PH = 310, 420
PX, PY = 24, 26
w, h = 720, 472
S = PW / 620.0


def p(x, y):
    return (PX + x * S, PY + y * S)


body = [img("why.png", PX, PY, PW, PH)]
right = PX + PW + 34
rows = [
    (p(470, 150), "menutup seluruh gigi", "seluruh korona tertutup logam", 92),
    (p(556, 420), "margin 1 mm subgingiva", "seal sekaligus retensi", 190),
    (p(120, 462), "bulbositas servikal", "undercut jadi sumber retensi", 300),
    (p(330, 600), "pulpa", "tanduk pulpa tinggi, dentin tipis", 404),
]
for (ax, ay), main, sub, ty in rows:
    body.append(callout(ax, ay, right, ty, main, sub, edge=PX + PW))
arts["why"] = (w, h, "".join(body), "Penampang molar desidui dengan crown terpasang")

# ------------------------------------------------------------------ PREP
# photo-prep.png 640x1035 -> 310x501 di (110,6)
PW2, PH2 = 310, 501
PX2, PY2 = 118, 6
w, h = 790, 552
S2 = PW2 / 640.0


def q(x, y):
    return (PX2 + x * S2, PY2 + y * S2)


body = [img("prep.png", PX2, PY2, PW2, PH2)]
right = PX2 + PW2 + 30
rows = [
    (q(300, 528), "reduksi oklusal 1,0–1,5 mm", "sumber lain: 1,5–2,0 mm", 96),
    (q(470, 655), "feather edge di proksimal", "kontak mesial dan distal putus", 196),
    (q(200, 782), "bulbositas servikal", "dipertahankan, jangan diratakan", 300),
    (q(452, 800), "margin servikal", "crown duduk 1 mm subgingiva", 410),
]
for (ax, ay), main, sub, ty in rows:
    body.append(callout(ax, ay, right, ty, main, sub, edge=PX2 + PW2))
body.append(label(PX2, 532, "Garis dan angka untuk orientasi, bukan skala.",
                  None, "start", 13))
arts["prep"] = (w, h, "".join(body), "Preparasi molar desidui dengan ukuran reduksi")

# ------------------------------------------------------------------ HALL
# photo-hall.png 700x800 -> 360x411 di (40,18)
PW3, PH3 = 360, 411
PX3, PY3 = 44, 20
w, h = 780, 496
S3 = PW3 / 700.0


def r(x, y):
    return (PX3 + x * S3, PY3 + y * S3)


body = [img("hall.png", PX3, PY3, PW3, PH3)]
right = PX3 + PW3 + 24
rows = [
    (r(300, 120), "crown menutup penuh", "tanpa pengurangan gigi", 92),
    (r(300, 320), "karies tidak dibuang", "tertutup dari substrat oral", 194),
    (r(556, 246), "margin di servikal", "semen mengisi celah margin", 296),
    (r(440, 258), "gingiva tertekan ringan", "mereda dalam beberapa minggu", 396),
]
for (ax, ay), main, sub, ty in rows:
    body.append(callout(ax, ay, right, ty, main, sub, edge=PX3 + PW3))
body.append(label(PX3, 470, "Semen GIC mengisi dua pertiga crown dan menyelimuti seluruh dinding,",
                  "lalu crown ditekan saat anak menggigit 2–3 menit.", "start", 13))
arts["hall"] = (w, h, "".join(body), "Crown Hall menutup karies tanpa preparasi")

# ------------------------------------------------------------------ ALTERNATIVES
CW, CH = 300, 106  # tiap mahkota di photo-esthetic 1440x508
w, h = 690, 300
SC = 0.44
body = [img("esthetic.png", 8, 6, 1440 * SC, 508 * SC, rx=14)]
base = 6 + 508 * SC + 30
for cx_img, t1, t2 in [(268, "Zirkonia", "monolitik, putih"), (700, "Pre-veneered", "SSC dengan veneer bukal"),
                       (1178, "SSC", "logam penuh")]:
    cx = 8 + cx_img * SC
    body.append('<text x="%.1f" y="%.1f" font-family="Inter" font-size="17" font-weight="600" '
                'fill="%s" text-anchor="middle">%s</text>' % (cx, base, INK, t1))
    body.append('<text x="%.1f" y="%.1f" font-family="Inter" font-size="14" fill="%s" '
                'text-anchor="middle">%s</text>' % (cx, base + 21, INK2, t2))
arts["alternatives"] = (w, h, "".join(body), "Tiga pilihan mahkota posterior anak")

# ------------------------------------------------------------------ SETUP
# photo-setup.jpg 1500x810 dipotong 1500x810 -> 700x378
w, h = 700, 300
body = [img("setup.jpg", 6, 4, 688, 262, rx=14)]
arts["setup"] = (w, h, "".join(body), "Alat anestesi dan isolasi untuk pemasangan SSC")

# ------------------------------------------------------------------ INSTRUMENTS
w, h = 700, 286
body = [img("instruments.jpg", 6, 4, 688, 250, rx=14)]
arts["instruments"] = (w, h, "".join(body), "Instrumen untuk pemasangan stainless steel crown")

for name, (w, h, body, title) in arts.items():
    with open(os.path.join(HERE, "fig-%s.svg" % name), "w", encoding="utf-8") as f:
        f.write(svg(w, h, body, title))
    print("wrote fig-%s.svg %dx%d" % (name, w, h))
