import React from 'react';
import {interpolate, spring, staticFile, useVideoConfig} from 'remotion';
import {PAL, TYPE} from './theme2d';

/**
 * Scene schedule and the hand-drawn data overlays for revision 3.
 *
 * Scene boundaries come straight from audio/timing3.json (exported to
 * src/data/shorts024Timeline.ts). Neighbouring scenes overlap by 18 frames so
 * the cut is a crossfade, not a hard switch.
 */

export type SceneDef = {
  key: string;
  from: number;
  to: number;
  img?: string;
  vector?: 'dossier' | 'chart' | 'vault';
  ken: 'in' | 'out' | 'up' | 'left' | 'right';
};

export const SCENES: SceneDef[] = [
  {key: 'vault', from: 0, to: 178, img: 's01_vault.png', ken: 'in'},
  {key: 'exchange', from: 160, to: 336, img: 's02_exchange.png', ken: 'right'},
  {key: 'hotwallet', from: 318, to: 497, img: 's03_hotwallet.png', ken: 'in'},
  {key: 'clock', from: 479, to: 725, img: 's04_clock.png', ken: 'up'},
  {key: 'bitcoin', from: 707, to: 875, img: 's05_bitcoin.png', ken: 'out'},
  {key: 'frozen', from: 857, to: 1052, img: 's06_frozen.png', ken: 'left'},
  {key: 'vault-intact', from: 1034, to: 1195, vector: 'vault', ken: 'in'},
  {key: 'interview', from: 1177, to: 1378, img: 's08_interview.png', ken: 'right'},
  {key: 'laptop', from: 1360, to: 1548, img: 's09_laptop_servers.png', ken: 'in'},
  {key: 'reopen', from: 1530, to: 1750, img: 's10_reopen.png', ken: 'up'},
  {key: 'dossier', from: 1732, to: 1868, vector: 'dossier', ken: 'in'},
  {key: 'chart', from: 1850, to: 2185, vector: 'chart', ken: 'in'},
];

export const sceneAt = (frame: number): SceneDef =>
  SCENES.find((s) => frame >= s.from && frame < s.to) ?? SCENES[SCENES.length - 1];

/* ------------------------------------------------------------------ card */

const kenTransform = (scene: SceneDef, p: number): string => {
  const e = interpolate(p, [0, 1], [0, 1], {extrapolateRight: 'clamp'});
  switch (scene.ken) {
    case 'out':
      return `scale(${interpolate(e, [0, 1], [1.14, 1.02])})`;
    case 'up':
      return `scale(${interpolate(e, [0, 1], [1.04, 1.14])}) translateY(${interpolate(e, [0, 1], [2.2, -2.2])}%)`;
    case 'left':
      return `scale(${interpolate(e, [0, 1], [1.04, 1.14])}) translateX(${interpolate(e, [0, 1], [1.8, -1.8])}%)`;
    case 'right':
      return `scale(${interpolate(e, [0, 1], [1.04, 1.14])}) translateX(${interpolate(e, [0, 1], [-1.8, 1.8])}%)`;
    default:
      return `scale(${interpolate(e, [0, 1], [1.03, 1.13])})`;
  }
};

/** One scene filling the illustration card, with a slow push and a crossfade. */
export const SceneLayer: React.FC<{
  scene: SceneDef;
  frame: number;
  /** Card height in px — the vector scenes size themselves to it. */
  h: number;
}> = ({scene, frame, h}) => {
  const p = interpolate(frame, [scene.from, scene.to], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const fadeIn = interpolate(frame, [scene.from, scene.from + 18], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const fadeOut = interpolate(frame, [scene.to - 18, scene.to], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <div
      style={{
        position: 'absolute',
        inset: 0,
        opacity: Math.min(fadeIn, fadeOut),
        transform: kenTransform(scene, p),
        transformOrigin: 'center center',
        willChange: 'transform',
      }}
    >
      {scene.img ? (
        <img
          src={staticFile(`shorts024/scenes/${scene.img}`)}
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            objectPosition: 'center center',
            display: 'block',
            filter: 'saturate(1.06) contrast(1.05) brightness(1.10)',
          }}
        />
      ) : scene.vector === 'dossier' ? (
        <DossierScene p={p} h={h} />
      ) : scene.vector === 'vault' ? (
        <VaultScene frame={frame - scene.from} h={h} />
      ) : (
        <ChartScene frame={frame - scene.from} h={h} />
      )}
    </div>
  );
};

