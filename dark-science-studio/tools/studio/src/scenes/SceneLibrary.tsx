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
        background: `radial-gradient(ellipse 78% 52% at 50% 45%, ${theme.accentSoft} 0%, rgba(5,7,10,0) 72%)`,
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
              opacity={0.20 * (1 - (r - 120) / 620)}
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
export const Ticker: React.FC<{label: string; right?: string}> = ({label, right = 'DARK SCIENCE'}) => (
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
    <span>{right}</span>
  </div>
);

/** Blocky instrument readouts — the DS-002 signature that fills dead space. */
export const HudPanel: React.FC<{
  side?: 'left' | 'right';
  top?: number;
  rows: [string, string][];
  accent?: boolean;
}> = ({side = 'left', top = 560, rows, accent}) => (
  <div
    style={{
      position: 'absolute',
      top,
      [side]: 60,
      width: 380,
      display: 'flex',
      flexDirection: 'column',
      gap: 0,
    }}
  >
    {rows.map(([k, v], i) => (
      <div
        key={i}
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'baseline',
          padding: '9px 12px',
          background: i % 2 === 0 ? `rgba(${theme.accentRGB},0.09)` : `rgba(${theme.accentRGB},0.04)`,
          borderLeft: `2px solid ${accent && i === 0 ? theme.accent : theme.accentGlow}`,
          fontFamily: theme.type.mono,
          fontSize: 19,
          letterSpacing: 1.5,
        }}
      >
        <span style={{color: 'rgba(255,255,255,0.55)'}}>{k}</span>
        <span style={{color: theme.accent, fontWeight: 600}}>{v}</span>
      </div>
    ))}
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
export const MirrorColony: React.FC<
  SceneProps & {label?: string; mirror?: boolean; divide?: boolean; hud?: [string, string][]}
