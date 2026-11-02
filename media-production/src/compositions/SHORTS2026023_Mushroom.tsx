import React from 'react';
import {
  AbsoluteFill,
  Audio,
  Easing,
  Img,
  interpolate,
  Sequence,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import {captions, sceneForFrame} from '../data/shorts2026023Timeline';
import {MushroomWorld} from '../scenes/shorts023/MushroomWorld';

const ease = Easing.bezier(0.22, 1, 0.36, 1);

const useFade = (start: number, end: number) => {
  const frame = useCurrentFrame();
  return interpolate(frame, [start, start + 10, end - 10, end], [0, 1, 1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: ease,
  });
};

const TopRail: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const pulse = 0.55 + Math.sin(frame / fps * 2.8) * 0.2;
  return (
    <>
      <div style={{position: 'absolute', top: 70, left: 64, right: 64, display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
        <div style={{display: 'flex', gap: 14, alignItems: 'center'}}>
          <div style={{height: 14, width: 14, borderRadius: 20, background: '#ff4e70', boxShadow: `0 0 22px rgba(255,78,112,${pulse})`}} />
          <div style={{fontFamily: 'Arial, sans-serif', fontWeight: 800, fontSize: 22, letterSpacing: 4, color: '#f9eee5'}}>DARK SCIENCE</div>
        </div>
        <div style={{fontFamily: 'Arial, sans-serif', fontWeight: 700, fontSize: 18, letterSpacing: 2, color: '#c9c4d5'}}>2026 RESEARCH</div>
      </div>
      <div style={{position: 'absolute', top: 116, left: 64, right: 64, height: 2, background: 'linear-gradient(90deg, #ff4e70, rgba(255,78,112,0.12), transparent)'}} />
    </>
  );
};

const TruthTag: React.FC<{label: string; color?: string}> = ({label, color = '#f4bc63'}) => (
  <div style={{
    alignSelf: 'flex-start',
    padding: '12px 18px',
    background: 'rgba(9,7,17,0.72)',
    border: `1px solid ${color}`,
    borderRadius: 999,
    fontFamily: 'Arial, sans-serif',
    fontWeight: 900,
    letterSpacing: 1.35,
    fontSize: 19,
    color,
    boxShadow: `0 0 20px ${color}33`,
  }}>{label}</div>
);

const CaptionLayer: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const cue = captions.find((item) => frame >= item.start && frame < item.end) ?? captions[captions.length - 1];
  const local = Math.max(0, frame - cue.start);
  const inSpring = spring({frame: local, fps, config: {damping: 13, stiffness: 150, mass: 0.7}});
  const out = interpolate(frame, [cue.end - 10, cue.end], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const words = cue.text.split(' ');
  return (
    <div style={{position: 'absolute', left: 54, right: 54, bottom: 210, display: 'flex', justifyContent: 'center', opacity: out, transform: `translateY(${(1 - inSpring) * 42}px) scale(${0.92 + inSpring * 0.08})`}}>
      <div style={{
        maxWidth: 930,
        padding: '22px 28px 24px',
        borderRadius: 24,
        background: 'linear-gradient(140deg, rgba(9,9,18,0.92), rgba(18,12,32,0.72))',
        border: '1px solid rgba(250,238,226,0.18)',
        boxShadow: '0 18px 50px rgba(0,0,0,0.45)',
        textAlign: 'center',
        fontFamily: 'Arial Black, Arial, sans-serif',
        fontWeight: 900,
        color: '#fff8ef',
        fontSize: cue.text.length > 48 ? 47 : 56,
        lineHeight: 1.08,
        letterSpacing: 0.6,
      }}>
        {words.map((word, index) => {
          const normalized = word.replace(/[.,—]/g, '');
          const isEmphasis = cue.emphasis?.includes(normalized);
          return <span key={`${word}-${index}`} style={{color: isEmphasis ? '#ffc66e' : '#fff8ef', textShadow: isEmphasis ? '0 0 24px rgba(255,159,72,0.45)' : '0 4px 12px rgba(0,0,0,0.7)'}}>{word}{' '}</span>;
        })}
      </div>
    </div>
  );
};

const DNAInfo: React.FC = () => {
  const opacity = useFade(272, 450);
  if (opacity <= 0.01) return null;
  return <div style={{position: 'absolute', top: 215, left: 62, right: 62, opacity, display: 'flex', flexDirection: 'column', gap: 14}}>
    <TruthTag label="DNA IDENTIFICATION • TWO REGIONS" color="#75ddff" />
    <div style={{fontFamily: 'Arial, sans-serif', color: '#d9efff', fontWeight: 700, fontSize: 28, letterSpacing: 0.5, textShadow: '0 2px 10px #000'}}>Yunnan, China  +  Northern Cordillera, Philippines</div>
  </div>;
};

const ChemistryInfo: React.FC = () => {
  const opacity = useFade(570, 830);
  if (opacity <= 0.01) return null;
  return <div style={{position: 'absolute', top: 210, left: 62, right: 62, opacity, display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 16}}>
    <TruthTag label="WHAT THE STUDY FOUND" color="#f4c462" />
    <div style={{fontFamily: 'Arial Black, Arial, sans-serif', color: '#fff6e6', fontWeight: 900, fontSize: 48, lineHeight: 1.0, textShadow: '0 3px 14px #000'}}>NO KNOWN<br /><span style={{color: '#ff7888'}}>PATHWAY</span> DETECTED</div>
    <div style={{fontFamily: 'Arial, sans-serif', fontWeight: 700, color: '#d6d0df', fontSize: 25, maxWidth: 600, lineHeight: 1.24}}>Genome mining did not find canonical genes for psilocybin or ibotenic acid.</div>
  </div>;
};

const SpeciesPhoto: React.FC = () => {
  const opacity = useFade(828, 950);
  const frame = useCurrentFrame();
  const local = frame - 828;
  if (opacity <= 0.01) return null;
  const slide = interpolate(local, [0, 18], [58, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <AbsoluteFill style={{opacity, background: 'radial-gradient(circle at 70% 30%, #35213b 0%, #110d19 54%, #07060e 100%)'}}>
    <div style={{position: 'absolute', top: 210, left: 62, right: 62, display: 'flex', flexDirection: 'column', gap: 16, transform: `translateY(${slide}px)`}}>
      <TruthTag label="SPECIES PHOTO • NOT FOOTAGE" color="#ffd77c" />
      <div style={{fontFamily: 'Arial Black, Arial, sans-serif', color: 'white', fontSize: 56, lineHeight: 0.96, textShadow: '0 3px 14px #000'}}>WHAT DNA<br />CAN — AND<br />CANNOT — PROVE</div>
    </div>
    <div style={{position: 'absolute', left: 62, right: 62, top: 610, height: 535, borderRadius: 28, overflow: 'hidden', border: '1px solid rgba(255,221,141,0.58)', background: '#332219', boxShadow: '0 28px 60px rgba(0,0,0,0.42)'}}>
      <Img src={staticFile('shorts023/images/lanmaoa-asiatica-reference.jpg')} style={{width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${1.04 + local / 1600})`, filter: 'saturate(1.08) contrast(1.06)'}} />
      <div style={{position: 'absolute', left: 0, right: 0, bottom: 0, padding: '16px 20px', background: 'linear-gradient(transparent, rgba(0,0,0,0.82))', fontFamily: 'Arial, sans-serif', color: '#fff7e4', fontWeight: 800, fontSize: 18, letterSpacing: 1.25}}>LANMAOA ASIATICA • STILL REFERENCE</div>
    </div>
    <div style={{position: 'absolute', left: 62, right: 62, bottom: 430, fontFamily: 'Arial, sans-serif', fontWeight: 700, fontSize: 25, lineHeight: 1.3, color: '#f4eee7'}}>China + Philippines were linked to <i>Lanmaoa asiatica</i>.<br />Papua New Guinea reports were not genetically verified.</div>
  </AbsoluteFill>;
};

const WarningCard: React.FC = () => {
  const opacity = useFade(942, 1055);
  if (opacity <= 0.01) return null;
  return <div style={{position: 'absolute', top: 250, left: 62, right: 62, opacity}}>
    <TruthTag label="SAFETY, NOT A CHALLENGE" color="#ff6178" />
    <div style={{marginTop: 22, padding: '22px 24px', background: 'rgba(35,6,16,0.82)', borderLeft: '7px solid #ff415f', borderRadius: 16, fontFamily: 'Arial Black, Arial, sans-serif', color: 'white', fontSize: 45, lineHeight: 1.03, boxShadow: '0 14px 44px rgba(0,0,0,0.35)'}}>WILD MUSHROOMS<br />CAN POISON.</div>
    <div style={{marginTop: 15, maxWidth: 620, fontFamily: 'Arial, sans-serif', fontSize: 26, lineHeight: 1.25, fontWeight: 700, color: '#f4dce3'}}>No tasting. No self-experiment. Seek medical help after a suspected poisoning.</div>
  </div>;
};

const ProgressTrack: React.FC = () => {
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  const pct = Math.round((frame / durationInFrames) * 100);
  return <div style={{position: 'absolute', bottom: 110, left: 64, right: 64}}>
    <div style={{display: 'flex', justifyContent: 'space-between', fontFamily: 'Arial, sans-serif', fontSize: 15, letterSpacing: 2, color: '#beb8c7', marginBottom: 10}}><span>CASE FILE 023</span><span>{String(pct).padStart(2, '0')}%</span></div>
    <div style={{height: 5, borderRadius: 12, background: 'rgba(255,255,255,0.18)', overflow: 'hidden'}}><div style={{width: `${pct}%`, height: '100%', background: 'linear-gradient(90deg, #ff526b, #ffc66e, #75ddff)', boxShadow: '0 0 18px #ffbb72'}} /></div>
  </div>;
};

export const MushroomShort: React.FC = () => {
  const frame = useCurrentFrame();
  const scene = sceneForFrame(frame);
  const sceneTag = scene === 'evidence' ? null : '3D SCIENTIFIC VISUALIZATION';
  const flash = [270, 580, 828, 942, 1050].reduce((acc, cut) => Math.max(acc, interpolate(frame, [cut - 1, cut + 4], [0.35, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})), 0);
  return <AbsoluteFill style={{background: '#07060e', overflow: 'hidden'}}>
    <MushroomWorld />
    <AbsoluteFill style={{pointerEvents: 'none', background: 'radial-gradient(ellipse at center, transparent 36%, rgba(3,2,8,0.58) 100%)'}} />
    <SpeciesPhoto />
    <TopRail />
    {sceneTag ? <div style={{position: 'absolute', top: 150, right: 62}}><TruthTag label={sceneTag} color="#b5aeff" /></div> : null}
    <DNAInfo />
    <ChemistryInfo />
    <WarningCard />
    <CaptionLayer />
    <ProgressTrack />
    <AbsoluteFill style={{background: `rgba(255,235,210,${flash})`, pointerEvents: 'none', mixBlendMode: 'screen'}} />
    <Audio src={staticFile('shorts023/audio/narration.mp3')} volume={1} />
    <Audio src={staticFile('shorts023/audio/ambient-bed.wav')} volume={0.18} />
    <Sequence from={0}><Audio src={staticFile('shorts023/audio/riser.wav')} volume={0.28} /></Sequence>
    <Sequence from={264}><Audio src={staticFile('shorts023/audio/shimmer.wav')} volume={0.20} /></Sequence>
    <Sequence from={570}><Audio src={staticFile('shorts023/audio/impact.wav')} volume={0.26} /></Sequence>
    <Sequence from={820}><Audio src={staticFile('shorts023/audio/shimmer.wav')} volume={0.20} /></Sequence>
    <Sequence from={936}><Audio src={staticFile('shorts023/audio/impact.wav')} volume={0.26} /></Sequence>
    <Sequence from={1145}><Audio src={staticFile('shorts023/audio/shimmer.wav')} volume={0.16} /></Sequence>
  </AbsoluteFill>;
};
