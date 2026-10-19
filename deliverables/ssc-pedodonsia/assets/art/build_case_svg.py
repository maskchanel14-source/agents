#!/usr/bin/env python3
"""Membuat dua ilustrasi skematik untuk slide kasus.

Bukan foto pasien dan bukan radiograf asli: keduanya gambar vektor yang
dilabeli supaya jelas mana karies, mana pulpa, dan mana dentine bridge.
Jalankan dari folder ini: python3 build_case_svg.py
"""
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))

INK = "#15323a"
INK2 = "#5b7378"
MUTED = "#7d8f93"
ACCENT = "#c65b45"
LINE = "#d8cbb8"
PAPER = "#fbf7ef"


def cr_path(pts):
    """Kurva tertutup Catmull-Rom -> Bezier."""
    n = len(pts)
    d = "M %.1f %.1f " % pts[0]
    for i in range(n):
        p0, p1, p2, p3 = pts[(i - 1) % n], pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6.0, p1[1] + (p2[1] - p0[1]) / 6.0)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6.0, p2[1] - (p3[1] - p1[1]) / 6.0)
        d += "C %.1f %.1f %.1f %.1f %.1f %.1f " % (c1[0], c1[1], c2[0], c2[1], p2[0], p2[1])
    return d + "Z"


def blob(cx, cy, r, n, seed=1, jitter=0.14, sx=1.0, sy=1.0):
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        k = 1.0 + jitter * math.sin(i * 2.7 + seed) * math.cos(i * 1.3 + seed * 0.7)
        pts.append((cx + math.cos(a) * r * k * sx, cy + math.sin(a) * r * k * sy))
    return cr_path(pts)


def superellipse(cx, cy, R, n=3.2, cusp=0.05, sx=1.12, sy=0.95, steps=72):
    pts = []
    for i in range(steps):
        t = 2 * math.pi * i / steps
        r = R / ((abs(math.cos(t)) ** n + abs(math.sin(t)) ** n) ** (1.0 / n))
        r *= 1.0 + cusp * math.cos(4 * (t - math.pi / 4))
        pts.append((cx + math.cos(t) * r * sx, cy + math.sin(t) * r * sy))
    return cr_path(pts)


def label(x, y, text, anchor="start", size=16, color=INK, weight=600):
    return ('<text x="%.1f" y="%.1f" font-family="Inter, sans-serif" font-size="%d" '
            'font-weight="%d" fill="%s" text-anchor="%s">%s</text>'
            % (x, y, size, weight, color, anchor, text))


def sub(x, y, text, anchor="start", size=14):
    return label(x, y, text, anchor=anchor, size=size, color=INK2, weight=400)


def leader(points, color=MUTED):
    d = "M %.1f %.1f " % points[0]
    for p in points[1:]:
        d += "L %.1f %.1f " % p
    return ('<path d="%s" fill="none" stroke="%s" stroke-width="1.1"/>'
            '<circle cx="%.1f" cy="%.1f" r="2.6" fill="%s"/>' % (d, color, points[0][0], points[0][1], color))


# ------------------------------------------------------------------ OKLUSAL
W, H = 420, 320
body = ['<rect width="%d" height="%d" fill="%s"/>' % (W, H, PAPER)]
body.append('<path d="%s" fill="#f5eedd" stroke="%s" stroke-width="2"/>' % (superellipse(205, 160, 128), INK))
body.append('<path d="%s" fill="#efe3cd"/>' % superellipse(205, 160, 86))
# grooves
body.append('<path d="M150 120 C180 145 200 155 205 160 C215 172 232 188 262 200" fill="none" '
            'stroke="#c9b79b" stroke-width="5" stroke-linecap="round"/>')
body.append('<path d="M196 96 C200 130 203 148 205 160" fill="none" stroke="#c9b79b" stroke-width="4" stroke-linecap="round"/>')
body.append('<path d="M205 160 C222 178 248 186 288 190" fill="none" stroke="#c9b79b" stroke-width="4" stroke-linecap="round"/>')
# karies pada sisi distal
body.append('<path d="%s" fill="%s" fill-opacity=".82" stroke="#8a3a26" stroke-width="1.4"/>'
            % (blob(330, 158, 52, 15, seed=4.2, jitter=0.2, sx=0.78, sy=1.05), ACCENT))
body.append('<path d="%s" fill="#7d3520" fill-opacity=".85"/>' % blob(343, 150, 22, 12, seed=8.1, jitter=0.25))
body.append('<circle cx="322" cy="196" r="5" fill="#7d3520" fill-opacity=".8"/>')
body.append('<circle cx="343" cy="196" r="3.6" fill="#7d3520" fill-opacity=".8"/>')
# label + penunjuk
body.append(leader([(316, 96), (330, 120), (336, 140)]))
body.append(label(300, 84, "karies oklusal-distal", anchor="end"))
body.append('<text x="60" y="252" font-family="Inter, sans-serif" font-size="14" fill="%s">mesial</text>' % MUTED)
body.append('<text x="352" y="252" font-family="Inter, sans-serif" font-size="14" fill="%s">distal</text>' % MUTED)
body.append(sub(205, 300, "gigi 85, pandangan oklusal", anchor="middle", size=15))
svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" '
       'role="img" aria-label="Ilustrasi skematik oklusal gigi 85 dengan karies oklusal-distal">%s</svg>'
       % (W, H, W, H, "".join(body)))
