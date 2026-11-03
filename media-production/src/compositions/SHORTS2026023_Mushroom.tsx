import React from 'react';
import {
  AbsoluteFill,
  Audio,
  Easing,
  interpolate,
  OffthreadVideo,
  Sequence,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import {CaptionTrack, EditorialEmphasis} from 'remotion-captions-kit';
import {
  captionEmphasis,
  captionPages,
  DURATION,
  editorialShots,
  narrationBeats,
  type EditorialShot,
} from '../data/shorts2026023Timeline';

const theme = {
  colors: {
    ink: '#050906',
    inkSoft: '#0b120d',
    paper: '#f7f4ea',
    muted: '#c7d0c3',
    lime: '#d8ff7e',
    limeSoft: '#a5cf59',
    cyan: '#91e6d4',
    amber: '#ffca72',
    danger: '#ff8b86',
    dangerSoft: '#561c1b',
    panel: 'rgba(5, 12, 8, 0.76)',
    panelHeavy: 'rgba(4, 8, 6, 0.90)',
    whiteDim: 'rgba(247, 244, 234, 0.74)',
    limeDim: 'rgba(216, 255, 126, 0.20)',
    grain: 'rgba(247, 244, 234, 0.10)',
    shadow: 'rgba(0, 0, 0, 0.88)',
  },
  eases: {
    soft: Easing.bezier(0.22, 1, 0.36, 1),
    snap: Easing.bezier(0.16, 1, 0.3, 1),
    exit: Easing.bezier(0.7, 0, 0.84, 0),
  },
  springs: {
    title: {damping: 15, stiffness: 165, mass: 0.68},
    card: {damping: 18, stiffness: 155, mass: 0.72},
  },
} as const;

const footage = {
  growth: staticFile('shorts023/footage/v2/growth-enhanced.mp4'),
  moss: staticFile('shorts023/footage/v2/moss-enhanced.mp4'),
  log: staticFile('shorts023/footage/v2/log-enhanced.mp4'),
};

const audio = {
  narration: staticFile('shorts023/audio/v2/narration-v2.m4a'),
  score: staticFile('shorts023/audio/v2/dark-pulse-score.wav'),
  whoosh: staticFile('shorts023/audio/v2/sfx-whoosh.wav'),
  throw: staticFile('shorts023/audio/v2/sfx-throw.wav'),
  hit: staticFile('shorts023/audio/v2/sfx-sub-hit.wav'),
  tick: staticFile('shorts023/audio/v2/sfx-tick.wav'),
};

const bounded = (frame: number, input: number[], output: number[], easing = theme.eases.soft) =>
  interpolate(frame, input, output, {
    easing,
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

const FontFaces: React.FC = () => (
  <style>{`
    @font-face {
      font-family: 'Shorts Space Grotesk';
      src: url('${staticFile('shorts023/fonts/space-grotesk-variable.woff2')}') format('woff2');
      font-weight: 300 700;
      font-style: normal;
      font-display: block;
    }
    @font-face {
      font-family: 'Shorts IBM Plex Mono';
      src: url('${staticFile('shorts023/fonts/ibm-plex-mono-500.woff2')}') format('woff2');
      font-weight: 500;
      font-style: normal;
      font-display: block;
    }
  `}</style>
);

const ClarityFinish: React.FC = () => {
  const frame = useCurrentFrame();
  const grainX = (frame * 17) % 7;
  const grainY = (frame * 31) % 9;
  return <>
    <AbsoluteFill style={{
      pointerEvents: 'none',
      background: 'linear-gradient(180deg, rgba(2, 7, 4, 0.40) 0%, transparent 34%, rgba(2, 7, 4, 0.08) 58%, rgba(2, 6, 4, 0.72) 100%)',
      mixBlendMode: 'multiply',
    }} />
    <AbsoluteFill style={{
      pointerEvents: 'none',
      background: 'radial-gradient(ellipse at 50% 46%, transparent 35%, rgba(0, 0, 0, 0.56) 100%)',
    }} />
    <AbsoluteFill style={{
      pointerEvents: 'none',
      opacity: 0.13,
      mixBlendMode: 'soft-light',
      backgroundImage: `radial-gradient(${theme.colors.grain} 0.8px, transparent 0.9px)`,
      backgroundSize: '3px 3px',
      backgroundPosition: `${grainX}px ${grainY}px`,
    }} />
  </>;
};

const FootageShot: React.FC<{shot: EditorialShot}> = ({shot}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const enter = spring({frame, fps, config: theme.springs.card});
  const scale = bounded(frame, [0, shot.duration], shot.zoom);
  const x = bounded(frame, [0, shot.duration], [0, shot.drift[0]]);
  const y = bounded(frame, [0, shot.duration], [0, shot.drift[1]]);
  const microX = Math.sin(frame * 0.29) * 1.6;
  const microY = Math.cos(frame * 0.23) * 1.3;
  const enterNudge = (1 - enter) * (shot.direction === 'left' ? 70 : -70);
  const edge = shot.direction === 'left'
    ? 'linear-gradient(90deg, rgba(216,255,126,0.16), transparent 25%)'
    : 'linear-gradient(270deg, rgba(216,255,126,0.16), transparent 25%)';

  return <AbsoluteFill style={{overflow: 'hidden', backgroundColor: theme.colors.ink}}>
    <OffthreadVideo
      src={footage[shot.source]}
      startFrom={shot.sourceStart}
      volume={0}
      style={{
        width: '100%',
        height: '100%',
        objectFit: 'cover',
        objectPosition: shot.position,
        filter: 'brightness(0.84) contrast(1.18) saturate(0.82) sepia(0.05)',
        transform: `translate3d(${x + microX + enterNudge}px, ${y + microY}px, 0) scale(${scale})`,
        transformOrigin: 'center center',
      }}
    />
    <AbsoluteFill style={{pointerEvents: 'none', background: edge, mixBlendMode: 'screen', opacity: 0.62}} />
  </AbsoluteFill>;
};

const CutImpact: React.FC<{direction: 'left' | 'right'}> = ({direction}) => {
  const frame = useCurrentFrame();
  const flash = bounded(frame, [0, 2, 7, 12], [0, 0.82, 0.18, 0], theme.eases.snap);
  const lineX = bounded(frame, [0, 10], [direction === 'left' ? -120 : 120, direction === 'left' ? 120 : -120], theme.eases.snap);
  return <AbsoluteFill style={{pointerEvents: 'none', opacity: flash}}>
    <div style={{position: 'absolute', inset: 0, background: 'rgba(216, 255, 126, 0.16)', mixBlendMode: 'screen'}} />
    <div style={{
      position: 'absolute', top: 0, bottom: 0, left: '50%', width: 10,
      background: theme.colors.lime,
      transform: `translateX(${lineX}px) skewX(-18deg)`,
      boxShadow: `0 0 50px ${theme.colors.lime}`,
    }} />
  </AbsoluteFill>;
};

const ContextLabel: React.FC = () => (
  <div style={{
    position: 'absolute', top: 54, right: 42,
    display: 'flex', alignItems: 'center', gap: 9,
    color: theme.colors.paper,
    fontFamily: 'Shorts IBM Plex Mono, monospace', fontWeight: 500,
    fontSize: 13, letterSpacing: 0.78,
    textShadow: `0 2px 9px ${theme.colors.shadow}`,
  }}>
    <span style={{width: 7, height: 7, borderRadius: 999, background: theme.colors.lime, boxShadow: `0 0 14px ${theme.colors.lime}`}} />
    GENERIC CONTEXT FOOTAGE
  </div>
);

const StoryKicker: React.FC = () => (
  <div style={{
    position: 'absolute', top: 54, left: 42,
    color: theme.colors.whiteDim,
    fontFamily: 'Shorts IBM Plex Mono, monospace', fontWeight: 500,
    fontSize: 14, letterSpacing: 1.05,
    textShadow: `0 2px 9px ${theme.colors.shadow}`,
  }}>FIELD NOTE // 023</div>
);

const PanelShell: React.FC<{duration: number; color?: string; children: React.ReactNode; align?: 'left' | 'center'}> = ({
  duration,
  color = theme.colors.lime,
  children,
  align = 'left',
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const progress = spring({frame, fps, config: theme.springs.card});
  const exit = bounded(frame, [Math.max(0, duration - 11), duration], [1, 0], theme.eases.exit);
  const y = (1 - progress) * 48;
  return <div style={{
    position: 'absolute', top: 282, left: 48, right: 48,
    opacity: progress * exit,
    transform: `translateY(${y}px) scale(${0.96 + 0.04 * progress})`,
    transformOrigin: align === 'left' ? 'left center' : 'center center',
    textAlign: align,
  }}>
    <div style={{
      display: 'inline-flex', alignItems: 'center', gap: 10,
      marginBottom: 15, padding: '8px 12px',
      border: `1px solid ${color}`,
      background: theme.colors.panelHeavy,
      color,
      fontFamily: 'Shorts IBM Plex Mono, monospace', fontWeight: 500,
      fontSize: 15, letterSpacing: 1.15,
    }}>
      <span style={{width: 8, height: 8, borderRadius: '50%', background: color, boxShadow: `0 0 16px ${color}`}} />
      EVIDENCE CHECK
    </div>
    {children}
  </div>;
};

const HookStrike: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const p = spring({frame, fps, config: theme.springs.title});
  const exit = bounded(frame, [66, 78], [1, 0], theme.eases.exit);
  return <div style={{position: 'absolute', top: 516, left: 45, right: 45, opacity: p * exit, transform: `translateY(${(1 - p) * 74}px) scale(${0.92 + p * 0.08})`}}>
    <div style={{fontFamily: 'Shorts IBM Plex Mono, monospace', fontSize: 18, letterSpacing: 2.4, color: theme.colors.muted, marginBottom: 10}}>REPORTS OF</div>
    <div style={{fontFamily: 'Shorts Space Grotesk, sans-serif', fontSize: 116, lineHeight: 0.84, fontWeight: 700, letterSpacing: -5, color: theme.colors.paper, textShadow: `0 8px 24px ${theme.colors.shadow}`}}>
      TINY <span style={{color: theme.colors.lime}}>PEOPLE?</span>
    </div>
    <div style={{marginTop: 22, height: 5, width: bounded(frame, [9, 33], [0, 318], theme.eases.snap), background: theme.colors.lime, boxShadow: `0 0 26px ${theme.colors.lime}`}} />
  </div>;
};

const DnaEvidence: React.FC = () => {
  const frame = useCurrentFrame();
  const line = bounded(frame, [16, 104], [0, 1], theme.eases.soft);
  const node = spring({frame: Math.max(0, frame - 55), fps: useVideoConfig().fps, config: theme.springs.card});
  return <PanelShell duration={180} color={theme.colors.cyan}>
    <div style={{padding: '22px 22px 18px', background: theme.colors.panel, borderLeft: `4px solid ${theme.colors.cyan}`}}>
      <div style={{fontFamily: 'Shorts Space Grotesk, sans-serif', color: theme.colors.paper, fontSize: 62, lineHeight: 0.9, fontWeight: 700, letterSpacing: -2.4}}>ONE DNA<br /><span style={{color: theme.colors.cyan}}>MATCH.</span></div>
      <div style={{position: 'relative', height: 98, marginTop: 21}}>
        <div style={{position: 'absolute', top: 50, left: 20, right: 20, height: 3, background: 'rgba(145, 230, 212, 0.25)'}} />
        <div style={{position: 'absolute', top: 50, left: 20, width: `calc(${line * 100}% - 40px)`, height: 3, background: theme.colors.cyan, boxShadow: `0 0 18px ${theme.colors.cyan}`}} />
        <div style={{position: 'absolute', top: 27, left: 7, color: theme.colors.paper, fontFamily: 'Shorts IBM Plex Mono, monospace', fontSize: 14, letterSpacing: 0.5}}>CHINA</div>
        <div style={{position: 'absolute', top: 27, right: 7, color: theme.colors.paper, fontFamily: 'Shorts IBM Plex Mono, monospace', fontSize: 14, letterSpacing: 0.5}}>PHILIPPINES</div>
        <div style={{position: 'absolute', top: 43, left: 12, width: 18, height: 18, borderRadius: 999, background: theme.colors.cyan, boxShadow: `0 0 20px ${theme.colors.cyan}`}} />
        <div style={{position: 'absolute', top: 43, right: 12, width: 18, height: 18, borderRadius: 999, background: theme.colors.cyan, opacity: node, transform: `scale(${0.4 + node * 0.6})`, boxShadow: `0 0 20px ${theme.colors.cyan}`}} />
      </div>
      <div style={{color: theme.colors.muted, fontFamily: 'Shorts Space Grotesk, sans-serif', fontSize: 23, lineHeight: 1.15, marginTop: 8}}>Reported mushrooms linked to <i>Lanmaoa asiatica</i>.</div>
    </div>
  </PanelShell>;
};

const PathwayEvidence: React.FC = () => {
  const frame = useCurrentFrame();
  const scan = bounded(frame, [4, 120], [-10, 104], theme.eases.soft);
  return <PanelShell duration={170} color={theme.colors.amber}>
    <div style={{padding: '22px 22px 20px', background: theme.colors.panel, borderLeft: `4px solid ${theme.colors.amber}`, overflow: 'hidden', position: 'relative'}}>
      <div style={{position: 'absolute', top: 0, bottom: 0, left: `${scan}%`, width: 4, background: theme.colors.amber, boxShadow: `0 0 34px ${theme.colors.amber}`}} />
      <div style={{fontFamily: 'Shorts IBM Plex Mono, monospace', color: theme.colors.amber, fontSize: 16, letterSpacing: 1.3, marginBottom: 13}}>GENOME MINING</div>
      <div style={{fontFamily: 'Shorts Space Grotesk, sans-serif', color: theme.colors.paper, fontSize: 58, lineHeight: 0.91, fontWeight: 700, letterSpacing: -2.2}}>NO KNOWN<br /><span style={{color: theme.colors.amber}}>PATHWAY.</span></div>
      <div style={{marginTop: 16, color: theme.colors.muted, fontFamily: 'Shorts Space Grotesk, sans-serif', fontSize: 23, lineHeight: 1.17}}>No canonical psilocybin or ibotenic-acid pathway.</div>
    </div>
  </PanelShell>;
};

const UnknownEvidence: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const q = spring({frame: Math.max(0, frame - 10), fps, config: theme.springs.title});
  return <PanelShell duration={154} color={theme.colors.lime} align="center">
    <div style={{padding: '18px 20px 21px', background: theme.colors.panel, borderTop: `1px solid ${theme.colors.lime}`, borderBottom: `1px solid ${theme.colors.lime}`}}>
      <div style={{fontFamily: 'Shorts IBM Plex Mono, monospace', color: theme.colors.muted, fontSize: 16, letterSpacing: 1.1}}>ACTIVE COMPOUND</div>
      <div style={{fontFamily: 'Shorts Space Grotesk, sans-serif', color: theme.colors.lime, fontSize: 190, fontWeight: 700, lineHeight: 0.75, transform: `scale(${0.58 + q * 0.42})`, textShadow: `0 0 54px ${theme.colors.lime}`}}>?</div>
      <div style={{fontFamily: 'Shorts Space Grotesk, sans-serif', color: theme.colors.paper, fontSize: 50, lineHeight: 0.95, fontWeight: 700, letterSpacing: -1.4}}>STILL UNKNOWN.</div>
    </div>
  </PanelShell>;
};

const CorrectionCard: React.FC = () => <PanelShell duration={94} color={theme.colors.lime}>
  <div style={{padding: '22px', background: theme.colors.panel, borderLeft: `4px solid ${theme.colors.lime}`}}>
    <div style={{fontFamily: 'Shorts Space Grotesk, sans-serif', color: theme.colors.paper, fontSize: 60, lineHeight: 0.91, fontWeight: 700, letterSpacing: -2.2}}>A LEAD.<br /><span style={{color: theme.colors.lime}}>NOT A DISCOVERY.</span></div>
  </div>
</PanelShell>;

const VerificationLimit: React.FC = () => <PanelShell duration={94} color={theme.colors.danger}>
  <div style={{padding: '21px 22px', background: 'rgba(42, 8, 8, 0.82)', borderLeft: `4px solid ${theme.colors.danger}`}}>
    <div style={{fontFamily: 'Shorts IBM Plex Mono, monospace', color: theme.colors.danger, fontSize: 15, letterSpacing: 1.3, marginBottom: 13}}>EVIDENCE LIMIT</div>
    <div style={{fontFamily: 'Shorts Space Grotesk, sans-serif', color: theme.colors.paper, fontSize: 49, lineHeight: 0.93, fontWeight: 700, letterSpacing: -1.8}}>PAPUA NEW GUINEA:<br /><span style={{color: theme.colors.danger}}>NOT DNA-VERIFIED.</span></div>
  </div>
</PanelShell>;

const SafetyCard: React.FC = () => <PanelShell duration={102} color={theme.colors.danger}>
  <div style={{padding: '21px 22px', background: theme.colors.panelHeavy, border: `1px solid ${theme.colors.danger}`}}>
    <div style={{fontFamily: 'Shorts IBM Plex Mono, monospace', color: theme.colors.danger, fontSize: 15, letterSpacing: 1.25, marginBottom: 12}}>SAFETY NOTE</div>
    <div style={{fontFamily: 'Shorts Space Grotesk, sans-serif', color: theme.colors.paper, fontSize: 63, lineHeight: 0.89, fontWeight: 700, letterSpacing: -2.3}}>DON'T TEST<br /><span style={{color: theme.colors.danger}}>WILD MUSHROOMS.</span></div>
  </div>
</PanelShell>;

const FinalPayoff: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const left = spring({frame, fps, config: theme.springs.card});
  const right = spring({frame: Math.max(0, frame - 8), fps, config: theme.springs.card});
  return <div style={{position: 'absolute', top: 310, left: 48, right: 48}}>
    <div style={{color: theme.colors.muted, fontFamily: 'Shorts IBM Plex Mono, monospace', fontSize: 16, letterSpacing: 1.2, marginBottom: 17}}>THE ACTUAL MYSTERY</div>
    <div style={{display: 'flex', flexDirection: 'column', gap: 13}}>
      <div style={{padding: '16px 18px', opacity: left, transform: `translateX(${(1 - left) * -58}px)`, background: theme.colors.panel, borderLeft: `4px solid ${theme.colors.cyan}`, color: theme.colors.paper, fontFamily: 'Shorts Space Grotesk, sans-serif', fontSize: 44, fontWeight: 650, letterSpacing: -1.2}}>SPECIES: <span style={{color: theme.colors.cyan}}>KNOWN</span></div>
      <div style={{padding: '16px 18px', opacity: right, transform: `translateX(${(1 - right) * 58}px)`, background: theme.colors.panelHeavy, borderLeft: `4px solid ${theme.colors.lime}`, color: theme.colors.paper, fontFamily: 'Shorts Space Grotesk, sans-serif', fontSize: 44, fontWeight: 650, letterSpacing: -1.2}}>MOLECULE: <span style={{color: theme.colors.lime}}>UNKNOWN</span></div>
    </div>
  </div>;
};

const CaptionLayer: React.FC = () => <CaptionTrack pages={captionPages}>
  {(page) => <EditorialEmphasis
    page={page}
    theme={{
      fontFamily: 'Shorts Space Grotesk, sans-serif',
      fontSize: 47,
      textColor: theme.colors.paper,
      activeColor: theme.colors.lime,
      position: 'bottom',
      edgeOffset: 0.17,
      paddingX: 0.095,
      maxWidth: 0.86,
    }}
    emphasis={captionEmphasis}
  />}
</CaptionTrack>;

const isDialogue = (frame: number) => narrationBeats.some(({start, end}) => frame >= Math.floor(start * 30) && frame < Math.ceil(end * 30));

const SoundDesign: React.FC = () => {
  const whooshHits = [42, 120, 216, 270, 390, 450, 570, 630, 750, 810, 930, 990, 1110, 1170];
  const throwHits = [42, 270, 450, 630, 810, 990, 1110];
  const subHits = [0, 270, 450, 630, 810, 990, 1110];
  const ticks = [301, 331, 361, 391, 668, 696, 724, 904];
  return <>
    <Audio src={audio.narration} volume={1.22} />
    <Audio src={audio.score} volume={(frame) => isDialogue(frame) ? 0.24 : 0.38} />
    {whooshHits.map((from) => <Sequence key={`whoosh-${from}`} from={Math.max(0, from - 5)} durationInFrames={28}><Audio src={audio.whoosh} volume={0.46} /></Sequence>)}
    {throwHits.map((from) => <Sequence key={`throw-${from}`} from={Math.max(0, from - 2)} durationInFrames={19}><Audio src={audio.throw} volume={0.34} /></Sequence>)}
    {subHits.map((from) => <Sequence key={`hit-${from}`} from={from} durationInFrames={32}><Audio src={audio.hit} volume={0.53} /></Sequence>)}
    {ticks.map((from) => <Sequence key={`tick-${from}`} from={from} durationInFrames={8}><Audio src={audio.tick} volume={0.33} /></Sequence>)}
  </>;
};

export const MushroomShort: React.FC = () => <AbsoluteFill style={{background: theme.colors.ink, overflow: 'hidden'}}>
  <FontFaces />
  {editorialShots.map((shot) => <Sequence key={`${shot.source}-${shot.from}`} from={shot.from} durationInFrames={shot.duration}><FootageShot shot={shot} /></Sequence>)}
  {editorialShots.filter((shot) => shot.from > 0).map((shot) => <Sequence key={`cut-${shot.from}`} from={shot.from} durationInFrames={13}><CutImpact direction={shot.direction} /></Sequence>)}
  <ClarityFinish />
  <StoryKicker />
  <ContextLabel />
  <Sequence from={4} durationInFrames={74}><HookStrike /></Sequence>
  <Sequence from={301} durationInFrames={175}><DnaEvidence /></Sequence>
  <Sequence from={477} durationInFrames={167}><PathwayEvidence /></Sequence>
  <Sequence from={645} durationInFrames={157}><UnknownEvidence /></Sequence>
  <Sequence from={803} durationInFrames={100}><CorrectionCard /></Sequence>
  <Sequence from={903} durationInFrames={92}><VerificationLimit /></Sequence>
  <Sequence from={995} durationInFrames={91}><SafetyCard /></Sequence>
  <Sequence from={1087} durationInFrames={143}><FinalPayoff /></Sequence>
  <CaptionLayer />
  <SoundDesign />
</AbsoluteFill>;

export const mushroomDurationInFrames = DURATION;
