/**
 * Procedural PBR materials for the semi-realist town.
 *
 * Every map is generated on a canvas at startup — there are no binary assets
 * in this repo, and the output must be byte-identical on every machine, so all
 * randomness comes from the seeded `mulberry32` in world.ts.
 *
 * Four maps per surface:
 *   map           albedo, sRGB
 *   bumpMap       height (three takes the screen-space derivative of this)
 *   roughnessMap  per-texel roughness — this is what stops everything from
 *                 looking like the same plastic
 *   emissiveMap   lit windows only
 *
 * Textures are `clone()`d per building so each facade can tile at its own
 * repeat while still sharing one GPU upload (three shares `texture.source`
 * across clones).
 */

import {
  CanvasTexture,
  Color,
  MeshStandardMaterial,
  RepeatWrapping,
  SRGBColorSpace,
  type Texture,
} from 'three';
import {PALETTE, SURFACE, type SurfaceName} from './theme';
import {mulberry32} from './world';

/* ------------------------------------------------------------------ noise */

type NoiseFn = (u: number, v: number) => number;

/** Tiling value-noise fBm. Deterministic for a given seed. */
const makeFbm = (rnd: () => number, octaves = 4, base = 4): NoiseFn => {
  const grids: Float32Array[] = [];
  const sizes: number[] = [];
  let n = base;
  for (let o = 0; o < octaves; o += 1) {
    const g = new Float32Array(n * n);
    for (let i = 0; i < n * n; i += 1) g[i] = rnd();
    grids.push(g);
    sizes.push(n);
    n *= 2;
  }
  return (u, v) => {
    let sum = 0;
    let amp = 0.5;
    let norm = 0;
    for (let o = 0; o < octaves; o += 1) {
      const nn = sizes[o];
      const g = grids[o];
      const x = u * nn;
      const y = v * nn;
      const x0 = Math.floor(x) % nn;
      const y0 = Math.floor(y) % nn;
      const x1 = (x0 + 1) % nn;
      const y1 = (y0 + 1) % nn;
      let fx = x - Math.floor(x);
      let fy = y - Math.floor(y);
      fx = fx * fx * (3 - 2 * fx);
      fy = fy * fy * (3 - 2 * fy);
      const a = g[y0 * nn + x0];
      const b = g[y0 * nn + x1];
      const c = g[y1 * nn + x0];
      const d = g[y1 * nn + x1];
      const top = a + (b - a) * fx;
      const bot = c + (d - c) * fx;
      sum += (top + (bot - top) * fy) * amp;
      norm += amp;
      amp *= 0.5;
    }
    return sum / norm;
  };
};

/* --------------------------------------------------------------- canvases */

const canvasOf = (size: number) => {
  const c = document.createElement('canvas');
  c.width = size;
  c.height = size;
  return c;
};

const hexToRgb255 = (hex: string): [number, number, number] => {
  const v = parseInt(hex.slice(1), 16);
  return [(v >> 16) & 255, (v >> 8) & 255, v & 255];
};

const mix255 = (
  a: [number, number, number],
  b: [number, number, number],
  t: number,
): [number, number, number] => [
  a[0] + (b[0] - a[0]) * t,
  a[1] + (b[1] - a[1]) * t,
  a[2] + (b[2] - a[2]) * t,
];

/** Per-pixel fBm mottling + fine grain, written over whatever is already there. */
const mottle = (
  ctx: CanvasRenderingContext2D,
  S: number,
  base: [number, number, number],
  rnd: () => number,
  opts: {coarse?: number; fine?: number; darkTo?: [number, number, number]} = {},
) => {
  const coarse = opts.coarse ?? 0.16;
  const fine = opts.fine ?? 0.05;
  const dark: [number, number, number] = opts.darkTo ?? [0, 0, 0];
  const fbm = makeFbm(rnd, 4, 4);
  const grain = makeFbm(rnd, 2, 96);
  const img = ctx.getImageData(0, 0, S, S);
  const d = img.data;
  for (let y = 0; y < S; y += 1) {
    for (let x = 0; x < S; x += 1) {
      const u = x / S;
      const v = y / S;
      const n = fbm(u, v) - 0.5;
      const g = grain(u, v) - 0.5;
      const t = n * coarse + g * fine;
      const c = t < 0 ? mix255(base, dark, -t * 2) : mix255(base, [255, 255, 255], t);
      const i = (y * S + x) * 4;
      d[i] = c[0];
      d[i + 1] = c[1];
      d[i + 2] = c[2];
      d[i + 3] = 255;
    }
  }
  ctx.putImageData(img, 0, 0);
};