open(os.path.join(HERE, "fig-case-oklusal.svg"), "w", encoding="utf-8").write(svg)

# ------------------------------------------------------------------ BITE WING
W, H = 420, 320
body = ['<rect width="%d" height="%d" fill="#f3eee4"/>' % (W, H)]
body.append('<rect x="0" y="196" width="%d" height="%d" fill="#ded6c6"/>' % (W, H - 196))
for x, y in [(16, 246), (42, 214), (68, 268), (94, 236), (126, 292), (158, 250), (196, 276),
             (232, 226), (262, 296), (292, 248), (322, 266), (352, 224), (386, 278), (406, 242),
             (34, 300), (150, 214), (300, 300), (240, 300)]:
    body.append('<circle cx="%d" cy="%d" r="1.6" fill="#cdc4b1"/>' % (x, y))
# gigi tetangga (hanya mahkota)
body.append('<path d="M8 72 L58 72 L58 196 L8 196 Z" fill="#e8dfce" stroke="#c3b9a6" stroke-width="1.2"/>')
body.append('<path d="M366 72 L414 72 L414 196 L366 196 Z" fill="#e8dfce" stroke="#c3b9a6" stroke-width="1.2"/>')
# akar gigi 85
body.append('<path d="M146 196 C150 218 156 236 164 250 C172 236 178 218 182 196 Z" fill="#f2ece0" stroke="#c3b9a6" stroke-width="1.2"/>')
body.append('<path d="M238 196 C242 218 248 236 256 250 C264 236 270 218 274 196 Z" fill="#f2ece0" stroke="#c3b9a6" stroke-width="1.2"/>')
# mahkota: enamel, lalu dentin
body.append('<path d="M130 196 L130 96 C130 80 144 72 160 72 L260 72 C276 72 290 80 290 96 L290 196 Z" '
            'fill="#fbf8f1" stroke="#b9b0a0" stroke-width="1.4"/>')
body.append('<path d="M150 196 L150 106 C150 96 158 90 168 90 L252 90 C262 90 270 96 270 106 L270 196 Z" fill="#eae1d0"/>')
# pulpa: kamar + dua saluran
body.append('<path d="M198 106 L222 106 L222 152 C222 162 214 168 210 174 C206 168 198 162 198 152 Z" fill="#6f6154"/>')
body.append('<path d="M203 172 C200 194 196 222 192 244" fill="none" stroke="#6f6154" stroke-width="4" stroke-linecap="round"/>')
body.append('<path d="M217 172 C224 194 232 222 238 244" fill="none" stroke="#6f6154" stroke-width="4" stroke-linecap="round"/>')
# karies distal: menempel di dinding distal, masuk ke dentin
body.append('<path d="%s" fill="#6a5f52" fill-opacity=".92" stroke="#4f463c" stroke-width="1"/>'
            % blob(272, 132, 21, 12, seed=2.4, jitter=0.16, sx=0.8, sy=1.2))
body.append('<rect x="282" y="112" width="7" height="40" fill="#6a5f52" fill-opacity=".92"/>')
# dentine bridge: pita lebih terang antara karies dan pulpa
body.append('<path d="M248 106 C254 124 254 148 248 168" fill="none" stroke="#fdfaf3" stroke-width="6" stroke-linecap="round"/>')
# penunjuk
body.append(leader([(296, 92), (290, 110), (286, 120)]))
body.append(label(300, 88, "karies distal"))
body.append('<path d="M300 186 L268 178 L256 162" fill="none" stroke="%s" stroke-width="1.1"/>' % MUTED)
body.append('<circle cx="256" cy="162" r="2.6" fill="%s"/>' % MUTED)
body.append(label(300, 190, "dentine bridge", size=15, color="#22605c"))
body.append(leader([(122, 128), (150, 128), (172, 128)]))
body.append(sub(118, 124, "pulpa", anchor="end"))
body.append(sub(210, 300, "gigi 85, skema bitewing", anchor="middle", size=15))
svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" '
       'role="img" aria-label="Ilustrasi skematik bitewing gigi 85: karies distal mendekati pulpa dengan dentine bridge">%s</svg>'
       % (W, H, W, H, "".join(body)))
open(os.path.join(HERE, "fig-case-bitewing.svg"), "w", encoding="utf-8").write(svg)

print("wrote fig-case-oklusal.svg dan fig-case-bitewing.svg")
