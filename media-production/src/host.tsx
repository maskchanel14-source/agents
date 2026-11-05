import React from 'react';
import {
  HOST_BROWS,
  HOST_CANVAS,
  HOST_CLOTHES,
  HOST_EYES,
  HOST_GESTURES,
  HOST_GLASSES,
  HOST_HAIR,
  HOST_HEAD,
  HOST_MOUTH,
  HOST_NOSE,
  type HostPart,
} from './host/parts';

/**
 * The host — the teacher who explains the case.
 *
 * The drawing is not hand-coded here: every part comes from the "Notionists"
 * character system by Zoish (CC0 1.0) through DiceBear, baked into
 * `src/host/parts.ts` by `scripts/dicebear_host.mjs` and recoloured to the
 * film's palette. Because the system is mix-and-match, each part can move on
 * its own, which is what makes him act rather than just appear:
 *
 *   head + face   tilt, nod and bob together around the neck
 *   eyes          close on a double-blink cycle
 *   mouth         opens with the real voice envelope (audio/mouth.json)
 *   eyebrows      lift on the "so how?" beat
 *   clothes       breathe
 *   gesture       swaps between beats, and swings while he talks
 *
 * The crop (HOST_VIEW) trims the library's square canvas down to the bust so
 * he fills the frame the way a presenter on camera would.
 */

export type Gesture = 'idle' | 'point' | 'open';

/** Which library gesture each beat uses. */
const GESTURE_OF: Record<Gesture, string> = {
  idle: 'hand',
  point: 'point',
  open: 'pointLongArm',
};

/** Canvas-space pivots, read off the part placements in src/host/parts.ts. */
const NECK = {x: 930, y: 1180};
const SHOULDER = {x: 700, y: 1250};

/**
 * The bust as drawn: wide enough for every gesture, tall enough to anchor him
 * at the bottom of the frame. keep the aspect at 520:780 so the composition's
 * width/height ratio lines up with no letterboxing.
 */
/**
 * The bust as drawn (measured off the rendered ink: canvas x 179–1535,
 * y 241–1763, union of all three gestures) plus a small margin.
 */
export const HOST_VIEW = {x: 172, y: 234, w: 1372, h: 1538};

/** width / height of the drawn bust — the composition sizes him from this. */
export const HOST_ASPECT = HOST_VIEW.w / HOST_VIEW.h;

/** One library part, placed the way the style places it, optionally transformed. */
const Part: React.FC<{p: HostPart; transform?: string}> = ({p, transform}) => (
  <g
    transform={`translate(${p.x} ${p.y})${transform ? ` ${transform}` : ''}`}
    dangerouslySetInnerHTML={{__html: p.body}}
  />
);

/** Scale a part about its own centre, in the part's local coordinates. */
const aboutCentre = (
  p: HostPart,
  sx: number,
  sy: number,
  dx = 0,
  dy = 0,
): string => {
  const cx = HOST_CENTRES[p.id]?.[0] ?? 0;
  const cy = HOST_CENTRES[p.id]?.[1] ?? 0;
  return `translate(${cx + dx} ${cy + dy}) scale(${sx} ${sy}) translate(${-(cx + dx)} ${-(cy + dy)})`;
};

/** Local centre of each part, from the component sizes in the style. */
const HOST_CENTRES: Record<string, [number, number]> = {
  mouth: [127.45, 78],
  eyes: [135.5, 46.85],
  hair: [529.5, 488.5],
  head: [292.5, 492.5],
};

export const Host: React.FC<{
  frame: number;
  /** 0–1 voice energy for this frame, straight from audio/mouth.json. */
  mouth: number;
  gesture: Gesture;
  /** 0–1 eyebrow lift — used on the "so how did they get in?" beat. */
  brow?: number;
  width: number;
  height: number;
}> = ({frame, mouth, gesture, brow = 0, width, height}) => {
  const t = frame / 30;
  const m = Math.min(1, Math.max(0, mouth));

  // a blink every ~3.9 s, with a second one 0.5 s later so it never looks
  // like a metronome
  const cyc = frame % 117;
  const blink =
    cyc < 5 ? Math.sin((cyc / 5) * Math.PI)
      : cyc > 15 && cyc < 20 ? Math.sin(((cyc - 15) / 5) * Math.PI)
        : 0;

  // mouth: one shape, opened on the voice. Squashing a hand-drawn mouth is
  // smoother than swapping between drawn expressions.
  const open = 0.09 + 0.91 * Math.pow(m, 0.85);
  const narrow = 1 - 0.1 * m;

  const rot = Math.sin(t * 1.08) * 1.1 + Math.sin(t * 0.41) * 0.5 + m * 0.45;
  const bob = Math.sin(t * 0.9) * 5;
  const breathe = 1 + Math.sin(t * 0.8) * 0.005;
  const headT = `translate(0 ${bob}) rotate(${rot} ${NECK.x} ${NECK.y})`;

  const g = HOST_GESTURES[GESTURE_OF[gesture]] ?? HOST_GESTURES.hand;
  const gRot = Math.sin(t * 1.05) * 0.9 + m * 1.7;

  return (
    <svg
      width={width}
      height={height}
      viewBox={`${HOST_VIEW.x} ${HOST_VIEW.y} ${HOST_VIEW.w} ${HOST_VIEW.h}`}
      preserveAspectRatio="xMidYMax meet"
      style={{display: 'block', overflow: 'visible'}}
    >
      <g
        transform={
          `translate(${NECK.x} ${NECK.y}) scale(${breathe} ${breathe}) ` +
          `translate(${-NECK.x} ${-NECK.y})`
        }
      >
        {/* head+neck first, so the collar sits on top of it */}
        <g transform={headT}>
          <Part p={HOST_HEAD} />
        </g>

        <Part p={HOST_CLOTHES} />

        {/* everything that belongs to the head moves with it */}
        <g transform={headT}>
          <Part p={HOST_HAIR} />
          <Part p={HOST_MOUTH} transform={aboutCentre(HOST_MOUTH, narrow, open)} />
          <Part p={HOST_NOSE} />
          <Part
            p={HOST_EYES}
            transform={aboutCentre(HOST_EYES, 1, 1 - 0.93 * blink)}
          />
          <Part p={HOST_GLASSES} />
          <Part p={HOST_BROWS} transform={`translate(0 ${-7 * brow})`} />
        </g>

        {/* the arm that carries the beat */}
        <g transform={`rotate(${gRot} ${SHOULDER.x} ${SHOULDER.y})`}>
          <Part p={g} />
        </g>
      </g>
    </svg>
  );
};
