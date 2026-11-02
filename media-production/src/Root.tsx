import {Composition} from 'remotion';
import {MushroomShort} from './compositions/SHORTS2026023_Mushroom';

export const RemotionRoot: React.FC = () => (
  <Composition
    id="SHORTS-2026-023-Mushroom"
    component={MushroomShort}
    durationInFrames={1230}
    fps={30}
    width={1080}
    height={1920}
  />
);
