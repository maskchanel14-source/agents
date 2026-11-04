import {useMemo} from 'react';
import {
  CanvasTexture,
  Color,
  MeshStandardMaterial,
  RepeatWrapping,
  SRGBColorSpace,
} from 'three';
import {MATERIAL, PALETTE} from './theme';
import {posCurve} from './camera';

/**
 * The painted world: a low-poly town at dusk, a golden vault at its centre,
 * ten bridges fanning out behind it (one per blockchain), a clock tower and a
 * DevOps tower with one lit window.
 *
 * Everything is procedural and deterministic (seeded RNG), so the render is
 * byte-identical on every machine.
 */

// ---------------------------------------------------------------------------
// Deterministic RNG
// ---------------------------------------------------------------------------
export const mulberry32 = (seed: number) => () => {
  seed |= 0;
  seed = (seed + 0x6d2b79f5) | 0;
  let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
  t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
};

// ---------------------------------------------------------------------------
// Painted textures — hand-painted brush noise, never a flat fill
// ---------------------------------------------------------------------------
const paintTexture = (hex: string, seed: number, grain = 0.16) => {
  const S = 256;
  const c = document.createElement('canvas');
  c.width = S;
  c.height = S;
  const ctx = c.getContext('2d')!;
  const rnd = mulberry32(seed);
  const base = new Color(hex);

  ctx.fillStyle = `#${base.getHexString()}`;
  ctx.fillRect(0, 0, S, S);

  // Brush strokes: broad, soft, slightly lighter / darker variants.
  for (let i = 0; i < 150; i += 1) {
    const hsl = {h: 0, s: 0, l: 0};
    base.getHSL(hsl);
    const dl = (rnd() - 0.5) * 0.22;
    const col = new Color().setHSL(hsl.h, hsl.s, Math.min(0.95, Math.max(0.05, hsl.l + dl)));
    ctx.globalAlpha = 0.05 + rnd() * 0.1;
    ctx.fillStyle = `#${col.getHexString()}`;
    const w = 20 + rnd() * 90;
    const h = 8 + rnd() * 34;
    ctx.save();
    ctx.translate(rnd() * S, rnd() * S);
    ctx.rotate((rnd() - 0.5) * 1.1);
    ctx.beginPath();
    ctx.ellipse(0, 0, w / 2, h / 2, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  }

  // Dry-brush grain.
  ctx.globalAlpha = grain;
  for (let i = 0; i < 2600; i += 1) {
    const dark = rnd() > 0.5;
    ctx.fillStyle = dark ? 'rgba(42,46,107,0.5)' : 'rgba(247,255,247,0.5)';
    ctx.fillRect(rnd() * S, rnd() * S, 1 + rnd() * 2, 1);
  }
  ctx.globalAlpha = 1;

  // Baked ambient occlusion.
  //
  // A real `aoMap` needs a second UV set (`uv1`), which the JSX geometry
  // primitives don't create — assigning one silently drops the mesh from the
  // draw. Baking the contact shading into the albedo instead is both cheaper
  // and closer to how a painted texture actually looks.
  // Strength is MATERIAL.aoIntensity (0.6) → up to 45 % darkening at contact.
  const ao = ctx.createLinearGradient(0, S * 0.52, 0, S);
  ao.addColorStop(0, 'rgba(42,46,107,0)');
  ao.addColorStop(1, `rgba(42,46,107,${(MATERIAL.aoIntensity * 0.5).toFixed(3)})`);
  ctx.fillStyle = ao;
  ctx.fillRect(0, S * 0.52, S, S * 0.48);

  // Cavity burn along the tile edges.
  const edge = S * 0.09;
  for (const [x0, y0, gw, gh, gx0, gy0, gx1, gy1] of [
    [0, 0, edge, S, 0, 0, edge, 0],
    [S - edge, 0, edge, S, S, 0, S - edge, 0],
    [0, S - edge, S, edge, 0, S, 0, S - edge],
  ] as number[][]) {
    const g = ctx.createLinearGradient(gx0, gy0, gx1, gy1);
    g.addColorStop(0, `rgba(42,46,107,${(MATERIAL.aoIntensity * 0.25).toFixed(3)})`);
    g.addColorStop(1, 'rgba(42,46,107,0)');
    ctx.fillStyle = g;
    ctx.fillRect(x0, y0, gw, gh);
  }

  const tex = new CanvasTexture(c);
  tex.wrapS = RepeatWrapping;
  tex.wrapT = RepeatWrapping;
  tex.colorSpace = SRGBColorSpace;
  tex.anisotropy = 2;
  return tex;
};

export type Painted = {
  color: MeshStandardMaterial;
  mapTexture: CanvasTexture;
};

/**
 * One painted material per palette colour: roughness 0.8, metalness 0,
 * ambient occlusion at 0.6 intensity. Reused across every building so the
 * whole town is 6 draw-call groups instead of 90.
 */
export const usePaintedMaterials = () =>
  useMemo(() => {
    const make = (hex: string, seed: number) => {
      const map = paintTexture(hex, seed);
      const color = new MeshStandardMaterial({
        color: new Color(hex),
        map,
        roughness: MATERIAL.roughness,
        metalness: MATERIAL.metalness,
      });
      return {color, mapTexture: map};
    };
    return {
      sun: make(PALETTE.sun, 11),
      pop: make(PALETTE.pop, 22),
      sky: make(PALETTE.sky, 33),
      town: make(PALETTE.town, 44),
      paper: make(PALETTE.paper, 55),
      shadow: make(PALETTE.shadow, 66),
    } as Record<'sun' | 'pop' | 'sky' | 'town' | 'paper' | 'shadow', Painted>;
  }, []);

// ---------------------------------------------------------------------------
// Town layout
// ---------------------------------------------------------------------------
export type Building = {
  key: string;
  pos: [number, number, number];
  size: [number, number, number];
  mat: 'sun' | 'pop' | 'sky' | 'town' | 'paper' | 'shadow';
  roof: 'flat' | 'gable' | 'tower';
  rot: number;
};

const ROOF_MATS: Building['mat'][] = ['pop', 'sun', 'sky', 'shadow'];

/**
 * Sample points along the camera spline (XZ only). The town is generated so it
 * never blocks these — otherwise the glide flies straight through a rooftop and
 * a building fills half the frame.
 */
const CAMERA_PATH_XZ: Array<[number, number]> = Array.from({length: 200}, (_, i) => {
  const p = posCurve.getPoint(i / 199);
  return [p.x, p.z];
});

/** Distance from (x, z) to the nearest point on the camera path, in world units. */
export const distanceToCameraPath = (x: number, z: number) => {
  let best = Infinity;
  for (const [cx, cz] of CAMERA_PATH_XZ) {
    const d = (x - cx) ** 2 + (z - cz) ** 2;
    if (d < best) best = d;
  }
  return Math.sqrt(best);
};

/** ~85 low-poly buildings laid out on a loose street grid around the vault. */
export const TOWN_BUILDINGS: Building[] = (() => {
  const rnd = mulberry32(20261029);
  const out: Building[] = [];
  const mats: Building['mat'][] = ['town', 'town', 'town', 'sky', 'pop', 'paper'];

  for (let i = 0; i < 96; i += 1) {
    const ring = i / 96;
    let x = 0;
    let z = 0;
    let guard = 0;
    do {
      x = -52 + rnd() * 60;
      z = (rnd() - 0.5) * 50;
      guard += 1;
    } while (
      guard < 40 &&
      // clear plaza around the vault ...
      (Math.hypot(x, z * 0.55) < 18 ||
        // ... and a clean corridor for the camera glide
        distanceToCameraPath(x, z) < 12)
    );

    const w = 2.2 + rnd() * 3.4;
    const d = 2.2 + rnd() * 3.4;
    let h = 2.5 + rnd() * (ring < 0.4 ? 9 : 5.5);

    // Anything close to the flight path has to stay under the camera.
    const clearance = distanceToCameraPath(x, z);
    if (clearance < 26) h = Math.min(h, 3.5 + (clearance - 12) * 0.45);

    out.push({
      key: `b${i}`,
      pos: [x, h / 2, z],
      size: [w, Math.max(2, h), d],
      mat: mats[Math.floor(rnd() * mats.length)],
      roof: rnd() > 0.72 ? 'gable' : 'flat',
      rot: (rnd() - 0.5) * 0.35,
    });
  }

  // A few landmark towers so the skyline is not a uniform carpet.
  // Landmark towers — placed far from the flight path so they read as skyline.
  const towers: Array<[number, number, number, Building['mat']]> = [
    [-44, 11, -18, 'town'],
    [-52, 9.5, 8, 'pop'],
    [-18, 8, -26, 'sky'],
    [26, 7.5, 22, 'town'],
    [-34, 10, 26, 'pop'],
  ];
  towers.forEach(([tx, ty, tz, mat], k) => {
    if (distanceToCameraPath(tx, tz) < 12) return;
    out.push({
      key: `t${k}`, pos: [tx, ty, tz],
      size: [3.2, ty * 2, 3.2], mat, roof: 'tower', rot: (k - 2) * 0.11,
    });
  });
  return out;
})();

export const ROOF_MATERIALS = ROOF_MATS;

// ---------------------------------------------------------------------------
// Landmarks
// ---------------------------------------------------------------------------
export const VAULT = {
  pos: [0, 0, 0] as [number, number, number],
  body: [9, 11, 9] as [number, number, number],
  doorSize: [4.4, 6, 0.6] as [number, number, number],
};

export const CLOCK_TOWER = {
  pos: [-30, 0, -2] as [number, number, number],
  body: [4.2, 24, 4.2] as [number, number, number],
  faceY: 19,
  faceR: 1.7,
};

/** The DevOps tower: one lit window at the top, and that window is the attack. */
export const DEV_TOWER = {
  pos: [10.5, 0, -11] as [number, number, number],
  body: [5.5, 20, 5.5] as [number, number, number],
  windowY: 13.6,
  windowSize: [3.0, 2.0] as [number, number],
};

export const BLOCKCHAINS = [
  'ETHEREUM', 'BITCOIN', 'TRON', 'XRP', 'SOLANA',
  'ARBITRUM', 'OPTIMISM', 'BASE', 'AVALANCHE', 'POLYGON',
] as const;

/** Ten bridges fanning out behind the vault — one lane per blockchain. */
export const BRIDGE_LANES = BLOCKCHAINS.map((name, i) => {
  const spread = 3.0;
  const z = (i - (BLOCKCHAINS.length - 1) / 2) * spread;
  const len = 26 - Math.abs(i - 4.5) * 0.9;
  return {
    key: name,
    index: i,
    name,
    z,
    length: len,
    startX: 6,
    y: 1.6,
    /** Bitcoin (index 1) is the lane nobody can freeze. */
    freezable: i !== 1,
    /** Tether/Circle could only stop the stablecoin-heavy lanes. */
    frozen: i === 0 || i === 2 || i === 3,
  };
});

// ---------------------------------------------------------------------------
// Marching coins
// ---------------------------------------------------------------------------
export const COIN_COUNT = 132;

/**
 * Coin i walks out along a lane. `t` is seconds; coins that have already left
 * wrap back to the vault door so the stream reads as continuous.
 */
/** The beat (seconds) at which Tether + Circle freeze the stablecoin lanes. */
export const FREEZE_AT = 30.4;

const wrap = (value: number, span: number) => ((value % span) + span) % span;

export const coinTransform = (
  i: number,
  t: number,
): {pos: [number, number, number]; rot: number; scale: number; frozen: number} => {
  const lane = BRIDGE_LANES[i % BRIDGE_LANES.length];
  const wave = Math.floor(i / BRIDGE_LANES.length);
  const speed = 1.7;
  const span = lane.length - 4;
  const phase = wave * 2.4 + i * 0.13;

  // Frozen lanes stop dead where they were when the freeze landed.
  // Bitcoin (lane 1) and the other unfreezable lanes keep marching.
  const stopped = lane.frozen && t > FREEZE_AT;
  const u = stopped ? wrap(FREEZE_AT * speed + phase, span) : wrap(t * speed + phase, span);
  const frozen = stopped ? Math.min(1, (t - FREEZE_AT) / 1.1) : 0;

  // March, don't slide: a quantised bob on every other half-beat.
  const bob = Math.floor(t * 3.2 + i) % 2 === 0 ? 0.12 : -0.12;
  const laneJitter = Math.sin(i * 3.7) * 0.34;

  return {
    pos: [lane.startX + u, lane.y + 0.55 + bob * (1 - frozen), lane.z + laneJitter],
    rot: t * 2.2 + i,
    scale: 1 - frozen * 0.07,
    frozen,
  };
};

/** Ground plane colour bands, painted in the palette. */
export const GROUND_SIZE = 220;
