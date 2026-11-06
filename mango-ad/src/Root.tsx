import React from 'react';
import {Composition} from 'remotion';
import {W, H, FPS} from './brand';
import {MangoAd, TOTAL} from './Main';

import '@fontsource/playfair-display/400.css';
import '@fontsource/playfair-display/500.css';
import '@fontsource/playfair-display/500-italic.css';
import '@fontsource/playfair-display/600.css';
import '@fontsource/montserrat/700.css';
import '@fontsource/montserrat/800.css';
import '@fontsource/inter/400.css';
import '@fontsource/inter/500.css';
import '@fontsource/inter/600.css';
import '@fontsource/inter/700.css';

export const RemotionRoot: React.FC = () => (
  <Composition
    id="MangoAd"
    component={MangoAd}
    fps={FPS}
    width={W}
    height={H}
    durationInFrames={TOTAL}
  />
);
