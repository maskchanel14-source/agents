/**
 * theme.ts — the channel's locked visual identity (Style Bible).
 *
 * Reference: cyan HUD "instrumentation" look. Near-black base, ONE accent colour
 * per video, thin rules, micro-label telemetry, Anton for shout text.
 */
type Theme = {
  bg: string;
  bgLift: string;
  ink: string;
  inkDim: string;
  inkFaint: string;
  accent: string;
  accentSoft: string;
  accentGlow: string;
  accentRGB: string;
  warn: string;
  type: {shout: string; display: string; ui: string; mono: string};
};

/** Channel default accent (DS-001..DS-003). */
export const BASE_THEME: Theme = {
  bg: '#05070A',
  bgLift: '#0A1017',
  ink: '#FFFFFF',
  inkDim: 'rgba(255,255,255,0.62)',
  inkFaint: 'rgba(255,255,255,0.28)',
  // one accent per video
  accent: '#22D3EE',
  accentSoft: 'rgba(34,211,238,0.18)',
  accentGlow: 'rgba(34,211,238,0.45)',
  accentRGB: '34,211,238',
  warn: '#FF2D2D',
  type: {
    shout: 'Anton, "Arial Black", sans-serif',
    display: 'Montserrat, "Helvetica Neue", sans-serif',
    ui: 'Inter, "Helvetica Neue", Arial, sans-serif',
    mono: '"JetBrains Mono", "SF Mono", monospace',
  },
};

/**
 * One accent per video (Style Bible rule). The active theme is set once per
 * render from props.meta.accent, so no scene has to know which film it is in.
 */
export let theme: Theme = BASE_THEME;

export function setAccent(hex: string): void {
  const m = /^#?([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})$/i.exec(hex.trim());
  if (!m) return;
  const [r, g, b] = [m[1], m[2], m[3]].map((h) => parseInt(h, 16));
  theme = {
    ...BASE_THEME,
    accent: `#${m[1]}${m[2]}${m[3]}`.toUpperCase(),
    accentSoft: `rgba(${r},${g},${b},0.18)`,
    accentGlow: `rgba(${r},${g},${b},0.45)`,
    accentRGB: `${r},${g},${b}`,
  };
}

export const SAFE = {
  // vertical Shorts safe zones (1080x1920)
  top: 240, // platform chrome
  bottom: 480, // captions + progress bar
  right: 120, // action buttons
} as const;

export const FPS = 30;
export const W = 1080;
export const H = 1920;
