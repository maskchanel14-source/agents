/**
 * Soft3D.tsx — software-projected 3D primitives.
 *
 * This box has NO usable WebGL context, so every "3D" element is a tiny
 * Canvas2D rasteriser with a perspective divide, painter's-algorithm sorting
 * and additive glow. You draw once per frame into a ref-driven canvas; the
 * helpers below do the maths.
 *
 * Budget: keep under ~1200 line segments per frame or the render crawls.
 */
import React, {useLayoutEffect, useRef} from 'react';
import {useCurrentFrame, useVideoConfig} from 'remotion';

export type V3 = [number, number, number];

export const v3 = {
  add: (a: V3, b: V3): V3 => [a[0] + b[0], a[1] + b[1], a[2] + b[2]],
  sub: (a: V3, b: V3): V3 => [a[0] - b[0], a[1] - b[1], a[2] - b[2]],
  scale: (a: V3, s: number): V3 => [a[0] * s, a[1] * s, a[2] * s],
  len: (a: V3) => Math.hypot(a[0], a[1], a[2]),
  norm: (a: V3): V3 => {
    const l = Math.hypot(a[0], a[1], a[2]) || 1;
    return [a[0] / l, a[1] / l, a[2] / l];
  },
  cross: (a: V3, b: V3): V3 => [
    a[1] * b[2] - a[2] * b[1],
    a[2] * b[0] - a[0] * b[2],
    a[0] * b[1] - a[1] * b[0],
  ],
  rotY: (a: V3, t: number): V3 => [
    a[0] * Math.cos(t) + a[2] * Math.sin(t),
    a[1],
    -a[0] * Math.sin(t) + a[2] * Math.cos(t),
  ],
  rotX: (a: V3, t: number): V3 => [
    a[0],
    a[1] * Math.cos(t) - a[2] * Math.sin(t),
    a[1] * Math.sin(t) + a[2] * Math.cos(t),
  ],
  rotZ: (a: V3, t: number): V3 => [
    a[0] * Math.cos(t) - a[1] * Math.sin(t),
    a[0] * Math.sin(t) + a[1] * Math.cos(t),
    a[2],
  ],
};

export type Cam = {rot: V3; dist: number; fov: number};

/** Project a world point to screen space. Returns null when behind the camera. */
export function project(p: V3, cam: Cam, w: number, h: number) {
  let q = v3.rotZ(p, cam.rot[2]);
  q = v3.rotX(q, cam.rot[0]);
  q = v3.rotY(q, cam.rot[1]);
  const z = q[2] + cam.dist;
  if (z <= 0.05) return null;
  const f = cam.fov / z;
  return {x: w / 2 + q[0] * f, y: h / 2 - q[1] * f, z, scale: f};
}

export type Seg = {a: V3; b: V3; c?: string; w?: number; glow?: number};

export const drawSegs = (
  ctx: CanvasRenderingContext2D,
  segs: Seg[],
  cam: Cam,
  w: number,
  h: number,
  opts: {accent?: string; baseAlpha?: number} = {}
) => {
  const accent = opts.accent ?? '#22D3EE';
  const projected = segs
    .map((s) => ({s, a: project(s.a, cam, w, h), b: project(s.b, cam, w, h)}))
    .filter((p) => p.a && p.b) as {s: Seg; a: {x: number; y: number; z: number}; b: any}[];

  projected.sort((p, q) => q.a.z - p.a.z); // far first

  for (const {s, a, b} of projected) {
    const depth = Math.min(1, 9 / (a.z + 3)); // fade with distance
    ctx.globalAlpha = Math.max(0.05, depth) * (opts.baseAlpha ?? 1);
    ctx.strokeStyle = s.c ?? accent;
    ctx.lineWidth = s.w ?? 1.6;
    if (s.glow) {
      ctx.shadowBlur = s.glow;
      ctx.shadowColor = s.c ?? accent;
    } else {
      ctx.shadowBlur = 0;
    }
    ctx.beginPath();
    ctx.moveTo(a.x, a.y);
    ctx.lineTo(b.x, b.y);
    ctx.stroke();
  }
  ctx.shadowBlur = 0;
  ctx.globalAlpha = 1;
};

/** A canvas that redraws every frame with the current frame number. */
export const Soft3D: React.FC<{
  width: number;
  height: number;
  draw: (ctx: CanvasRenderingContext2D, frame: number, t: number) => void;
  style?: React.CSSProperties;
}> = ({width, height, draw, style}) => {
  const ref = useRef<HTMLCanvasElement>(null);
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  useLayoutEffect(() => {
    const c = ref.current;
    if (!c) return;
    const ctx = c.getContext('2d');
    if (!ctx) return;
    ctx.clearRect(0, 0, width, height);
    ctx.lineCap = 'round';
    draw(ctx, frame, frame / fps);
  }, [frame, fps, width, height, draw]);

  return <canvas ref={ref} width={width} height={height} style={{...style, display: 'block'}} />;
};

