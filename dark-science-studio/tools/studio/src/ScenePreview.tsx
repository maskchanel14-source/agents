/**
 * ScenePreview.tsx — renders ONE scene full-screen for 2 s so a new scene can
 * be eyeballed before it is wired into an episode. `--props='{"scene":"..."}'`
 * picks the scene; every field is passed straight through.
 */
import React from 'react';
import {AbsoluteFill} from 'remotion';
import {theme, W, H} from './brand/theme';
import {NeutrinoShower, NerveInvasion, StarWake, MirrorColony} from './scenes/SceneLibrary';

type Props = {scene?: string; props?: Record<string, unknown>};

export const ScenePreview: React.FC<Props> = ({scene = 'neutrino_shower', props = {}}) => {
  const p = 0.55;
  const base = {p, frame: 33, dur: 60, ...props} as any;
  let node: React.ReactNode = null;
  switch (scene) {
    case 'nerve_invasion':
      node = <NerveInvasion {...base} />;
      break;
    case 'star_wake':
      node = <StarWake {...base} />;
      break;
    case 'mirror_colony':
      node = <MirrorColony {...base} />;
      break;
    default:
      node = <NeutrinoShower {...base} />;
  }
  return <AbsoluteFill style={{background: theme.bg}}>{node}</AbsoluteFill>;
};