const makeTex = (
  c: HTMLCanvasElement,
  srgb: boolean,
  repeat: number,
  aniso = 4,
): CanvasTexture => {
  const t = new CanvasTexture(c);
  if (srgb) t.colorSpace = SRGBColorSpace;
  t.wrapS = RepeatWrapping;
  t.wrapT = RepeatWrapping;
  t.repeat.set(repeat, repeat);
  t.anisotropy = aniso;
  return t;
};

/* ---------------------------------------------------------------- facades */

type WinRect = {x: number; y: number; w: number; h: number; lit: boolean};

const layoutWindows = (
  S: number,
  cols: number,
  rows: number,
  litChance: number,
  rnd: () => number,
): WinRect[] => {
  const mx = S * 0.05;
  const my = S * 0.06;
  const cw = (S - mx * 2) / cols;
  const ch = (S - my * 2) / rows;
  const out: WinRect[] = [];
  for (let r = 0; r < rows; r += 1) {
    for (let c = 0; c < cols; c += 1) {
      const padX = cw * 0.22;
      const padY = ch * 0.20;
      out.push({
        x: mx + c * cw + padX,
        y: my + r * ch + padY,
        w: cw - padX * 2,
        h: ch - padY * 2 - ch * 0.12,
        lit: rnd() < litChance,
      });
    }
  }
  return out;
};

type FacadeOpts = {
  seed: number;
  wall: string;
  cols: number;
  rows: number;
  litChance: number;
  glass?: string;
  /** Extra horizontal banding (floor slabs). */
  banding?: number;
};

type FacadeMaps = {
  map: CanvasTexture;
  bumpMap: CanvasTexture;
  roughnessMap: CanvasTexture;
  emissiveMap: CanvasTexture;
};

/**
 * One facade variant. The four canvases are drawn from the same window layout
 * so albedo, height, roughness and emission stay registered to each other.
 */
