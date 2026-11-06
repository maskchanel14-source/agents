/**
 * SmokeTest.tsx — 3 s 1080x1920 render gate: spinning 3D wireframe sphere,
 * a caption, and a sine-tone track. Rendered after any environment rebuild.
 */
import React from 'react';
import {AbsoluteFill, Audio, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {theme, W, H} from './brand/theme';
import {Soft3D, sphereSegs, drawSegs, Cam} from './fx/Soft3D';

const SEGS = sphereSegs(6.2, 14, 20, undefined, 1.6);

export const SmokeTest: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;

  return (
    <AbsoluteFill style={{background: theme.bg}}>
      <Soft3D
        width={W}
        height={H}
        style={{position: 'absolute'}}
        draw={(ctx, f, tt) => {
          const cam: Cam = {rot: [0.22 + Math.sin(tt) * 0.1, tt * 1.4, 0], dist: 16.5, fov: 900};
          drawSegs(ctx, SEGS, cam, W, H, {accent: theme.accent, baseAlpha: 0.9});
        }}
      />
      <div
        style={{
          position: 'absolute',
          top: H * 0.62,
          width: '100%',
          textAlign: 'center',
          fontFamily: theme.type.shout,
          fontSize: 96,
          letterSpacing: 2,
          color: '#fff',
        }}
      >
        SMOKE TEST
      </div>
      <Audio src={staticFile('audio/smoke.wav')} />
    </AbsoluteFill>
  );
};
