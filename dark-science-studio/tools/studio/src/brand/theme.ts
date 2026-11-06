/**
 * theme.ts — the channel's locked visual identity (Style Bible).
 *
 * Reference: cyan HUD "instrumentation" look. Near-black base, ONE accent colour
 * per video, thin rules, micro-label telemetry, Anton for shout text.
 */
export const theme = {
  bg: '#05070A',
  bgLift: '#0A1017',
  ink: '#FFFFFF',
  inkDim: 'rgba(255,255,255,0.62)',
  inkFaint: 'rgba(255,255,255,0.28)',
  // one accent per video
  accent: '#22D3EE',
  accentSoft: 'rgba(34,211,238,0.18)',
  accentGlow: 'rgba(34,211,238,0.45)',
  warn: '#FF2D2D',
  type: {
    shout: 'Anton, "Arial Black", sans-serif',
    display: 'Montserrat, "Helvetica Neue", sans-serif',
    ui: 'Inter, "Helvetica Neue", Arial, sans-serif',
    mono: '"JetBrains Mono", "SF Mono", monospace',
  },
} as const;

export const SAFE = {
  // vertical Shorts safe zones (1080x1920)
  top: 240, // platform chrome
  bottom: 480, // captions + progress bar
  right: 120, // action buttons
} as const;

export const FPS = 30;
export const W = 1080;
export const H = 1920;
