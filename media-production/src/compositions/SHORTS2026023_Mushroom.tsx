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
import {captions} from '../data/shorts2026023Timeline';

const ease = Easing.bezier(0.22, 1, 0.36, 1);

const footage = {
  growth: staticFile('shorts023/footage/mushroom-growth-timelapse-1080p.mp4'),
  moss: staticFile('shorts023/footage/mushroom-moss-macro-hd.mp4'),
  log: staticFile('shorts023/footage/fungus-moss-log-macro-1080p.mp4'),
};

type FootageSource = keyof typeof footage;

type FootageShotProps = {
  source: FootageSource;
  startFrom?: number;
  endAt?: number;
  position?: string;
  zoom?: [number, number];
  drift?: [number, number];
  grade?: string;
  fadeOut?: boolean;
};

const FootageShot: React.FC<FootageShotProps> = ({
  source,
  startFrom = 0,
  endAt,
  position = '50% 50%',
  zoom = [1.06, 1.14],
  drift = [0, 0],
  grade = 'saturate(0.92) contrast(1.12) brightness(0.74)',
  fadeOut = true,
}) => {
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  const scale = interpolate(frame, [0, durationInFrames], zoom, {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: ease});
  const x = interpolate(frame, [0, durationInFrames], [0, drift[0]], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: ease});
  const y = interpolate(frame, [0, durationInFrames], [0, drift[1]], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: ease});
  const opacity = fadeOut
    ? interpolate(frame, [0, 8, durationInFrames - 10, durationInFrames], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})
    : 1;

  return <AbsoluteFill style={{overflow: 'hidden', opacity, backgroundColor: '#090d0b'}}>
    <OffthreadVideo
      src={footage[source]}
      startFrom={startFrom}
      endAt={endAt}
      volume={0}
      style={{
        width: '100%',
        height: '100%',
        objectFit: 'cover',
        objectPosition: position,
        filter: grade,
        transform: `translate(${x}px, ${y}px) scale(${scale})`,
      }}
    />
    <AbsoluteFill style={{pointerEvents: 'none', background: 'linear-gradient(180deg, rgba(3,8,7,0.74) 0%, rgba(3,6,5,0.02) 32%, rgba(2,5,5,0.08) 51%, rgba(2,4,4,0.88) 100%)'}} />
    <AbsoluteFill style={{pointerEvents: 'none', background: 'radial-gradient(ellipse at center, transparent 34%, rgba(0,0,0,0.48) 100%)'}} />
  </AbsoluteFill>;
};

const GenericFootageLabel: React.FC = () => (
  <div style={{
    position: 'absolute',
    top: 66,
    right: 48,
    padding: '10px 15px',
    border: '1px solid rgba(232,243,219,0.6)',
    borderRadius: 7,
    background: 'rgba(5,11,8,0.7)',
    color: '#edf6e7',
    fontFamily: 'Arial, sans-serif',
    fontWeight: 800,
    fontSize: 16,
    letterSpacing: 1.4,
  }}>GENERIC MUSHROOM FOOTAGE</div>
);

const FieldNote: React.FC<{children: React.ReactNode; color?: string}> = ({children, color = '#bfeaa2'}) => (
  <div style={{
    display: 'inline-flex',
    alignItems: 'center',
    gap: 10,
    padding: '10px 14px',
    background: 'rgba(4,10,7,0.72)',
    borderLeft: `4px solid ${color}`,
    color,
    fontFamily: 'Arial, sans-serif',
    fontWeight: 900,
    fontSize: 18,
    letterSpacing: 1.7,
  }}>{children}</div>
);

const CaptionLayer: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const cue = captions.find((item) => frame >= item.start && frame < item.end) ?? captions[captions.length - 1];
  const local = Math.max(0, frame - cue.start);
  const inSpring = spring({frame: local, fps, config: {damping: 15, stiffness: 140, mass: 0.72}});
  const out = interpolate(frame, [cue.end - 9, cue.end], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const words = cue.text.split(' ');

  return <div style={{position: 'absolute', left: 52, right: 52, bottom: 154, opacity: out, transform: `translateY(${(1 - inSpring) * 30}px)`}}>
    <div style={{
      padding: '18px 4px 8px',
      textAlign: 'center',
      color: '#fffdf4',
      fontFamily: 'Arial Black, Arial, sans-serif',
      fontWeight: 900,
      fontSize: cue.text.length > 48 ? 45 : 55,
      lineHeight: 1.04,
      letterSpacing: 0.2,
      textShadow: '0 3px 4px rgba(0,0,0,0.96), 0 12px 36px rgba(0,0,0,0.9)',
    }}>
      {words.map((word, index) => {
        const normalized = word.replace(/[.,—]/g, '');
        const highlight = cue.emphasis?.includes(normalized);
        return <span key={`${word}-${index}`} style={{color: highlight ? '#d8ff9a' : '#fffdf4'}}>{word}{' '}</span>;
      })}
    </div>
  </div>;
};

