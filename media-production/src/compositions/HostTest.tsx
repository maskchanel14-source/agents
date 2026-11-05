import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {Host, type Gesture} from '../host';

/** TEMP: character rig for iterating on src/host.tsx. Removed before delivery. */
export const HostTest: React.FC<{
  gesture: Gesture;
  mouth: number;
  brow: number;
}> = ({gesture, mouth, brow}) => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{backgroundColor: '#7C8794', alignItems: 'center'}}>
      <div style={{position: 'absolute', left: 140, top: 40, width: 800, height: 1200}}>
        <Host frame={frame} mouth={mouth} gesture={gesture} brow={brow} width={800} height={1200} />
      </div>
    </AbsoluteFill>
  );
};