const buildFacade = (o: FacadeOpts, S = 512): FacadeMaps => {
  const rnd = mulberry32(o.seed);
  const wall = hexToRgb255(o.wall);
  const glass = hexToRgb255(o.glass ?? PALETTE.glass);
  const lit = hexToRgb255(PALETTE.glassLit);
  const banding = o.banding ?? 0.05;

  const wins = layoutWindows(S, o.cols, o.rows, o.litChance, rnd);

  // --- albedo -------------------------------------------------------------
  const cMap = canvasOf(S);
  const xMap = cMap.getContext('2d')!;
  xMap.fillStyle = `rgb(${wall[0]},${wall[1]},${wall[2]})`;
  xMap.fillRect(0, 0, S, S);
  mottle(xMap, S, wall, rnd, {coarse: 0.20, fine: 0.05, darkTo: [40, 34, 30]});

  // floor slabs
  const rowsN = o.rows;
  for (let r = 0; r <= rowsN; r += 1) {
    const y = S * 0.06 + (r * (S * 0.88)) / rowsN;
    xMap.fillStyle = `rgba(30,26,24,${banding})`;
    xMap.fillRect(0, y - S * 0.006, S, S * 0.012);
    xMap.fillStyle = `rgba(255,250,240,${banding * 0.55})`;
    xMap.fillRect(0, y + S * 0.006, S, S * 0.006);
  }

  // windows
  for (const w of wins) {
    // reveal / frame
    xMap.fillStyle = 'rgba(24,20,18,0.55)';
    xMap.fillRect(w.x - 3, w.y - 3, w.w + 6, w.h + 6);
    xMap.fillStyle = `rgba(232,226,214,${0.16 + rnd() * 0.10})`;
    xMap.fillRect(w.x - 3, w.y - 3, w.w + 6, 3);
    // glass
    if (w.lit) {
      const g = xMap.createLinearGradient(0, w.y, 0, w.y + w.h);
      g.addColorStop(0, `rgb(${lit[0]},${lit[1]},${lit[2]})`);
      g.addColorStop(1, `rgb(${Math.round(lit[0] * 0.72)},${Math.round(lit[1] * 0.6)},${Math.round(lit[2] * 0.45)})`);
      xMap.fillStyle = g;
    } else {
      // dark glass, slightly lighter at the top where it catches the sky
      const g = xMap.createLinearGradient(0, w.y, 0, w.y + w.h);
      g.addColorStop(0, `rgb(${Math.round(glass[0] * 1.5)},${Math.round(glass[1] * 1.5)},${Math.round(glass[2] * 1.4)})`);
      g.addColorStop(1, `rgb(${Math.round(glass[0] * 0.7)},${Math.round(glass[1] * 0.7)},${Math.round(glass[2] * 0.7)})`);
      xMap.fillStyle = g;
    }
    xMap.fillRect(w.x, w.y, w.w, w.h);
    // mullion
    xMap.fillStyle = 'rgba(20,18,16,0.45)';
    xMap.fillRect(w.x + w.w / 2 - 1, w.y, 2, w.h);
  }

  // grime running down from the sills
  for (const w of wins) {
    if (rnd() > 0.45) continue;
    xMap.fillStyle = `rgba(38,32,28,${0.05 + rnd() * 0.07})`;
    xMap.fillRect(w.x, w.y + w.h, w.w, S * (0.02 + rnd() * 0.06));
  }

  // --- bump ---------------------------------------------------------------
  const cBump = canvasOf(S);
  const xBump = cBump.getContext('2d')!;
  xBump.fillStyle = '#808080';
  xBump.fillRect(0, 0, S, S);
  mottle(xBump, S, [128, 128, 128], rnd, {coarse: 0.35, fine: 0.30});
  for (const w of wins) {
    // recessed glazing
    xBump.fillStyle = '#3A3A3A';
    xBump.fillRect(w.x - 3, w.y - 3, w.w + 6, w.h + 6);
    // proud sill
    xBump.fillStyle = '#B4B4B4';
    xBump.fillRect(w.x - 5, w.y + w.h + 2, w.w + 10, 5);
  }

  // --- roughness ----------------------------------------------------------
  const cRough = canvasOf(S);
  const xRough = cRough.getContext('2d')!;
  const wallR = Math.round(SURFACE.concrete.roughness * 255);
  xRough.fillStyle = `rgb(${wallR},${wallR},${wallR})`;
  xRough.fillRect(0, 0, S, S);
  mottle(xRough, S, [wallR, wallR, wallR], rnd, {coarse: 0.30, fine: 0.22});
  for (const w of wins) {
    // glass is smooth → low roughness → it picks up the environment
    xRough.fillStyle = 'rgb(28,28,28)';
    xRough.fillRect(w.x - 3, w.y - 3, w.w + 6, w.h + 6);
  }

  // --- emissive -----------------------------------------------------------
  const cEmis = canvasOf(S);
  const xEmis = cEmis.getContext('2d')!;
  xEmis.fillStyle = '#000000';
  xEmis.fillRect(0, 0, S, S);
  for (const w of wins) {
    if (!w.lit) continue;
    xEmis.fillStyle = `rgb(${lit[0]},${lit[1]},${lit[2]})`;
    xEmis.fillRect(w.x, w.y, w.w, w.h);
    // a soft bloom-ish halo outside the frame
    const g = xEmis.createRadialGradient(
      w.x + w.w / 2, w.y + w.h / 2, 1,
      w.x + w.w / 2, w.y + w.h / 2, w.w * 1.3,
    );
    g.addColorStop(0, `rgba(${lit[0]},${lit[1]},${lit[2]},0.45)`);
    g.addColorStop(1, 'rgba(0,0,0,0)');
    xEmis.fillStyle = g;
    xEmis.fillRect(w.x - w.w, w.y - w.h, w.w * 3, w.h * 3);
  }

  return {
    map: makeTex(cMap, true, 1),
    bumpMap: makeTex(cBump, false, 1),
    roughnessMap: makeTex(cRough, false, 1),
    emissiveMap: makeTex(cEmis, true, 1),
  };
};

