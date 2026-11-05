import {Composition} from 'remotion';
import {MushroomShort} from './compositions/SHORTS2026023_Mushroom';
import {Binance63B} from './compositions/Binance63B';
import {Binance63B2D} from './compositions/Binance63B2D';
import {HostTest} from './compositions/HostTest';
import {REV3_DURATION} from './data/shorts024Timeline';
import {DURATION_IN_FRAMES, FPS, HEIGHT, WIDTH} from './theme';

export const RemotionRoot: React.FC = () => (
  <>
    <Composition
      id="SHORTS-2026-023-Mushroom"
      component={MushroomShort}
      durationInFrames={1230}
      fps={30}
      width={1080}
      height={1920}
    />
    {/* 71.5 s @ 30 fps — "The Twenty-Minute Heist", revision 4 (2D explainer + host) */}
    <Composition
      id="SHORTS-2026-024-Binance63B"
      component={Binance63B2D}
      durationInFrames={REV3_DURATION}
      fps={FPS}
      width={WIDTH}
      height={HEIGHT}
    />

    {/* Authoring tool (not part of the film): character rig for tweaking src/host.tsx */}
    <Composition
      id="HostTest"
      component={HostTest}
      durationInFrames={120}
      fps={30}
      width={1080}
      height={1920}
      defaultProps={{gesture: 'idle', mouth: 0.1, brow: 0}}
    />
    {/* revision 2 master, kept renderable — semi-realist 3D */}
    <Composition
      id="SHORTS-2026-024-Binance63B-3D-rev2"
      component={Binance63B}
      durationInFrames={DURATION_IN_FRAMES}
      fps={FPS}
      width={WIDTH}
      height={HEIGHT}
    />
  </>
);
