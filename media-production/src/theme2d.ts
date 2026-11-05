/**
 * Style system for SHORTS-2026-024 revision 3 — the 2D editorial explainer.
 *
 * Revision 2 was semi-realist 3D. Revision 3 goes the other way on purpose:
 * flat vector illustration, a host who talks to camera, and type that carries
 * the numbers. This file is the single place the look is defined so the whole
 * film reads as one piece.
 *
 * Rules that keep it from looking cheap:
 *   - one warm editorial palette, no pure black, no pure white
 *   - generous margins (60 px gutters) and a real type hierarchy
 *   - every scene moves (Ken Burns), every word of the caption animates in
 *   - film grain + vignette over the whole frame
 */

export const PAL = {
  // background
  ink: '#0B1220',
  navy: '#12203A',
  navySoft: '#1B2C4A',
  navyLine: 'rgba(244, 237, 226, 0.14)',

  // paper
  cream: '#F4EDE2',
  paper: '#FBF7F0',
  slate: '#93A0B5',
  slateDim: 'rgba(147, 160, 181, 0.62)',

  // accents
  gold: '#E8B33A',
  terracotta: '#C75B2E',
  teal: '#2E7D74',
  ice: '#9FD3E8',

  // host
  skin: '#E8B58A',
  skinShade: '#D19A70',
  hair: '#2A1F18',
  blazer: '#2C4670',
  blazerDark: '#22385C',
  shirt: '#F4EDE2',
  tie: '#C75B2E',
} as const;

export const TYPE = {
  display: "'Space Grotesk Variable', 'Space Grotesk', system-ui, sans-serif",
  mono: "'IBM Plex Mono', ui-monospace, monospace",
} as const;

/** Frame geometry — 1080x1920. */
export const W = 1080;
export const H = 1920;

/**
 * Two layout modes. When the host steps up full-frame the illustration card
 * shrinks and everything lifts, so his head never collides with the caption.
 */
export const LAYOUT = {
  cardX: 60,
  cardW: 960,
  card: {
    y: 250, //  host off
    yHost: 196, //  host full-frame
    h: 660,
    hHost: 520,
    radius: 26,
  },
  headline: {
    top: 986, //  host off
    topHost: 820, //  host full-frame
  },
  // host is centred and anchored to the bottom edge, cropped by the frame
  host: {
    centerX: 540,
    bottom: 1936,
    hFull: 852,
    hPresent: 704,
  },
} as const;

/** Chrome: kicker row + progress rule live at the top, the bottom stays clear. */
export const CHROME = {
  kickerY: 92,
  ruleY: 150,
} as const;

/** The two webfonts, served from public/shorts023/fonts (already in the repo). */
export const fontCss = (displayUrl: string, monoUrl: string) => `
@font-face {
  font-family: 'Space Grotesk Variable';
  font-style: normal;
  font-weight: 300 800;
  font-display: block;
  src: url('${displayUrl}') format('woff2');
}
@font-face {
  font-family: 'IBM Plex Mono';
  font-style: normal;
  font-weight: 400 600;
  font-display: block;
  src: url('${monoUrl}') format('woff2');
}
`;
