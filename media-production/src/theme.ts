/**
 * Style bible for the viral animated shorts — measured from the reference channel
 * and hard-coded here so every module reads the same numbers.
 *
 * Palette is capped at 6 colours. Pure black is banned: shadows use #2A2E6B.
 */

export const FPS = 30;
export const WIDTH = 1080;
export const HEIGHT = 1920;
export const DURATION_IN_FRAMES = 2010; // 67.0 s — same length as the reference short

/** The only six colours allowed in the frame. */
export const PALETTE = {
  sun: '#FFD23F', // gold — the money, the vault, the key light
  pop: '#FF6B6B', // character pop / danger
  sky: '#4ECDC4', // sky + ice (frozen funds)
  town: '#1A535C', // painted town, dark masses
  paper: '#F7FFF7', // paper base / highlights
  shadow: '#2A2E6B', // shadows + ink. NEVER #000000
} as const;

export const SHADOW_RGB: [number, number, number] = [0x2a / 255, 0x2e / 255, 0x6b / 255];

/** Camera language — no hard cuts anywhere in the short. */
export const CAMERA = {
  lerp: 0.08, // exponential smoothing on the look-at target
  dolly: 0.8, // units / second of travel
  orbitDegPerSec: 2, // slow orbital drift added on top of the path
  orbitRadius: 1.15, // world units — keeps the framing readable at 2 deg/s
  parallax: 0.05, // 5 % offset between character planes and the town
  fov: 42,
  near: 0.1,
  far: 220,
} as const;

/** Lens: DepthOfField is on for the whole short. */
export const LENS = {
  focusDistance: 2.5, // style-bible value → worldFocusDistance bias
  aperture: 0.05, // → bokehScale (see lensPxForAperture)
  backgroundBlurPx: 10, // target 8–12 px
  foregroundBlurPx: 4, // when a plane is very close
  dofHeight: 480, // kept for the @react-three/postprocessing backend
  worldFocusRange: 12, // world units either side of focus that stay sharp
} as const;

/**
 * Aperture → `bokehScale`.
 *
 * `bokehScale` is measured in the DOF buffer's own pixel space, and that buffer
 * runs at `dofHeight` (480) before being upscaled to the 1920 px frame. So the
 * 4x upscale has to be divided out, or a 10 px background blur becomes 40 px.
 */
export const lensPxForAperture = (
  aperture: number,
  dofHeight: number = 480,
  frameHeight: number = 1920,
) => Math.min(14, Math.max(2, aperture * 200)) * (dofHeight / frameHeight);

/** Ink. Outline weight varies with camera distance; the line boils every frame. */
export const INK = {
  minPx: 2.5,
  maxPx: 4.0,
  boilMinPx: 0.3,
  boilMaxPx: 0.8,
  boilSpeed: 10.0, // sin(uTime * 10.0 + x * 5.0) * 0.008
  boilSpread: 5.0,
  boilAmount: 0.008,
} as const;

/** Materials — painted, never glossy. */
export const MATERIAL = {
  roughness: 0.8,
  metalness: 0.0,
  aoIntensity: 0.6,
} as const;

/** Lighting: warm key + cool fill, shadow tinted with the palette shadow colour. */
export const LIGHT = {
  keyIntensity: 1.2,
  keyColor: '#FFE3A8',
  fillIntensity: 0.4,
  fillColor: '#8FD6FF',
  ambientIntensity: 0.35,
  shadowOpacity: 0.6, // shadow colour at 60 % opacity
} as const;

/** Grade applied as a DOM layer above the WebGL canvas. */
export const GRADE = {
  temperature: 5, // warm +5
  contrast: 10, // +10
  vignette: 0.15, // corner falloff, in #2A2E6B
} as const;

export const hexToRgb = (hex: string): [number, number, number] => {
  const v = parseInt(hex.slice(1), 16);
  return [((v >> 16) & 255) / 255, ((v >> 8) & 255) / 255, (v & 255) / 255];
};
