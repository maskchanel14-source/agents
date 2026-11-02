import React, {useMemo} from 'react';
import {ThreeCanvas} from '@remotion/three';
import {interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import * as THREE from 'three';

const clamp = (value: number) => Math.max(0, Math.min(1, value));
const fade = (frame: number, from: number, to: number) =>
  interpolate(frame, [from, from + 14, to - 14, to], [0, 1, 1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

const SporeCloud: React.FC<{count?: number; tint?: string; intensity?: number}> = ({
  count = 58,
  tint = '#ffb16e',
  intensity = 1,
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const spores = useMemo(
    () =>
      Array.from({length: count}, (_, i) => {
        const a = i * 2.399963229728653;
        return {
          angle: a,
          radius: 0.5 + ((i * 17) % 100) / 100 * 3.7,
          height: ((i * 31) % 100) / 100 * 5 - 1.5,
          speed: 0.28 + ((i * 7) % 100) / 100 * 0.62,
          size: 0.018 + ((i * 13) % 100) / 100 * 0.04,
        };
      }),
    [count],
  );
  const t = frame / fps;
  return (
    <group>
      {spores.map((spore, i) => {
        const r = spore.radius + Math.sin(t * spore.speed + i) * 0.32 * intensity;
        const x = Math.cos(spore.angle + t * spore.speed * 0.5) * r;
        const z = Math.sin(spore.angle + t * spore.speed * 0.5) * r;
        const y = spore.height + Math.sin(t * 1.5 + i) * 0.32;
        return (
          <mesh key={i} position={[x, y, z]}>
            <sphereGeometry args={[spore.size * intensity, 10, 10]} />
            <meshStandardMaterial color={tint} emissive={tint} emissiveIntensity={1.2} transparent opacity={0.5} />
          </mesh>
        );
      })}
    </group>
  );
};

const Mushroom: React.FC<{scale?: number; glow?: number; rotation?: number}> = ({scale = 1, glow = 0.8, rotation = 0}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const breathing = 1 + Math.sin((frame / fps) * 1.9) * 0.018;
  return (
    <group scale={scale * breathing} rotation={[0, rotation, 0]} position={[0, -1.72, 0]}>
      <mesh position={[0, 1.42, 0]} castShadow>
        <cylinderGeometry args={[0.52, 0.68, 2.86, 32, 8]} />
        <meshStandardMaterial color="#d47a45" roughness={0.78} metalness={0.03} />
      </mesh>
      <mesh position={[0, 2.65, 0]} scale={[1.05, 0.34, 1.05]} castShadow>
        <sphereGeometry args={[1.82, 48, 32]} />
        <meshStandardMaterial color="#c83542" roughness={0.42} metalness={0.08} emissive="#5d101c" emissiveIntensity={glow * 0.20} />
      </mesh>
      {[[-0.65, 2.92, 1.5], [0.48, 3.01, 1.42], [0.95, 2.62, 1.14], [-0.98, 2.48, 1.13], [0.05, 3.22, 1.3]].map(([x, y, z], i) => (
        <mesh key={i} position={[x, y, z]} scale={[1, 0.44, 1]}>
          <sphereGeometry args={[0.15 + (i % 2) * 0.035, 14, 14]} />
          <meshStandardMaterial color="#ffe2b5" emissive="#ffbf75" emissiveIntensity={0.26} />
        </mesh>
      ))}
      <pointLight position={[0, 2.6, 1.2]} color="#ff7b55" intensity={glow * 18} distance={7} decay={2} />
    </group>
  );
};

const MiniFigure: React.FC<{index: number; phase: number; color?: string}> = ({index, phase, color = '#62e6ff'}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  const lane = index % 2 === 0 ? -1 : 1;
  const z = -0.5 + index * 0.56;
  const x = lane * (1.55 + Math.sin(t * 0.6 + index) * 0.22) + Math.sin(t * 2.5 + phase) * 0.1;
  const y = -0.56 + Math.abs(Math.sin(t * 4.1 + phase)) * 0.12;
  const walk = Math.sin(t * 6 + phase) * 0.52;
  return (
    <group position={[x, y, z]} rotation={[0, lane * -0.35, 0]} scale={0.38}>
      <mesh position={[0, 0.92, 0]}>
        <sphereGeometry args={[0.27, 20, 20]} />
        <meshStandardMaterial color="#ffd1ac" roughness={0.5} />
      </mesh>
      <mesh position={[0, 0.48, 0]}>
        <cylinderGeometry args={[0.2, 0.26, 0.55, 14]} />
        <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.18} />
      </mesh>
      <mesh position={[-0.1, 0.02, 0]} rotation={[walk, 0, 0]}>
        <cylinderGeometry args={[0.055, 0.07, 0.55, 8]} />
        <meshStandardMaterial color="#293452" />
      </mesh>
      <mesh position={[0.1, 0.02, 0]} rotation={[-walk, 0, 0]}>
        <cylinderGeometry args={[0.055, 0.07, 0.55, 8]} />
        <meshStandardMaterial color="#293452" />
      </mesh>
      <mesh position={[-0.27, 0.54, 0]} rotation={[0, 0, -walk * 0.8]}>
        <cylinderGeometry args={[0.04, 0.055, 0.48, 8]} />
        <meshStandardMaterial color="#ffd1ac" />
      </mesh>
      <mesh position={[0.27, 0.54, 0]} rotation={[0, 0, walk * 0.8]}>
        <cylinderGeometry args={[0.04, 0.055, 0.48, 8]} />
        <meshStandardMaterial color="#ffd1ac" />
      </mesh>
    </group>
  );
};

const DnaHelix: React.FC<{opacity: number}> = ({opacity}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  const nodes = useMemo(() => Array.from({length: 34}, (_, i) => i), []);
  return (
    <group position={[0, 0.55, 0]} rotation={[0.22, t * 0.26, 0]}>
      {nodes.map((i) => {
        const y = -3.1 + i * 0.19;
        const a = i * 0.55;
        const x1 = Math.cos(a) * 0.72;
        const z1 = Math.sin(a) * 0.72;
        const x2 = Math.cos(a + Math.PI) * 0.72;
        const z2 = Math.sin(a + Math.PI) * 0.72;
        const hue = i % 2 === 0 ? '#ff6b6b' : '#73d5ff';
        return (
          <group key={i}>
            <mesh position={[x1, y, z1]}>
              <sphereGeometry args={[0.095, 12, 12]} />
              <meshStandardMaterial color={hue} emissive={hue} emissiveIntensity={1.1} transparent opacity={opacity} />
            </mesh>
            <mesh position={[x2, y, z2]}>
              <sphereGeometry args={[0.095, 12, 12]} />
              <meshStandardMaterial color={hue} emissive={hue} emissiveIntensity={1.1} transparent opacity={opacity} />
            </mesh>
            {i % 3 === 0 ? (
              <mesh position={[0, y, 0]} rotation={[0, -a, Math.PI / 2]}>
                <cylinderGeometry args={[0.024, 0.024, 1.42, 8]} />
                <meshStandardMaterial color="#fff0bd" emissive="#ffcc70" emissiveIntensity={0.4} transparent opacity={opacity * 0.72} />
              </mesh>
            ) : null}
          </group>
        );
      })}
    </group>
  );
};

const MolecularLattice: React.FC<{unknown?: boolean}> = ({unknown = false}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  const atoms = useMemo(
    () =>
      Array.from({length: 22}, (_, i) => ({
        x: Math.sin(i * 5.17) * (1.3 + (i % 3) * 0.32),
        y: Math.cos(i * 2.31) * 2.2,
        z: Math.sin(i * 7.71) * 1.15,
        r: 0.13 + (i % 4) * 0.022,
      })),
    [],
  );
  return (
    <group rotation={[t * 0.18, t * 0.37, 0.08]} position={[0, 0.4, 0]}>
      {atoms.map((atom, i) => {
        const c = unknown ? (i % 3 === 0 ? '#f6c453' : '#805cff') : i % 2 === 0 ? '#66d7ff' : '#ff6d8a';
        return (
          <React.Fragment key={i}>
            <mesh position={[atom.x, atom.y, atom.z]}>
              <sphereGeometry args={[atom.r, 18, 18]} />
              <meshStandardMaterial color={c} emissive={c} emissiveIntensity={0.45} metalness={0.18} roughness={0.35} />
            </mesh>
            {i < atoms.length - 1 ? (
              <mesh position={[(atom.x + atoms[i + 1].x) / 2, (atom.y + atoms[i + 1].y) / 2, (atom.z + atoms[i + 1].z) / 2]} rotation={[0, i * 0.62, Math.PI / 2.4]}>
                <cylinderGeometry args={[0.025, 0.025, 0.95, 8]} />
                <meshStandardMaterial color="#e4d9ff" emissive="#7e68ff" emissiveIntensity={0.24} transparent opacity={0.68} />
              </mesh>
            ) : null}
          </React.Fragment>
        );
      })}
    </group>
  );
};

const Soil: React.FC = () => {
  const rocks = useMemo(() => Array.from({length: 26}, (_, i) => i), []);
  return (
    <group position={[0, -2.65, 0]}>
      <mesh rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
        <planeGeometry args={[22, 22, 24, 24]} />
        <meshStandardMaterial color="#120f19" roughness={1} />
      </mesh>
      {rocks.map((i) => {
        const a = i * 2.43;
        const r = 2.1 + (i % 5) * 0.46;
        return (
          <mesh key={i} position={[Math.cos(a) * r, 0.06, Math.sin(a) * r]} rotation={[i, a, 0.3]} scale={[0.16 + (i % 3) * 0.06, 0.07, 0.16 + (i % 4) * 0.05]}>
            <dodecahedronGeometry args={[1, 0]} />
            <meshStandardMaterial color={i % 2 === 0 ? '#33232a' : '#242635'} roughness={0.9} />
          </mesh>
        );
      })}
    </group>
  );
};

const QuestionMark: React.FC<{opacity: number}> = ({opacity}) => {
  return (
    <group position={[0, 0.2, 0]} scale={1.2}>
      <mesh position={[0, 0.7, 0]} rotation={[0, 0, -0.15]}>
        <torusGeometry args={[0.78, 0.17, 12, 40, Math.PI * 1.45]} />
        <meshStandardMaterial color="#fbd476" emissive="#e38739" emissiveIntensity={1.4} transparent opacity={opacity} />
      </mesh>
      <mesh position={[0.2, -0.12, 0]}>
        <cylinderGeometry args={[0.17, 0.17, 0.6, 16]} />
        <meshStandardMaterial color="#fbd476" emissive="#e38739" emissiveIntensity={1.4} transparent opacity={opacity} />
      </mesh>
      <mesh position={[0.2, -1.05, 0]}>
        <sphereGeometry args={[0.2, 18, 18]} />
        <meshStandardMaterial color="#fbd476" emissive="#e38739" emissiveIntensity={1.4} transparent opacity={opacity} />
      </mesh>
    </group>
  );
};

export const MushroomWorld: React.FC = () => {
  const frame = useCurrentFrame();
  const {width, height, fps} = useVideoConfig();
  const t = frame / fps;
  const visions = fade(frame, 0, 270);
  const dna = fade(frame, 250, 440);
  const reveal = fade(frame, 395, 610);
  const molecule = fade(frame, 540, 855);
  const warning = fade(frame, 910, 1070);
  const outro = fade(frame, 1040, 1230);
  const cameraZ = interpolate(frame, [0, 260, 590, 900, 1230], [9.1, 7.1, 8.0, 7.3, 10.5], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const cameraY = interpolate(frame, [0, 260, 590, 900, 1230], [0.3, 0.1, 0.4, 0.3, 1.2], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const capPop = spring({frame, fps, config: {damping: 15, stiffness: 70}});
  return (
    <ThreeCanvas width={width} height={height} camera={{position: [0, cameraY, cameraZ], rotation: [-Math.atan2(cameraY, cameraZ), 0, 0], fov: 44}} shadows>
      <color attach="background" args={[new THREE.Color('#07060e')]} />
      <fog attach="fog" args={['#07060e', 8, 19]} />
      <ambientLight intensity={0.38} color="#6670a8" />
      <directionalLight position={[4.5, 7, 4]} intensity={2.1} color="#ffd19d" castShadow />
      <pointLight position={[-4, 1.5, 3]} intensity={24} color="#5b5cff" distance={9} decay={2} />
      <pointLight position={[3, 2.2, -1]} intensity={18} color="#ff375f" distance={7} decay={2} />
      <Soil />
      <group rotation={[0, t * 0.12, 0]} scale={0.86 + capPop * 0.14}>
        <Mushroom scale={1.15} glow={0.9 + Math.sin(t * 2) * 0.18} rotation={t * 0.04} />
      </group>
      <group visible={visions > 0.01} scale={visions}>
        {[0, 1, 2, 3, 4].map((i) => <MiniFigure key={i} index={i} phase={i * 1.3} color={i % 2 === 0 ? '#61e6ff' : '#f76dd5'} />)}
      </group>
      {visions > 0.01 ? <SporeCloud tint="#ffd4a0" intensity={0.95} /> : null}
      {dna > 0.01 ? <DnaHelix opacity={dna} /> : null}
      {reveal > 0.01 ? <QuestionMark opacity={reveal} /> : null}
      {molecule > 0.01 ? <MolecularLattice unknown /> : null}
      {warning > 0.01 ? (
        <group scale={0.9 + Math.sin(t * 4) * 0.05} position={[0, 0.5, 0]}>
          <mesh rotation={[Math.PI / 2, 0, 0]}>
            <torusGeometry args={[2.5, 0.09, 16, 80]} />
            <meshStandardMaterial color="#ff3d58" emissive="#ff1f3c" emissiveIntensity={1.6} transparent opacity={warning} />
          </mesh>
          <mesh position={[0, 0.15, 0]} rotation={[0, 0, Math.PI / 4]}>
            <boxGeometry args={[0.18, 4.2, 0.18]} />
            <meshStandardMaterial color="#ff3d58" emissive="#ff1f3c" emissiveIntensity={1.4} transparent opacity={warning} />
          </mesh>
        </group>
      ) : null}
      {outro > 0.01 ? <QuestionMark opacity={outro} /> : null}
    </ThreeCanvas>
  );
};
