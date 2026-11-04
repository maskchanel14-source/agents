import {DURATION_IN_FRAMES} from './theme';

/**
 * Shot list for SHORTS-2026-024 "The Twenty-Minute Heist" (67 s @ 30 fps).
 *
 * Frame boundaries come from audio/timing.json — each VO clip measured after
 * atempo, so the picture turns on the exact frame the narrator starts a line.
 *
 * There are NO hard cuts: `camera.ts` threads every `camera.pos` below into one
 * continuous Catmull-Rom spline and glides through them for the whole 67 s.
 */

export type CharAction =
  | 'idle'
  | 'walk'
  | 'march'
  | 'scared'
  | 'freeze'
  | 'type'
  | 'salute';

export type Shot = {
  id: number;
  start: number;
  end: number;
  camera: {pos: [number, number, number]; lookAt: [number, number, number]};
  /** Which VO clip this shot carries (see audio/timing.json → clips[].id). */
  voId: string;
  /** Spoken line this shot illustrates. */
  script: string;
  /** Primary character action for the beat. */
  action: CharAction;
  /** Big on-screen number / label for the beat (null = none). */
  overlay: string | null;
  /** Caption burned in at the bottom of the frame. */
  caption: string;
};

export const SHOTS: Shot[] = [
  {
    id: 1,
    start: 0,
    end: 200, // 0.00 – 6.67 s
    camera: {pos: [-58, 30, 44], lookAt: [-6, 6, 0]},
    voId: 'L1',
    script: 'In twenty minutes, $6.3 billion walked out of Binance.',
    action: 'march',
    overlay: '$6.3 BILLION',
    caption: 'In twenty minutes, $6.3 billion walked out of Binance.',
  },
  {
    id: 2,
    start: 200,
    end: 455, // 6.67 – 15.17 s
    camera: {pos: [-46, 22, 30], lookAt: [-30, 19, 0]},
    voId: 'B1',
    script: "October 29, 2026. 8:05 PM UTC. The world's largest crypto exchange started draining.",
    action: 'idle',
    overlay: '29 OCT 2026 · 20:05 UTC',
    caption: "29 Oct 2026, 20:05 UTC — the world's largest crypto exchange started draining.",
  },
  {
    id: 3,
    start: 455,
    end: 705, // 15.17 – 23.50 s
    camera: {pos: [-26, 16, 30], lookAt: [2, 6, 0]},
    voId: 'B2a',
    script: 'Money left hot wallets on ten blockchains at once.',
    action: 'march',
    overlay: '10 BLOCKCHAINS',
    caption: 'Money left hot wallets on ten blockchains at once.',
  },
  {
    id: 4,
    start: 705,
    end: 910, // 23.50 – 30.33 s
    camera: {pos: [2, 10, 26], lookAt: [16, 3, -2]},
    voId: 'B2b',
    script: 'Eighteen thousand two hundred seventy Bitcoin went too.',
    action: 'scared',
    overlay: '18,270 BTC',
    caption: '18,270 Bitcoin went too — and nobody can freeze Bitcoin.',
  },
  {
    id: 5,
    start: 910,
    end: 1060, // 30.33 – 35.33 s
    camera: {pos: [16, 8, 14], lookAt: [24, 2, 4]},
    voId: 'B2c',
    script: 'Only after Tether and Circle froze three billion dollars did the bleeding slow.',
    action: 'freeze',
    overlay: '$3B FROZEN',
    caption: 'Tether and Circle froze $3 billion. The bleeding slowed.',
  },
  {
    id: 6,
    start: 1060,
    end: 1400, // 35.33 – 46.67 s
    camera: {pos: [2, 15, 8], lookAt: [10.5, 13.6, -8.2]},
    voId: 'B3b',
    script: 'But the door wasn’t a broken vault.',
    action: 'type',
    overlay: 'FAKE JOB INTERVIEW',
    caption: "A wallet engineer sat through a fake job interview with the 'CEO' of a company that did not exist.",
  },
  {
    id: 7,
    start: 1400,
    end: 1530, // 46.67 – 51.00 s
    camera: {pos: [8, 14.2, -2], lookAt: [10.5, 13.4, -8.4]},
    voId: 'B3c',
    script: 'From that one laptop, the attacker took the whole system.',
    action: 'type',
    overlay: 'ONE LAPTOP',
    caption: 'From that one laptop, the attacker took the whole system.',
  },
  {
    id: 8,
    start: 1530,
    end: 1685, // 51.00 – 56.17 s
    camera: {pos: [10, 18, 18], lookAt: [0, 6, 0]},
    voId: 'P1',
    script: 'Binance paid every dollar back from its own treasury.',
    action: 'salute',
    overlay: '$6.34B REFUNDED',
    caption: 'Binance paid every dollar back from its own treasury.',
  },
  {
    id: 9,
    start: 1685,
    end: DURATION_IN_FRAMES, // 56.17 – 67.00 s
    camera: {pos: [-6, 34, 52], lookAt: [0, 8, 0]},
    voId: 'P2',
    script: 'The FBI blamed TraderTraitor — the largest crypto theft in history.',
    action: 'idle',
    overlay: 'LARGEST CRYPTO THEFT IN HISTORY',
    caption: 'The FBI blamed TraderTraitor. The largest crypto theft in history.',
  },
];

export const shotAt = (frame: number): Shot => {
  for (let i = SHOTS.length - 1; i >= 0; i -= 1) {
    if (frame >= SHOTS[i].start) return SHOTS[i];
  }
  return SHOTS[0];
};

/** 0 → 1 progress through a shot, clamped. */
export const shotProgress = (frame: number): number => {
  const s = shotAt(frame);
  return Math.min(1, Math.max(0, (frame - s.start) / (s.end - s.start)));
};

export const STORY_TOTAL_FRAMES = DURATION_IN_FRAMES;
