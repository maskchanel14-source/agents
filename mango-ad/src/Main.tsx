/**
 * Main.tsx — the cut.
 *
 * Shot list is data, in one place, so a retime is an edit here and a re-render
 * — nothing else touches timing. 45 s at 30 fps = 1350 frames.
 */
import React from 'react';
import {AbsoluteFill, Sequence, Audio, staticFile, useCurrentFrame} from 'remotion';
import {C, W, H, FPS, clamp, easeOut} from './brand';
import {S1Orchard, S2Hero, S3Flesh, S4Numbers, S5Lineup, S6Pack, S7Slice, S8Water, S9End} from './Scenes';

type Shot = {name: string; from: number; to: number};

export const SHOTS: Shot[] = [
  {name: 'orchard', from: 0, to: 150}, // 0.0 – 5.0  establishing
  {name: 'hero', from: 150, to: 300}, // 5.0 – 10.0 fruit hero
  {name: 'flesh', from: 300, to: 450}, // 10.0 – 15.0 texture
  {name: 'numbers', from: 450, to: 660}, // 15.0 – 22.0 the data
  {name: 'lineup', from: 660, to: 840}, // 22.0 – 28.0 varieties
  {name: 'pack', from: 840, to: 1020}, // 28.0 – 34.0 supply chain
  {name: 'slice', from: 1020, to: 1170}, // 34.0 – 39.0 brix
  {name: 'water', from: 1170, to: 1260}, // 39.0 – 42.0 ready
  {name: 'end', from: 1260, to: 1365}, // 42.0 – 45.5 sign-off
];

export const TOTAL = SHOTS[SHOTS.length - 1].to;

const Render: React.FC<{name: string; p: number}> = ({name, p}) => {
  switch (name) {
    case 'orchard':
      return <S1Orchard p={p} />;
    case 'hero':
      return <S2Hero p={p} />;
    case 'flesh':
      return <S3Flesh p={p} />;
    case 'numbers':
      return <S4Numbers p={p} />;
    case 'lineup':
      return <S5Lineup p={p} />;
    case 'pack':
      return <S6Pack p={p} />;
    case 'slice':
      return <S7Slice p={p} />;
    case 'water':
      return <S8Water p={p} />;
    case 'end':
      return <S9End p={p} />;
    default:
      return null;
  }
};

/** Short dip-to-black between acts — 4 frames, never a dissolve. */
const Act: React.FC<{shot: Shot}> = ({shot}) => {
  const frame = useCurrentFrame();
  const dur = Math.max(1, shot.to - shot.from);
  const p = clamp(frame / dur);
  const dipIn = shot.from === 0 ? 0 : clamp(frame / 5);
  const dipOut = clamp((dur - frame) / 5);
  const black = Math.max(1 - dipIn, 1 - dipOut);
  return (
    <>
      <Render name={shot.name} p={p} />
      <AbsoluteFill style={{backgroundColor: '#000', opacity: black * 0.55}} />
    </>
  );
};

/** Thin progress hairline at the very bottom — "film", not "story". */
const Progress: React.FC = () => {
  const frame = useCurrentFrame();
  const w = (frame / TOTAL) * W;
  return (
    <>
      <div style={{position: 'absolute', bottom: 0, left: 0, width: W, height: 2, background: 'rgba(246,237,226,0.12)'}} />
      <div style={{position: 'absolute', bottom: 0, left: 0, width: w, height: 2, background: C.amber}} />
    </>
  );
};

export const MangoAd: React.FC = () => {
  return (
    <AbsoluteFill style={{backgroundColor: C.ink}}>
      {SHOTS.map((s, i) => (
        <Sequence key={i} from={s.from} durationInFrames={s.to - s.from} name={`${i + 1}_${s.name}`}>
          <Act shot={s} />
        </Sequence>
      ))}
      <Progress />
      <Audio src={staticFile('audio/mix.wav')} />
    </AbsoluteFill>
  );
};
