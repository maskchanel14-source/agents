import React from 'react';
import {Composition} from 'remotion';
import {H, W, FPS} from './brand/theme';
import {ShortComposition, TimelineProps} from './ShortComposition';
import {SmokeTest} from './SmokeTest';
import {ScenePreview} from './ScenePreview';

// Fonts: loaded locally via @fontsource so no network is needed at render time.
import '@fontsource/anton/400.css';
import '@fontsource/montserrat/800.css';
import '@fontsource/inter/400.css';
import '@fontsource/inter/600.css';
import '@fontsource/jetbrains-mono/400.css';

const fallback: TimelineProps = {
  shots: [{scene: 'mirror_colony', from: 0, to: 60, props: {}}],
  words: [],
  durationInFrames: 60,
};

export const Root: React.FC = () => (
  <>
    <Composition id="ScenePreview" component={ScenePreview} fps={30} width={W} height={H} durationInFrames={60} />
    <Composition id="SmokeTest" component={SmokeTest} fps={30} width={W} height={H} durationInFrames={90} />
    <Composition
      id="DarkScienceShort"
      component={ShortComposition}
      fps={FPS}
      width={W}
      height={H}
      defaultProps={fallback}
      // Duration is DATA: read it from props so renders/stills honour the timeline.
      calculateMetadata={({props}) => ({
        durationInFrames: (props as TimelineProps).durationInFrames ?? 60,
        fps: FPS,
        width: W,
        height: H,
      })}
    />
  </>
);