// ------------------------------------------------------------------ primitives

/** UV sphere as lat/long wireframe segments. */
export function sphereSegs(
  r: number,
  rings = 9,
  meridians = 12,
  colour?: string,
  width = 1.2
): Seg[] {
  const out: Seg[] = [];
  for (let i = 1; i < rings; i++) {
    const phi = (i / rings) * Math.PI;
    const y = Math.cos(phi) * r;
    const rr = Math.sin(phi) * r;
    for (let j = 0; j < meridians; j++) {
      const a0 = (j / meridians) * Math.PI * 2;
      const a1 = ((j + 1) / meridians) * Math.PI * 2;
      out.push({
        a: [Math.cos(a0) * rr, y, Math.sin(a0) * rr],
        b: [Math.cos(a1) * rr, y, Math.sin(a1) * rr],
        c: colour,
        w: width,
      });
    }
  }
  for (let j = 0; j < meridians; j++) {
    const a = (j / meridians) * Math.PI * 2;
    const x = Math.cos(a) * r;
    const z = Math.sin(a) * r;
    for (let i = 0; i < rings; i++) {
      const p0 = (i / rings) * Math.PI;
      const p1 = ((i + 1) / rings) * Math.PI;
      out.push({
        a: [x * Math.sin(p0), Math.cos(p0) * r, z * Math.sin(p0)],
        b: [x * Math.sin(p1), Math.cos(p1) * r, z * Math.sin(p1)],
        c: colour,
        w: width,
      });
    }
  }
  return out;
}

/** Icosahedron edges — reads as a virus capsid / phage head. */
export function icosaSegs(r: number, colour?: string, width = 1.6): Seg[] {
  const t = (1 + Math.sqrt(5)) / 2;
  const raw: V3[] = [
    [-1, t, 0], [1, t, 0], [-1, -t, 0], [1, -t, 0],
    [0, -1, t], [0, 1, t], [0, -1, -t], [0, 1, -t],
    [t, 0, -1], [t, 0, 1], [-t, 0, -1], [-t, 0, 1],
  ];
  const verts = raw.map((p) => v3.scale(v3.norm(p as V3), r));
  const edges: [number, number][] = [];
  for (let i = 0; i < verts.length; i++) {
    for (let j = i + 1; j < verts.length; j++) {
      const d = v3.len(v3.sub(verts[i], verts[j]));
      if (d < r * 1.15) edges.push([i, j]);
    }
  }
  return edges.map(([i, j]) => ({a: verts[i], b: verts[j], c: colour, w: width}));
}

/** Double helix. `twist=+1` is right-handed, `-1` left-handed (enantiomers). */
export function helixSegs(
  r: number,
  height: number,
  turns: number,
  handed: 1 | -1,
  per = 180,
  colour?: string
): Seg[] {
  const out: Seg[] = [];
  const pt = (t: number): V3 => {
    const a = handed * t * turns * Math.PI * 2;
    return [Math.cos(a) * r, (t - 0.5) * height, Math.sin(a) * r];
  };
  for (let i = 0; i < per; i++) {
    const t0 = i / per;
    const t1 = (i + 1) / per;
    out.push({a: pt(t0), b: pt(t1), c: colour, w: 2.2, glow: 6});
    if (i % 6 === 0) {
      const a0 = handed * t0 * turns * Math.PI * 2;
      const mirror: V3 = [Math.cos(a0 + Math.PI) * r, (t0 - 0.5) * height, Math.sin(a0 + Math.PI) * r];
      out.push({a: pt(t0), b: mirror, c: colour, w: 1, glow: 0});
    }
  }
  return out;
}

/** Random-ish membrane ring of points (seeded, deterministic per index). */
export function ringPoints(
  n: number,
  radius: number,
  jitter: number,
  seed = 1,
  y = 0
): V3[] {
  const pts: V3[] = [];
  let s = seed * 9301 + 49297;
  const rnd = () => {
    s = (s * 9301 + 49297) % 233280;
    return s / 233280;
  };
  for (let i = 0; i < n; i++) {
    const a = (i / n) * Math.PI * 2;
    const r = radius + (rnd() - 0.5) * jitter * 2;
    pts.push([Math.cos(a) * r, y + (rnd() - 0.5) * jitter, Math.sin(a) * r]);
  }
  return pts;
}

/** Tube segments through a point list (closed loop by default). */
export function tubeSegs(pts: V3[], colour?: string, width = 1.6, glow = 0): Seg[] {
  const out: Seg[] = [];
  for (let i = 0; i < pts.length; i++) {
    out.push({a: pts[i], b: pts[(i + 1) % pts.length], c: colour, w: width, glow});
  }
  return out;
}
