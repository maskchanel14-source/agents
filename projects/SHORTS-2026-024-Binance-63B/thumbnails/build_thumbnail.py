"""Build the clickbait thumbnail for SHORTS-2026-024B.

Reproduce with:
    pip install --break-system-packages pillow numpy resvg-py fonttools brotli
    npm install --prefix /tmp/fonts @fontsource/anton @fontsource/inter
    python3 -c "from fontTools.ttLib import TTFont; import glob; \\
        TTFont('/tmp/fonts/node_modules/@fontsource/anton/files/anton-latin-400-normal.woff').save('/tmp/fonts/Anton.ttf'); \\
        TTFont(sorted(glob.glob('/tmp/fonts/node_modules/@fontsource/inter/files/inter-latin-8*-normal.woff'))[-1]).save('/tmp/fonts/Inter-Black.ttf'); \\
        TTFont(sorted(glob.glob('/tmp/fonts/node_modules/@fontsource/inter/files/inter-latin-6*-normal.woff'))[-1]).save('/tmp/fonts/Inter-Bold.ttf')"
    python3 build_thumbnail.py

The host is NOT redrawn for the thumbnail: he is the same DiceBear Notionists
character the film uses (CC0 1.0, Zoish), read out of
media-production/src/host/parts.ts and rasterised with resvg in the pose
`pointLongArm` — brow raised, mid-sentence — so the thumbnail and the film show
the same person. The background is generated art; every glyph is drawn with PIL
so the spelling is exact at any size.

Layout rule: all type lives above y 706, the host owns everything below y 766.
That keeps the two from colliding and keeps the type clear of the Shorts UI.
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

PAPER = (251, 247, 240)   # theme2d paper
GOLD = (232, 179, 58)     # theme2d gold
RED = (224, 51, 59)       # alarm accent, thumbnail only
INK = (11, 18, 32)        # theme2d ink

ANTON = '/tmp/fonts/Anton.ttf'
INTER_B = '/tmp/fonts/Inter-Black.ttf'
INTER = '/tmp/fonts/Inter-Bold.ttf'


def font(path, size):
    return ImageFont.truetype(path, size)


def text_w(draw, s, f, spacing=0):
    if not spacing:
        return draw.textbbox((0, 0), s, font=f)[2]
    return sum(draw.textbbox((0, 0), c, font=f)[2] for c in s) + spacing * (len(s) - 1)


def draw_tracked(draw, xy, s, f, fill, spacing=0, stroke=0, sc=INK):
    """Draw text with manual letterspacing and an outline."""
    x, y = xy
    for c in s:
        draw.text((x, y), c, font=f, fill=fill, stroke_width=stroke, stroke_fill=sc)
        x += draw.textbbox((0, 0), c, font=f)[2] + spacing
    return x


# ---------------------------------------------------------------- background
bg = Image.open(BG).convert('RGB').resize((W, H), Image.LANCZOS)
a = np.asarray(bg, dtype=np.float32) / 255
a = np.clip(a, 0, 1) ** 0.72 * 1.06          # lift the midtones
yy = np.linspace(0, 1, H, dtype=np.float32)[:, None]
a = a * (1 - 0.55 * np.clip((0.30 - yy) / 0.30, 0, 1)[..., None])   # keep the top dark
a = a * (1 - 0.72 * np.clip((yy - 0.62) / 0.38, 0, 1)[..., None])   # ground the bottom
a[..., 0] *= 1.03
a[..., 2] *= 0.97
img = Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8), 'RGB')

# amber glow behind the number stack
glow = Image.new('RGB', (W, H), (0, 0, 0))
gd = ImageDraw.Draw(glow)
cx, cy, r = 700, 470, 620
for i in range(28, 0, -1):
    rr = r * i / 28
    t = (1 - i / 28) ** 2
    gd.ellipse([cx - rr, cy - rr * 0.85, cx + rr, cy + rr * 0.85],
               fill=(int(232 * t * 0.55), int(170 * t * 0.45), int(60 * t * 0.25)))
glow = glow.filter(ImageFilter.GaussianBlur(90))
img = Image.blend(img, Image.fromarray(np.clip(
    np.asarray(img, np.float32) + np.asarray(glow, np.float32) * 0.85, 0, 255).astype(np.uint8)), 0.55)

if os.environ.get('DUMP'):
    img.save('/tmp/thumb/_0_bg.png')

# ---------------------------------------------------------------------- host
HH, HX, HY = 1200, -190, 760                  # measured: hair top 766, face 1000-1420
hp = Image.open(io.BytesIO(bytes(resvg_py.svg_to_bytes(
    svg_string=build_host_svg('pointLongArm', mouth=0.62, brow=1.0))))).convert('RGBA')
hw = int(hp.width * HH / hp.height)
hp = hp.resize((hw, HH), Image.LANCZOS)

# rim light: dilate the silhouette, keep only the ring, tint it warm
big = hp.split()[3].filter(ImageFilter.MaxFilter(9))
ring = Image.new('RGBA', hp.size, (0, 0, 0, 0))
ring.putalpha(Image.eval(ImageChops.subtract(big, hp.split()[3]), lambda v: int(v * 1.5)))
ring.paste((255, 226, 178, 255), (0, 0), ring.split()[3])
ring = ring.filter(ImageFilter.GaussianBlur(3))

# warm separation glow behind the head
headglow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
ImageDraw.Draw(headglow).ellipse([HX + 120, HY + 40, HX + 760, HY + 700], fill=(232, 179, 58, 120))
headglow = headglow.filter(ImageFilter.GaussianBlur(120))
img = Image.alpha_composite(img.convert('RGBA'), headglow).convert('RGB')

# drop shadow / ground contact
shadow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
shadow.alpha_composite(Image.new('RGBA', (hw, HH), (0, 0, 0, 190)), (HX + 14, HY + 18))
shadow.putalpha(shadow.split()[3].filter(ImageFilter.GaussianBlur(18)))
img = Image.alpha_composite(img.convert('RGBA'), shadow).convert('RGB')

rim = Image.new('RGBA', (W, H), (0, 0, 0, 0))
rim.paste(ring, (HX, HY), ring)
img = Image.alpha_composite(img.convert('RGBA'), rim).convert('RGB')
img.paste(hp, (HX, HY), hp)

if os.environ.get('DUMP'):
    img.save('/tmp/thumb/_A_bg_host.png')

d = ImageDraw.Draw(img)

# ---------------------------------------------------------------- typography
f_badge = font(INTER_B, 42)
badge = 'LARGEST CRYPTO HEIST'
bw = text_w(d, badge, f_badge, 6) + 56
bx, by, bh = 90, 88, 80
d.rounded_rectangle([bx, by, bx + bw, by + bh], radius=bh // 2, fill=RED)
draw_tracked(d, (bx + 28, by + 19), badge, f_badge, PAPER, 6)

RIGHT = 990
f_num = font(ANTON, 320)
f_bil = font(ANTON, 200)
w1 = text_w(d, '$6.3', f_num)
draw_tracked(d, (RIGHT - w1, 190), '$6.3', f_num, PAPER, 0, stroke=10, sc=(6, 10, 20))
w2 = text_w(d, 'BILLION', f_bil, 2)
d.line([(RIGHT - w2, 434), (RIGHT, 434)], fill=GOLD, width=9)
draw_tracked(d, (RIGHT - w2, 452), 'BILLION', f_bil, GOLD, 2, stroke=9, sc=(6, 10, 20))

f_bar = font(INTER_B, 64)
bar = 'GONE IN 20 MINUTES'
bwd = text_w(d, bar, f_bar, 2) + 56
bx2, by2, bh2 = RIGHT - bwd, 610, 96
d.rounded_rectangle([bx2, by2, bx2 + bwd, by2 + bh2], radius=10, fill=RED)
draw_tracked(d, (bx2 + 28, by2 + 20), bar, f_bar, PAPER, 2)

if os.environ.get('DUMP'):
    img.save('/tmp/thumb/_B_all.png')

# ----------------------------------------------------------------- vignette
xx = np.linspace(-1, 1, W, dtype=np.float32)[None, :]
yy2 = np.linspace(-1, 1, H, dtype=np.float32)[:, None]
rr = np.sqrt(xx ** 2 * 0.55 + yy2 ** 2 * 0.42)
vg = np.clip((rr - 0.62) / 0.75, 0, 1) ** 1.5 * 0.62
arr = np.asarray(img, np.float32) * (1 - vg[..., None])
img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), 'RGB')

img.save(OUT)
img.resize((540, 960), Image.LANCZOS).save(os.path.join(HERE, '01_THUMBNAIL_540x960.png'))
print('wrote', OUT, img.size)