const DNAOverlay: React.FC = () => {
  const frame = useCurrentFrame();
  const line = interpolate(frame, [8, 95], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: ease});
  const opacity = interpolate(frame, [0, 10, 135, 150], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <div style={{position: 'absolute', top: 190, left: 50, right: 50, opacity}}>
    <FieldNote color="#9ee9ff">DNA IDENTIFICATION</FieldNote>
    <div style={{marginTop: 18, padding: '20px 22px', background: 'linear-gradient(100deg, rgba(4,18,19,0.78), rgba(4,18,19,0.22))', borderTop: '1px solid rgba(158,233,255,0.54)', borderBottom: '1px solid rgba(158,233,255,0.22)'}}>
      <div style={{fontFamily: 'Arial Black, Arial, sans-serif', fontSize: 45, color: '#f3fffe', lineHeight: 1.0, textShadow: '0 2px 8px #000'}}>TWO REGIONS.<br /><span style={{color: '#9ee9ff'}}>ONE SPECIES LINK.</span></div>
      <div style={{position: 'relative', height: 74, marginTop: 20, borderLeft: '2px solid rgba(158,233,255,0.55)', borderRight: '2px solid rgba(158,233,255,0.55)'}}>
        <div style={{position: 'absolute', top: 35, left: 0, height: 3, width: `${line * 100}%`, background: '#9ee9ff', boxShadow: '0 0 16px #9ee9ff'}} />
        <div style={{position: 'absolute', top: 8, left: 0, fontFamily: 'Arial, sans-serif', fontWeight: 800, fontSize: 16, letterSpacing: 1.1, color: '#eaffff'}}>YUNNAN, CHINA</div>
        <div style={{position: 'absolute', bottom: 1, right: 0, textAlign: 'right', fontFamily: 'Arial, sans-serif', fontWeight: 800, fontSize: 16, letterSpacing: 1.1, color: '#eaffff'}}>N. CORDILLERA, PHILIPPINES</div>
      </div>
    </div>
  </div>;
};

const PathwayOverlay: React.FC = () => {
  const frame = useCurrentFrame();
  const scan = interpolate(frame, [0, 135], [-12, 104], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <div style={{position: 'absolute', top: 196, left: 50, right: 50}}>
    <FieldNote color="#ffd381">GENOME MINING</FieldNote>
    <div style={{marginTop: 20, padding: '24px 22px', background: 'rgba(13,10,4,0.74)', border: '1px solid rgba(255,211,129,0.56)', overflow: 'hidden', position: 'relative'}}>
      <div style={{position: 'absolute', top: 0, bottom: 0, left: `${scan}%`, width: 4, background: '#ffe19a', boxShadow: '0 0 30px #ffe19a'}} />
      <div style={{fontFamily: 'Arial Black, Arial, sans-serif', color: '#fff9e8', fontSize: 43, lineHeight: 1.0}}>NO CANONICAL<br /><span style={{color: '#ffd381'}}>PSILOCYBIN OR IBOTENIC-ACID</span><br />PATHWAY DETECTED.</div>
      <div style={{marginTop: 16, color: '#e6dcc5', fontFamily: 'Arial, sans-serif', fontWeight: 700, fontSize: 21, lineHeight: 1.25}}>That does not identify the active molecule.</div>
    </div>
  </div>;
};

const SpeciesEvidenceOverlay: React.FC = () => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 12, 98, 114], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <div style={{position: 'absolute', top: 205, left: 50, right: 50, opacity}}>
    <FieldNote color="#ffd381">SPECIES EVIDENCE • DNA LINK</FieldNote>
    <div style={{marginTop: 18, padding: '22px', background: 'linear-gradient(105deg, rgba(31,23,5,0.8), rgba(8,15,8,0.44))', border: '1px solid rgba(255,211,129,0.5)'}}>
      <div style={{fontFamily: 'Arial Black, Arial, sans-serif', color: '#fff9ec', fontSize: 44, lineHeight: 1.0}}>CHINA + PHILIPPINES:<br /><span style={{color: '#ffe093'}}>DNA-LINKED TO<br /><i>LANMAOA ASIATICA.</i></span></div>
      <div style={{marginTop: 14, color: '#ede4cf', fontFamily: 'Arial, sans-serif', fontWeight: 700, fontSize: 20, lineHeight: 1.28}}>Background is generic mushroom footage, not the named species.</div>
    </div>
  </div>;
};

const UnverifiedOverlay: React.FC = () => (
  <div style={{position: 'absolute', top: 205, left: 50, right: 50}}>
    <FieldNote color="#ff9a9a">EVIDENCE LIMIT</FieldNote>
    <div style={{marginTop: 18, padding: '22px', background: 'rgba(31,5,8,0.78)', border: '1px solid rgba(255,135,143,0.58)', fontFamily: 'Arial Black, Arial, sans-serif', color: '#fff2f1', fontSize: 42, lineHeight: 1.02}}>PAPUA NEW GUINEA REPORTS<br /><span style={{color: '#ff9a9a'}}>NOT GENOMICALLY VERIFIED.</span></div>
  </div>
);

