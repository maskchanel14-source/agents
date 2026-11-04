/**
 * Style bible for SHORTS-2026-024B — SEMI-REALIST revision.
 *
 * Revision 2 (2026-11-04). The original brief called for a painted, ink-outlined
 * 2D-in-3D look. This revision moves the same story to:
 *
 *   - real 3D humanoid characters with a jointed rig (no billboards)
 *   - physically-based materials with roughness / bump / metalness variation
 *   - an image-based environment (procedural dusk equirect → PMREM) so metal
 *     and glass actually reflect the sky
 *   - soft shadow maps + contact shadow decals
 *   - filmic (ACES) tone mapping, no ink outlines, natural dusk colour
 *
 * The 6-colour cap and the pure-black ban are lifted for the environment, but
 * every surface still lands on a documented value here so the grade stays
 * controllable. Text/graphic overlays keep their own small palette.
 */

export const FPS = 30;
export const WIDTH = 1080;
export const HEIGHT = 1920;
export const DURATION_IN_FRAMES = 2010; // 67.0 s

/* ------------------------------------------------------------------ colour */

/** Natural dusk palette. No pure black anywhere — the darkest value is #14121B. */
export const PALETTE = {
  // --- atmosphere ---------------------------------------------------------
  zenith: '#16233C', // top of the sky
  skyMid: '#3D5A80', // mid sky
  horizon: '#C98B5E', // warm dusk band at the horizon
  sunGlow: '#FFD9A0', // the sun itself (just below the horizon → glow only)
  haze: '#6E7484', // distance fog

  // --- built world --------------------------------------------------------
  concrete: '#B7B2A7',
  plaster: '#C6B49C',
  brick: '#8E5B4C',
  slate: '#4B5160',
  asphalt: '#5A5C64',
  stone: '#7E7A73',

  // --- metal / glass ------------------------------------------------------
  brass: '#C9A227',
  steel: '#98A1AD',
  glass: '#3E5A78',
  glassLit: '#FFC178',

  // --- figures ------------------------------------------------------------
  skin: '#C9977A',
  skinDeep: '#8D6047',
  cloth: '#33404F',
  clothWarm: '#7A4A3A',
  hair: '#2A2320',
  shoe: '#23212A',

  // --- accents / graphics -------------------------------------------------
  paper: '#F4F1EA',
  shadow: '#1B1824',
  lamp: '#FFB765',
  danger: '#C4553F',
  ice: '#8FB6CC',
} as const;

/**
 * Per-surface PBR response. `bump` is the bumpMap scale; `bump: 0` skips the
 * map entirely (cheaper fragment shader — used on small props).
 */
export const SURFACE = {
  concrete: {roughness: 0.88, metalness: 0.0, bump: 0.02},
  plaster: {roughness: 0.80, metalness: 0.0, bump: 0.015},
  brick: {roughness: 0.92, metalness: 0.0, bump: 0.03},
  slate: {roughness: 0.72, metalness: 0.0, bump: 0.012},
  asphalt: {roughness: 0.95, metalness: 0.0, bump: 0.025},
  stone: {roughness: 0.85, metalness: 0.0, bump: 0.02},
  brass: {roughness: 0.34, metalness: 0.90, bump: 0.004},
  steel: {roughness: 0.42, metalness: 0.85, bump: 0.004},
  glass: {roughness: 0.08, metalness: 0.10, bump: 0},
  cloth: {roughness: 0.95, metalness: 0.0, bump: 0.008},
  skin: {roughness: 0.64, metalness: 0.0, bump: 0.003},
} as const;

export type SurfaceName = keyof typeof SURFACE;

/* ------------------------------------------------------------------ camera */

/**
 * Camera language — no hard cuts anywhere in the short.
 *
 * fov drops from 42 → 38 for this revision: a longer lens is both more
 * filmic and it magnifies the characters, which were reading at 3–5 % of
 * frame height.
 */
export const CAMERA = {
  lerp: 0.08, // exponential smoothing on the look-at target
  dolly: 0.8, // units / second of travel
  orbitDegPerSec: 2, // slow orbital drift added on top of the path
  orbitRadius: 1.15, // world units
  parallax: 0.05, // 5 % offset between the cast and the town
  fov: 38,
  near: 0.5,
  far: 520,
} as const;

/** Lens: depth of field is on for the whole short. */
export const LENS = {
  focusDistance: 2.5,
  aperture: 0.05,
  backgroundBlurPx: 8, // 8–12 px per the brief; 8 keeps it filmic, not mushy
  foregroundBlurPx: 4,
  dofHeight: 480,
  worldFocusRange: 12,
} as const;

/**
 * Aperture → `bokehScale`, measured in the DOF buffer's own 480 px space and
 * then divided by the 4x upscale to the 1920 px frame.
 */
export const lensPxForAperture = (
  aperture: number,
  dofHeight: number = 480,
  frameHeight: number = 1920,
) => Math.min(14, Math.max(2, aperture * 200)) * (dofHeight / frameHeight);

/* ------------------------------------------------------------------ light */

/**
 * Dusk: a low warm key raking across the town, a cool sky dome for fill, and
 * the environment map carrying the ambient. No pure-black falloff — the
 * hemisphere ground colour keeps unlit faces readable.
 */
export const LIGHT = {
  keyIntensity: 2.9,
  keyColor: '#FFC48A',
  keyPosition: [42, 20, 26] as [number, number, number],
  fillIntensity: 0.55,
  fillColor: '#7EA6C9',
  rimIntensity: 1.0,
  rimColor: '#9FC4E8',
  hemiIntensity: 0.55,
  hemiSky: '#5B7EA6',
  hemiGround: '#4A3E30',
  ambient: 0.10,
  envIntensity: 0.85,
  exposure: 1.9,
  shadowMapSize: 2048,
  shadowRadius: 3,
  shadowBias: -0.0006,
} as const;

/** Atmosphere — exponential fog reads as real haze, unlike a linear band. */
export const ATMOSPHERE = {
  color: PALETTE.haze,
  density: 0.0038,
} as const;

/* ------------------------------------------------------------------ grade */

/** Applied as a CSS filter on the WebGL layer — filmic, not cartoonish. */
export const GRADE = {
  contrast: 6, // +6 %
  saturate: 1.03,
  vignette: 0.20,
  vignetteColor: '10,8,16',
} as const;

/* ------------------------------------------------------------------ utils */

export const hexToRgb = (hex: string): [number, number, number] => {
  const v = parseInt(hex.slice(1), 16);
  return [((v >> 16) & 255) / 255, ((v >> 8) & 255) / 255, (v & 255) / 255];
};

export const clamp01 = (v: number) => (v < 0 ? 0 : v > 1 ? 1 : v);

export const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
