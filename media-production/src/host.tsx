import React from 'react';
import {interpolate} from 'remotion';
import {PAL} from './theme2d';

/**
 * The host — a flat vector presenter who talks straight to camera.
 *
 * Drawn as one SVG so every part can be driven by the frame: the mouth is
 * driven by the real VO energy curve (audio/mouth.json -> REV3_MOUTH), the eyes
 * blink on a deterministic cycle, the torso breathes and the right arm takes a
 * gesture (`idle` | `point` | `open`).
 *
 * Canonical box: 520 x 780, character centred on x = 260, cropped by the frame
 * at the bottom on purpose — he stands behind the lower edge of the picture.
 */

export type Gesture = 'idle' | 'point' | 'open';

const SHOULDER = {x: 400, y: 436};
const ELBOW = {x: 405, y: 610};

const GESTURE: Record<Gesture, {shoulder: number; elbow: number}> = {
  idle: {shoulder: 0, elbow: 6},
  point: {shoulder: 112, elbow: 8},
  open: {shoulder: 46, elbow: -30},
};

/** Deterministic double-blink, 3.8 s cycle. Returns an eyelid scale (0.06-1). */
const lid = (frame: number): number => {
  const c = frame % 114;
  if (c < 3) return interpolate(c, [0, 3], [1, 0.06]);
  if (c < 6) return interpolate(c, [3, 6], [0.06, 1]);
  if (c > 14 && c < 17) return interpolate(c, [14, 17], [1, 0.06]);
  if (c >= 17 && c < 20) return interpolate(c, [17, 20], [0.06, 1]);
  return 1;
};

