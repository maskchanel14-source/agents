/**
 * scenes.tsx — the reusable scene library. Each scene is a pure function of
 * (progress, props) and takes the full 1080x1920 frame.
 *
 * Rule from the style bible: something meaningful must change every 1.5-3 s.
 * Every scene therefore carries its own internal motion — never a static card.
 */
import React from 'react';
import {interpolate, spring, useVideoConfig} from 'remotion';
import {theme, W, H} from '../brand/theme';
import {
  Cam,
  Seg,
  Soft3D,
  drawSegs,
  helixSegs,
  icosaSegs,
  ringPoints,
  sphereSegs,
  tubeSegs,
  v3,
  V3,
} from '../fx/Soft3D';

export type SceneProps = {
  p: number; // 0..1 progress through the shot
  frame: number;
  dur: number; // shot length in frames
};

const clamp = (x: number, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const ease = (x: number) => x * x * (3 - 2 * x);

// ------------------------------------------------------------------ chrome
/** Soft instrument glow + ring backdrop placed under every 3D scene. */
const SceneBackdrop: React.FC<{p: number; rings?: boolean}> = ({p, rings = true}) => (
  <>
    <div
      style={{
        position: 'absolute',
        inset: 0,
        background: `radial-gradient(ellipse 70% 46% at 50% 46%, ${theme.accentSoft} 0%, rgba(5,7,10,0) 68%)`,
      }}
    />
    {rings ? (
      <svg width={W} height={H} style={{position: 'absolute', inset: 0}}>
        {Array.from({length: 7}, (_, i) => {
          const r = 120 + ((i * 96 + p * 150) % 620);
          return (
            <circle
              key={i}
              cx={W / 2}
              cy={H * 0.47}
              r={r}
              fill="none"
              stroke={theme.accent}
              strokeWidth={1}
              opacity={0.10 * (1 - (r - 120) / 620)}
            />
          );
        })}
      </svg>
    ) : null}
  </>
);
export const Vignette: React.FC = () => (
  <>
    <div
      style={{
        position: 'absolute',
        inset: 0,
        background:
          'radial-gradient(ellipse 78% 62% at 50% 46%, rgba(0,0,0,0) 42%, rgba(0,0,0,0.72) 100%)',
      }}
    />
    <div
      style={{
        position: 'absolute',
        inset: 0,
        background: 'linear-gradient(180deg, rgba(0,0,0,0.65) 0%, rgba(0,0,0,0) 26%)',
      }}
    />
  </>
);

/** Faint drifting stars so the background is never dead flat. */
const Starfield: React.FC<{p: number; n?: number; speed?: number}> = ({p, n = 90, speed = 1}) => {
  const stars = React.useMemo(() => {
    let s = 12345;
    const rnd = () => {
      s = (s * 9301 + 49297) % 233280;
      return s / 233280;
    };
    return Array.from({length: n}, () => ({
      x: rnd() * W,
      y: rnd() * H,
      r: 0.6 + rnd() * 1.9,
      a: 0.15 + rnd() * 0.55,
      k: 0.4 + rnd() * 0.9,
    }));
  }, [n]);

  return (
    <svg width={W} height={H} style={{position: 'absolute', inset: 0}}>
      {stars.map((s, i) => {
        const y = ((s.y - p * 260 * speed * s.k) % H + H) % H;
        const tw = 0.65 + 0.35 * Math.sin((p * 18 + i) * 1.7);
        return <circle key={i} cx={s.x} cy={y} r={s.r} fill="#BFE9F5" opacity={s.a * tw} />;
      })}
    </svg>
  );
};

/** Top-left telemetry rail — the channel's signature "instrument" frame. */
export const Ticker: React.FC<{label: string; right?: string}> = ({label, right}) => (
  <div
    style={{
      position: 'absolute',
      top: 132,
      left: 64,
      right: 64,
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      fontFamily: theme.type.mono,
      fontSize: 22,
      letterSpacing: 4,
      color: theme.inkDim,
    }}
  >
    <span style={{color: theme.accent}}>{label}</span>
    <span>{right ?? 'MIRROR / DS-003'}</span>
  </div>
);

/** The thin top + bottom rules that frame every shot. */
export const FrameRules: React.FC = () => (
  <>
    <div style={{position: 'absolute', top: 178, left: 64, right: 64, height: 1.5, background: theme.accent, opacity: 0.5}} />
    <div style={{position: 'absolute', bottom: 470, left: 64, right: 64, height: 1, background: theme.inkFaint}} />
  </>
);

const Caption: React.FC<{children: React.ReactNode; y?: number; size?: number; colour?: string}> = ({
  children,
  y = 1290,
  size = 74,
  colour = theme.ink,
}) => (
  <div
    style={{
      position: 'absolute',
      top: y,
      left: 64,
      right: 64,
      textAlign: 'center',
      fontFamily: 'Anton, "Arial Black", sans-serif',
      fontSize: size,
      lineHeight: 1.1,
      letterSpacing: 1,
      color: colour,
      textShadow: '0 4px 28px rgba(0,0,0,0.95), 0 0 60px rgba(0,0,0,0.7)',
      textTransform: 'uppercase',
    }}
  >
    {children}
  </div>
);

// ============================================================ 1. mirror colony
/** A membrane ring of cells. `mirror` tints half of them the accent colour. */
export const MirrorColony: React.FC<SceneProps & {label?: string; mirror?: boolean; divide?: boolean}> = ({
  p,
  label = 'CULTURE / CHIRAL',
  mirror = true,
  divide = false,
}) => {
  const cam: Cam = {rot: [-0.34 + p * 0.16, p * 1.5, 0], dist: 22 - p * 2.8, fov: 700};
  const draw = React.useCallback(
    (ctx: CanvasRenderingContext2D, frame: number, t: number) => {
      const segs: Seg[] = [];
      const n = 13;
      for (let i = 0; i < n; i++) {
        const a = (i / n) * Math.PI * 2 + t * 0.22;
        const rad = 7.2 + Math.sin(i * 2.1 + t * 0.7) * 1.4;
        const cx = Math.cos(a) * rad;
        const cz = Math.sin(a) * rad;
        const cy = Math.sin(i * 1.7 + t * 0.5) * 1.6;
        const size = 2.0 + (i % 3) * 0.34;
        const isMirror = mirror && i % 2 === 1;
        const col = isMirror ? theme.accent : 'rgba(210,240,250,0.92)';

        // hollow membrane ring
        const ring = ringPoints(22, size, size * 0.16, i + 7).map(
          ([x, y, z]) => [x + cx, y + cy, z + cz] as V3
        );
        segs.push(...tubeSegs(ring, col, isMirror ? 2.0 : 1.4, isMirror ? 7 : 0));

        // bright nucleoid + a second one when the cell is splitting
        const nucleoids = divide ? [v3.add([cx, cy, cz], [0, 0, 0]), v3.add([cx, cy, cz], [size * 0.9 * Math.sin(a), 0, size * 0.9 * Math.cos(a)])] : [[cx, cy, cz] as V3];
        for (const nb of nucleoids) {
          segs.push(...sphereSegs(size * 0.24, 4, 5, '#EAFBFF', 1.4).map((s) => ({
            a: v3.add(s.a, nb as V3),
            b: v3.add(s.b, nb as V3),
            c: '#EAFBFF',
            w: 1.3,
            glow: 9,
          })));
        }
      }
      drawSegs(ctx, segs, cam, W, H, {accent: theme.accent});
    },
    [cam.dist, cam.rot[1], mirror, divide]
  );

  return (
    <>
      <SceneBackdrop p={p} />
      <Starfield p={p} n={70} />
      <Soft3D width={W} height={H} draw={draw} style={{position: 'absolute', inset: 0}} />
      <Vignette />
      <FrameRules />
      <Ticker label={label} />
    </>
  );
};

// ============================================================ 2. glitch reveal
/** Hard-cut keyword card with RGB split, punch-in and scan tear. */
export const GlitchReveal: React.FC<
  SceneProps & {lines: string[]; sub?: string; kicker?: string; scale?: number}
> = ({p, lines, sub, kicker, scale = 1}) => {
  const {fps} = useVideoConfig();
  const punch = 1 + 0.09 * Math.exp(-((p * 2.6) % 1) * 6);
  const glitch = Math.max(0, 1 - p * 2.2) + (p > 0.62 && p < 0.72 ? 0.7 : 0);
  const jitter = glitch * 14;
  const barY = (p * 1.7 % 1) * H;

  return (
    <>
      <Starfield p={p} n={50} speed={1.6} />
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background: `radial-gradient(circle at 50% 44%, ${theme.accentSoft} 0%, rgba(0,0,0,0) 62%)`,
        }}
      />
      {/* scan tear */}
      <div
        style={{
          position: 'absolute',
          top: barY,
          left: 0,
          right: 0,
          height: 3 + glitch * 16,
          background: theme.accent,
          opacity: 0.12 + glitch * 0.25,
          filter: 'blur(2px)',
        }}
      />
      {kicker ? (
        <div
          style={{
            position: 'absolute',
            top: 430,
            left: 0,
            right: 0,
            textAlign: 'center',
            fontFamily: theme.type.mono,
            fontSize: 26,
            letterSpacing: 10,
            color: theme.accent,
            opacity: 0.9,
          }}
        >
          {kicker}
        </div>
      ) : null}

      <div
        style={{
          position: 'absolute',
          inset: 0,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          gap: 6,
          transform: `translate(${Math.sin(p * 90) * jitter}px, 0) scale(${punch * scale})`,
        }}
      >
        {lines.map((ln, i) => (
          <div key={i} style={{position: 'relative'}}>
            {/* RGB ghosts */}
            <div
              style={{
                position: 'absolute',
                inset: 0,
                color: '#FF2D6A',
                opacity: glitch * 0.55,
                transform: `translateX(${-jitter * 0.6}px)`,
                fontFamily: theme.type.shout,
                fontSize: 150,
                lineHeight: 0.94,
                textAlign: 'center',
                textTransform: 'uppercase',
              }}
            >
              {ln}
            </div>
            <div
              style={{
                position: 'absolute',
                inset: 0,
                color: '#22D3EE',
                opacity: glitch * 0.55,
                transform: `translateX(${jitter * 0.6}px)`,
                fontFamily: theme.type.shout,
                fontSize: 150,
                lineHeight: 0.94,
                textAlign: 'center',
                textTransform: 'uppercase',
              }}
            >
              {ln}
            </div>
            <div
              style={{
                fontFamily: theme.type.shout,
                fontSize: 150,
                lineHeight: 0.94,
                textAlign: 'center',
                textTransform: 'uppercase',
                color: theme.ink,
                textShadow: `0 0 70px ${theme.accentGlow}, 0 10px 40px rgba(0,0,0,0.9)`,
                letterSpacing: 2,
              }}
            >
              {ln}
            </div>
          </div>
        ))}
      </div>

      {sub ? (
        <div
          style={{
            position: 'absolute',
            top: 1220,
            left: 64,
            right: 64,
            textAlign: 'center',
            fontFamily: theme.type.ui,
            fontWeight: 600,
            fontSize: 40,
            letterSpacing: 3,
            color: theme.inkDim,
          }}
        >
          {sub}
        </div>
      ) : null}
      <Vignette />
      <FrameRules />
    </>
  );
};