/* --------------------------------------------------------- simple surfaces */

type PlainMaps = {map: CanvasTexture; bumpMap: CanvasTexture; roughnessMap: CanvasTexture};

/** One-colour surface with fBm mottling — plaster, brick, slate, asphalt… */
const buildPlain = (
  seed: number,
  hex: string,
  repeat: number,
  s: SurfaceName,
  extra?: (ctx: CanvasRenderingContext2D, S: number, rnd: () => number) => void,
  S = 256,
): PlainMaps => {
  const rnd = mulberry32(seed);
  const base = hexToRgb255(hex);

  const cMap = canvasOf(S);
  const xMap = cMap.getContext('2d')!;
  xMap.fillStyle = `rgb(${base[0]},${base[1]},${base[2]})`;
  xMap.fillRect(0, 0, S, S);
  mottle(xMap, S, base, rnd, {coarse: 0.18, fine: 0.06, darkTo: [34, 30, 28]});
  if (extra) extra(xMap, S, rnd);

  const cBump = canvasOf(S);
  const xBump = cBump.getContext('2d')!;
  xBump.fillStyle = '#808080';
  xBump.fillRect(0, 0, S, S);
  mottle(xBump, S, [128, 128, 128], rnd, {coarse: 0.35, fine: 0.30});
  if (extra) {
    // keep the raised pattern registered with the albedo overlay
    extra(xBump, S, mulberry32(seed));
  }

  const cRough = canvasOf(S);
  const xRough = cRough.getContext('2d')!;
  const rv = Math.max(0, Math.min(255, Math.round(SURFACE[s].roughness * 255)));
  xRough.fillStyle = `rgb(${rv},${rv},${rv})`;
  xRough.fillRect(0, 0, S, S);
  mottle(xRough, S, [rv, rv, rv], rnd, {coarse: 0.28, fine: 0.20});

  return {
    map: makeTex(cMap, true, repeat),
    bumpMap: makeTex(cBump, false, repeat),
    roughnessMap: makeTex(cRough, false, repeat),
  };
};

/** Mortar grid — stone paving for the vault plaza. */
const pavingExtra = (ctx: CanvasRenderingContext2D, S: number) => {
  const n = 6;
  const step = S / n;
  ctx.strokeStyle = 'rgba(38,34,30,0.55)';
  ctx.lineWidth = Math.max(1, S * 0.008);
  for (let i = 0; i <= n; i += 1) {
    ctx.beginPath();
    ctx.moveTo(i * step, 0);
    ctx.lineTo(i * step, S);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(0, i * step);
    ctx.lineTo(S, i * step);
    ctx.stroke();
  }
};

/** Asphalt: cracks, patches and a faint crown. */
const asphaltExtra = (ctx: CanvasRenderingContext2D, S: number, rnd: () => number) => {
  for (let i = 0; i < 26; i += 1) {
    ctx.strokeStyle = `rgba(24,24,26,${0.18 + rnd() * 0.25})`;
    ctx.lineWidth = 1 + rnd() * 2;
    ctx.beginPath();
    let x = rnd() * S;
    let y = rnd() * S;
    ctx.moveTo(x, y);
    for (let k = 0; k < 5; k += 1) {
      x += (rnd() - 0.5) * S * 0.28;
      y += (rnd() - 0.5) * S * 0.28;
      ctx.lineTo(x, y);
    }
    ctx.stroke();
  }
  for (let i = 0; i < 14; i += 1) {
    ctx.fillStyle = `rgba(84,82,80,${0.05 + rnd() * 0.10})`;
    ctx.beginPath();
    ctx.ellipse(rnd() * S, rnd() * S, S * (0.03 + rnd() * 0.09), S * (0.02 + rnd() * 0.06), rnd() * 3, 0, Math.PI * 2);
    ctx.fill();
  }
};