/* ------------------------------------------------------- vector scene: dossier */

const DossierScene: React.FC<{p: number; h: number}> = ({p, h}) => {
  const slide = interpolate(p, [0, 0.35], [40, 0], {extrapolateRight: 'clamp'});
  const rot = interpolate(p, [0, 0.5], [-6, -3], {extrapolateRight: 'clamp'});
  const k = Math.min(1, h / 660);
  return (
    <div
      style={{
        width: '100%',
        height: '100%',
        transform: `scale(${interpolate(k, [0, 1], [0.8, 1])})`,
        background: `radial-gradient(120% 90% at 22% 12%, ${PAL.navySoft} 0%, ${PAL.ink} 62%)`,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      {/* abstract landmass behind the file */}
      <svg
        viewBox="0 0 400 240"
        style={{position: 'absolute', width: 460, opacity: 0.5, top: 60}}
      >
        <path
          d="M 40 200 C 60 150 96 138 120 150 C 150 118 196 106 226 128 C 258 100 300 108 318 140 C 352 138 372 168 358 202 Z"
          fill="#1E3355"
        />
        <circle cx={120} cy={150} r={4} fill={PAL.terracotta} />
        <circle cx={226} cy={128} r={4} fill={PAL.terracotta} />
      </svg>

      {/* manila folder */}
      <div
        style={{
          position: 'relative',
          width: 560,
          height: 380,
          background: 'linear-gradient(160deg, #E7D7B4 0%, #D7C29A 100%)',
          borderRadius: 10,
          transform: `translateY(${slide}px) rotate(${rot}deg)`,
          boxShadow: '0 40px 80px rgba(0,0,0,0.45)',
          padding: '26px 30px',
          fontFamily: TYPE.mono,
          color: '#3A2C17',
        }}
      >
        <div
          style={{
            width: 250,
            height: 34,
            background: '#C9B183',
            borderRadius: '8px 8px 0 0',
            marginTop: -46,
            marginLeft: -6,
          }}
        />
        <div style={{fontSize: 20, letterSpacing: 5, opacity: 0.65}}>CASE FILE / ATTRIBUTION</div>
        <div style={{height: 2, background: 'rgba(58,44,23,0.28)', margin: '16px 0 18px'}} />
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            style={{
              height: 10,
              width: i === 2 ? '52%' : '84%',
              background: 'rgba(58,44,23,0.22)',
              borderRadius: 5,
              marginBottom: 14,
            }}
          />
        ))}
        <div style={{fontSize: 22, letterSpacing: 3, marginTop: 8}}>TRADERTRAITOR · DPRK</div>
        {/* red stamp */}
        <div
          style={{
            position: 'absolute',
            right: 34,
            bottom: 26,
            width: 132,
            height: 132,
            border: `5px solid ${PAL.terracotta}`,
            borderRadius: '50%',
            transform: 'rotate(-14deg)',
            opacity: 0.86,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: PAL.terracotta,
            fontSize: 19,
            letterSpacing: 2,
            textAlign: 'center',
            lineHeight: 1.1,
          }}
        >
          STATE
          <br />
          ACTOR
        </div>
      </div>
    </div>
  );
};

/* --------------------------------------------------------- vector scene: vault */

/**
 * The twist beat: the vault was never broken. A closed, bolted door with no
 * light escaping — the same object as the hook, sealed instead of gaping.
 */