// ============================================================ 3. handed helix
/** Two helices side by side: same molecule, opposite handedness. */
export const HandedHelix: React.FC<SceneProps & {label?: string; split?: boolean}> = ({
  p,
  label = 'CHIRALITY / L vs D',
  split = true,
}) => {
  const sep = split ? interpolate(p, [0, 0.35], [0, 5.4], {extrapolateRight: 'clamp'}) : 0;
  const cam: Cam = {rot: [0.16 + p * 0.1, -0.5 + p * 1.15, 0], dist: 26 - p * 2.2, fov: 640};
  const draw = React.useCallback(
    (ctx: CanvasRenderingContext2D, frame: number, t: number) => {
      const segs: Seg[] = [];
      const spin = t * 0.5;
      for (const side of [-1, 1] as const) {
        const x = side * sep;
        const handed: 1 | -1 = side === 1 ? -1 : 1; // right side is the mirror (D)
        const col = side === 1 ? theme.accent : 'rgba(215,240,250,0.92)';
        const h = helixSegs(1.5, 15, 2.6, handed, 150, col);
        for (const s of h) {
          segs.push({
            a: v3.add([x, 0, 0], v3.rotY(s.a, spin)),
            b: v3.add([x, 0, 0], v3.rotY(s.b, spin)),
            c: s.c,
            w: s.w,
            glow: s.glow,
          });
        }
        // backbone pair runs the opposite way, which is the whole point
        const back = helixSegs(2.05, 15, 2.6, handed, 120, side === 1 ? theme.accent : 'rgba(215,240,250,0.6)');
        for (const s of back) {
          segs.push({
            a: v3.add([x, 0, 0], v3.rotY(s.a, spin)),
            b: v3.add([x, 0, 0], v3.rotY(s.b, spin)),
            c: s.c,
            w: 1.1,
          });
        }
      }
      drawSegs(ctx, segs, cam, W, H, {accent: theme.accent});
    },
    [cam.dist, cam.rot[1], sep]
  );

  return (
    <>
      <SceneBackdrop p={p} />
      <Starfield p={p} n={60} />
      <Soft3D width={W} height={H} draw={draw} style={{position: 'absolute', inset: 0}} />
      {/* axis labels */}
      <div style={{position: 'absolute', top: 980, left: 90, fontFamily: theme.type.mono, fontSize: 26, letterSpacing: 5, color: theme.inkDim}}>L / LEFT</div>
      <div style={{position: 'absolute', top: 980, right: 90, fontFamily: theme.type.mono, fontSize: 26, letterSpacing: 5, color: theme.accent}}>D / MIRROR</div>
      <Vignette />
      <FrameRules />
      <Ticker label={label} />
    </>
  );
};