/** Brushed metal — fine directional scratches. */
const metalExtra = (ctx: CanvasRenderingContext2D, S: number, rnd: () => number) => {
  for (let i = 0; i < 900; i += 1) {
    const y = rnd() * S;
    const x = rnd() * S;
    const len = S * (0.01 + rnd() * 0.10);
    ctx.strokeStyle = `rgba(255,255,255,${rnd() * 0.06})`;
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(x, y);
    ctx.lineTo(x + len, y + (rnd() - 0.5) * 1.2);
    ctx.stroke();
  }
};

/** Shingle courses for the pyramid roofs. */
const shingleExtra = (ctx: CanvasRenderingContext2D, S: number, rnd: () => number) => {
  const rows = 10;
  const step = S / rows;
  for (let r = 0; r < rows; r += 1) {
    ctx.fillStyle = `rgba(20,20,24,${0.20 + rnd() * 0.12})`;
    ctx.fillRect(0, r * step + step * 0.72, S, step * 0.28);
    const cols = 12;
    const cw = S / cols;
    for (let c = 0; c < cols; c += 1) {
      ctx.fillStyle = `rgba(255,255,255,${rnd() * 0.05})`;
      ctx.fillRect(c * cw + ((r % 2) * cw) / 2, r * step, cw * 0.92, step * 0.7);
    }
  }
};

/* ------------------------------------------------------------ contact AO */

/**
 * A soft radial blob used as a contact-shadow decal under the cast and under
 * the landmarks. Real shadow maps are too coarse to catch the point where a
 * foot meets the ground; this is the trick that sells the contact.
 */
export const buildContactShadowTexture = (): CanvasTexture => {
  const S = 128;
  const c = canvasOf(S);
  const ctx = c.getContext('2d')!;
  const g = ctx.createRadialGradient(S / 2, S / 2, 0, S / 2, S / 2, S / 2);
  g.addColorStop(0, 'rgba(0,0,0,0.62)');
  g.addColorStop(0.45, 'rgba(0,0,0,0.34)');
  g.addColorStop(0.78, 'rgba(0,0,0,0.08)');
  g.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, S, S);
  const t = new CanvasTexture(c);
  t.anisotropy = 2;
  return t;
};

/* ------------------------------------------------------------ the library */

export type SurfaceMaps = {
  map: Texture;
  bumpMap?: Texture | null;
  roughnessMap?: Texture | null;
  emissiveMap?: Texture | null;
};

export type MaterialLibrary = {
  /** Building facades, already varied. Call `facadeFor()` to pick one. */
  facades: Array<{
    maps: FacadeMaps;
    make: (repeatX: number, repeatY: number) => MeshStandardMaterial;
    cache: Map<string, MeshStandardMaterial>;
  }>;
  plaster: MeshStandardMaterial;
  brick: MeshStandardMaterial;
  slate: MeshStandardMaterial;
  roof: MeshStandardMaterial;
  ground: MeshStandardMaterial;
  plaza: MeshStandardMaterial;
  brass: MeshStandardMaterial;
  steel: MeshStandardMaterial;
  glass: MeshStandardMaterial;
  glassLit: MeshStandardMaterial;
  stone: MeshStandardMaterial;
  concrete: MeshStandardMaterial;
  /** Figure materials. */
  skin: MeshStandardMaterial;
  skinDeep: MeshStandardMaterial;
  cloth: MeshStandardMaterial;
  clothWarm: MeshStandardMaterial;
  hoodie: MeshStandardMaterial;
  hair: MeshStandardMaterial;
  shoe: MeshStandardMaterial;
  eye: MeshStandardMaterial;
  ice: MeshStandardMaterial;
  contactShadow: CanvasTexture;
};