const VaultScene: React.FC<{frame: number; h: number}> = ({frame, h}) => {
  const {fps} = useVideoConfig();
  // the question mark snaps in, then the shot just sits there: nothing happens
  // to this door, which is exactly the point of the beat.
  const pop = spring({
    fps,
    frame: frame - 6,
    config: {damping: 13, stiffness: 110, mass: 0.7},
  });
  const k = Math.min(1, h / 660);
  return (
    <div
      style={{
        width: '100%',
        height: '100%',
        transform: `scale(${interpolate(k, [0, 1], [0.82, 1])})`,
        background: `radial-gradient(115% 85% at 30% 8%, ${PAL.navySoft} 0%, ${PAL.ink} 66%)`,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      <svg viewBox="0 0 520 520" style={{width: 520, height: 520}}>
        <defs>
          <radialGradient id="vsDoor" cx="34%" cy="26%" r="86%">
            <stop offset="0%" stopColor="#4B6698" />
            <stop offset="58%" stopColor="#2C4370" />
            <stop offset="100%" stopColor="#1A2A47" />
          </radialGradient>
          <linearGradient id="vsWall" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#1E3355" />
            <stop offset="100%" stopColor="#131E33" />
          </linearGradient>
        </defs>

        {/* wall + floor slab */}
        <rect x={0} y={0} width={520} height={520} fill="url(#vsWall)" />
        <rect x={0} y={462} width={520} height={58} fill="#0E1829" />
        <ellipse cx={260} cy={462} rx={168} ry={18} fill="rgba(0,0,0,0.34)" />

        {/* the door — shut, so the seam under it is a dark line, not a glow */}
        <circle cx={260} cy={278} r={164} fill="#16263C" opacity={0.55} />
        <circle cx={260} cy={278} r={152} fill="#22375A" stroke="#101C30" strokeWidth={9} />
        <circle cx={260} cy={278} r={132} fill="url(#vsDoor)" stroke="#54739E" strokeWidth={2.5} />
        {Array.from({length: 16}).map((_, i) => {
          const a = (i / 16) * Math.PI * 2;
          return (
            <circle
              key={i}
              cx={260 + Math.cos(a) * 117}
              cy={278 + Math.sin(a) * 117}
              r={6}
              fill="#93AAC7"
            />
          );
        })}
        {/* spokes */}
        <g stroke="#3D5A8C" strokeWidth={20} strokeLinecap="round" opacity={0.85}>
          <path d="M 260 278 L 260 168" />
          <path d="M 260 278 L 260 388" />
          <path d="M 260 278 L 150 278" />
          <path d="M 260 278 L 370 278" />
        </g>
        {/* dial */}
        <circle cx={260} cy={278} r={56} fill="#1B2C48" stroke={PAL.gold} strokeWidth={6} />
        <circle cx={260} cy={278} r={36} fill="#22375A" stroke="#4A6A9C" strokeWidth={2} />
        <circle cx={260} cy={278} r={12} fill={PAL.gold} />
        <path d="M 260 278 L 260 232" stroke={PAL.gold} strokeWidth={5} strokeLinecap="round" />
        {/* hinge */}
        <rect x={392} y={236} width={24} height={86} rx={12} fill="#16263C" />
        {/* rim light top-left, so the door reads as solid metal */}
        <path
          d="M 148 196 A 152 152 0 0 1 292 130"
          stroke="rgba(158, 196, 232, 0.30)"
          strokeWidth={7}
          fill="none"
        />

        {/* the question — and then nothing: this door never opens */}
        <text
          x={260}
          y={104}
          textAnchor="middle"
          fontFamily={TYPE.display}
          fontSize={Math.round(126 * (0.62 + 0.38 * pop))}
          fill={PAL.gold}
          opacity={pop * 0.92}
        >
          ?
        </text>
      </svg>
    </div>
  );
};

/* --------------------------------------------------------- vector scene: chart */

const ChartScene: React.FC<{frame: number; h: number}> = ({frame, h}) => {
  const {fps} = useVideoConfig();
  // the bars start growing as soon as the scene appears — the caption is already
  // talking about the record by then
  const a = spring({frame: frame - 8, fps, config: {damping: 16, stiffness: 90, mass: 0.9}});
  const b = spring({frame: frame - 22, fps, config: {damping: 17, stiffness: 74, mass: 1.0}});

  const base = 86; //  room under each bar for its caption
  const big = Math.min(h * 0.58, 470);
  const small = big / 4.24; //  6.36 / 1.5
  const barW = 128;
  const leftA = 480 - (barW * 2 + 62) / 2;
  const leftB = leftA + barW + 62;

  const bar = (
    v: string,
    height: number,
    s: number,
    fill: string,
    color: string,
    fs: number,
    caption: string,
    captionColor: string,
    left: number,
    glow?: string,
  ) => (
    <div key={v}>
      <div
        style={{
          position: 'absolute',
          left,
          bottom: base,
          width: barW,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'flex-end',
          zIndex: 1,
        }}
      >
        <div
          style={{
            fontFamily: TYPE.display,
            fontWeight: 800,
            fontSize: fs,
            color,
            marginBottom: 10,
            letterSpacing: -1,
          }}
        >
          {v}
        </div>
        <div
          style={{
            width: barW,
            height: height * s,
            background: fill,
            borderRadius: '10px 10px 0 0',
            boxShadow: glow,
          }}
        />
      </div>
      <div
        style={{
          position: 'absolute',
          left,
          bottom: 30,
          width: barW,
          textAlign: 'center',
          fontFamily: TYPE.mono,
          fontSize: 19,
          letterSpacing: 2,
          color: captionColor,
          zIndex: 1,
        }}
      >
        {caption}
      </div>
    </div>
  );

  return (
    <div
      style={{
        position: 'relative',
        width: '100%',
        height: '100%',
        background: `linear-gradient(180deg, ${PAL.navySoft} 0%, ${PAL.ink} 72%)`,
        overflow: 'hidden',
      }}
    >
      {/* light shaft */}
      <div
        style={{
          position: 'absolute',
          top: -280,
          left: 90,
          width: 420,
          height: 900,
          background: 'linear-gradient(180deg, rgba(232,179,58,0.16), rgba(232,179,58,0))',
          transform: 'rotate(18deg)',
        }}
      />
      {/* floor line */}
      <div
        style={{
          position: 'absolute',
          left: 0,
          right: 0,
          bottom: base - 2,
          height: 2,
          background: 'rgba(244,237,226,0.16)',
        }}
      />
      {bar('$1.5B', small, a, 'linear-gradient(180deg, #6B86A6 0%, #35506E 100%)',
        PAL.slate, 34, 'BYBIT · 2025', PAL.slateDim, leftA)}
      {bar('$6.36B', big, b, `linear-gradient(180deg, ${PAL.gold} 0%, #A9762A 100%)`,
        PAL.gold, 52, 'BINANCE · 2026', PAL.gold, leftB, '0 0 70px rgba(232,179,58,0.28)')}
      {/* 4x badge */}
      <div
        style={{
          position: 'absolute',
          right: 54,
          top: h * 0.16,
          opacity: b,
          transform: `scale(${interpolate(b, [0, 1], [0.7, 1])})`,
          border: `3px solid ${PAL.gold}`,
          color: PAL.gold,
          fontFamily: TYPE.display,
          fontWeight: 800,
          fontSize: 46,
          padding: '10px 22px',
          borderRadius: 12,
          background: 'rgba(232,179,58,0.10)',
          zIndex: 2,
        }}
      >
        4×
      </div>
    </div>
  );
};

/* ------------------------------------------------------------- overlays */

const Chip: React.FC<{
  label: string;
  delay: number;
  frame: number;
  accent?: string;
}> = ({label, delay, frame, accent = PAL.gold}) => {
  const {fps} = useVideoConfig();
  const s = spring({frame: frame - delay, fps, config: {damping: 14, stiffness: 150, mass: 0.6}});
  return (
    <div
      style={{
        fontFamily: TYPE.mono,
        fontSize: 24,
        letterSpacing: 3,
        color: accent,
        border: `1.5px solid ${accent}55`,
        background: 'rgba(11, 18, 32, 0.72)',
        padding: '8px 14px',
        borderRadius: 999,
        opacity: s,
        transform: `translateY(${interpolate(s, [0, 1], [14, 0])}px) scale(${interpolate(s, [0, 1], [0.9, 1])})`,
        backdropFilter: 'blur(6px)',
      }}
    >
      {label}
    </div>
  );
};

/** Data overlays drawn on top of the illustration, one set per VO line. */
export const Overlay: React.FC<{id: string; frame: number}> = ({id, frame}) => {
  const {fps} = useVideoConfig();

  if (id === 'B2a') {
    const names = ['ETH', 'BTC', 'TRON', 'SOL',
      'CHAIN', 'CHAIN', 'CHAIN', 'CHAIN', 'CHAIN', 'CHAIN'];
    return (
      <>
        <div style={{position: 'absolute', left: 28, top: 24}}>
          <Chip label="29 OCT · 20:05 UTC" delay={0} frame={frame} accent={PAL.cream} />
        </div>
        <div
          style={{
            position: 'absolute',
            left: 28,
            right: 28,
            bottom: 24,
            display: 'flex',
            flexWrap: 'wrap',
            gap: 10,
            justifyContent: 'flex-start',
          }}
        >
          {names.map((n, i) => (
            <Chip key={i} label={n} delay={104 + i * 7} frame={frame} />
          ))}
        </div>
      </>
    );
  }

  if (id === 'B2b') {
    const count = spring({frame: frame - 4, fps, config: {damping: 20, stiffness: 60, mass: 1}});
    const value = Math.round(interpolate(count, [0, 1], [0, 18270]));
    return (
      <>
        <div
          style={{
            position: 'absolute',
            left: 34,
            top: 26,
            fontFamily: TYPE.display,
            fontWeight: 800,
            fontSize: 92,
            color: PAL.gold,
            letterSpacing: -2,
            textShadow: '0 8px 30px rgba(0,0,0,0.6)',
          }}
        >
          {value.toLocaleString('en-US')}
          <span style={{fontSize: 34, color: PAL.cream, marginLeft: 12, letterSpacing: 2}}>BTC</span>
        </div>
        <div
          style={{
            position: 'absolute',
            left: 34,
            bottom: 26,
            display: 'flex',
            gap: 10,
          }}
        >
          {['1,000', '1,000', '100', '100'].map((n, i) => (
            <Chip key={i} label={n} delay={70 + i * 8} frame={frame} accent={PAL.terracotta} />
          ))}
        </div>
      </>
    );
  }

  if (id === 'B2c') {
    const w = spring({frame: frame - 20, fps, config: {damping: 18, stiffness: 90, mass: 0.9}});
    const frozenW = 540 * 0.556 * w;
    const goneW = 540 * 0.444 * w;
    return (
      <div
        style={{
          position: 'absolute',
          left: 34,
          right: 34,
          bottom: 30,
          display: 'flex',
          height: 64,
          borderRadius: 10,
          overflow: 'hidden',
          boxShadow: '0 12px 40px rgba(0,0,0,0.5)',
        }}
      >
        <div
          style={{
            width: frozenW,
            background: `linear-gradient(180deg, ${PAL.ice}, #4E93B8)`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontFamily: TYPE.mono,
            fontSize: 24,
            letterSpacing: 3,
            color: '#0B2740',
          }}
        >
          $3.0B FROZEN
        </div>
        <div
          style={{
            width: goneW,
            background: `linear-gradient(180deg, ${PAL.terracotta}, #8E3A1B)`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontFamily: TYPE.mono,
            fontSize: 24,
            letterSpacing: 3,
            color: PAL.cream,
          }}
        >
          $2.4B GONE
        </div>
      </div>
    );
  }

  if (id === 'B3c') {
    const grow = spring({frame: frame - 60, fps, config: {damping: 20, stiffness: 70, mass: 1}});
    const filled = Math.round(interpolate(grow, [0, 1], [0, 50]));
    return (
      <div style={{position: 'absolute', left: 34, right: 34, bottom: 30}}>
        <div
          style={{
            fontFamily: TYPE.mono,
            fontSize: 24,
            letterSpacing: 4,
            color: PAL.terracotta,
            marginBottom: 10,
          }}
        >
          1 LAPTOP → {filled} SIGNED AUTHORISATIONS
        </div>
        <div style={{display: 'flex', gap: 5, flexWrap: 'wrap'}}>
          {Array.from({length: 50}).map((_, i) => (
            <div
              key={i}
              style={{
                width: 12,
                height: 18,
                borderRadius: 3,
                background: i < filled ? PAL.terracotta : 'rgba(244,237,226,0.18)',
              }}
            />
          ))}
        </div>
      </div>
    );
  }

  if (id === 'P1') {
    return (
      <div style={{position: 'absolute', left: 28, top: 24, display: 'flex', gap: 10}}>
        <Chip label="1 NOV 2026" delay={92} frame={frame} accent={PAL.teal} />
        <Chip label="WITHDRAWALS OPEN" delay={102} frame={frame} accent={PAL.teal} />
      </div>
    );
  }

  return null;
};
