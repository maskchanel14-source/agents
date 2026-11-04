import {Composition} from 'remotion';
import {MushroomShort} from './compositions/SHORTS2026023_Mushroom';
import {Binance63B} from './compositions/Binance63B';
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
    {/* 67.0 s @ 30 fps — "The Twenty-Minute Heist" (Binance, 29 Oct 2026) */}
    <Composition
      id="SHORTS-2026-024-Binance63B"
      component={Binance63B}
      durationInFrames={DURATION_IN_FRAMES}
      fps={FPS}
      width={WIDTH}
      height={HEIGHT}
    />
  </>
);