let LIB: MaterialLibrary | null = null;

const standard = (
  hex: string,
  s: SurfaceName,
  maps: Partial<SurfaceMaps> = {},
  extra: Partial<{
    emissive: string;
    emissiveIntensity: number;
    envMapIntensity: number;
    transparent: boolean;
    opacity: number;
  }> = {},
) => {
  const m = new MeshStandardMaterial({
    color: new Color(hex),
    roughness: SURFACE[s].roughness,
    metalness: SURFACE[s].metalness,
    ...maps,
    ...(extra.emissive
      ? {emissive: new Color(extra.emissive), emissiveIntensity: extra.emissiveIntensity ?? 1}
      : {}),
    ...(extra.transparent ? {transparent: true, opacity: extra.opacity ?? 1} : {}),
  });
  if (maps.bumpMap) m.bumpScale = SURFACE[s].bump;
  m.envMapIntensity = extra.envMapIntensity ?? 1;
  return m;
};

/**
 * Built once, lazily. Components call this instead of `useMemo` per component —
 * the old code rebuilt six 256² painted textures in *every* component that
 * needed them, which meant seven separate sets of identical textures.
 */
export const getMaterials = (): MaterialLibrary => {
  if (LIB) return LIB;

  const FACADE_SPECS: FacadeOpts[] = [
    {seed: 101, wall: PALETTE.concrete, cols: 3, rows: 4, litChance: 0.30},
    {seed: 202, wall: PALETTE.plaster, cols: 2, rows: 3, litChance: 0.22},
    {seed: 303, wall: PALETTE.brick, cols: 3, rows: 5, litChance: 0.26, banding: 0.03},
    {seed: 404, wall: PALETTE.slate, cols: 4, rows: 6, litChance: 0.34, glass: '#33506E'},
    {seed: 505, wall: PALETTE.stone, cols: 2, rows: 5, litChance: 0.18},
  ];

  const facades = FACADE_SPECS.map((spec) => {
    const maps = buildFacade(spec, 512);
    const cache = new Map<string, MeshStandardMaterial>();
    const make = (repeatX: number, repeatY: number) => {
      const key = `${repeatX}x${repeatY}`;
      const hit = cache.get(key);
      if (hit) return hit;
      const map = maps.map.clone();
      const bumpMap = maps.bumpMap.clone();
      const roughnessMap = maps.roughnessMap.clone();
      const emissiveMap = maps.emissiveMap.clone();
      map.needsUpdate = true;
      bumpMap.needsUpdate = true;
      roughnessMap.needsUpdate = true;
      emissiveMap.needsUpdate = true;
      map.repeat.set(repeatX, repeatY);
      bumpMap.repeat.set(repeatX, repeatY);
      roughnessMap.repeat.set(repeatX, repeatY);
      emissiveMap.repeat.set(repeatX, repeatY);
      const m = new MeshStandardMaterial({
        color: new Color('#ffffff'),
        map,
        bumpMap,
        roughnessMap,
        emissiveMap,
        emissive: new Color(PALETTE.glassLit),
        emissiveIntensity: 0.9,
        roughness: 1.0,
        metalness: 0.0,
        envMapIntensity: 1.0,
      });
      m.bumpScale = SURFACE.concrete.bump;
      cache.set(key, m);
      return m;
    };
    return {maps, make, cache};
  });

  const groundMaps = buildPlain(909, PALETTE.asphalt, 90, 'asphalt', asphaltExtra, 512);
  // slate/plaza/concrete are built once and shared; see LIB below.
  const plazaMaps = buildPlain(808, PALETTE.stone, 7, 'stone', pavingExtra, 512);
  const brassMaps = buildPlain(707, PALETTE.brass, 2, 'brass', metalExtra, 256);
  const slateMaps = buildPlain(606, PALETTE.slate, 3, 'slate', undefined, 256);
  const roofMaps = buildPlain(5050, '#3E4652', 4, 'slate', shingleExtra, 256);
  const brickMaps = buildPlain(4040, PALETTE.brick, 3, 'brick', undefined, 256);
  const plasterMaps = buildPlain(3030, PALETTE.plaster, 2, 'plaster', undefined, 256);
  const concreteMaps = buildPlain(2020, PALETTE.concrete, 2, 'concrete', undefined, 256);

  const lib: MaterialLibrary = {
    facades,

    plaster: standard(PALETTE.plaster, 'plaster', plasterMaps, {envMapIntensity: 0.9}),
    brick: standard(PALETTE.brick, 'brick', brickMaps, {envMapIntensity: 0.9}),
    slate: standard(PALETTE.slate, 'slate', slateMaps, {envMapIntensity: 0.9}),
    roof: standard('#3E4652', 'slate', roofMaps, {envMapIntensity: 0.85}),
    concrete: standard(PALETTE.concrete, 'concrete', concreteMaps, {envMapIntensity: 0.9}),
    stone: standard(PALETTE.stone, 'stone', slateMaps, {envMapIntensity: 0.9}),
    plaza: standard(PALETTE.stone, 'stone', plazaMaps, {envMapIntensity: 0.9}),

    ground: (() => {
      const m = standard(PALETTE.asphalt, 'asphalt', groundMaps, {envMapIntensity: 0.7});
      if (m.map) m.map.anisotropy = 8;
      return m;
    })(),

    brass: (() => {
      const m = standard(PALETTE.brass, 'brass', brassMaps, {envMapIntensity: 1.25});
      return m;
    })(),
    steel: standard(PALETTE.steel, 'steel', undefined, {envMapIntensity: 1.2}),
    glass: standard(PALETTE.glass, 'glass', undefined, {envMapIntensity: 1.5}),
    glassLit: standard(PALETTE.glassLit, 'glass', undefined, {
      emissive: PALETTE.glassLit,
      emissiveIntensity: 0.40,
      envMapIntensity: 1.4,
    }),

    skin: standard(PALETTE.skin, 'skin', undefined, {envMapIntensity: 0.55}),
    skinDeep: standard(PALETTE.skinDeep, 'skin', undefined, {envMapIntensity: 0.55}),
    cloth: standard(PALETTE.cloth, 'cloth', undefined, {envMapIntensity: 0.6}),
    clothWarm: standard(PALETTE.clothWarm, 'cloth', undefined, {envMapIntensity: 0.6}),
    hoodie: standard('#26262E', 'cloth', undefined, {envMapIntensity: 0.5}),
    hair: standard(PALETTE.hair, 'cloth', undefined, {envMapIntensity: 0.45}),
    shoe: standard(PALETTE.shoe, 'cloth', undefined, {envMapIntensity: 0.4}),
    eye: standard('#221C1E', 'glass', undefined, {envMapIntensity: 0.9}),
    ice: standard(PALETTE.ice, 'glass', undefined, {envMapIntensity: 1.3}),

    contactShadow: buildContactShadowTexture(),
  };

  LIB = lib;
  return lib;
};

/**
 * Pick a facade for building `i` at the right tiling scale. One window cell is
 * roughly 2.4 world units, so the repeat is derived from the box size — a
 * 3-unit cottage and an 11-unit block get the same window size.
 */
export const facadeFor = (
  lib: MaterialLibrary,
  i: number,
  width: number,
  height: number,
): MeshStandardMaterial => {
  const variant = lib.facades[i % lib.facades.length];
  const rx = Math.max(1, Math.min(4, Math.round(width / 2.4)));
  const ry = Math.max(1, Math.min(6, Math.round(height / 2.4)));
  return variant.make(rx, ry);
};