// ============================================================ 4. immune siege
/** Antibodies orbiting a cell they cannot bind to. Three-lobed halo, jittered. */
export const ImmuneSiege: React.FC<SceneProps & {label?: string}> = ({p, label = 'IMMUNE RESPONSE'}) => {
  const cam: Cam = {rot: [0.2 + p * 0.12, p * 1.9, 0], dist: 24, fov: 640};
  const draw = React.useCallback(
    (ctx: CanvasRenderingContext2D, frame: number, t: number) => {
      const segs: Seg[] = [];
      // target cell: icosahedral capsid
      segs.push(...icosaSegs(3.4, 'rgba(220,245,252,0.9)', 2.2).map((s) => ({...s, glow: 6})));
      segs.push(...sphereSegs(3.1, 5, 7, theme.accent, 1.0));

      // antibodies: Y shapes on a three-lobed, jittered orbit — never a perfect wreath
      const n = 11;
      for (let i = 0; i < n; i++) {
        const base = (i / n) * Math.PI * 2;
        const lobe = Math.sin(base * 3 + t * 0.6) * 2.2;
        const a = base + t * 0.42;
        const rad = 7.4 + lobe + Math.sin(t * 1.7 + i) * 0.5;
        const y = Math.sin(base * 2 + t * 0.4) * 2.6;
        const anchor: V3 = [Math.cos(a) * rad, y, Math.sin(a) * rad];
        const tip = v3.norm(v3.sub([0, 0, 0], anchor));
        const armLen = 1.5;
        const perp = v3.norm(v3.cross(tip, [0, 1, 0]));
        const perp2 = v3.norm(v3.cross(tip, perp));
        const basePt = v3.add(anchor, v3.scale(tip, -armLen * 1.6));
        segs.push({a: basePt, b: anchor, c: 'rgba(255,90,90,0.85)', w: 2.2, glow: 5});
        for (const s of [1, -1]) {
          const fork = v3.add(v3.add(anchor, v3.scale(tip, armLen)), v3.scale(s === 1 ? perp : perp2, armLen * 0.8));
          segs.push({a: anchor, b: fork, c: 'rgba(255,90,90,0.85)', w: 2.0, glow: 5});
        }
      }

      // failed-attachment sparks: small X marks near the surface
      for (let i = 0; i < 7; i++) {
        const a = i * 2.1 + t * 0.9;
        const r = 4.2 + (i % 3) * 0.5;
        const c: V3 = [Math.cos(a) * r, Math.sin(a * 1.7) * 2.2, Math.sin(a) * r];
        const flick = 0.35 + 0.65 * Math.abs(Math.sin(t * 5 + i * 1.9));
        segs.push({a: v3.add(c, [-0.35, 0, 0]), b: v3.add(c, [0.35, 0, 0]), c: `rgba(255,255,255,${flick})`, w: 2});
        segs.push({a: v3.add(c, [0, -0.35, 0]), b: v3.add(c, [0, 0.35, 0]), c: `rgba(255,255,255,${flick})`, w: 2});
      }
      drawSegs(ctx, segs, cam, W, H, {accent: theme.accent});
    },
    [cam.dist, cam.rot[1]]
  );

  return (
    <>
      <SceneBackdrop p={p} />
      <Starfield p={p} n={50} speed={0.6} />
      <Soft3D width={W} height={H} draw={draw} style={{position: 'absolute', inset: 0}} />
      <Vignette />
      <FrameRules />
      <Ticker label={label} right="BINDING: FAILED" />
    </>
  );
};

