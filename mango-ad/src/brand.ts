/**
 * brand.ts — one palette for the whole spot.
 *
 * Derived from the fruit itself: burnt amber (#E8871E) as the hero accent,
 * deep ink for the negative space, and a cold slate for the operational
 * section so the product colour always pops against it.
 */
export const C = {
  ink: '#07080A',
  ink2: '#0E1014',
  slate: '#12151B',
  amber: '#E8871E',
  amberHot: '#FFB03A',
  amberDeep: '#B4530C',
  blush: '#7B1E3A',
  cream: '#F6EDE2',
  creamDim: 'rgba(246,237,226,0.62)',
  creamFaint: 'rgba(246,237,226,0.26)',
  cool: '#5BC8D8',
} as const;

export const T = {
  serif: '"Playfair Display", Georgia, serif',
  sans: 'Montserrat, "Helvetica Neue", sans-serif',
  ui: 'Inter, Arial, sans-serif',
} as const;

export const W = 1080;
export const H = 1920;
export const FPS = 30;

/** Easing helpers shared by scenes. */
export const clamp = (x: number, a = 0, b = 1) => Math.max(a, Math.min(b, x));
export const easeOut = (x: number) => 1 - Math.pow(1 - clamp(x), 3);
export const easeInOut = (x: number) => {
  const t = clamp(x);
  return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
};
/** 0→1→0 bell, useful for one-shot accents. */
export const bell = (x: number, a = 0, b = 1) => {
  const t = clamp((x - a) / (b - a));
  return Math.sin(t * Math.PI);
};
