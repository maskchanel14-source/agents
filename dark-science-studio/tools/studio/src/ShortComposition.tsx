/**
 * ShortComposition.tsx — renders one video straight from timeline.json.
 *
 * Props come from build/<ID>/props.json:
 *   {durationInFrames, shots: [{scene, from, to, props}], words: [...], meta}
 *
 * All scene timing lives in data, never in code, so a retime is a JSON edit
 * plus a re-render.
 */
import React from 'react';
import {AbsoluteFill, Audio, Sequence, interpolate, staticFile, useCurrentFrame} from 'remotion';
import {theme, setAccent, W, H, FPS} from './brand/theme';
import {KineticCaptions, Word} from './captions/KineticCaptions';
import {
  CounterSlam,
  GlitchReveal,
  HandWall,
  HandedHelix,
  ImmuneSiege,
  MirrorColony,
  MisfoldChain,
  MortalityPlate,
  PedigreeTree,
  PhageStorm,
  Ribosome,
  SceneProps,
  ThalamusGrid,
} from './scenes/SceneLibrary';

export type Shot = {
  scene: string;
  from: number; // frames
  to: number;
  props?: Record<string, unknown>;
};

export type TimelineProps = {
  shots: Shot[];
  words: Word[];
  durationInFrames: number;
  mixFile?: string;
  /** per-video identity: accent colour, episode id, duration for the rail */
  meta?: {accent?: string; id?: string; durationS?: number};
};

/** Wraps a scene and injects {p, frame, dur}. */
const ShotRenderer: React.FC<{shot: Shot}> = ({shot}) => {
  const frame = useCurrentFrame();
  const dur = Math.max(1, shot.to - shot.from);
  const p = interpolate(frame, [0, dur], [0, 1], {extrapolateRight: 'clamp'});
  const sceneProps: SceneProps & Record<string, unknown> = {p, frame, dur, ...(shot.props ?? {})};

  switch (shot.scene) {
    case 'mirror_colony':
      return <MirrorColony {...(sceneProps as any)} />;
    case 'glitch_reveal':
      return <GlitchReveal {...(sceneProps as any)} />;
    case 'handed_helix':
      return <HandedHelix {...(sceneProps as any)} />;
    case 'immune_siege':
      return <ImmuneSiege {...(sceneProps as any)} />;
    case 'phage_storm':
      return <PhageStorm {...(sceneProps as any)} />;
    case 'ribosome':
      return <Ribosome {...(sceneProps as any)} />;
    case 'counter_slam':
      return <CounterSlam {...(sceneProps as any)} />;
    case 'hand_wall':
      return <HandWall {...(sceneProps as any)} />;
    case 'misfold_chain':
      return <MisfoldChain {...(sceneProps as any)} />;
    case 'thalamus_grid':
      return <ThalamusGrid {...(sceneProps as any)} />;
    case 'pedigree':
      return <PedigreeTree {...(sceneProps as any)} />;
    case 'mortality':
      return <MortalityPlate {...(sceneProps as any)} />;
    default:
      return <MirrorColony {...(sceneProps as any)} />;
  }
};

/**
 * HARD CUTS by default — a dissolve kills the cut energy and makes automatic
 * scene detection read zero cuts. Only an explicit `softCut` prop cross-fades.
 */
const ShotFade: React.FC<{shot: Shot; children: React.ReactNode}> = ({shot, children}) => {
  const frame = useCurrentFrame();
  const dur = Math.max(1, shot.to - shot.from);
  if (!shot.props?.softCut) return <AbsoluteFill>{children}</AbsoluteFill>;
  const a = interpolate(frame, [0, 6], [0, 1], {extrapolateRight: 'clamp'});
  return <AbsoluteFill style={{opacity: a}}>{children}</AbsoluteFill>;
};

export const ShortComposition: React.FC<TimelineProps> = ({shots, words, mixFile, meta}) => {
  // Apply the poster's accent before any scene renders. Rendering is
  // synchronous and single-pass per frame, so a module-level set is safe here.
  if (meta?.accent) setAccent(meta.accent);

  return (
    <AbsoluteFill style={{backgroundColor: theme.bg}}>
      {/* film grain, always on top of scenes but under captions */}
      <AbsoluteFill style={{backgroundColor: theme.bg}} />
      {shots.map((shot, i) => (
        <Sequence key={i} from={shot.from} durationInFrames={Math.max(1, shot.to - shot.from)} name={`${i}_${shot.scene}`}>
          <ShotFade shot={shot}>
            <ShotRenderer shot={shot} />
          </ShotFade>
        </Sequence>
      ))}

      <KineticCaptions words={words} from={0} to={1e9} />

      {/* progress rail */}
      <ProgressRail meta={meta} />
      {mixFile ? <Audio src={staticFile(mixFile)} /> : null}
    </AbsoluteFill>
  );
};

const ProgressRail: React.FC<{meta?: TimelineProps['meta']}> = ({meta}) => {
  const frame = useCurrentFrame();
  const totalS = meta?.durationS ?? 58.8;
  return (
    <>
      <div style={{position: 'absolute', bottom: 372, left: 64, right: 64, height: 2, background: 'rgba(255,255,255,0.14)'}} />
      <div
        style={{
          position: 'absolute',
          bottom: 372,
          left: 64,
          width: `${Math.min(1, frame / (totalS * FPS)) * (W - 128)}px`,
          height: 2,
          background: theme.accent,
          boxShadow: `0 0 12px ${theme.accentGlow}`,
        }}
      />
      <div
        style={{
          position: 'absolute',
          bottom: 330,
          left: 64,
          fontFamily: theme.type.mono,
          fontSize: 20,
          letterSpacing: 4,
          color: 'rgba(255,255,255,0.35)',
        }}
      >
        DARK SCIENCE · {meta?.id ?? 'DS-003'}
      </div>
    </>
  );
};
