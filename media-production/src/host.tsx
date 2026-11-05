import React from 'react';
import {interpolate} from 'remotion';
import {PAL} from './theme2d';

/**
 * The host — a flat vector presenter who talks straight to camera.
 *
 * Drawn as one SVG, 520 x 780, centred on x = 260, cropped by the frame at the
 * bottom on purpose: he stands behind the lower edge of the picture.
 *
 * Craft notes (this is what keeps him from looking cheap):
 *   - the head is a real skull-and-jaw path, not an ellipse, with ears,
 *     temples and a soft jaw shadow
 *   - the hair is a swept shape with a low side parting, plus a highlight
 *   - eyes are almonds with an iris, a pupil and a catchlight, and they blink
 *   - the mouth is lips + opening + teeth + tongue, so it opens like a mouth
 *     instead of turning into a dark hole
 *   - hands have fingers and a thumb; the gesturing arm sits in front of the
 *     torso so a raised arm is never hidden behind the chest
 *   - every shadow is a blurred shape, never a hard grey patch
 */

export type Gesture = 'idle' | 'point' | 'open';

const SHOULDER = {x: 370, y: 434};
const ELBOW = {x: 377, y: 604};

const GESTURE: Record<Gesture, {shoulder: number; elbow: number}> = {
  idle: {shoulder: 0, elbow: 4},
  point: {shoulder: 55, elbow: 6},
  open: {shoulder: 32, elbow: -26},
};

/** Deterministic double-blink on a 3.8 s cycle. Returns an eyelid scale. */
const lid = (frame: number): number => {
  const c = frame % 114;
  if (c < 3) return interpolate(c, [0, 3], [1, 0.06]);
  if (c < 6) return interpolate(c, [3, 6], [0.06, 1]);
  if (c > 14 && c < 17) return interpolate(c, [14, 17], [1, 0.06]);
  if (c >= 17 && c < 20) return interpolate(c, [17, 20], [0.06, 1]);
  return 1;
};

/** A hand: palm, four fingers and a thumb. `hang` points down, `open` is a
 *  palm-up fan, `point` is a loose fist with the index finger out. */
const Hand: React.FC<{cx: number; cy: number; mode: 'hang' | 'point' | 'open'}> = ({
  cx,
  cy,
  mode,
}) => {
  const skin = PAL.skin;
  const shade = PAL.skinShade;
  if (mode === 'hang') {
    return (
      <g>
        <rect x={cx - 24} y={cy} width={48} height={52} rx={22} fill={skin} />
        <rect x={cx - 22} y={cy + 28} width={12} height={32} rx={6} fill={skin} />
        <rect x={cx - 8} y={cy + 30} width={12} height={34} rx={6} fill={skin} />
        <rect x={cx + 6} y={cy + 28} width={12} height={31} rx={6} fill={skin} />
        <rect x={cx + 19} y={cy + 22} width={11} height={26} rx={5.5} fill={shade} />
        <rect
          x={cx - 35}
          y={cy + 4}
          width={13}
          height={30}
          rx={6.5}
          fill={skin}
          transform={`rotate(-18 ${cx - 28} ${cy + 18})`}
        />
        <path
          d={`M ${cx - 22} ${cy + 34} h 40`}
          stroke={shade}
          strokeWidth={2.5}
          opacity={0.5}
          fill="none"
        />
      </g>
    );
  }
  if (mode === 'point') {
    return (
      <g>
        <rect x={cx - 22} y={cy} width={44} height={46} rx={20} fill={skin} />
        <rect x={cx - 7} y={cy + 28} width={14} height={42} rx={7} fill={skin} />
        <rect
          x={cx - 25}
          y={cy + 6}
          width={12}
          height={26}
          rx={6}
          fill={shade}
          transform={`rotate(16 ${cx - 19} ${cy + 18})`}
        />
        <rect x={cx + 8} y={cy + 12} width={12} height={24} rx={6} fill={shade} />
        <rect x={cx + 18} y={cy + 8} width={11} height={22} rx={5.5} fill={shade} />
      </g>
    );
  }
  return (
    <g>
      <rect x={cx - 22} y={cy} width={44} height={44} rx={20} fill={skin} />
      <rect
        x={cx - 25}
        y={cy + 24}
        width={12}
        height={30}
        rx={6}
        fill={shade}
        transform={`rotate(-18 ${cx - 19} ${cy + 32})`}
      />
      <rect
        x={cx - 10}
        y={cy + 28}
        width={12}
        height={33}
        rx={6}
        fill={skin}
        transform={`rotate(-6 ${cx - 4} ${cy + 36})`}
      />
      <rect
        x={cx + 4}
        y={cy + 28}
        width={12}
        height={32}
        rx={6}
        fill={skin}
        transform={`rotate(6 ${cx + 10} ${cy + 36})`}
      />
      <rect
        x={cx + 18}
        y={cy + 24}
        width={11}
        height={27}
        rx={5.5}
        fill={shade}
        transform={`rotate(18 ${cx + 23} ${cy + 30})`}
      />
      <ellipse
        cx={cx - 26}
        cy={cy + 12}
        rx={9}
        ry={13}
        fill={skin}
        transform={`rotate(-30 ${cx - 26} ${cy + 12})`}
      />
    </g>
  );
};