> = ({
  p,
  label = 'CULTURE / CHIRAL',
  mirror = true,
  divide = false,
  hud = [
    ['CELLS', '13'],
    ['CHIRALITY', mirror ? 'D / MIRROR' : 'L / NATIVE'],
    ['STATUS', 'VIABLE'],
  ],
}) => {
  const cam: Cam = {rot: [-0.34 + p * 0.42, p * 2.4, 0], dist: 17.5 - p * 2.6, fov: 760};
  const draw = React.useCallback(
    (ctx: CanvasRenderingContext2D, frame: number, t: number) => {
      const segs: Seg[] = [];
      const n = 11;
      for (let i = 0; i < n; i++) {
        const a = (i / n) * Math.PI * 2 + t * 0.22;
        const rad = 8.4 + Math.sin(i * 2.1 + t * 0.7) * 1.3;
        const cx = Math.cos(a) * rad;
        const cz = Math.sin(a) * rad;
        const cy = Math.sin(i * 1.7 + t * 0.5) * 1.6;
        const size = 1.35 + (i % 3) * 0.24;
        const isMirror = mirror && i % 2 === 1;
        const col = isMirror ? theme.accent : 'rgba(210,240,250,0.92)';

        // hollow membrane ring
        // 3D membrane: jitter in y as well as radius, plus a slow wobble so the
        // cell is a blob with depth, never a flat plate.
        const ring = ringPoints(20, size, size * 0.14, i + 7, 0)
          .map(([x, y, z], k) => {
            const a = (k / 20) * Math.PI * 2;
            const wob = Math.sin(a * 3 + t * 2.2 + i) * size * 0.34;
            return [x + cx, y + cy + wob, z + cz] as V3;
          });
        segs.push(...tubeSegs(ring, col, isMirror ? 1.7 : 1.25, isMirror ? 7 : 0));

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
      {hud ? <HudPanel rows={hud} /> : null}
    </>
  );
};

// ============================================================ 2. glitch reveal
/** Hard-cut keyword card with RGB split, punch-in and scan tear. */
export const GlitchReveal: React.FC<
  SceneProps & {lines: string[]; sub?: string; kicker?: string; scale?: number}
> = ({p, lines, sub, kicker, scale = 1}) => {
  const {fps} = useVideoConfig();
  // A `sub` line lives at y=862. Reserve the whole band under the shout block
  // instead of nudging it up 54px — that nudge used to leave the sub sitting
  // *inside* the type, which read as a ghosted double image.
  const shoutSize = lines.length > 1 ? 118 : 150;
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
          paddingBottom: sub ? 420 : 0,
          gap: 6,
          transform: `translate(${Math.sin(p * 90) * jitter}px, 0px) scale(${punch * scale})`,
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
                fontSize: shoutSize,
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
                color: theme.accent,
                opacity: glitch * 0.55,
                transform: `translateX(${jitter * 0.6}px)`,
                fontFamily: theme.type.shout,
                fontSize: shoutSize,
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
                fontSize: shoutSize,
                lineHeight: 0.94,
                textAlign: 'center',
                textTransform: 'uppercase',
                color: theme.ink,
                // a soft trailing echo instead of a solid double image: the
                // shadow keeps the punch but no longer reads as a typo
                textShadow: `6px 6px 0 rgba(${theme.accentRGB},0.13), -6px -6px 0 rgba(255,45,106,0.07), 0 0 80px ${theme.accentGlow}, 0 10px 40px rgba(0,0,0,0.95)`,
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
            top: 862,
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
  const cam: Cam = {rot: [0.16 + p * 0.32, -0.5 + p * 1.7, 0], dist: 19 - p * 2.2, fov: split ? 900 : 720};
  const draw = React.useCallback(
    (ctx: CanvasRenderingContext2D, frame: number, t: number) => {
      const segs: Seg[] = [];
      const spin = t * 0.85;
      // when the shot is about a single molecule, draw a single molecule —
      // overlaying both enantiomers at sep=0 reads as spaghetti
      const sides: readonly (-1 | 1)[] = split ? ([-1, 1] as const) : ([-1] as const);
      for (const side of sides) {
        const x = side * sep;
        const handed: 1 | -1 = side === 1 ? -1 : 1; // right side is the mirror (D)
        const col = side === 1 ? theme.accent : 'rgba(215,240,250,0.92)';
        const h = helixSegs(2.05, 15, 2.6, handed, 104, col);
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
        const back = helixSegs(2.9, 15, 2.6, handed, 76, side === 1 ? theme.accent : 'rgba(215,240,250,0.6)');
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
    [cam.dist, cam.rot[1], sep, split]
  );

  return (
    <>
      <SceneBackdrop p={p} />
      <Starfield p={p} n={60} />
      <Soft3D width={W} height={H} draw={draw} style={{position: 'absolute', inset: 0}} />
      {/* axis labels */}
      <div style={{position: 'absolute', top: 980, left: 90, fontFamily: theme.type.mono, fontSize: 26, letterSpacing: 5, color: theme.inkDim}}>
        {split ? 'L / LEFT' : 'PRNP / 253 CODONS'}
      </div>
      {split ? (
        <div style={{position: 'absolute', top: 980, right: 90, fontFamily: theme.type.mono, fontSize: 26, letterSpacing: 5, color: theme.accent}}>D / MIRROR</div>
      ) : null}
      <Vignette />
      <FrameRules />
      <Ticker label={label} />
      <HudPanel
        side="right"
        top={300}
        rows={split ? [['SENSE', 'L'], ['MIRROR', 'D'], ['Δ PITCH', '2.6 nm']] : [['GENE', 'PRNP'], ['LOCUS', '20p13'], ['CODON 178', 'GAC→AAC']]}
      />
    </>
  );
};

// ============================================================ 4. immune siege
/** Antibodies orbiting a cell they cannot bind to. Three-lobed halo, jittered. */
export const ImmuneSiege: React.FC<SceneProps & {label?: string}> = ({p, label = 'IMMUNE RESPONSE'}) => {
  const cam: Cam = {rot: [0.2 + p * 0.12, p * 1.9, 0], dist: 19.5, fov: 710};
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
      <HudPanel side="left" top={880} accent rows={[['ANTIBODIES', '11'], ['BOUND', '0'], ['RESULT', 'EVADED']]} />
    </>
  );
};

// ============================================================ 5. phage storm
export const PhageStorm: React.FC<SceneProps & {label?: string}> = ({p, label = 'PHAGE ASSAY'}) => {
  const cam: Cam = {rot: [0.3 - p * 0.14, p * 1.2 - 0.4, 0], dist: 18, fov: 700};
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
      <HudPanel side="left" top={880} rows={[['PHAGES', '9'], ['ATTACH', '0'], ['LYSIS', '—']]} />
    </>
  );
};

// ============================================================ 6. ribosome
export const Ribosome: React.FC<SceneProps & {label?: string}> = ({p, label = 'TRANSLATION'}) => {
  const cam: Cam = {rot: [0.24, 0.9 + p * 0.75, 0], dist: 20, fov: 680};
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
      <HudPanel side="right" top={880} rows={[['SUBUNITS', '2 / SPLIT'], ['mRNA', 'ACTIVE'], ['PEPTIDE', '+9']]} />
    </>
  );
};

// ============================================================ 7. counter slam
/** Giant number that counts and slams in with a white flash. */
export const CounterSlam: React.FC<
  SceneProps & {from: number; to: number; suffix?: string; prefix?: string; caption: string; label?: string}
> = ({p, from, to, suffix = '', prefix = '', caption, label = 'ESTIMATE'}) => {
  const {fps} = useVideoConfig();
  // Count fast, then LOCK on the target for the rest of the shot.
  const raw = interpolate(p, [0.08, 0.55], [from, to], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const val = p >= 0.55 ? to : Math.round(raw);
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
          const breathe = 1 + 0.16 * Math.sin(t * 2.6 + (r * 1.7 + c * 2.3));
          const s = 26;
          const col = (r + c) % 2 === 0 ? 'rgba(210,240,252,0.85)' : theme.accent;
          ctx.save();
          ctx.translate(cx + Math.sin(t * 1.9 + r * 1.3) * 11, cy + Math.cos(t * 1.6 + c * 1.2) * 11);
          ctx.scale(breathe, breathe);
          ctx.globalAlpha = 0.58 + 0.40 * Math.sin(t * 2.2 + r * 0.7 + c * 0.4);
          ctx.strokeStyle = col;
          ctx.lineWidth = 3.2;
          ctx.shadowBlur = 16;
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
      <div style={{position: 'absolute', inset: 0, background: 'radial-gradient(circle at 50% 46%, rgba(5,7,10,0.35) 0%, rgba(5,7,10,0.86) 76%)'}} />
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
          transform: `scale(${1.02 + p * 0.06}) rotate(${(p - 0.5) * 0.6}deg)`,
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

// ============================================================ 9. misfolding chain
/**
 * One misfolded protein recruits its neighbour, which recruits the next.
 * Drawn as a beta-strand stack: each residue is a strand, native strands are
 * thin and evenly spaced, converted strands thicken, twist and lock together.
 * `state`: 'clear' | 'seeding' | 'locked'
 */
export const MisfoldChain: React.FC<
  SceneProps & {
    label?: string;
    state?: 'clear' | 'seeding' | 'locked';
    count?: number;
    hud?: [string, string][] | null;
    /** poster mode: tighter framing, no panels */
    cover?: boolean;
  }
> = ({
  p,
  label = 'PRION / CONFORMATIONAL',
  state = 'seeding',
  count = 15,
  cover = false,
  hud = state === 'clear'
    ? ([
        ['CONFORMATION', 'NATIVE (PrP-C)'],
        ['FOLD', 'ALPHA HELIX'],
        ['TURNOVER', 'NORMAL'],
      ] as [string, string][])
    : ([
        ['CONFORMATION', 'MISFOLDED (PrP-Sc)'],
        ['SEEDING', 'YES'],
        ['DISINFECTION', 'INEFFECTIVE'],
      ] as [string, string][]),
}) => {
  const seeded = state !== 'clear';
  // how far up the stack the corruption has spread this shot
  const front = state === 'locked' ? 1 : clamp(p * 1.5);
  const cam: Cam = cover
    ? {rot: [-0.24 + p * 0.18, -1.5 + p * 0.5, 0], dist: 11.5, fov: 1500}
    : {rot: [-0.30 + p * 0.22, -0.9 + p * 1.5, 0], dist: 17.5 - p * 1.5, fov: 1500};

  const draw = React.useCallback(
    (ctx: CanvasRenderingContext2D, frame: number, t: number) => {
      const segs: Seg[] = [];
      const RAD = 4.4; // fibre radius
      const HGT = 11.2; // half-height of the fibre
      const N = count;

      // every residue = a loop of backbone at one height up the axis
      for (let i = 0; i < N; i++) {
        const u = i / (N - 1);
        const y = (u - 0.5) * HGT * 2;
        const converted = seeded && u <= front;
        // converted strands collapse inward and tilt: the beta-stack squeeze
        const r = converted ? RAD * 0.62 : RAD;
        const tilt = converted ? 0.34 : 0;
        const spin = t * 0.5 + i * 0.22 + (converted ? 0.5 : 0);

        const loop: V3[] = Array.from({length: 16}, (_, k) => {
          const a = (k / 16) * Math.PI * 2;
          return [
            Math.cos(a + spin) * r,
            y + Math.sin(a * 2 + spin) * 0.42 + tilt * Math.cos(a),
            Math.sin(a + spin) * r,
          ] as V3;
        });
        const col = converted ? theme.accent : 'rgba(200,232,248,0.85)';
        segs.push(...tubeSegs(loop, col, converted ? 2.5 : 1.3, converted ? 11 : 0));

        // the backbone axis, brighter where it has converted
        if (i < N - 1) {
          const y2 = ((i + 1) / (N - 1) - 0.5) * HGT * 2;
          segs.push({
            a: [0, y, 0],
            b: [0, y2, 0],
            c: converted ? theme.accent : 'rgba(200,232,248,0.30)',
            w: converted ? 3.0 : 1.2,
            glow: converted ? 12 : 0,
          });
        }

        // side chains sticking out — four per residue, they flatten on conversion
        for (let k = 0; k < 4; k++) {
          const a = (k / 4) * Math.PI * 2 + spin * 0.5 + i * 0.4;
          const len = converted ? 1.05 : 2.1;
          segs.push({
            a: [Math.cos(a) * r, y, Math.sin(a) * r],
            b: [Math.cos(a) * (r + len), y + (converted ? 0.35 : 0), Math.sin(a) * (r + len)],
            c: converted ? 'rgba(179,107,255,0.9)' : 'rgba(200,232,248,0.55)',
            w: converted ? 1.7 : 1,
            glow: converted ? 6 : 0,
          });
        }
      }

      // the seed itself: the first converted residue, pulsing
      if (seeded) {
        const y0 = -HGT;
        const pulse = 1.1 + Math.sin(t * 6) * 0.16;
        segs.push(...tubeSegs(sphereOutline([0, y0, 0], RAD * 0.9 * pulse), theme.accent, 2.4, 20));
        for (let k = 0; k < 3; k++) {
          const rr = RAD * (1.3 + k * 0.55) * pulse;
          segs.push(...tubeSegs(sphereOutline([0, y0, 0], rr), theme.accent, 1, 6));
        }
      }

      // recruitment battens between neighbouring converted strands
      if (seeded) {
        for (let i = 1; i < N; i++) {
          const u = i / (N - 1);
          if (u > front || i % 2 !== 0) continue;
          const y = (u - 0.5) * HGT * 2;
          const y2 = ((i - 1) / (N - 1) - 0.5) * HGT * 2;
          const a = 0.7 + t * 0.2;
          segs.push({
            a: [Math.cos(a) * RAD * 0.62, y, Math.sin(a) * RAD * 0.62],
            b: [Math.cos(a) * RAD * 0.62, y2, Math.sin(a) * RAD * 0.62],
            c: 'rgba(255,255,255,0.75)',
            w: 1.1,
            glow: 7,
          });
        }
      }

      drawSegs(ctx, segs, cam, W, H, {accent: theme.accent});
    },
    [cam.dist, cam.rot[1], count, seeded, front]
  );

  return (
    <>
      <SceneBackdrop p={p} />
      <Starfield p={p} n={46} speed={0.7} />
      <Soft3D width={W} height={H} draw={draw} style={{position: 'absolute', inset: 0}} />
      {cover ? null : <div style={{position: 'absolute', top: 452, left: 0, right: 0, textAlign: 'center', fontFamily: theme.type.mono, fontSize: 20, letterSpacing: 7, color: seeded ? theme.accent : 'rgba(210,240,252,0.7)'}}>
        {state === 'clear' ? 'NATIVE MONOMER' : state === 'locked' ? 'AMYLOID FIBRE / LOCKED' : 'FIBRE GROWING'}
      </div>}
      <Vignette />
      <FrameRules />
      <Ticker label={label} right="STRAIN / FFI" />
      {hud ? <HudPanel rows={hud} top={300} /> : null}
    </>
  );
};

/** Cheap wireframe sphere used as a highlight cap. */
function sphereOutline(c: V3, r: number): V3[] {
  return Array.from({length: 12}, (_, i) => {
    const a = (i / 12) * Math.PI * 2;
    return [c[0] + Math.cos(a) * r, c[1] + Math.sin(a) * r * 0.55, c[2] + Math.sin(a) * r] as V3;
  });
}

// ============================================================ 10. thalamus grid
/**
 * The thalamus as an instrument: two egg-shaped nuclei, a sleep-wake spindle
 * running through them, and separate EEG traces for wake / light / deep / REM.
 * `dead`: 'spindles' | 'deep' | 'rem' | null  — which sleep stage has collapsed.
 */
export const ThalamusGrid: React.FC<
  SceneProps & {
    label?: string;
    dead?: 'spindles' | 'deep' | 'rem' | null;
    hud?: [string, string][];
  }
> = ({
  p,
  label = 'THALAMUS / SLEEP SWITCH',
  dead = null,
  hud = [
    ['REGION', 'THALAMUS'],
    ['SPINDLES', dead ? 'ABSENT' : 'PRESENT'],
    ['DEEP', dead === 'deep' || dead === 'rem' ? 'ABSENT' : 'PRESENT'],
    ['REM', dead === 'rem' ? 'ABSENT' : 'PRESENT'],
  ],
}) => {
  const cam: Cam = {rot: [-0.42 + p * 0.5, -0.35 + p * 0.7, 0], dist: 16.0 - p * 1.6, fov: 1320};

  const draw = React.useCallback(
    (ctx: CanvasRenderingContext2D, frame: number, t: number) => {
      const segs: Seg[] = [];
      // two thalamic lobes, egg-shaped: a sphere squashed on x and stretched on y
      for (const side of [-1, 1] as const) {
        const cx = side * 3.55;
        const base = sphereSegs(3.0, 6, 9);
        for (const s of base) {
          const squash = (q: V3): V3 => [q[0] * 0.74 + cx, q[1] * 1.18 + Math.sin(t * 0.7) * 0.12, q[2] * 0.92];
          segs.push({a: squash(s.a), b: squash(s.b), c: 'rgba(198,230,246,0.78)', w: 0.9, glow: 2});
        }
        // cell bodies inside — small bright nucleoids that dim as they die
        const alive = dead ? 0.35 : 1;
        for (let k = 0; k < 26; k++) {
          const a = (k / 26) * Math.PI * 2 + t * 0.3;
          const rr = 0.5 + (k % 5) * 0.44;
          const c: V3 = [
            cx + Math.cos(a) * rr * 0.62,
            Math.sin(k * 2.3) * 2.4 + Math.cos(k * 1.1) * 0.6,
            Math.sin(a) * rr * 0.78,
          ];
          const flick = 0.75 + 0.25 * Math.sin(t * 3 + k * 1.7);
          segs.push(...tubeSegs(sphereOutline(c, 0.21 * alive), alive > 0.5 ? theme.accent : 'rgba(255,90,90,0.85)', 1.6, alive > 0.5 ? 9 * flick : 4));
        }
      }

      // midline sleep-wake spindle: a sine that loses its burst when spindles die
      const burst = dead === 'spindles' ? 0 : 1;
      for (let i = 0; i < 64; i++) {
        const u0 = i / 64;
        const u1 = (i + 1) / 64;
        const amp = (1.35 * burst + 0.06) * Math.sin(u0 * Math.PI);
        const y0 = Math.sin(u0 * 26 + t * 5) * amp;
        const y1 = Math.sin(u1 * 26 + t * 5) * amp;
        segs.push({a: [(u0 - 0.5) * 16.5, y0, 0], b: [(u1 - 0.5) * 16.5, y1, 0], c: theme.accent, w: 2.6, glow: 16});
      }
      // an arrowhead marking the midline axis
      segs.push({a: [0, -8.4, 0], b: [0, -6.6, 0], c: theme.accent, w: 3.4, glow: 14});

      // lift the anatomy into the upper half so the trace block below it stays clear
      drawSegs(ctx, segs, cam, W, H, {accent: theme.accent, yOffset: -205});
    },
    [cam.dist, cam.rot[1], dead]
  );

  // four trace lanes; each is real motion, each dies on cue
  const lanes: {k: string; dead: boolean; f: (x: number) => number}[] = [
    {k: 'WAKE', dead: false, f: (x) => Math.sin(x * 34) * 0.55 + Math.sin(x * 71) * 0.3},
    {k: 'SPINDLES', dead: dead === 'spindles', f: (x) => Math.sin(x * 13) * Math.sin(x * 1.4) * 1.5},
    {k: 'DEEP', dead: dead === 'deep' || dead === 'rem', f: (x) => Math.sin(x * 5.5) * 1.1},
    {k: 'REM', dead: dead === 'rem', f: (x) => Math.sin(x * 27) * 0.4 + Math.sin(x * 9) * 0.5},
  ];

  return (
    <>
      <SceneBackdrop p={p} rings={false} />
      <Soft3D width={W} height={H} draw={draw} style={{position: 'absolute', inset: 0}} />
      {/* trace block sits above the caption band */}
      <div style={{position: 'absolute', top: 1002, left: 64, right: 64}}>
        {lanes.map((ln, i) => {
          const wob = ln.dead ? 0 : 1;
          const pts = Array.from({length: 90}, (_, k) => {
            const w = k / 89;
            const y = ln.dead ? 0 : ln.f(w * 9 + p * 6) * wob;
            return `${(w * 100).toFixed(2)},${(12 + y * 5).toFixed(2)}`;
          }).join(' ');
          return (
            <div key={ln.k} style={{display: 'flex', alignItems: 'center', height: 36, paddingLeft: 4}}>
              <div style={{width: 132, fontFamily: theme.type.mono, fontSize: 17, letterSpacing: 2.5, color: ln.dead ? 'rgba(255,80,80,0.9)' : theme.inkDim}}>
                {ln.k}
              </div>
              <svg width={W - 64 - 64 - 150} height={28} style={{overflow: 'visible'}}>
                <polyline
                  points={pts}
                  fill="none"
                  stroke={ln.dead ? 'rgba(255,70,70,0.75)' : i === 0 ? theme.accent : 'rgba(205,235,248,0.85)'}
                  strokeWidth={ln.dead ? 1.2 : 2}
                />
              </svg>
              <div style={{width: 96, textAlign: 'right', fontFamily: theme.type.mono, fontSize: 15, letterSpacing: 1.5, color: ln.dead ? 'rgba(255,80,80,0.9)' : theme.accent}}>
                {ln.dead ? 'FLAT' : 'OK'}
              </div>
            </div>
          );
        })}
      </div>
      <Vignette />
      <FrameRules />
      <Ticker label={label} right="PSG / 4 LANES" />
      <HudPanel rows={hud} top={330} />
    </>
  );
};

// ============================================================ 11. pedigree
/**
 * Autosomal dominance, drawn: eight founders, three generations, half of them
 * carrying the mutation. Carriers fill in one generation at a time.
 */
export const PedigreeTree: React.FC<
  SceneProps & {label?: string; generations?: number; found?: boolean; hud?: [string, string][]}
> = ({
  p,
  label = 'PRNP / D178N',
  generations = 3,
  found = true,
  hud = [
    ['INHERITANCE', 'DOMINANT'],
    ['GENE', 'PRNP / CHR 20'],
    ['MUTATION', 'D178N+129M'],
    ['PENETRANCE', '100%'],
  ],
}) => {
  const ROW_Y = [700, 940, 1180];
  const NODES = [8, 4, 2];
  const CARRIER = [5, 1, 0]; // which sibling carries it, per generation
  // how far down the tree the reveal has reached
  const reached = clamp(p * (generations + 0.5));

  const xOf = (g: number, i: number, parentX: number) => {
    const n = NODES[g];
    if (g === 0) {
      const spread = W - 280;
      return 140 + (spread / (n - 1)) * i;
    }
    // children fan evenly around the carrier they descend from
    const spread = g === 1 ? 560 : 300;
    const x0 = parentX - spread / 2;
    return x0 + (spread / (n - 1)) * i;
  };

  // resolve positions generation by generation so children follow carriers
  const pos: {x: number; y: number}[] = [];
  const rows: {x: number; y: number}[][] = [];
  let parentX = 0;
  for (let g = 0; g < generations; g++) {
    const row: {x: number; y: number}[] = [];
    for (let i = 0; i < NODES[g]; i++) {
      const x = xOf(g, i, parentX);
      row.push({x, y: ROW_Y[g]});
    }
    rows.push(row);
    parentX = row[CARRIER[g]].x;
  }
  void pos;

  return (
    <>
      <SceneBackdrop p={p} rings={false} />
      <Starfield p={p} n={34} speed={0.4} />
      <svg width={W} height={H} style={{position: 'absolute', inset: 0}}>
        {/* descent buses: one carrier above, a fan of children below */}
        {rows.slice(1).map((row, gi) => {
          const g = gi + 1;
          const parent = rows[g - 1][CARRIER[g - 1]];
          const busY = (ROW_Y[g - 1] + ROW_Y[g]) / 2;
          const xs = row.map((n) => n.x);
          if (g > reached) return null;
          return (
            <g key={`bus${g}`}>
              <line x1={parent.x} y1={ROW_Y[g - 1] + 23} x2={parent.x} y2={busY} stroke="rgba(255,255,255,0.30)" strokeWidth={1.6} />
              <line x1={Math.min(...xs)} y1={busY} x2={Math.max(...xs)} y2={busY} stroke="rgba(255,255,255,0.30)" strokeWidth={1.6} />
              {xs.map((x, i) => (
                <line key={i} x1={x} y1={busY} x2={x} y2={ROW_Y[g] - 23} stroke="rgba(255,255,255,0.30)" strokeWidth={1.6} />
              ))}
            </g>
          );
        })}

        {rows.map((row, g) => {
          if (g > reached) return null;
          const lit = g <= reached;
          return (
            <g key={g}>
              <line x1={84} x2={W - 84} y1={ROW_Y[g] - 104} y2={ROW_Y[g] - 104} stroke={theme.accent} strokeWidth={1} opacity={0.14 + 0.12 * (0.5 + 0.5 * Math.sin(p * 12 + g))} />
              <text x={86} y={ROW_Y[g] - 66} fill={theme.inkDim} fontFamily={theme.type.mono} fontSize={17} letterSpacing={4}>
                {`G${g + 1}`}
              </text>
              {row.map((n, i) => {
                const carrier = i === CARRIER[g];
                const on = lit && carrier && found;
                const spin = 0.5 + 0.5 * Math.sin(p * 8 + i + g);
                // every node breathes: the tree must never sit still, or the
                // freeze detector (rightly) flags these long holds
                const breathe = 1 + 0.06 * Math.sin(p * 26 + i * 1.7 + g * 2.1);
                return (
                  <g key={i} transform={`translate(${n.x},${n.y}) scale(${breathe}) translate(${-n.x},${-n.y})`}>
                    <rect
                      x={n.x - 23}
                      y={n.y - 23}
                      width={46}
                      height={46}
                      rx={2}
                      fill={on ? theme.accent : 'rgba(5,7,10,0.92)'}
                      stroke={on ? theme.accent : 'rgba(205,235,248,0.66)'}
                      strokeWidth={2.2}
                      style={{filter: on ? `drop-shadow(0 0 18px ${theme.accentGlow})` : 'none'}}
                    />
                    {on ? (
                      <circle cx={n.x} cy={n.y} r={33 + spin * 8} fill="none" stroke={theme.accent} strokeWidth={1} opacity={0.42 - spin * 0.2} />
                    ) : null}
                  </g>
                );
              })}
            </g>
          );
        })}

        {/* a scan band sweeping the tree: continuous motion, reads as sequencing */}
        <g opacity={0.5}>
          <rect
            x={84}
            y={560 + ((p * 1.15) % 1) * 700}
            width={W - 168}
            height={2}
            fill={theme.accent}
            opacity={0.5}
          />
          <rect
            x={84}
            y={560 + ((p * 1.15) % 1) * 700 - 26}
            width={W - 168}
            height={26}
            fill={theme.accent}
            opacity={0.05}
          />
        </g>
        {/* the 1-in-2 readout, drawn as a bar that splits */}
        <g opacity={barIn(p)}>
          <text x={84} y={1392} fill={theme.accent} fontFamily={theme.type.mono} fontSize={19} letterSpacing={4}>
            50% INHERIT
          </text>
          <text x={W - 84} y={1392} textAnchor="end" fill={theme.inkDim} fontFamily={theme.type.mono} fontSize={19} letterSpacing={4}>
            50% DO NOT
          </text>
          <rect x={84} y={1408} width={(W - 168) * 0.5} height={9} fill={theme.accent} />
          <rect x={84 + (W - 168) * 0.5} y={1408} width={(W - 168) * 0.5} height={9} fill="rgba(205,235,248,0.26)" />
        </g>
      </svg>
      <Vignette />
      <FrameRules />
      <Ticker label={label} right="PEDIGREE / 3 GENS" />
      <HudPanel rows={hud} top={300} />
    </>
  );
};

const barIn = (p: number) => (p > 0.1 ? 1 : 0);

// ============================================================ 12. mortality
/**
 * The last number: 100%, and it never moves. A needle that climbs to full and
 * locks, a rising bar, and a struck "NO SURVIVORS" plate.
 */
export const MortalityPlate: React.FC<
  SceneProps & {label?: string; readout?: string; caption?: string; hud?: [string, string][]}
> = ({
  p,
  label = 'OUTCOME / FFI',
  readout = '100',
  caption = 'OF EVERY DIAGNOSIS',
  hud = [
    ['SURVIVORS', '0'],
    ['TREATMENT', 'NONE'],
    ['ONSET', 'MEAN AGE 51'],
  ],
}) => {
  // DS-004 holds the dial from the first frame: a fatality readout that is
  // still climbing when the shot ends reads as a data error, not tension.
  const climb = 1;
  const lock = true;
  const punch = 1 + 0.035 * Math.sin(p * 9);
  const flash = Math.max(0, 1 - p * 7);

  return (
    <>
      <Starfield p={p} n={44} speed={0.5} />
      {/* dial */}
      <svg width={W} height={H} style={{position: 'absolute', inset: 0}}>
        <g transform={`translate(${W / 2}, 700)`}>
          <circle r={252} fill="none" stroke="rgba(205,235,248,0.16)" strokeWidth={2} />
          <circle r={286} fill="none" stroke="rgba(205,235,248,0.09)" strokeWidth={1} />
          <circle r={332} fill="none" stroke="rgba(205,235,248,0.06)" strokeWidth={1} />
          {/* radial spokes + slow sweep so the plate is never static */}
          {Array.from({length: 24}, (_, i) => {
            const a = (i / 24) * Math.PI * 2 + p * 0.5;
            return (
              <line
                key={`sp${i}`}
                x1={Math.cos(a) * 108}
                y1={Math.sin(a) * 108}
                x2={Math.cos(a) * 150}
                y2={Math.sin(a) * 150}
                stroke="rgba(205,235,248,0.10)"
                strokeWidth={1}
              />
            );
          })}
          <g transform={`rotate(${(p * 360) % 360})`}>
            <path d={describeArc(0, 0, 318, -90, -58)} fill="none" stroke={theme.accent} strokeWidth={2} opacity={0.45} />
          </g>
          {Array.from({length: 60}, (_, i) => {
            const a = -Math.PI * 0.75 + (i / 59) * Math.PI * 1.5;
            const on = i / 59 <= climb;
            return (
              <line
                key={i}
                x1={Math.cos(a) * 214}
                y1={Math.sin(a) * 214}
                x2={Math.cos(a) * (i % 5 === 0 ? 190 : 200)}
                y2={Math.sin(a) * (i % 5 === 0 ? 190 : 200)}
                stroke={on ? theme.accent : 'rgba(255,255,255,0.22)'}
                strokeWidth={i % 5 === 0 ? 3 : 1.4}
              />
            );
          })}
          {/* the arc that fills */}
          <path
            d={describeArc(0, 0, 168, -135, -135 + 270 * climb)}
            fill="none"
            stroke={theme.accent}
            strokeWidth={9}
            strokeLinecap="round"
            style={{filter: `drop-shadow(0 0 22px ${theme.accentGlow})`}}
          />
          {/* needle */}
          <g transform={`rotate(${-135 + 270 * climb})`}>
            <line x1={0} y1={0} x2={158} y2={0} stroke={theme.ink} strokeWidth={4} strokeLinecap="round" />
            <circle r={11} fill={theme.ink} />
          </g>
        </g>
      </svg>
      <div
        style={{
          position: 'absolute',
          top: 566,
          left: 0,
          right: 0,
          textAlign: 'center',
          fontFamily: theme.type.shout,
          fontSize: 230,
          lineHeight: 1,
          color: theme.ink,
          textShadow: `0 0 110px ${theme.accentGlow}`,
          transform: `scale(${punch})`,
        }}
      >
        {Math.round(climb * 100)}
        <span style={{fontSize: 116, color: theme.accent}}>%</span>
      </div>
      <div
        style={{
          position: 'absolute',
          top: 812,
          left: 0,
          right: 0,
          textAlign: 'center',
          fontFamily: theme.type.mono,
          fontSize: 26,
          letterSpacing: 11,
          color: theme.accent,
        }}
      >
        {readout === '100' ? 'CASE FATALITY' : label}
      </div>
      <div
        style={{
          position: 'absolute',
          top: 890,
          left: 0,
          right: 0,
          textAlign: 'center',
          fontFamily: theme.type.ui,
          fontWeight: 700,
          fontSize: 42,
          letterSpacing: 6,
          color: 'rgba(255,255,255,0.72)',
        }}
      >
        {caption}
      </div>
      <div style={{position: 'absolute', inset: 0, background: '#fff', opacity: flash * 0.18}} />
      <Vignette />
      <FrameRules />
      <Ticker label={label} right="NO SURVIVORS" />
      <HudPanel rows={hud} top={1006} />
    </>
  );
};

/** SVG arc path for the dial sweep. */
function describeArc(cx: number, cy: number, r: number, a0: number, a1: number): string {
  const rad = (d: number) => (d * Math.PI) / 180;
  const x0 = cx + r * Math.cos(rad(a0));
  const y0 = cy + r * Math.sin(rad(a0));
  const x1 = cx + r * Math.cos(rad(a1));
  const y1 = cy + r * Math.sin(rad(a1));
  const large = Math.abs(a1 - a0) > 180 ? 1 : 0;
  return `M ${x0} ${y0} A ${r} ${r} 0 ${large} 1 ${x1} ${y1}`;
}

// ======================================================= 13. neutrino shower
/**
 * A single neutrino crosses an entire planet and lights a cone of Cherenkov
 * light in the last kilometre of water/ice. Used for DS-005.
 *
 * props:
 *   label   telemetry text, left
 *   depth   string for the right-hand readout ("-3,450 M")
 *   cone    show the expanding light cone (default true)
 *   impact  0..1 where along the track the interaction happens
 */
export const NeutrinoShower: React.FC<
  SceneProps & {label?: string; depth?: string; cone?: boolean; impact?: number}
> = ({p, frame, label = 'KM3NeT / ARCA', depth = '-3,450 M', cone = true, impact = 0.34}) => {
  const cam: Cam = {rot: [0.1 + p * 0.06, -0.35 + p * 0.5, 0], dist: 14.5, fov: 900};
  const draw = React.useCallback(
    (ctx: CanvasRenderingContext2D, f: number, t: number) => {
      const segs: Seg[] = [];

      // ---- detector: 8 vertical strings of optical modules
      const strings = 8;
      for (let i = 0; i < strings; i++) {
        const a = (i / strings) * Math.PI * 2 + 0.3;
        const rx = 5.6;
        const x = Math.cos(a) * rx;
        const z = Math.sin(a) * rx;
        const top = 7.2;
        segs.push({a: [x, -top, z], b: [x, top, z], c: 'rgba(140,215,235,0.55)', w: 1.5});
        for (let m = 0; m < 9; m++) {
          const y = -top + (m / 8) * top * 2;
          const lit = Math.max(0, 1 - Math.abs((y + 2.4) - t * 0.8) * 0.8);
          segs.push(...sphereSegs(0.30, 3, 4, lit > 0.28 ? theme.accent : 'rgba(150,220,235,0.35)', 1.0).map((s) => ({
            a: v3.add(s.a, [x, y, z]),
            b: v3.add(s.b, [x, y, z]),
            c: lit > 0.28 ? theme.accent : 'rgba(150,220,235,0.35)',
            w: 1.0,
            glow: lit > 0.28 ? 10 : 0,
          })));
        }
      }
      // seabed
      for (let i = 0; i < 26; i++) {
        const a0 = (i / 26) * Math.PI * 2;
        const a1 = ((i + 1) / 26) * Math.PI * 2;
        segs.push({a: [Math.cos(a0) * 9, -7.6, Math.sin(a0) * 9], b: [Math.cos(a1) * 9, -7.6, Math.sin(a1) * 9], c: 'rgba(90,150,175,0.22)', w: 1.0});
      }

      // ---- the track: nearly horizontal, crossing everything
      const u = p;
      const hitT = Math.min(1, u / Math.max(0.05, impact));
      const headX = -14 + hitT * 28;
      const headY = -2.4 + Math.sin(u * 2) * 0.14;
      segs.push({a: [-14, headY, 0.4], b: [headX, headY, 0.4], c: '#EAFBFF', w: 4.2, glow: 26});
      segs.push({a: [-14, headY + 0.18, 0.4], b: [headX, headY + 0.18, 0.4], c: theme.accent, w: 1.6, glow: 18});
      // trail sparkle behind the head
      for (let i = 0; i < 26; i++) {
        const x = -14 + ((i / 26) * (headX + 14));
        const j = (Math.sin(i * 12.9 + f * 0.6) * 0.5 + 0.5) * 0.9;
        segs.push({a: [x, headY + (j - 0.45) * 1.5, 0.4], b: [x + 0.12, headY + (j - 0.45) * 1.5, 0.4], c: theme.accent, w: 1.2, glow: 8});
      }

      // ---- Cherenkov cone, only after the interaction
      if (cone && p > impact) {
        const k = Math.min(1, (p - impact) / 0.35);
        const cx = -14 + impact * 28;
        const len = 3 + k * 15;
        const spread = 0.9 + k * 3.6;
        for (let i = 0; i < 16; i++) {
          const a = (i / 16) * Math.PI * 2;
          const tip: V3 = [cx + len, headY, 0.4];
          const rim: V3 = [cx, headY + Math.cos(a) * spread, 0.4 + Math.sin(a) * spread];
          segs.push({a: rim, b: tip, c: theme.accent, w: 1.0, glow: 9});
        }
        for (let i = 0; i < 12; i++) {
          const r = (i / 12) * spread;
          segs.push(...tubeSegs(ringPoints(18, Math.max(0.05, r), 0.04, i + 3, 0).map(([x, y, z]) => [x + cx, y + headY, z + 0.4] as V3), theme.accent, 1.0, 6));
        }
      }

      drawSegs(ctx, segs, cam, W, H, {accent: theme.accent});
    },
    [p, impact, cone]
  );

  return (
    <>
      <SceneBackdrop p={p} />
      <Starfield p={p} n={40} speed={0.25} />
      <Soft3D width={W} height={H} draw={draw} style={{position: 'absolute', inset: 0}} />
      <Vignette />
      <FrameRules />
      <Ticker label={label} right={depth} />
    </>
  );
};

// ==================================================== 14. nerve invasion
/**
 * The amoeba enters the nasal cavity, crosses the cribriform plate and runs
 * along the olfactory nerve into the brain. Used for DS-006.
 *
 * props:
 *   label      telemetry text
 *   invasion   0..1 how far the amoebae have travelled (driven by p if omitted)
 *   count      number of organisms (default 7)
 */
export const NerveInvasion: React.FC<SceneProps & {label?: string; invasion?: number; count?: number}> = ({
  p,
  label = 'OLFACTORY ROUTE',
  invasion,
  count = 9,
}) => {
  const k = Math.min(1, Math.max(0, invasion ?? p));
  const cam: Cam = {rot: [0.18 + p * 0.2, -0.55 + p * 0.9, 0], dist: 13.0, fov: 1000};

  const draw = React.useCallback(
    (ctx: CanvasRenderingContext2D, f: number, t: number) => {
      const segs: Seg[] = [];
      // cribriform plate: a sieve of bone the nerve passes through
      for (let i = 0; i < 9; i++) {
        const x = -6 + i * 1.5;
        segs.push({a: [x, 2.4, -3.2], b: [x, 2.4, 3.2], c: 'rgba(150,190,205,0.35)', w: 1.3});
        for (let j = 0; j < 5; j++) {
          const z = -3.2 + j * 1.6;
          segs.push(...tubeSegs(ringPoints(10, 0.26, 0.03, i * 7 + j, 0).map(([px, py, pz]) => [x + px, 2.4 + py, z + pz] as V3), 'rgba(120,170,190,0.30)', 1.0, 0));
        }
      }
      // olfactory nerve bundle: tapering filaments running up into the bulb
      const filaments = 9;
      for (let i = 0; i < filaments; i++) {
        const off = (i / (filaments - 1) - 0.5) * 5.2;
        const pts: V3[] = [];
        for (let s = 0; s <= 16; s++) {
          const u = s / 16;
          pts.push([
            off * (1 - u * 0.55) + Math.sin(u * 6 + i) * 0.16,
            -4.2 + u * 6.6,
            Math.cos(u * 5 + i * 1.7) * 0.55 * (1 - u * 0.4),
          ]);
        }
        segs.push(...tubeSegs(pts, 'rgba(140,205,225,0.42)', 1.2, 0));
      }
      // olfactory bulb: a swelling where the nerve meets the brain
      segs.push(...sphereSegs(2.5, 7, 10, 'rgba(160,220,240,0.45)', 1.2).map((s) => ({
        a: [s.a[0] - 0.4, s.a[1] + 4.4, s.a[2]] as V3,
        b: [s.b[0] - 0.4, s.b[1] + 4.4, s.b[2]] as V3,
        c: 'rgba(160,220,240,0.45)',
        w: 1.2,
      })));

      // the organisms: comma-shaped trophozoites crawling up the nerve
      for (let i = 0; i < count; i++) {
        const stagger = i / count;
        const u = Math.min(1, Math.max(0, k * 1.25 - stagger * 0.25));
        const off = (i / (count - 1) - 0.5) * 3.0;
        const y = -4.6 + u * 8.2;
        const x = off * (1 - u * 0.5) + Math.sin(t * 3 + i * 2) * 0.22;
        const z = Math.cos(t * 2 + i) * 0.7;
        const col = u > 0.55 ? '#FF6B4A' : theme.accent;
        // teardrop body
        const body = ringPoints(16, 0.72, 0.10, i + 5, 0).map(([px, py, pz], j) => {
          const a = (j / 14) * Math.PI * 2;
          const stretch = 1 + 0.8 * Math.cos(a);
          return [px * stretch + x, py + y, pz + z] as V3;
        });
        segs.push(...tubeSegs(body, col, 1.9, 12));
        // trailing flagellum wobble
        const fl: V3[] = [];
        for (let s = 0; s <= 6; s++) {
          const q = s / 6;
          fl.push([x - 0.4 - q * 0.9, y - 0.5 - q * 1.1 + Math.sin(t * 6 + s) * 0.14, z]);
        }
        segs.push(...tubeSegs(fl, col, 1.2, 8));
      }

      drawSegs(ctx, segs, cam, W, H, {accent: theme.accent});
    },
    [k, count]
  );

  return (
    <>
      <SceneBackdrop p={p} />
      <Starfield p={p} n={28} speed={0.18} />
      <Soft3D width={W} height={H} draw={draw} style={{position: 'absolute', inset: 0}} />
      <Vignette />
      <FrameRules />
      <Ticker label={label} right="CNS" />
    </>
  );
};

// ================================================== 15. wreck wake (star)
/**
 * A giant star with a small hot companion carving a wake through its outer
 * atmosphere: the star's disc visibly distorts as the companion passes.
 * Used for DS-007.
 *
 * props: label, r (star radius), sep (0..1 companion separation)
 */
export const StarWake: React.FC<SceneProps & {label?: string; r?: number; sep?: number}> = ({
  p,
  frame,
  label = 'BETELGEUSE / SIWARHA',
  r = 8.2,
  sep,
}) => {
  const separation = sep ?? 0.5 + 0.5 * Math.sin(p * Math.PI * 2);
  const cam: Cam = {rot: [0.42, p * 0.5 - 0.2, 0], dist: 23, fov: 1050};

  const draw = React.useCallback(
    (ctx: CanvasRenderingContext2D, f: number, t: number) => {
      const segs: Seg[] = [];
      // photosphere: latitude/longitude wireframe squashed by the companion
      const squash = 1 + 0.16 * Math.sin(p * Math.PI * 2) * separation;
      const base = sphereSegs(r, 13, 20, 'rgba(255,160,95,0.85)', 1.6);
      for (const s of base) {
        const dst = (q: V3): V3 => [q[0] * squash, q[1], q[2]];
        segs.push({a: dst(s.a), b: dst(s.b), c: s.c, w: s.w, glow: 7});
      }
      // convective granules: brighter mottling that drifts
      for (let i = 0; i < 46; i++) {
        const a = (i * 2.399) % (Math.PI * 2);
        const y = Math.sin(i * 1.7) * r * 0.86;
        const rr = Math.sqrt(Math.max(0, r * r - y * y)) * 0.92;
        const x = Math.cos(a + t * 0.14) * rr * squash;
        const z = Math.sin(a + t * 0.14) * rr;
        segs.push(...tubeSegs(ringPoints(8, 0.22 + (i % 4) * 0.12, 0.05, i, 0).map(([px, py, pz]) => [x + px, y + py, z + pz] as V3), 'rgba(255,215,160,0.55)', 0.9, 5));
      }
      // the companion: tiny, hot, blue-white, inside the envelope
      const ang = p * Math.PI * 2;
      const cd = r * (1.05 + 0.28 * separation);
      // an inclined ellipse with the crossing point held in front of the disc,
      // so the companion never disappears behind the photosphere mid-shot
      const cx = Math.cos(ang) * cd * squash;
      const cy = Math.sin(ang) * r * 0.5;
      const cz = r * 0.55 + Math.sin(ang) * r * 0.22;
      segs.push(...sphereSegs(0.62, 5, 7, '#DDF3FF', 1.8).map((s) => ({
        a: [s.a[0] + cx, s.a[1] + cy, s.a[2] * 0.4 + cz] as V3,
        b: [s.b[0] + cx, s.b[1] + cy, s.b[2] * 0.4 + cz] as V3,
        c: '#DDF3FF',
        w: 1.8,
        glow: 22,
      })));
      // hot spot: a tiny bright ring so the companion reads at phone size
      segs.push(...tubeSegs(ringPoints(18, 1.05, 0.05, 3, 0).map(([px, py, pz]) => [px + cx, py + cy, pz * 0.4 + cz] as V3), '#EAF9FF', 1.5, 26));
      // wake: an arc of disturbed gas trailing the companion
      for (let w = 0; w < 3; w++) {
        const pts: V3[] = [];
        for (let s = 0; s <= 22; s++) {
          const q = s / 22;
          const aa = ang - 0.18 - q * 1.7;
          const rr = r * (1.05 + 0.28 * separation) * (1 + w * 0.13);
          pts.push([Math.cos(aa) * rr * squash, Math.sin(aa) * r * 0.5, r * 0.55 + Math.sin(aa) * r * 0.22]);
        }
        segs.push(...tubeSegs(pts, `rgba(200,242,255,${0.55 - w * 0.13})`, 2.0, 14));
      }
      // outer atmosphere shell
      segs.push(...sphereSegs(r * 1.55, 9, 14, 'rgba(255,120,70,0.16)', 1.0));
      drawSegs(ctx, segs, cam, W, H, {accent: theme.accent});
    },
    [p, r, separation]
  );

  return (
    <>
      <SceneBackdrop p={p} />
      <Starfield p={p} n={60} speed={0.5} />
      <Soft3D width={W} height={H} draw={draw} style={{position: 'absolute', inset: 0}} />
      <Vignette />
      <FrameRules />
      <Ticker label={label} right="VLA + ALMA" />
    </>
  );
};