// ============================================================ 5. phage storm
export const PhageStorm: React.FC<SceneProps & {label?: string}> = ({p, label = 'PHAGE ASSAY'}) => {
  const cam: Cam = {rot: [0.3 - p * 0.14, p * 1.2 - 0.4, 0], dist: 22, fov: 620};
  const draw = React.useCallback(
    (ctx: CanvasRenderingContext2D, frame: number, t: number) => {
      const segs: Seg[] = [];
      const n = 9;
      for (let i = 0; i < n; i++) {
        const ring = Math.floor(i / 3);
        const a = (i / 3) * Math.PI * 2 * (1 / 1) + t * (0.3 + ring * 0.16) + ring * 1.1;
        const rad = 4.4 + ring * 3.1;
        const c: V3 = [Math.cos(a) * rad, Math.sin(a * 1.3 + i) * 1.8, Math.sin(a) * rad];
        const head = icosaSegs(0.95, 'rgba(225,248,255,0.9)', 1.5).map((s) => ({
          a: v3.add(s.a, c),
          b: v3.add(s.b, c),
          c: s.c,
          w: 1.4,
          glow: 5,
        }));
        segs.push(...head);
        // tail fibres pointing at the (uninfectable) centre
        const inward = v3.norm(v3.sub([0, 0, 0], c));
        for (let f = 0; f < 4; f++) {
          const ang = (f / 4) * Math.PI * 2 + t;
          const off = v3.scale(v3.norm(v3.cross(inward, [0, 1, 0])), Math.cos(ang) * 0.7);
          const off2 = v3.scale(v3.norm(v3.cross(inward, off)), Math.sin(ang) * 0.7);
          const knee = v3.add(v3.add(c, v3.scale(inward, 0.95)), v3.add(off, off2));
          const tip = v3.add(knee, v3.scale(inward, 1.5));
          segs.push({a: c, b: knee, c: theme.accent, w: 1.5, glow: 4});
          segs.push({a: knee, b: tip, c: theme.accent, w: 1.3});
        }
      }
      // the cell they cannot penetrate
      const core = sphereSegs(2.3, 6, 8, 'rgba(230,250,255,0.85)', 1.3);
      segs.push(...core);
      drawSegs(ctx, segs, cam, W, H, {accent: theme.accent});
    },
    [cam.dist, cam.rot[1]]
  );

  return (
    <>
      <SceneBackdrop p={p} />
      <Starfield p={p} n={40} speed={0.8} />
      <Soft3D width={W} height={H} draw={draw} style={{position: 'absolute', inset: 0}} />
      <Vignette />
      <FrameRules />
      <Ticker label={label} right="INFECTION: 0%" />
    </>
  );
};

