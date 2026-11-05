import React from 'react';
import {
  AbsoluteFill,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import {REV3_CLIPS, REV3_DURATION} from '../data/shorts024Timeline';
import {REV3_MOUTH} from '../data/shorts024Mouth';
import {Host, HOST_ASPECT, type Gesture} from '../host';
import {CHROME, H, LAYOUT, PAL, TYPE, W, fontCss} from '../theme2d';
import {Overlay, SCENES, SceneLayer} from '../scenes2d';

/**
 * SHORTS-2026-024B "The Twenty-Minute Heist" — revision 3.
 *
 * A 2D editorial explainer with a host. One illustration per beat, the numbers
 * drawn as type, and a vector presenter who steps up for the hook, the concept
 * beats and the close.
 *
 * Everything is driven by audio/timing3.json (src/data/shorts024Timeline.ts) and
 * audio/mouth.json (src/data/shorts024Mouth.ts), so the picture cannot drift
 * away from the voice.
 */

const FONT_CSS = fontCss(
  staticFile('shorts023/fonts/space-grotesk-variable.woff2'),
  staticFile('shorts023/fonts/ibm-plex-mono-500.woff2'),
);

const GRAIN = `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='180' height='180'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='3'/%3E%3C/filter%3E%3Crect width='180' height='180' filter='url(%23n)'/%3E%3C/svg%3E")`;

type Cap = {text: string; startFrame: number; endFrame: number; clipId: string};

const CAPTIONS: Cap[] = REV3_CLIPS.flatMap((c) =>
  c.captions.map((cap) => ({...cap, clipId: c.id})),
);

const clipAt = (frame: number) =>
  REV3_CLIPS.find((c) => frame >= c.startFrame - 8 && frame < c.endFrame + 8);

type HostWindow = {
  from: number;
  to: number;
  mode: 'full' | 'present';
  gesture: Gesture;
  brow?: number;
};

const HOST_WINDOWS: HostWindow[] = [
  {from: 12, to: 172, mode: 'full', gesture: 'idle'},
  {from: 316, to: 485, mode: 'present', gesture: 'point'},
  {from: 1032, to: 1200, mode: 'full', gesture: 'open', brow: 1},
  {from: 1358, to: 1536, mode: 'present', gesture: 'open'},
  {from: 1985, to: REV3_DURATION + 40, mode: 'full', gesture: 'idle'},
];

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

/** Chapter rail under the caption — the beats of the story, current one lit. */
const RAIL = ['HOOK', 'MARKET', 'WALLET', 'DRAIN', 'BTC', 'FROZEN', 'ENTRY',
  'CLICK', 'REPAID', 'RECORD'];

/** Ramp 0→1 inside a window with soft edges. */
const windowRamp = (frame: number, a: number, b: number, edge = 12): number =>
  Math.min(
    interpolate(frame, [a, a + edge], [0, 1], clamp),
    interpolate(frame, [b - edge, b], [1, 0], clamp),
  );

const maxRamp = (frame: number, mode: 'full' | 'present'): number =>
  HOST_WINDOWS.filter((w) => w.mode === mode).reduce(
    (m, w) => Math.max(m, windowRamp(frame, w.from, w.to, 14)),
    0,
  );

/** punch / stat / plain decides weight, colour and size of a caption line. */
const capRole = (text: string): 'punch' | 'stat' | 'plain' => {
  if (/\d/.test(text)) return 'stat';
  if (text.split(' ').length <= 2) return 'punch';
  return 'plain';
};

const capSize = (text: string): number => {
  if (text.length >= 26) return 76;
  if (text.length >= 21) return 84;
  return 94;
};

export const Binance63B2D: React.FC = () => {
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();

  const fullP = maxRamp(frame, 'full');
  const presentP = maxRamp(frame, 'present');

  const cardY = interpolate(fullP, [0, 1], [LAYOUT.card.y, LAYOUT.card.yHost]);
  const cardH = interpolate(fullP, [0, 1], [LAYOUT.card.h, LAYOUT.card.hHost]);
  const headlineTop = interpolate(fullP, [0, 1], [
    LAYOUT.headline.top,
    LAYOUT.headline.topHost,
  ]);

  const scenes = SCENES.filter((s) => frame >= s.from - 26 && frame < s.to + 26);
  const clip = clipAt(frame);
  const mouth = (REV3_MOUTH[frame] ?? 0) / 100;

  return (
    <AbsoluteFill style={{backgroundColor: PAL.ink}}>
      <style>{FONT_CSS}</style>

      {/* backdrop */}
      <AbsoluteFill
        style={{
          // a designed deep-navy page, not a black void: the floor never drops
          // below #131E33 so the frame still reads on a phone at low brightness
          background:
            'radial-gradient(120% 78% at 50% -8%, #2C4473 0%, #1E2F50 34%, #131E33 74%)',
        }}
      />

      {/* ------------------------------------------------ illustration card */}
      <div
        style={{
          position: 'absolute',
          left: LAYOUT.cardX,
          top: cardY,
          width: LAYOUT.cardW,
          height: cardH,
          borderRadius: LAYOUT.card.radius,
          overflow: 'hidden',
          border: `1px solid ${PAL.navyLine}`,
          boxShadow: '0 44px 90px rgba(0, 0, 0, 0.55)',
        }}
      >
        {scenes.map((s) => (
          <SceneLayer key={s.key} scene={s} frame={frame} h={cardH} />
        ))}
        {/* legibility scrim at the bottom of the card */}
        <div
          style={{
            position: 'absolute',
            left: 0,
            right: 0,
            bottom: 0,
            height: 160,
            background: 'linear-gradient(180deg, rgba(6,10,18,0) 0%, rgba(6,10,18,0.55) 100%)',
          }}
        />
        {clip ? <Overlay id={clip.id} frame={frame - clip.startFrame} /> : null}
      </div>

      {/* --------------------------------------------------------- captions */}
      {CAPTIONS.filter((c) => frame >= c.startFrame - 6 && frame < c.endFrame + 8).map((c) => {
        const role = capRole(c.text);
        const size = capSize(c.text);
        const words = c.text.split(' ');
        const out = interpolate(frame, [c.endFrame - 2, c.endFrame + 6], [1, 0], clamp);
        const color = role === 'stat' ? PAL.gold : PAL.cream;
        return (
          <div key={`${c.clipId}-${c.startFrame}`}>
            <div
              style={{
                position: 'absolute',
                left: LAYOUT.cardX,
                top: headlineTop,
                width: LAYOUT.cardW,
                display: 'flex',
                flexWrap: 'wrap',
                justifyContent: 'center',
                columnGap: 20,
                rowGap: 2,
                opacity: out,
              }}
            >
              {words.map((w, i) => {
                const p = interpolate(
                  frame,
                  [c.startFrame + i * 2.6, c.startFrame + i * 2.6 + 8],
                  [0, 1],
                  clamp,
                );
                return (
                  <span
                    key={i}
                    style={{
                      display: 'inline-block',
                      fontFamily: TYPE.display,
                      fontWeight: role === 'plain' ? 700 : 800,
                      fontSize: role === 'punch' ? size + 14 : size,
                      letterSpacing: role === 'punch' ? -1.5 : -1,
                      lineHeight: 1.02,
                      color,
                      opacity: p,
                      transform: `translateY(${interpolate(p, [0, 1], [22, 0])}px) scale(${interpolate(p, [0, 1], [0.94, 1])})`,
                      textShadow: '0 12px 34px rgba(0,0,0,0.45)',
                    }}
                  >
                    {w}
                  </span>
                );
              })}
            </div>
            {role === 'punch' ? (
              <div
                style={{
                  position: 'absolute',
                  left: W / 2 - 70,
                  top: headlineTop + size + 46,
                  height: 4,
                  width: 140 * interpolate(frame, [c.startFrame + 2, c.startFrame + 16], [0, 1], clamp),
                  background: PAL.gold,
                  borderRadius: 2,
                  opacity: out * 0.9,
                }}
              />
            ) : null}
          </div>
        );
      })}

      {/* ------------------------------------------------------------- host */}
      {HOST_WINDOWS.map((w, wi) => {
        if (frame < w.from - 16 || frame > w.to + 16) return null;
        const enter = interpolate(frame, [w.from - 2, w.from + 16], [0, 1], clamp);
        const exit = interpolate(frame, [w.to - 10, w.to + 8], [0, 1], clamp);
        const height = w.mode === 'full' ? LAYOUT.host.hFull : LAYOUT.host.hPresent;
        const width = height * HOST_ASPECT;
        const top = LAYOUT.host.bottom - height;
        const left = LAYOUT.host.centerX - width / 2;
        return (
          <div key={wi}>
            {/* spotlight behind him */}
            <div
              style={{
                position: 'absolute',
                left: left - 90,
                top: top + height * 0.02,
                width: width + 180,
                height: height * 0.72,
                background:
                  'radial-gradient(46% 46% at 50% 52%, rgba(232,179,58,0.20) 0%, rgba(232,179,58,0) 70%), radial-gradient(60% 40% at 50% 26%, rgba(126,176,226,0.16) 0%, rgba(126,176,226,0) 72%)',
                opacity: enter * (1 - exit),
              }}
            />
            <div
              style={{
                position: 'absolute',
                left,
                top,
                width,
                height,
                opacity: enter * (1 - exit),
                transform: `translateY(${interpolate(enter, [0, 1], [120, 0]) + interpolate(exit, [0, 1], [0, 80])}px) scale(${interpolate(enter, [0, 1], [0.95, 1])})`,
                filter: 'drop-shadow(0 -10px 40px rgba(0,0,0,0.45))',
              }}
            >
              <Host
                frame={frame}
                mouth={mouth}
                gesture={w.gesture}
                brow={w.brow ?? 0}
                width={width}
                height={height}
              />
            </div>
          </div>
        );
      })}

      {/* --------------------------------------- chapter rail + stat strip */}
      {(() => {
        const railFade = 1 - Math.max(fullP, presentP);
        if (railFade <= 0.02) return null;
        const active = REV3_CLIPS.reduce(
          (acc, c, i) => (frame >= c.startFrame - 12 ? i : acc),
          0,
        );
        const stats = [
          {v: '$6.36B', l: 'STOLEN', clip: 'L1'},
          {v: '20 MIN', l: 'WINDOW', clip: 'L1'},
          {v: '10', l: 'CHAINS', clip: 'B2a'},
          {v: '$2.4B', l: 'UNREACHABLE', clip: 'B2c'},
        ];
        const statClip = REV3_CLIPS[active]?.id;
        return (
          <div style={{opacity: railFade}}>
            {/* chapters */}
            <div
              style={{
                position: 'absolute',
                left: LAYOUT.cardX,
                top: 1324,
                width: LAYOUT.cardW,
                display: 'flex',
                justifyContent: 'space-between',
              }}
            >
              {RAIL.map((label, i) => {
                const on = i <= active;
                return (
                  <div key={label} style={{width: 92, textAlign: 'center'}}>
                    <div
                      style={{
                        fontFamily: TYPE.mono,
                        fontSize: 17,
                        letterSpacing: 2,
                        color: i === active ? PAL.gold : PAL.slate,
                        opacity: i === active ? 1 : on ? 0.7 : 0.38,
                      }}
                    >
                      {label}
                    </div>
                    <div
                      style={{
                        marginTop: 10,
                        height: 3,
                        borderRadius: 2,
                        background: i === active ? PAL.gold : 'rgba(244,237,226,0.18)',
                        width: i === active ? 92 : 92 * (on ? 0.7 : 0.38),
                        transition: 'none',
                      }}
                    />
                  </div>
                );
              })}
            </div>

            {/* key numbers */}
            <div
              style={{
                position: 'absolute',
                left: LAYOUT.cardX,
                top: 1462,
                width: LAYOUT.cardW,
                display: 'flex',
                justifyContent: 'space-between',
                borderTop: `1px solid ${PAL.navyLine}`,
                borderBottom: `1px solid ${PAL.navyLine}`,
                padding: '22px 0',
              }}
            >
              {stats.map((s) => {
                const on = s.clip === statClip;
                return (
                  <div key={s.l} style={{textAlign: 'center', flex: 1}}>
                    <div
                      style={{
                        fontFamily: TYPE.display,
                        fontWeight: 800,
                        fontSize: 46,
                        letterSpacing: -1,
                        color: on ? PAL.gold : PAL.cream,
                        opacity: on ? 1 : 0.82,
                      }}
                    >
                      {s.v}
                    </div>
                    <div
                      style={{
                        fontFamily: TYPE.mono,
                        fontSize: 17,
                        letterSpacing: 3,
                        color: PAL.slate,
                        marginTop: 6,
                      }}
                    >
                      {s.l}
                    </div>
                  </div>
                );
              })}
            </div>

            {/* sources */}
            <div
              style={{
                position: 'absolute',
                left: LAYOUT.cardX,
                top: 1616,
                width: LAYOUT.cardW,
                textAlign: 'center',
                fontFamily: TYPE.mono,
                fontSize: 18,
                letterSpacing: 3,
                color: PAL.slateDim,
              }}
            >
              SOURCES: TRM LABS · CHAINALYSIS · AP · CNN · NBC · REUTERS · AL JAZEERA
            </div>
          </div>
        );
      })()}

      {/* --------------------------------------------------------- end card */}
      {frame >= 2004 ? (
        <div
          style={{
            position: 'absolute',
            left: LAYOUT.cardX,
            top: headlineTop - 78,
            width: LAYOUT.cardW,
            textAlign: 'center',
            opacity: interpolate(frame, [2004, 2030], [0, 1], clamp),
          }}
        >
          <div
            style={{
              fontFamily: TYPE.mono,
              fontSize: 22,
              letterSpacing: 6,
              color: PAL.slateDim,
              marginBottom: 10,
            }}
          >
            SHORTS-2026-024 · BINANCE · 29 OCT 2026
          </div>
          <div
            style={{
              fontFamily: TYPE.mono,
              fontSize: 20,
              letterSpacing: 3,
              color: PAL.gold,
            }}
          >
            SOURCES: TRM LABS · CHAINALYSIS · AP · CNN · NBC · REUTERS
          </div>
        </div>
      ) : null}

      {/* ----------------------------------------------------------- chrome */}
      <div
        style={{
          position: 'absolute',
          left: LAYOUT.cardX,
          right: LAYOUT.cardX,
          top: CHROME.kickerY,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          fontFamily: TYPE.mono,
          fontSize: 22,
          letterSpacing: 5,
          color: PAL.slate,
        }}
      >
        <span>CASE FILE 024 · CRYPTO HEIST</span>
        <span style={{color: PAL.slateDim}}>20 MIN · $6.3B</span>
      </div>

      {/* progress */}
      <div
        style={{
          position: 'absolute',
          left: LAYOUT.cardX,
          top: CHROME.ruleY,
          width: LAYOUT.cardW,
          height: 5,
          borderRadius: 3,
          background: 'rgba(244, 237, 226, 0.14)',
          overflow: 'hidden',
        }}
      >
        <div
          style={{
            width: (frame / Math.max(1, durationInFrames - 1)) * LAYOUT.cardW,
            height: '100%',
            background: PAL.gold,
            borderRadius: 3,
          }}
        />
      </div>

      {/* -------------------------------------------------------- grade pass */}
      <AbsoluteFill
        style={{
          background:
            'radial-gradient(74% 58% at 50% 42%, rgba(0,0,0,0) 40%, rgba(0,0,0,0.42) 100%)',
          pointerEvents: 'none',
        }}
      />
      <AbsoluteFill
        style={{
          backgroundImage: GRAIN,
          backgroundSize: '180px 180px',
          opacity: 0.055,
          mixBlendMode: 'overlay',
          pointerEvents: 'none',
        }}
      />
      {/* faint warm bloom, ties the illustrated card to the type */}
      <AbsoluteFill
        style={{
          background:
            'linear-gradient(180deg, rgba(232,179,58,0.05) 0%, rgba(232,179,58,0) 26%)',
          pointerEvents: 'none',
        }}
      />
      <div style={{position: 'absolute', left: 0, top: 0, width: W, height: H}} />
    </AbsoluteFill>
  );
};