const SafetyOverlay: React.FC = () => (
  <div style={{position: 'absolute', top: 215, left: 50, right: 50}}>
    <FieldNote color="#ff8999">SAFETY, NOT A CHALLENGE</FieldNote>
    <div style={{marginTop: 18, padding: '24px 22px', background: 'rgba(32,4,9,0.83)', borderLeft: '7px solid #ff5571', boxShadow: '0 16px 40px rgba(0,0,0,0.35)'}}>
      <div style={{fontFamily: 'Arial Black, Arial, sans-serif', color: 'white', fontSize: 48, lineHeight: 0.98}}>DO NOT TEST IT.</div>
      <div style={{marginTop: 13, color: '#ffd9df', fontFamily: 'Arial, sans-serif', fontWeight: 800, fontSize: 25, lineHeight: 1.2}}>Wild mushrooms can poison. No tasting, no self-experiment.</div>
    </div>
  </div>
);

const EndingOverlay: React.FC = () => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [75, 145], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <div style={{position: 'absolute', top: 195, left: 50, right: 50, opacity}}>
    <FieldNote color="#d8ff9a">THE ACTUAL MYSTERY</FieldNote>
    <div style={{marginTop: 18, fontFamily: 'Arial Black, Arial, sans-serif', color: '#fffdf4', fontSize: 55, lineHeight: 0.96, textShadow: '0 3px 12px #000'}}>THE MOLECULE<br /><span style={{color: '#d8ff9a'}}>IS STILL UNKNOWN.</span></div>
  </div>;
};

const FootageTimeline: React.FC = () => (
  <>
    <Sequence from={0} durationInFrames={78}><FootageShot source="growth" startFrom={0} endAt={150} position="50% 68%" zoom={[1.12, 1.22]} drift={[-18, -8]} /></Sequence>
    <Sequence from={70} durationInFrames={200}><FootageShot source="moss" startFrom={20} endAt={620} position="52% 50%" zoom={[1.1, 1.2]} drift={[18, -12]} /></Sequence>
    <Sequence from={262} durationInFrames={158}><FootageShot source="log" startFrom={30} endAt={540} position="52% 50%" zoom={[1.14, 1.25]} drift={[-22, 4]} /></Sequence>
    <Sequence from={412} durationInFrames={168}><FootageShot source="growth" startFrom={300} endAt={800} position="50% 65%" zoom={[1.14, 1.25]} drift={[16, -16]} /></Sequence>
    <Sequence from={572} durationInFrames={136}><FootageShot source="moss" startFrom={210} endAt={610} position="50% 50%" zoom={[1.18, 1.26]} drift={[-20, 10]} /></Sequence>
    <Sequence from={700} durationInFrames={132}><FootageShot source="log" startFrom={100} endAt={480} position="50% 50%" zoom={[1.13, 1.22]} drift={[16, -8]} /></Sequence>
    <Sequence from={820} durationInFrames={122}><FootageShot source="moss" startFrom={190} endAt={560} position="50% 50%" zoom={[1.16, 1.25]} drift={[-14, 6]} /></Sequence>
    <Sequence from={934} durationInFrames={124}><FootageShot source="log" startFrom={90} endAt={460} position="50% 50%" zoom={[1.18, 1.28]} drift={[20, -8]} /></Sequence>
    <Sequence from={1048} durationInFrames={182}><FootageShot source="growth" startFrom={640} endAt={1230} position="50% 66%" zoom={[1.15, 1.29]} drift={[-16, -12]} fadeOut={false} /></Sequence>
  </>
);

export const MushroomShort: React.FC = () => {
  const frame = useCurrentFrame();
  return <AbsoluteFill style={{background: '#070b08', overflow: 'hidden'}}>
    <FootageTimeline />
    <GenericFootageLabel />
    <Sequence from={270} durationInFrames={150}><DNAOverlay /></Sequence>
    <Sequence from={420} durationInFrames={160}><PathwayOverlay /></Sequence>
    <Sequence from={828} durationInFrames={114}><SpeciesEvidenceOverlay /></Sequence>
    <Sequence from={905} durationInFrames={37}><UnverifiedOverlay /></Sequence>
    <Sequence from={942} durationInFrames={108}><SafetyOverlay /></Sequence>
    <Sequence from={1050} durationInFrames={180}><EndingOverlay /></Sequence>
    <CaptionLayer />
    <Audio src={staticFile('shorts023/audio/narration.mp3')} volume={1} />
    <Audio src={staticFile('shorts023/audio/ambient-bed.wav')} volume={0.18} />
    <Sequence from={264}><Audio src={staticFile('shorts023/audio/shimmer.wav')} volume={0.2} /></Sequence>
    <Sequence from={570}><Audio src={staticFile('shorts023/audio/impact.wav')} volume={0.24} /></Sequence>
    <Sequence from={936}><Audio src={staticFile('shorts023/audio/impact.wav')} volume={0.24} /></Sequence>
    <Sequence from={1145}><Audio src={staticFile('shorts023/audio/shimmer.wav')} volume={0.16} /></Sequence>
  </AbsoluteFill>;
};