// ============================================================ 6. ribosome
export const Ribosome: React.FC<SceneProps & {label?: string}> = ({p, label = 'TRANSLATION'}) => {
  const cam: Cam = {rot: [0.24, 0.9 + p * 0.75, 0], dist: 26, fov: 600};
  const draw = React.useCallback(
    (ctx: CanvasRenderingContext2D, frame: number, t: number) => {
      const segs: Seg[] = [];
      // two subunits that split apart across the shot
      const splitGap = interpolate(p, [0.25, 0.9], [0, 2.6], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
      segs.push(...sphereSegs(2.7, 6, 9, 'rgba(220,244,252,0.85)', 1.3).map((s) => ({
        a: v3.add(s.a, [0, 1.5 + splitGap, 0]),
        b: v3.add(s.b, [0, 1.5 + splitGap, 0]),
        c: 'rgba(220,244,252,0.85)',
        w: 1.2,
      })));
      segs.push(...sphereSegs(2.2, 5, 8, theme.accent, 1.4).map((s) => ({
        a: v3.add(s.a, [0, -1.9 - splitGap * 0.5, 0]),
        b: v3.add(s.b, [0, -1.9 - splitGap * 0.5, 0]),
        c: theme.accent,
        w: 1.3,
        glow: 5,
      })));
      // mRNA strand threading through, with codons ticking past
      const strand: V3[] = [];
      for (let i = 0; i < 40; i++) {
        const x = (i / 39 - 0.5) * 22;
        strand.push([x, -0.4 + Math.sin(i * 0.5 + t * 2) * 0.5, Math.cos(i * 0.4 + t * 1.4) * 1.2]);
      }
      segs.push(...tubeSegs(strand, 'rgba(190,235,250,0.55)', 1.6).slice(0, 39));
      for (let i = 0; i < 12; i++) {
        const x = (i / 11 - 0.5) * 20;
        const y = -0.4 + Math.sin(i * 0.5 + t * 2) * 0.5;
        segs.push({a: [x, y, 0], b: [x, y + 0.9, 0], c: theme.accent, w: 2, glow: 6});
      }
      // emerging peptide chain
      for (let i = 0; i < 9; i++) {
        const a = i * 0.5 + t * 0.8;
        const r = 1.6 + i * 0.32;
        const c: V3 = [Math.cos(a) * r, 4.2 + splitGap + i * 0.42, Math.sin(a) * r];
        segs.push({a: c, b: v3.add(c, [0.3, 0.3, 0]), c: 'rgba(240,255,255,0.9)', w: 2.2, glow: 4});
      }
      drawSegs(ctx, segs, cam, W, H, {accent: theme.accent});
    },
    [cam.dist, cam.rot[1], p]
  );

  return (
    <>
      <SceneBackdrop p={p} />
      <Starfield p={p} n={50} />
      <Soft3D width={W} height={H} draw={draw} style={{position: 'absolute', inset: 0}} />
      <Vignette />
      <FrameRules />
      <Ticker label={label} right="BUILDING PROTEIN" />
    </>
  );
};

// ============================================================ 7. counter slam
/** Giant number that counts and slams in with a white flash. */
export const CounterSlam: React.FC<
  SceneProps & {from: number; to: number; suffix?: string; prefix?: string; caption: string; label?: string}
> = ({p, from, to, suffix = '', prefix = '', caption, label = 'ESTIMATE'}) => {
  const {fps} = useVideoConfig();
  const raw = interpolate(p, [0.1, 0.62], [from, to], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const val = Math.round(raw);
  const punch = 1 + 0.12 * Math.exp(-p * 8);
  const flash = Math.max(0, 1 - p * 6);

  return (
    <>
      <Starfield p={p} n={40} speed={0.4} />
      {/* concentric radar rings */}
      <svg width={W} height={H} style={{position: 'absolute', inset: 0}}>
        {Array.from({length: 6}, (_, i) => {
          const r = 160 + ((i * 110 + p * 240) % 660);
          const o = 0.30 * (1 - (r - 160) / 660);
          return <circle key={i} cx={W / 2} cy={760} r={r} fill="none" stroke={theme.accent} strokeWidth={1.4} opacity={o} />;
        })}
      </svg>
      <div
        style={{
          position: 'absolute',
          top: 640,
          left: 0,
          right: 0,
          textAlign: 'center',
          transform: `scale(${punch})`,
        }}
      >
        <div
          style={{
            fontFamily: theme.type.shout,
            fontSize: 260,
            lineHeight: 1,
            color: theme.ink,
            textShadow: `0 0 90px ${theme.accentGlow}`,
            letterSpacing: -4,
          }}
        >
          {prefix}
          {val}
          <span style={{fontSize: 150, color: theme.accent}}>{suffix}</span>
        </div>
        <div style={{fontFamily: theme.type.mono, fontSize: 30, letterSpacing: 12, color: theme.accent, marginTop: 18}}>
          {label}
        </div>
      </div>
      <div style={{position: 'absolute', inset: 0, background: '#fff', opacity: flash * 0.25}} />
      <Vignette />
      <FrameRules />
    </>
  );
};

// ============================================================ 8. hand wall
/** A pinwheel lattice of hands — STOP. Built from rings, not emoji. */
export const HandWall: React.FC<SceneProps & {label?: string; word?: string}> = ({
  p,
  label = 'PETITION / 38 SIGNATORIES',
  word = 'STOP',
}) => {
  const draw = React.useCallback(
    (ctx: CanvasRenderingContext2D, frame: number, t: number) => {
      const cols = 5;
      const rows = 7;
      const cw = W / cols;
      const ch = H / rows;
      for (let r = 0; r < rows; r++) {
        for (let c = 0; c < cols; c++) {
          const cx = cw * (c + 0.5);
          const cy = ch * (r + 0.5);
          const spin = t * 0.5 + (r + c) * 0.32;
          const s = 20;
          const col = (r + c) % 2 === 0 ? 'rgba(210,240,252,0.85)' : theme.accent;
          ctx.save();
          ctx.translate(cx, cy);
          ctx.globalAlpha = 0.46 + 0.30 * Math.sin(t * 1.4 + r * 0.7 + c * 0.4);
          ctx.strokeStyle = col;
          ctx.lineWidth = 2.6;
          ctx.shadowBlur = 12;
          ctx.shadowColor = col;
          // palm
          ctx.beginPath();
          ctx.ellipse(0, 0, s * 0.5, s * 0.62, 0, 0, Math.PI * 2);
          ctx.stroke();
          // four fingers + thumb, pinwheeled
          for (let f = 0; f < 4; f++) {
            const a = -Math.PI / 2 + (f - 1.5) * 0.22 + Math.sin(spin + f) * 0.06;
            ctx.beginPath();
            ctx.moveTo(Math.cos(a) * s * 0.34, Math.sin(a) * s * 0.5);
            ctx.lineTo(Math.cos(a) * s * 1.05, Math.sin(a) * s * 1.22);
            ctx.stroke();
          }
          const ta = 0.5 + Math.sin(spin) * 0.2;
          ctx.beginPath();
          ctx.moveTo(Math.cos(ta) * s * 0.4, Math.sin(ta) * s * 0.5);
          ctx.lineTo(Math.cos(ta) * s * 1.0, Math.sin(ta) * s * 0.55);
          ctx.stroke();
          ctx.restore();
        }
      }
      ctx.globalAlpha = 1;
      ctx.shadowBlur = 0;
    },
    []
  );

  return (
    <>
      <div style={{position: 'absolute', inset: 0, background: theme.bgLift}} />
      <Soft3D width={W} height={H} draw={draw} style={{position: 'absolute', inset: 0}} />
      <div style={{position: 'absolute', inset: 0, background: 'radial-gradient(circle at 50% 46%, rgba(5,7,10,0.55) 0%, rgba(5,7,10,0.92) 72%)'}} />
      <div
        style={{
          position: 'absolute',
          top: 700,
          left: 0,
          right: 0,
          textAlign: 'center',
          fontFamily: theme.type.shout,
          fontSize: 300,
          lineHeight: 1,
          color: theme.ink,
          letterSpacing: 8,
          textShadow: `0 0 100px ${theme.accentGlow}`,
        }}
      >
        {word}
      </div>
      <Vignette />
      <FrameRules />
      <Ticker label={label} />
    </>
  );
};