export const Host: React.FC<{
  frame: number;
  /** Voice energy 0-1 (drives the mouth). */
  mouth: number;
  gesture?: Gesture;
  /** Extra eyebrow raise, 0-1 (used on the question beats). */
  brow?: number;
  width: number;
  height: number;
}> = ({frame, mouth, gesture = 'idle', brow = 0, width, height}) => {
  const t = frame / 30;
  const g = GESTURE[gesture];

  const breathe = 1 + Math.sin(t * 0.8) * 0.006;
  const headRot = Math.sin(t * 1.15) * 1.5 + Math.sin(t * 0.47) * 0.7;
  const headY = Math.sin(t * 0.95) * 3.4;
  const eye = lid(frame);
  const browLift = -7 * brow;
  const emphasis = mouth * 3.4;

  const shoulderRot = g.shoulder + Math.sin(t * (gesture === 'idle' ? 0.9 : 2.1)) * 1.8 + emphasis;
  const elbowRot = g.elbow + Math.sin(t * 1.7) * 2.2;

  const mouthRy = 5 + 26 * Math.pow(mouth, 0.85);
  const mouthRx = 33 - 4 * mouth;

  return (
    <svg
      width={width}
      height={height}
      viewBox="0 0 520 780"
      preserveAspectRatio="xMidYMax meet"
      style={{display: 'block', overflow: 'visible'}}
    >
      <defs>
        <linearGradient id="hostBlazer" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#385585" />
          <stop offset="100%" stopColor="#22385C" />
        </linearGradient>
        <linearGradient id="hostSkin" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#EDBD93" />
          <stop offset="100%" stopColor="#DEA874" />
        </linearGradient>
        <radialGradient id="hostCheek" cx="0.5" cy="0.5" r="0.5">
          <stop offset="0%" stopColor="#C75B2E" stopOpacity="0.30" />
          <stop offset="100%" stopColor="#C75B2E" stopOpacity="0" />
        </radialGradient>
      </defs>

      {/* ---- body -------------------------------------------------------- */}
      <g transform={`translate(260 780) scale(1 ${breathe}) translate(-260 -780)`}>
        {/* left arm, hanging */}
        <g transform="rotate(-2 135 460)">
          <rect x={100} y={424} width={76} height={262} rx={38} fill={PAL.blazerDark} />
          <rect x={106} y={640} width={66} height={128} rx={33} fill={PAL.blazerDark} />
          <rect x={104} y={726} width={70} height={26} rx={13} fill="#182A44" />
          <ellipse cx={139} cy={766} rx={29} ry={33} fill={PAL.skin} />
        </g>

        {/* right arm — the gesturing one */}
        <g transform={`rotate(${shoulderRot} ${SHOULDER.x} ${SHOULDER.y})`}>
          <rect x={372} y={414} width={66} height={212} rx={33} fill={PAL.blazerDark} />
          <g transform={`rotate(${elbowRot} ${ELBOW.x} ${ELBOW.y})`}>
            <rect x={376} y={592} width={58} height={170} rx={29} fill={PAL.blazerDark} />
            <rect x={374} y={734} width={62} height={26} rx={13} fill="#182A44" />
            {gesture === 'point' ? (
              <rect x={396} y={736} width={17} height={62} rx={8.5} fill={PAL.skin} />
            ) : null}
            <ellipse cx={405} cy={774} rx={28} ry={32} fill={PAL.skin} />
            {gesture === 'open' ? (
              <g fill={PAL.skin}>
                <rect x={383} y={786} width={13} height={30} rx={6.5} transform="rotate(-12 389 800)" />
                <rect x={399} y={788} width={13} height={32} rx={6.5} />
                <rect x={415} y={786} width={13} height={28} rx={6.5} transform="rotate(12 421 800)" />
                <ellipse cx={381} cy={776} rx={10} ry={14} transform="rotate(-24 381 776)" />
              </g>
            ) : null}
          </g>
        </g>

        {/* torso */}
        <path
          d="M 92 780 L 100 566 C 106 470 168 414 232 398 L 288 398 C 352 414 414 470 420 566 L 428 780 Z"
          fill="url(#hostBlazer)"
        />
        {/* shirt */}
        <path d="M 232 398 L 288 398 L 288 520 L 260 566 L 232 520 Z" fill={PAL.shirt} />
        {/* collar */}
        <path d="M 232 398 L 260 440 L 246 398 Z" fill="#E6DCCB" />
        <path d="M 288 398 L 260 440 L 274 398 Z" fill="#E6DCCB" />
        {/* tie */}
        <path d="M 251 424 L 269 424 L 275 450 L 245 450 Z" fill={PAL.tie} />
        <path d="M 245 450 L 275 450 L 268 566 L 260 580 L 252 566 Z" fill="#B04E25" />
        {/* lapels */}
        <path d="M 230 396 L 258 496 L 188 470 Z" fill={PAL.blazer} />
        <path d="M 290 396 L 262 496 L 332 470 Z" fill={PAL.blazer} />
        {/* rim light along the silhouette so he separates from the backdrop */}
        <path
          d="M 92 780 L 100 566 C 106 470 168 414 232 398"
          stroke="rgba(158, 196, 232, 0.34)"
          strokeWidth={6}
          fill="none"
        />
        {/* neck */}
        <rect x={232} y={266} width={58} height={86} rx={22} fill={PAL.skinShade} />
        <ellipse cx={261} cy={282} rx={36} ry={16} fill="rgba(60,34,20,0.20)" />
      </g>

      {/* ---- head -------------------------------------------------------- */}
      <g transform={`translate(0 ${headY}) rotate(${headRot} 260 300)`}>
        {/* hair, back mass */}
        <ellipse cx={260} cy={172} rx={101} ry={105} fill={PAL.hair} />
        {/* ears */}
        <ellipse cx={167} cy={196} rx={16} ry={24} fill={PAL.skinShade} />
        <ellipse cx={353} cy={196} rx={16} ry={24} fill={PAL.skinShade} />
        {/* face */}
        <ellipse cx={260} cy={186} rx={90} ry={100} fill="url(#hostSkin)" />
        {/* fringe */}
        <path
          d="M 172 176 C 176 108 214 80 262 80 C 310 80 346 108 349 176 C 332 130 300 112 262 120 C 226 128 190 138 172 176 Z"
          fill={PAL.hair}
        />
        {/* cheeks */}
        <ellipse cx={212} cy={228} rx={30} ry={20} fill="url(#hostCheek)" />
        <ellipse cx={308} cy={228} rx={30} ry={20} fill="url(#hostCheek)" />
        {/* brows */}
        <g stroke={PAL.hair} strokeWidth={10} strokeLinecap="round" fill="none"
           transform={`translate(0 ${browLift})`}>
          <path d="M 202 152 Q 230 136 258 150" />
          <path d="M 291 150 Q 319 136 347 152" />
        </g>
        {/* eyes */}
        <g fill="#241A14">
          <ellipse cx={233} cy={188} rx={13} ry={15 * eye} />
          <ellipse cx={343} cy={188} rx={13} ry={15 * eye} />
        </g>
        {/* glasses */}
        <g stroke={PAL.gold} strokeWidth={7} fill="rgba(180, 214, 232, 0.10)">
          <rect x={192} y={156} width={82} height={64} rx={18} />
          <rect x={302} y={156} width={82} height={64} rx={18} />
          <path d="M 274 178 Q 288 168 302 178" fill="none" />
          <path d="M 192 174 L 162 186" fill="none" />
          <path d="M 384 174 L 358 186" fill="none" />
        </g>
        {/* nose */}
        <path d="M 286 198 Q 298 228 281 238" stroke="#C98B62" strokeWidth={7}
              strokeLinecap="round" fill="none" />
        {/* mouth — driven by the voice */}
        <ellipse cx={288} cy={264} rx={mouthRx} ry={mouthRy} fill="#5E2A26" />
        <path d="M 264 272 Q 288 282 312 272" stroke="#C98B62" strokeWidth={4}
              fill="none" strokeLinecap="round" opacity={0.5} />
        {/* chin shadow */}
        <ellipse cx={288} cy={292} rx={38} ry={9} fill="rgba(60,34,20,0.10)" />
        {/* rim light on the head */}
        <path
          d="M 173 214 C 166 140 204 92 258 84"
          stroke="rgba(158, 196, 232, 0.26)"
          strokeWidth={6}
          fill="none"
          strokeLinecap="round"
        />
      </g>
    </svg>
  );
};
