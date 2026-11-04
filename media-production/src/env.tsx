import React, {useLayoutEffect} from 'react';
import {useThree} from '@react-three/fiber';
import {
  CanvasTexture,
  EquirectangularReflectionMapping,
  LinearFilter,
  PMREMGenerator,
  SRGBColorSpace,
} from 'three';
import {LIGHT, PALETTE} from './theme';
import {mulberry32} from './world';

/**
 * The sky is the light.
 *
 * A single procedural equirectangular canvas drives three things at once:
 *
 *   1. `scene.background`  — the visible sky
 *   2. `scene.environment` — the PMREM-filtered copy that every PBR surface
 *      reflects and that carries most of the ambient light
 *   3. the sun disc        — positioned from `LIGHT.keyPosition` so the bright
 *      spot you can see is the same direction the key light comes from
 *
 * Without (2) every metal and glass surface in the town reads as flat grey no
 * matter how the lights are tuned — that is the single biggest difference
 * between "3D looking" and "real looking".
 *
 * three's equirect convention: u = atan2(z, x)/2π + 0.5, v = asin(y)/π + 0.5,
 * and CanvasTexture flips Y, so canvas row 0 is the zenith.
 */

const dirToCanvas = (
  dx: number, dy: number, dz: number, W: number, H: number,
): [number, number] => {
  const l = Math.hypot(dx, dy, dz) || 1;
  const x = dx / l;
  const y = dy / l;
  const z = dz / l;
  const u = Math.atan2(z, x) / (Math.PI * 2) + 0.5;
  const v = Math.asin(Math.max(-1, Math.min(1, y))) / Math.PI + 0.5;
  return [u * W, (1 - v) * H];
};

export const buildEquirectSky = (W = 1024, H = 512): CanvasTexture => {
  const c = document.createElement('canvas');
  c.width = W;
  c.height = H;
  const ctx = c.getContext('2d')!;

  // --- vertical gradient: zenith → mid → warm horizon → ground -------------
  const g = ctx.createLinearGradient(0, 0, 0, H);
  g.addColorStop(0.00, PALETTE.zenith);
  g.addColorStop(0.24, '#24406B');
  g.addColorStop(0.36, PALETTE.skyMid);
  g.addColorStop(0.45, '#8B7E86');
  g.addColorStop(0.485, PALETTE.horizon);
  g.addColorStop(0.505, '#6E5A50');
  g.addColorStop(0.56, '#3A3640');
  g.addColorStop(1.00, '#14121B');
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, W, H);

  // --- sun: glow first, then the disc -------------------------------------
  const [sx, sy] = dirToCanvas(LIGHT.keyPosition[0], LIGHT.keyPosition[1], LIGHT.keyPosition[2], W, H);

  ctx.globalCompositeOperation = 'lighter';

  const glow = ctx.createRadialGradient(sx, sy, 0, sx, sy, H * 0.62);
  glow.addColorStop(0.00, 'rgba(255,214,160,0.95)');
  glow.addColorStop(0.06, 'rgba(255,190,124,0.55)');
  glow.addColorStop(0.22, 'rgba(226,148,96,0.24)');
  glow.addColorStop(0.55, 'rgba(150,110,96,0.08)');
  glow.addColorStop(1.00, 'rgba(0,0,0,0)');
  ctx.fillStyle = glow;
  ctx.fillRect(0, 0, W, H);

  // horizon haze pulled towards the sun
  const haze = ctx.createLinearGradient(0, sy - H * 0.16, 0, sy + H * 0.16);
  haze.addColorStop(0, 'rgba(0,0,0,0)');
  haze.addColorStop(0.5, 'rgba(255,196,138,0.16)');
  haze.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = haze;
  ctx.fillRect(0, sy - H * 0.16, W, H * 0.32);

  const disc = ctx.createRadialGradient(sx, sy, 0, sx, sy, H * 0.045);
  disc.addColorStop(0.00, 'rgba(255,248,232,1)');
  disc.addColorStop(0.45, 'rgba(255,226,180,0.85)');
  disc.addColorStop(1.00, 'rgba(255,196,138,0)');
  ctx.fillStyle = disc;
  ctx.fillRect(sx - H * 0.05, sy - H * 0.05, H * 0.10, H * 0.10);

  ctx.globalCompositeOperation = 'source-over';

  // --- cloud bands ---------------------------------------------------------
  // Long, low, stretched horizontally the way dusk stratocumulus actually is.
  const rnd = mulberry32(31337);
  for (let i = 0; i < 46; i += 1) {
    const cy = H * (0.20 + rnd() * 0.26);
    const cx = rnd() * W;
    const cw = W * (0.04 + rnd() * 0.16);
    const ch = H * (0.006 + rnd() * 0.022);
    const near = Math.abs(((cx - sx + W * 1.5) % W) - W * 0.5) / (W * 0.5);
    const warm = Math.max(0, 1 - near);
    const a = 0.05 + rnd() * 0.16;
    ctx.save();
    ctx.translate(cx, cy);
    ctx.beginPath();
    ctx.ellipse(0, 0, cw / 2, ch / 2, 0, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(${Math.round(52 + warm * 190)},${Math.round(50 + warm * 130)},${Math.round(58 + warm * 84)},${a})`;
    ctx.fill();
    ctx.restore();
  }

  // A handful of darker clouds to give the upper sky some structure.
  for (let i = 0; i < 18; i += 1) {
    const cy = H * (0.08 + rnd() * 0.30);
    const cx = rnd() * W;
    ctx.save();
    ctx.translate(cx, cy);
    ctx.beginPath();
    ctx.ellipse(0, 0, W * (0.03 + rnd() * 0.09), H * (0.008 + rnd() * 0.02), 0, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(26,32,48,${0.05 + rnd() * 0.10})`;
    ctx.fill();
    ctx.restore();
  }

  const tex = new CanvasTexture(c);
  tex.mapping = EquirectangularReflectionMapping;
  tex.colorSpace = SRGBColorSpace;
  tex.minFilter = LinearFilter;
  tex.magFilter = LinearFilter;
  tex.generateMipmaps = false;
  return tex;
};

/**
 * Installs the sky + PMREM environment on the scene. Rendered as a component
 * (not a hook) so it sits next to the lights in the JSX.
 */
export const SkyEnvironment: React.FC<{noSky?: boolean}> = ({noSky = false}) => {
  const gl = useThree((s) => s.gl);
  const scene = useThree((s) => s.scene);

  useLayoutEffect(() => {
    const src = buildEquirectSky(1024, 512);

    if (!noSky) {
      scene.background = src;
      scene.backgroundIntensity = 1.0;
      scene.backgroundBlurriness = 0.0;
    }

    const pmrem = new PMREMGenerator(gl);
    const rt = pmrem.fromEquirectangular(src);
    scene.environment = rt.texture;
    scene.environmentIntensity = LIGHT.envIntensity;
    pmrem.dispose();

    return () => {
      scene.background = null;
      scene.environment = null;
      rt.dispose();
      src.dispose();
    };
  }, [gl, scene, noSky]);

  return null;
};
