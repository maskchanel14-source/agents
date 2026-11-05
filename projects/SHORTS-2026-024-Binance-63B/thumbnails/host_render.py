"""Render the real DiceBear host (src/host/parts.ts) to a transparent PNG.
Replicates the rig in src/host.tsx statically, with a pose chosen for a thumbnail."""
import re, sys, io
PARTS = '/home/user/agents/media-production/src/host/parts.ts'
src = open(PARTS).read()

def grab(name):
    m = re.search(r'export const HOST_%s: HostPart = \{id: .(\w+)., x: ([\d.]+), y: ([\d.]+), body: `(.*?)`\};' % name, src, re.S)
    return {'id': m.group(1), 'x': float(m.group(2)), 'y': float(m.group(3)), 'body': m.group(4)}

P = {n: grab(n) for n in ('HEAD','CLOTHES','HAIR','MOUTH','NOSE','EYES','GLASSES','BROWS')}
gsec = src[src.index('export const HOST_GESTURES'):]
G = {}
for m in re.finditer(r"(\w+): \{id: '(\w+)', x: (-?[\d.]+), y: (-?[\d.]+), body: `(.*?)`\}", gsec, re.S):
    G[m.group(1)] = {'id': m.group(2), 'x': float(m.group(3)), 'y': float(m.group(4)), 'body': m.group(5)}

VIEW = (172, 234, 1372, 1538)
CENTRES = {'mouth': (127.45, 78), 'eyes': (135.5, 46.85), 'hair': (529.5, 488.5), 'head': (292.5, 492.5)}

def part(p, transform=None):
    t = f'translate({p["x"]} {p["y"]})'
    if transform: t += ' ' + transform
    return f'<g transform="{t}">{p["body"]}</g>'

def about_centre(p, sx, sy, dx=0, dy=0):
    cx, cy = CENTRES.get(p['id'], (0, 0))
    return f'translate({cx+dx} {cy+dy}) scale({sx} {sy}) translate({-(cx+dx)} {-(cy+dy)})'

def build(gesture='pointLongArm', mouth=0.55, brow=1.0, rot=0.0, g_rot=0.0, bob=0.0):
    m = max(0.0, min(1.0, mouth))
    open_ = 0.09 + 0.91 * m ** 0.85
    narrow = 1 - 0.1 * m
    head_t = f'translate(0 {bob}) rotate({rot} 930 1180)'
    g = G[gesture]
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{VIEW[0]} {VIEW[1]} {VIEW[2]} {VIEW[3]}" '
            f'width="{VIEW[2]}" height="{VIEW[3]}">'
            f'<g transform="{head_t}">{part(P["HEAD"])}</g>'
            f'{part(P["CLOTHES"])}'
            f'<g transform="{head_t}">'
            f'{part(P["HAIR"])}'
            f'{part(P["MOUTH"], about_centre(P["MOUTH"], narrow, open_))}'
            f'{part(P["NOSE"])}'
            f'{part(P["EYES"], about_centre(P["EYES"], 1, 1))}'
            f'{part(P["GLASSES"])}'
            f'{part(P["BROWS"], f"translate(0 {-7*brow})")}'
            f'</g>'
            f'<g transform="rotate({g_rot} 700 1250)">{part(g)}</g>'
            f'</svg>')