export const Host: React.FC<{
  frame: number;
  /** Voice energy 0-1 (drives the mouth). */
  mouth: number;
  gesture?: Gesture;
  /** Extra eyebrow raise, 0-1 (question beats). */
  brow?: number;
  width: number;
  height: number;
}> = ({frame, mouth, gesture = 'idle', brow = 0, width, height}) => {
  const t = frame / 30;
  const g = GESTURE[gesture];

  const breathe = 1 + Math.sin(t * 0.8) * 0.006;
  const headRot = Math.sin(t * 1.15) * 1.4 + Math.sin(t * 0.47) * 0.6;
  const headY = Math.sin(t * 0.95) * 3.2;
  const eye = lid(frame);
  const browLift = -7 * brow;
  const emphasis = mouth * 3.2;

  const shoulderRot = g.shoulder + Math.sin(t * (gesture === 'idle' ? 0.9 : 1.9)) * 1.6 + emphasis;
  const elbowRot = g.elbow + Math.sin(t * 1.6) * 2.0;
  const handMode = gesture === 'open' ? 'open' : gesture === 'point' ? 'point' : 'hang';

  // mouth geometry: 44 px wide, opens to 22 px — a mouth, not a hole
  const open = 2 + 20 * Math.pow(mouth, 0.9);
  const teeth = Math.min(1, mouth * 1.6);

  return (
    <svg
      width={width}
      height={height}
      viewBox="0 0 520 780"
      preserveAspectRatio="xMidYMax meet"
      style={{display: 'block', overflow: 'visible'}}
    >
      <defs>
        <linearGradient id="hSkin" x1="0.2" y1="0" x2="0.8" y2="1">
          <stop offset="0%" stopColor="#F0C398" />
          <stop offset="55%" stopColor="#E8B58A" />
          <stop offset="100%" stopColor="#D69E70" />
        </linearGradient>
        <linearGradient id="hHair" x1="0.1" y1="0" x2="0.9" y2="1">
          <stop offset="0%" stopColor="#3B2C21" />
          <stop offset="60%" stopColor="#2A1F18" />
          <stop offset="100%" stopColor="#1D150F" />
        </linearGradient>
        <linearGradient id="hBlazer" x1="0" y1="0" x2="0.3" y2="1">
          <stop offset="0%" stopColor="#35517F" />
          <stop offset="55%" stopColor="#2A4370" />
          <stop offset="100%" stopColor="#1E3355" />
        </linearGradient>
        <linearGradient id="hSleeve" x1="0" y1="0" x2="0.4" y2="1">
          <stop offset="0%" stopColor="#43619A" />
          <stop offset="60%" stopColor="#33507F" />
          <stop offset="100%" stopColor="#263C63" />
        </linearGradient>
        <linearGradient id="hKnit" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#F2EADA" />
          <stop offset="100%" stopColor="#DED3BE" />
        </linearGradient>
        <radialGradient id="hCheek" cx="0.5" cy="0.5" r="0.5">
          <stop offset="0%" stopColor="#C75B2E" stopOpacity="0.22" />
          <stop offset="100%" stopColor="#C75B2E" stopOpacity="0" />
        </radialGradient>
        <filter id="hSoft" x="-40%" y="-40%" width="180%" height="180%">
          <feGaussianBlur stdDeviation="7" />
        </filter>
        <filter id="hSoft2" x="-40%" y="-40%" width="180%" height="180%">
          <feGaussianBlur stdDeviation="4" />
        </filter>
      </defs>

      {/* ---- body -------------------------------------------------------- */}
      <g transform={`translate(260 780) scale(1 ${breathe}) translate(-260 -780)`}>
        {/* neck — runs well under the collar so there is never a gap between
            the head and the shoulders */}
        <path
          d="M 226 272 L 226 400 C 226 424 240 442 260 442 C 280 442 294 424 294 400 L 294 272 Z"
          fill={PAL.skinShade}
        />
        <ellipse cx={260} cy={286} rx={42} ry={15} fill="#6B4426" opacity={0.32} filter="url(#hSoft2)" />

        {/* knit sweater */}
        <path
          d="M 146 420 C 170 390 202 378 228 382 C 244 414 272 414 288 382 C 314 378 346 390 370 420 L 386 780 L 130 780 Z"
          fill="url(#hKnit)"
        />
        <path d="M 228 382 C 244 414 272 414 288 382" stroke="#CFC2AB" strokeWidth={9} fill="none" />

        {/* blazer */}
        <path
          d="M 146 420 C 170 390 202 378 228 382 L 200 780 L 102 780 C 98 620 114 496 146 420 Z"
          fill="url(#hBlazer)"
        />
        <path
          d="M 370 420 C 346 390 314 378 288 382 L 316 780 L 414 780 C 418 620 402 496 370 420 Z"
          fill="url(#hBlazer)"
        />
        {/* jacket front — closes under the lapels so the knit only shows in
            the V, the way a real jacket does */}
        <path d="M 226 382 L 260 494 L 294 382 L 320 780 L 196 780 Z" fill="url(#hBlazer)" />
        {/* lapels */}
        <path
          d="M 226 382 C 238 422 250 456 260 494 L 192 530 C 184 472 198 412 226 382 Z"
          fill="#22375A"
        />
        <path
          d="M 294 382 C 282 422 270 456 260 494 L 328 530 C 336 472 322 412 294 382 Z"
          fill="#22375A"
        />
        <path
          d="M 226 382 C 238 422 250 456 260 494"
          stroke="#4A6A9C"
          strokeWidth={2.5}
          fill="none"
          opacity={0.8}
        />
        {/* buttons sit on the overlap */}
        <circle cx={276} cy={578} r={6} fill="#16263C" />
        <circle cx={276} cy={640} r={6} fill="#16263C" />

        {/* left arm — hangs */}
        <g transform="rotate(-4 128 442)">
          <rect x={94} y={412} width={74} height={248} rx={37} fill="url(#hSleeve)"
                stroke="rgba(9, 16, 29, 0.55)" strokeWidth={3} />
          <rect x={100} y={618} width={62} height={112} rx={31} fill="url(#hSleeve)"
                stroke="rgba(9, 16, 29, 0.55)" strokeWidth={3} />
          <ellipse cx={131} cy={418} rx={38} ry={16} fill="rgba(9,16,29,0.35)" filter="url(#hSoft2)" />
          <g stroke="#1B2C48" strokeWidth={2.5} opacity={0.6} fill="none">
            <path d="M 102 560 C 116 554 136 554 150 560" />
            <path d="M 104 604 C 118 598 138 598 152 604" />
          </g>
          <Hand cx={131} cy={700} mode="hang" />
        </g>

        {/* right arm — the gesturing one, drawn in front so it is never hidden */}
        <ellipse cx={328} cy={530} rx={54} ry={150} fill="rgba(9,16,29,0.30)"
                 filter="url(#hSoft)" opacity={gesture === 'idle' ? 0.5 : 1} />
        <g transform={`rotate(${shoulderRot} ${SHOULDER.x} ${SHOULDER.y})`}>
          <rect x={338} y={412} width={70} height={208} rx={35} fill="url(#hSleeve)"
                stroke="rgba(9, 16, 29, 0.55)" strokeWidth={3} />
          <g transform={`rotate(${elbowRot} ${ELBOW.x} ${ELBOW.y})`}>
            <rect x={346} y={584} width={62} height={124} rx={31} fill="url(#hSleeve)"
                  stroke="rgba(9, 16, 29, 0.55)" strokeWidth={3} />
            <rect x={344} y={682} width={66} height={20} rx={10} fill="#16263C" />
            <Hand cx={377} cy={700} mode={handMode} />
          </g>
        </g>
      </g>

      {/* ---- head -------------------------------------------------------- */}
      <g transform={`translate(0 ${headY}) rotate(${headRot} 260 300)`}>
        {/* ears */}
        <ellipse cx={166} cy={184} rx={15} ry={23} fill={PAL.skinShade} />
        <ellipse cx={354} cy={184} rx={15} ry={23} fill={PAL.skinShade} />
        <ellipse cx={168} cy={187} rx={6.5} ry={11} fill="#B9835A" opacity={0.7} />
        <ellipse cx={352} cy={187} rx={6.5} ry={11} fill="#B9835A" opacity={0.7} />

        {/* face */}
        <path
          d="M 260 72 C 302 72 344 92 352 142 C 358 180 352 226 332 256
             C 314 282 290 296 260 296 C 230 296 206 282 188 256
             C 168 226 162 180 168 142 C 176 92 218 72 260 72 Z"
          fill="url(#hSkin)"
        />

        {/* cheek warmth + jaw shadow */}
        <ellipse cx={206} cy={228} rx={30} ry={22} fill="url(#hCheek)" />
        <ellipse cx={314} cy={228} rx={30} ry={22} fill="url(#hCheek)" />
        <ellipse cx={260} cy={276} rx={54} ry={20} fill="#6B4426" opacity={0.13} filter="url(#hSoft)" />

        {/* hair */}
        <path
          d="M 166 148 C 160 96 202 62 258 62 C 312 62 352 92 354 144
             C 348 116 332 100 306 92 C 292 106 272 112 250 108
             C 220 102 192 116 176 140 C 172 143 169 145 166 148 Z"
          fill="url(#hHair)"
        />
        <path
          d="M 198 116 C 216 86 248 74 282 76 C 252 86 224 98 208 124 Z"
          fill="#5A4433"
          opacity={0.55}
        />
        <g stroke="#3A2B1F" strokeWidth={2.5} fill="none" opacity={0.75} strokeLinecap="round">
          <path d="M 258 104 C 272 100 286 104 296 114" />
          <path d="M 248 108 C 258 104 268 104 276 110" />
        </g>
        {/* sideburns */}
        <path d="M 172 150 C 176 172 178 190 180 206 C 186 190 186 168 182 150 Z" fill="#2A1F18" opacity={0.85} />
        <path d="M 348 150 C 344 172 342 190 340 206 C 334 190 334 168 338 150 Z" fill="#2A1F18" opacity={0.85} />

        {/* brows */}
        <g fill={PAL.hair} transform={`translate(0 ${browLift})`}>
          <path d="M 190 152 C 200 133 226 127 246 137 C 224 135 204 143 192 160 Z" />
          <path d="M 274 137 C 294 127 320 133 330 152 C 318 143 298 135 276 160 Z" />
        </g>

        {/* eyes */}
        <g>
          <g transform={`translate(0 176) scale(1 ${eye}) translate(0 -176)`}>
            <path d="M 196 178 C 206 163 232 161 246 174 C 232 191 206 191 196 178 Z" fill="#F8F3EA" />
            <circle cx={221} cy={176} r={9.5} fill="#33261C" />
            <circle cx={221} cy={176} r={4.6} fill="#120C08" />
            <circle cx={217} cy={172} r={2.8} fill="#FFFFFF" opacity={0.92} />
          </g>
          <g transform={`translate(0 176) scale(1 ${eye}) translate(0 -176)`}>
            <path d="M 274 174 C 288 161 314 163 324 178 C 314 191 288 191 274 174 Z" fill="#F8F3EA" />
            <circle cx={299} cy={176} r={9.5} fill="#33261C" />
            <circle cx={299} cy={176} r={4.6} fill="#120C08" />
            <circle cx={295} cy={172} r={2.8} fill="#FFFFFF" opacity={0.92} />
          </g>
          {/* lids */}
          <path
            d="M 196 178 C 206 163 232 161 246 174"
            stroke="#3A2A1E"
            strokeWidth={4}
            fill="none"
            strokeLinecap="round"
          />
          <path
            d="M 274 174 C 288 161 314 163 324 178"
            stroke="#3A2A1E"
            strokeWidth={4}
            fill="none"
            strokeLinecap="round"
          />
        </g>

        {/* glasses — thin gold rims */}
        <g stroke="#C79A34" strokeWidth={5} fill="rgba(196, 222, 236, 0.12)">
          <rect x={192} y={150} width={70} height={54} rx={15} />
          <rect x={268} y={150} width={70} height={54} rx={15} />
          <path d="M 262 166 C 265 162 267 162 268 166" fill="none" />
          <path d="M 192 164 L 168 174" fill="none" />
          <path d="M 338 164 L 352 174" fill="none" />
        </g>
        {/* glass highlights */}
        <g stroke="rgba(255,255,255,0.38)" strokeWidth={6} strokeLinecap="round">
          <path d="M 203 194 L 219 158" />
          <path d="M 279 194 L 295 158" />
        </g>

        {/* nose */}
        <path
          d="M 257 190 C 255 212 249 227 243 232"
          stroke="#C08756"
          strokeWidth={6}
          strokeLinecap="round"
          fill="none"
        />
        <ellipse cx={243} cy={233} rx={4} ry={3} fill="#A8703F" opacity={0.8} />
        <ellipse cx={264} cy={233} rx={4} ry={3} fill="#A8703F" opacity={0.7} />

        {/* mouth */}
        <g>
          <path
            d={`M 238 250 C 248 246 270 246 280 250 C 278 ${250 + open} 240 ${250 + open} 238 250 Z`}
            fill="#7A2E2A"
          />
          <rect
            x={241}
            y={250}
            width={36}
            height={5.5 * teeth}
            rx={2.5}
            fill="#FBF3E6"
            opacity={teeth}
          />
          <ellipse
            cx={259}
            cy={250 + open - 4}
            rx={11}
            ry={4.5 * Math.min(1, mouth * 1.4)}
            fill="#B45A52"
            opacity={Math.min(1, mouth * 1.6)}
          />
          <path
            d={`M 238 250 C 248 246 270 246 280 250 C 270 ${252 + open * 0.4} 248 ${252 + open * 0.4} 238 250 Z`}
            fill="#B4674F"
            opacity={0.9}
          />
        </g>
        <ellipse cx={259} cy={272} rx={17} ry={5} fill="#6B4426" opacity={0.10} filter="url(#hSoft2)" />

        {/* rim light, so he never melts into the backdrop */}
        <path
          d="M 168 142 C 162 180 168 226 188 256 C 206 282 230 296 260 296"
          stroke="rgba(158, 196, 232, 0.30)"
          strokeWidth={5}
          fill="none"
          strokeLinecap="round"
        />
        <path
          d="M 146 420 C 170 390 202 378 228 382"
          stroke="rgba(158, 196, 232, 0.22)"
          strokeWidth={4}
          fill="none"
        />
      </g>
    </svg>
  );
};
