"""Build the clickbait thumbnail for SHORTS-2026-024B.

Standard: what a 50-million-subscriber channel would publish. That means

  * one idea, three words, legible at a 100 px tile — nothing else on screen;
  * a face big enough to read the emotion (26 % of frame height) with a hard
    sticker outline so it separates from any background;
  * bright, saturated, high-key art — dark muddy thumbnails do not get clicked;
  * strict size hierarchy: kicker → number → bar, nothing in between.

The host is NOT redrawn: he is the same DiceBear Notionists character the film
uses (CC0 1.0, Zoish), read out of media-production/src/host/parts.ts and
rasterised with resvg in the `pointLongArm` pose — brow raised, mid-sentence —
so the thumbnail and the film show the same person. The background is generated
art, thrown out of focus and graded high-key; every glyph is drawn with PIL, so
the spelling is exact at any size.

Reproduce with:
    pip install --break-system-packages pillow numpy resvg-py fonttools brotli
    npm install --prefix /tmp/fonts @fontsource/anton @fontsource/inter
    python3 -c "from fontTools.ttLib import TTFont; import glob; \\
        TTFont('/tmp/fonts/node_modules/@fontsource/anton/files/anton-latin-400-normal.woff').save('/tmp/fonts/Anton.ttf'); \\
        TTFont(sorted(glob.glob('/tmp/fonts/node_modules/@fontsource/inter/files/inter-latin-8*-normal.woff'))[-1]).save('/tmp/fonts/Inter-Black.ttf')"
    python3 build_thumbnail.py
"""
import io, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from host_render import build as build_host_svg
import resvg_py

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1920
BG = os.path.join(HERE, '_bg_source.png')
OUT = os.path.join(HERE, '01_THUMBNAIL_1080x1920.png')
SMALL = os.path.join(HERE, '01_THUMBNAIL_540x960.png')

PAPER = (255, 252, 246)
GOLD = (255, 198, 58)
RED = (255, 45, 58)
INK = (8, 13, 26)

ANTON = '/tmp/fonts/Anton.ttf'
INTER_B = '/tmp/fonts/Inter-Black.ttf'


def font(path, size):
    return ImageFont.truetype(path, size)


def text_w(draw, s, f, spacing=0):
    if not spacing:
        return draw.textbbox((0, 0), s, font=f)[2]
    return sum(draw.textbbox((0, 0), c, font=f)[2] for c in s) + spacing * (len(s) - 1)


def draw_tracked(draw, xy, s, f, fill, spacing=0, stroke=0, sc=INK):
    x, y = xy
    for c in s:
        draw.text((x, y), c, font=f, fill=fill, stroke_width=stroke, stroke_fill=sc)
        x += draw.textbbox((0, 0), c, font=f)[2] + spacing
    return x


def drop_shadow(base, layer_fn, blur=22):
    """Blur a copy of `layer_fn` and paste it under the crisp version."""
    sh = Image.new('RGBA', base.size, (0, 0, 0, 0))
    layer_fn(ImageDraw.Draw(sh))
    base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(blur)))


# ---------------------------------------------------------------- background
# The generated art is a texture, not the subject: throw it out of focus so it
# reads as depth, then grade it high-key. Dark thumbnails do not get clicked.
bg = Image.open(BG).convert('RGB').resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(32))
a = np.asarray(bg, dtype=np.float32) / 255
a = np.clip(a, 0, 1) ** 0.55                       # lift hard
a = np.clip(a * 1.34 + 0.10, 0, 1)                 # brighten, keep a floor
yy = np.linspace(0, 1, H, dtype=np.float32)[:, None]
a = a * (1 - 0.28 * np.clip((0.34 - yy) / 0.34, 0, 1)[..., None])   # navy wash up top
a = a * (1 - 0.30 * np.clip((yy - 0.66) / 0.34, 0, 1)[..., None])   # ground the bottom
a[..., 0] *= 1.05
a[..., 2] *= 0.92                                  # warmer
img = Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8), 'RGB').convert('RGBA')

# big warm burst behind the host so his head sits on light, not on mush
burst = Image.new('RGBA', (W, H), (0, 0, 0, 0))
bd = ImageDraw.Draw(burst)
cx, cy, r = 430, 1080, 760
# NB: vary the ALPHA, not the colour — an opaque near-black disc would paint
# the background out instead of lighting it.
for i in range(30, 0, -1):
    rr = r * i / 30
    t = (1 - i / 30) ** 2
    bd.ellipse([cx - rr, cy - rr, cx + rr, cy + rr],
               fill=(255, 176, 52, int(255 * t * 0.92)))
burst = burst.filter(ImageFilter.GaussianBlur(120))
img = Image.alpha_composite(img, burst)

# crisp light rays for depth
rays = Image.new('RGBA', (W, H), (0, 0, 0, 0))
rd = ImageDraw.Draw(rays)
for ang, wd, al in ((-38, 190, 26), (-14, 120, 20), (26, 150, 18), (58, 90, 14)):
    box = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(box).polygon([(cx, cy),
                                 (cx + 3000 * np.cos(np.radians(ang - wd / 2)), cy + 3000 * np.sin(np.radians(ang - wd / 2))),
                                 (cx + 3000 * np.cos(np.radians(ang + wd / 2)), cy + 3000 * np.sin(np.radians(ang + wd / 2)))],
                                fill=(255, 214, 130, al))
    rays = Image.alpha_composite(rays, box)
