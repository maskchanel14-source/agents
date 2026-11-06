/**
 * Photo.tsx — the cinematic move applied to a still.
 *
 * Every shot in this spot is a photograph with camera motion, so the whole
 * film reads as a shot rather than a slide. Moves are slow, eased and
 * sub-pixel-free at 30fps: Ken Burns push, lateral drift, and a rack-focus
 * style blur ramp. Pressure-tested against the 9:16 crop.
 */
import React from 'react';
import {useCurrentFrame, useVideoConfig, Img, staticFile, interpolate} from 'remotion';
import {W, H, easeInOut, clamp} from './brand';

export type Move = 'push' | 'pull' | 'driftL' | 'driftR' | 'driftUp' | 'tilt';

export const Photo: React.FC<{
  src: string;
  /** 0..1 progress through the shot — drive it from the parent. */
  p: number;
  move?: Move;
  /** extra zoom on top of the move, e.g. 1.06 */
  zoom?: number;
  /** px offset to bias the crop (negative = up) */
  offsetY?: number;
  blur?: number;
  scaleFrom?: number;
  scaleTo?: number;
  children?: React.ReactNode;
}> = ({src, p, move = 'push', zoom = 1, offsetY = 0, blur = 0, scaleFrom, scaleTo, children}) => {
  const e = easeInOut(p);

  const presets: Record<Move, {s0: number; s1: number; x: number; y: number}> = {
    push: {s0: 1.04, s1: 1.16, x: 0, y: 0},
    pull: {s0: 1.16, s1: 1.04, x: 0, y: 0},
    driftL: {s0: 1.12, s1: 1.12, x: 26, y: 0},
    driftR: {s0: 1.12, s1: 1.12, x: -26, y: 0},
    driftUp: {s0: 1.12, s1: 1.12, x: 0, y: 34},
    tilt: {s0: 1.06, s1: 1.13, x: -14, y: 14},
  };
  const pr = presets[move];
  const s0 = scaleFrom ?? pr.s0;
  const s1 = scaleTo ?? pr.s1;
  const scale = (s0 + (s1 - s0) * e) * zoom;
  const dx = pr.x * e;
  const dy = pr.y * e;

  return (
    <div style={{position: 'absolute', inset: 0, overflow: 'hidden', background: '#000'}}>
      <Img
        src={staticFile(src)}
        style={{
          position: 'absolute',
          width: '100%',
          height: '100%',
          objectFit: 'cover',
          transform: `translate3d(${dx}px, ${dy + offsetY}px, 0) scale(${scale})`,
          filter: blur > 0.01 ? `blur(${blur}px)` : undefined,
          willChange: 'transform',
        }}
      />
      {children}
    </div>
  );
};

/**
 * Grain + vignette + a very subtle chromatic edge. This is the cheap trick that
 * makes procedural stills read as "graded footage" instead of "a JPEG".
 */
export const Grade: React.FC<{p: number; strength?: number; warm?: number}> = ({
  p,
  strength = 1,
  warm = 0.06,
}) => {
  const frame = useCurrentFrame();
  return (
    <>
      {/* vignette */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background:
            'radial-gradient(ellipse 76% 62% at 50% 46%, rgba(0,0,0,0) 30%, rgba(0,0,0,0.55) 78%, rgba(0,0,0,0.86) 100%)',
        }}
      />
      {/* warm lift in the shadows */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background: `linear-gradient(200deg, rgba(232,135,30,${warm}) 0%, rgba(0,0,0,0) 45%, rgba(10,6,4,${0.18 * strength}) 100%)`,
          mixBlendMode: 'soft-light',
        }}
      />
      {/* fine scan grain, animated per frame */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          opacity: 0.11 * strength,
          mixBlendMode: 'overlay',
          backgroundImage: `url("data:image/svg+xml;utf8,${encodeURIComponent(
            `<svg xmlns='http://www.w3.org/2000/svg' width='140' height='140'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='3' seed='${Math.floor(
              frame / 2
            ) % 9}'/></filter><rect width='140' height='140' filter='url(%23n)' opacity='0.6'/></svg>`
          )}")`,
          backgroundSize: '140px 140px',
        }}
      />
    </>
  );
};

/** Slow horizontal light sweep — used on product hero beats. */
export const LightSweep: React.FC<{p: number; delay?: number; duration?: number; opacity?: number}> = ({
  p,
  delay = 0.1,
  duration = 0.5,
  opacity = 0.5,
}) => {
  const t = clamp((p - delay) / duration);
  const x = interpolate(t, [0, 1], [-40, 140]);
  if (t <= 0 || t >= 1) return null;
  return (
    <div
      style={{
        position: 'absolute',
        inset: 0,
        background: `linear-gradient(105deg, rgba(255,255,255,0) ${x - 18}%, rgba(255,240,214,${opacity}) ${x}%, rgba(255,255,255,0) ${x + 18}%)`,
        mixBlendMode: 'screen',
        pointerEvents: 'none',
      }}
    />
  );
};

/** 1px hairline rules + corner ticks: the "corporate film" furniture. */
export const Frame: React.FC<{opacity?: number; inset?: number; accent?: string}> = ({
  opacity = 0.5,
  inset = 64,
  accent = 'rgba(246,237,226,0.35)',
}) => (
  <>
    <div style={{position: 'absolute', top: inset, left: inset, right: inset, height: 1, background: accent, opacity}} />
    <div style={{position: 'absolute', bottom: inset, left: inset, right: inset, height: 1, background: accent, opacity}} />
    {[
      {top: inset - 10, left: inset - 10},
      {top: inset - 10, right: inset - 10},
      {bottom: inset - 10, left: inset - 10},
      {bottom: inset - 10, right: inset - 10},
    ].map((pos, i) => (
      <div
        key={i}
        style={{
          position: 'absolute',
          ...pos,
          width: 20,
          height: 20,
          borderTop: i < 2 ? `1.5px solid rgba(232,135,30,0.85)` : undefined,
          borderBottom: i >= 2 ? `1.5px solid rgba(232,135,30,0.85)` : undefined,
          borderLeft: i % 2 === 0 ? `1.5px solid rgba(232,135,30,0.85)` : undefined,
          borderRight: i % 2 === 1 ? `1.5px solid rgba(232,135,30,0.85)` : undefined,
          opacity: 0.8,
        }}
      />
    ))}
  </>
);