rays = rays.filter(ImageFilter.GaussianBlur(60))
img = Image.alpha_composite(img, rays)

if os.environ.get('DUMP'):
    img.convert('RGB').save('/tmp/thumb/_0_bg.png')

# ---------------------------------------------------------------------- host
# Big: the face must read the emotion. Measured fractions of the drawn bust:
# hair top 0.005, face 0.200-0.550 of the height.
HH, HX, HY = 1380, -230, 680
hp = Image.open(io.BytesIO(bytes(resvg_py.svg_to_bytes(
    svg_string=build_host_svg('pointLongArm', mouth=0.62, brow=1.0))))).convert('RGBA')
hw = int(hp.width * HH / hp.height)
hp = hp.resize((hw, HH), Image.LANCZOS)
alpha0 = hp.split()[3]

# 1. hard sticker outline — how the big channels keep a subject off the art
out = Image.new('RGBA', hp.size, (0, 0, 0, 0))
out.putalpha(alpha0.filter(ImageFilter.MaxFilter(21)))
out = Image.new('RGBA', hp.size, INK + (255,))
out.putalpha(Image.eval(alpha0.filter(ImageFilter.MaxFilter(21)), lambda v: int(v * 0.96)))
out = out.filter(ImageFilter.GaussianBlur(2))

# 2. warm rim inside the outline
big = alpha0.filter(ImageFilter.MaxFilter(11))
rim = Image.new('RGBA', hp.size, (0, 0, 0, 0))
rim.putalpha(Image.eval(ImageChops.subtract(big, alpha0), lambda v: int(min(255, v * 1.7))))
rim.paste((255, 226, 170, 255), (0, 0), rim.split()[3])
rim = rim.filter(ImageFilter.GaussianBlur(3))

# 3. contact shadow
shadow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
shadow.alpha_composite(Image.new('RGBA', (hw, HH), (0, 0, 0, 200)), (HX + 12, HY + 26))
shadow.putalpha(shadow.split()[3].filter(ImageFilter.GaussianBlur(26)))
img = Image.alpha_composite(img, shadow)

for layer in (out, rim, hp):
    plate = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    plate.paste(layer, (HX, HY), layer if layer is hp else layer)
    img = Image.alpha_composite(img, plate)

if os.environ.get('DUMP'):
    img.convert('RGB').save('/tmp/thumb/_A_bg_host.png')

# ---------------------------------------------------------------- typography
# Three sizes only. Kicker → number → bar. Everything above the hair line
# (y 627) and inside a 90 px side margin.
f_kick = font(INTER_B, 54)
f_num = font(ANTON, 420)
f_bar = font(INTER_B, 66)

sizer = ImageDraw.Draw(img)
kick = 'LARGEST CRYPTO HEIST'
num = '$6.3B'
bar = 'GONE IN 20 MINUTES'
RIGHT, LEFT = 990, 90


def block(d, text, f, size, xy, fill, spacing, stroke, sc=INK, shadow=True):
    if shadow:
        drop_shadow(img, lambda dd: draw_tracked(dd, (xy[0], xy[1] + 12), text, f,
                                                 (0, 0, 0, 210), spacing, stroke, (0, 0, 0, 210)), blur=26)
    draw_tracked(d, xy, text, f, fill, spacing, stroke, sc)


d = ImageDraw.Draw(img)
# kicker, top left
block(d, kick, f_kick, 54, (LEFT, 70), PAPER, 8, stroke=9)

# the number — the one thing you read first
w1 = text_w(sizer, num, f_num)
block(d, num, f_num, 420, (RIGHT - w1, 150), PAPER, 0, stroke=20)

# gold rule + bar
bwd = text_w(sizer, bar, f_bar, 4) + 60
bx2, by2, bh2 = RIGHT - bwd, 480, 104
sh = Image.new('RGBA', (W, H), (0, 0, 0, 0))
ImageDraw.Draw(sh).rounded_rectangle([bx2 + 6, by2 + 12, bx2 + bwd + 6, by2 + bh2 + 12], radius=12, fill=(0, 0, 0, 200))
img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(22)))
d.rounded_rectangle([bx2, by2, bx2 + bwd, by2 + bh2], radius=12, fill=RED)
draw_tracked(d, (bx2 + 30, by2 + 22), bar, f_bar, PAPER, 4)

if os.environ.get('DUMP'):
    img.convert('RGB').save('/tmp/thumb/_B_all.png')

# ----------------------------------------------------------------- vignette
xx = np.linspace(-1, 1, W, dtype=np.float32)[None, :]
yy2 = np.linspace(-1, 1, H, dtype=np.float32)[:, None]
rr = np.sqrt(xx ** 2 * 0.52 + yy2 ** 2 * 0.40)
vg = np.clip((rr - 0.72) / 0.70, 0, 1) ** 1.4 * 0.30
arr = np.asarray(img.convert('RGB'), np.float32) * (1 - vg[..., None])
img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), 'RGB')

img.save(OUT)
img.resize((540, 960), Image.LANCZOS).save(SMALL)
print('wrote', OUT, img.size)
