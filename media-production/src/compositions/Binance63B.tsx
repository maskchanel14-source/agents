import React, {useLayoutEffect, useMemo, useRef} from 'react';
import {
  AbsoluteFill,
  Easing,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import {ThreeCanvas} from '@remotion/three';
import {LensBlur} from '../lens';
import {SkyEnvironment} from '../env';
import {
  ACESFilmicToneMapping,
  Color,
  CylinderGeometry,
  InstancedMesh,
  Object3D,
  PerspectiveCamera,
} from 'three';
import {useThree} from '@react-three/fiber';

import {getCameraState} from '../camera';
import {shotAt, shotProgress, SHOTS, type Shot} from '../story';
import {Character, type CharacterKey} from '../characters';
import {facadeFor, getMaterials, type MaterialLibrary} from '../materials';
import {
  BRIDGE_LANES,
  CLOCK_TOWER,
  COIN_COUNT,
  coinTransform,
  DEV_TOWER,
  TOWN_BUILDINGS,
  VAULT,
} from '../world';
import {
  ATMOSPHERE,
  CAMERA,
  GRADE,
  HEIGHT,
  LENS,
  LIGHT,
  PALETTE,
  lensPxForAperture,
} from '../theme';

/* ------------------------------------------------------------------ fonts */
const FONTS = `
@font-face {
  font-family: 'Shorts Space Grotesk';
  src: url('${staticFile('shorts023/fonts/space-grotesk-variable.woff2')}') format('woff2');
  font-weight: 300 800; font-display: block;
}
@font-face {
  font-family: 'Shorts IBM Plex Mono';
  src: url('${staticFile('shorts023/fonts/ibm-plex-mono-500.woff2')}') format('woff2');
  font-weight: 500; font-display: block;
}`;

const DISPLAY = "'Shorts Space Grotesk', system-ui, sans-serif";
const MONO = "'Shorts IBM Plex Mono', ui-monospace, monospace";

/* --------------------------------------------------- renderer settings */
/**
 * Tone mapping has to be set on the renderer instance — R3F passes the `gl`
 * object straight to the WebGLRenderer constructor, which ignores it.
 *
 * ACES filmic is the whole reason the highlights roll off instead of clipping;
 * it is the single biggest difference between a CG-looking render and a
 * photographic one.
 */
const RendererSettings: React.FC<{exposure: number}> = ({exposure}) => {
  const gl = useThree((s) => s.gl);
  gl.toneMapping = ACESFilmicToneMapping;
  gl.toneMappingExposure = exposure;
  return null;
};

/* --------------------------------------------------------------- camera */
const CameraRig: React.FC<{
  frame: number;
  cameraOverride?: [number, number, number];
  lookOverride?: [number, number, number];
}> = ({frame, cameraOverride, lookOverride}) => {
  const camera = useThree((s) => s.camera) as PerspectiveCamera;
  const {position, lookAt} = getCameraState(frame);
  const p = cameraOverride ?? [position.x, position.y, position.z];
  const l = lookOverride ?? [lookAt.x, lookAt.y, lookAt.z];
  camera.position.set(p[0], p[1], p[2]);
  camera.lookAt(l[0], l[1], l[2]);
  camera.updateProjectionMatrix();
  return null;
};

/* ------------------------------------------------------------ street kit */
/** Lamp posts. Emissive bulbs only — no point lights, they are too expensive
 *  under software GL and the glow reads the same at this framing. */
const LAMP_POSTS: Array<[number, number]> = [
  [-9, 8], [-9, -6], [10, 9], [10, -8],
  [24, 4], [24, -10], [-24, 6], [-24, -3],
];

const StreetKit: React.FC = () => {
  const lib = getMaterials();
  const postGeo = useMemo(() => new CylinderGeometry(0.07, 0.09, 5.2, 10), []);
  const armGeo = useMemo(() => new CylinderGeometry(0.055, 0.055, 0.9, 8), []);
  const bulbGeo = useMemo(() => new CylinderGeometry(0.20, 0.13, 0.30, 12), []);
  return (
    <group>
      {LAMP_POSTS.map(([x, z], i) => (
        <group key={`lamp${i}`} position={[x, 0, z]}>
          <mesh geometry={postGeo} position={[0, 2.6, 0]} castShadow material={lib.steel} />
          <mesh
            geometry={armGeo}
            position={[0.42, 5.15, 0]}
            rotation={[0, 0, Math.PI / 2]}
            castShadow
            material={lib.steel}
          />
          <mesh geometry={bulbGeo} position={[0.86, 5.02, 0]} material={lib.glassLit} />
        </group>
      ))}
    </group>
  );
};

/* ----------------------------------------------------------------- town */
const Town: React.FC = () => {
  const lib = getMaterials();
  return (
    <group>
      {TOWN_BUILDINGS.map((b, i) => {
        const [w, h, d] = b.size;
        const corniceY = h / 2 + b.cornice / 2;
        return (
          <group key={b.key} position={b.pos} rotation={[0, b.rot, 0]}>
            <mesh castShadow receiveShadow material={facadeFor(lib, b.facade, w, h)}>
              <boxGeometry args={b.size} />
            </mesh>

            {/* cornice — the one detail that stops a box reading as a box */}
            <mesh
              position={[0, corniceY, 0]}
              castShadow
              receiveShadow
              material={lib.stone}
            >
              <boxGeometry args={[w + 0.34, b.cornice, d + 0.34]} />
            </mesh>

            {b.roof === 'gable' ? (
              // triangular prism: 3-sided cylinder laid on its side
              <mesh
                position={[0, h / 2 + b.cornice + w * 0.31, 0]}
                rotation={[-Math.PI / 2, 0, 0]}
                castShadow
                material={lib.roof}
              >
                <cylinderGeometry args={[w * 0.62, w * 0.62, d * 1.06, 3]} />
              </mesh>
            ) : null}

            {b.roof === 'tower' ? (
              <mesh
                position={[0, h / 2 + b.cornice + 1.7, 0]}
                rotation={[0, Math.PI / 4, 0]}
                castShadow
                material={lib.brass}
              >
                <coneGeometry args={[w * 0.80, 3.4, 4]} />
              </mesh>
            ) : null}
          </group>
        );
      })}
    </group>
  );
};

/* ------------------------------------------------------------- landmarks */
const Vault: React.FC = () => {
  const lib = getMaterials();
  const [bw, bh, bd] = VAULT.body;
  return (
    <group position={VAULT.pos}>
      {/* plaza */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.02, 0]} receiveShadow material={lib.stone}>
        <circleGeometry args={[13, 48]} />
      </mesh>
      {/* steps */}
      <mesh position={[0, 0.3, 6.4]} castShadow receiveShadow material={lib.concrete}>
        <boxGeometry args={[7, 0.6, 2.6]} />
      </mesh>
      <mesh position={[0, 0.15, 7.9]} castShadow receiveShadow material={lib.concrete}>
        <boxGeometry args={[7.6, 0.3, 0.7]} />
      </mesh>
      {/* podium + body */}
      <mesh position={[0, 1.1, 0]} castShadow receiveShadow material={lib.concrete}>
        <boxGeometry args={[bw + 1.2, 2.2, bd + 1.2]} />
      </mesh>
      <mesh position={[0, bh / 2 + 1.4, 0]} castShadow receiveShadow
        material={facadeFor(lib, 4, bw, bh)}>
        <boxGeometry args={[bw, bh, bd]} />
      </mesh>
      {/* cornice */}
      <mesh position={[0, bh + 1.9, 0]} castShadow receiveShadow material={lib.stone}>
        <boxGeometry args={[bw + 1.0, 1.0, bd + 1.0]} />
      </mesh>
      {/* copper pyramid */}
      <mesh position={[0, bh + 4.6, 0]} rotation={[0, Math.PI / 4, 0]} castShadow material={lib.brass}>
        <coneGeometry args={[bw * 0.86, 4.6, 4]} />
      </mesh>

      {/* the round vault door — brass, with spokes */}
      <group position={[0, 4.0, bd / 2 + 0.18]}>
        <mesh rotation={[Math.PI / 2, 0, 0]} castShadow receiveShadow material={lib.brass}>
          <cylinderGeometry args={[2.55, 2.55, 0.75, 40]} />
        </mesh>
        <mesh rotation={[Math.PI / 2, 0, 0]} position={[0, 0, 0.40]} material={lib.steel}>
          <cylinderGeometry args={[2.05, 2.05, 0.10, 36]} />
        </mesh>
        {[0, 1, 2, 3].map((k) => (
          <mesh
            key={k}
            position={[0, 0, 0.46]}
            rotation={[0, 0, (k * Math.PI) / 4]}
            material={lib.steel}
          >
            <boxGeometry args={[3.7, 0.16, 0.12]} />
          </mesh>
        ))}
        <mesh rotation={[Math.PI / 2, 0, 0]} position={[0, 0, 0.52]} castShadow material={lib.brass}>
          <cylinderGeometry args={[0.62, 0.62, 0.22, 24]} />
        </mesh>
      </group>
    </group>
  );
};

const ClockTower: React.FC = () => {
  const lib = getMaterials();
  // 20:05 → hour hand at 242.5°, minute hand at 30° (clockwise from 12).
  const hour = ((8 + 5 / 60) / 12) * Math.PI * 2;
  const minute = (5 / 60) * Math.PI * 2;
  const [bw, bh, bd] = CLOCK_TOWER.body;
  return (
    <group position={CLOCK_TOWER.pos}>
      <mesh position={[0, bh / 2, 0]} castShadow receiveShadow
        material={facadeFor(lib, 2, bw, bh)}>
        <boxGeometry args={CLOCK_TOWER.body} />
      </mesh>
      <mesh position={[0, bh + 0.5, 0]} castShadow receiveShadow material={lib.stone}>
        <boxGeometry args={[bw + 0.8, 1.0, bd + 0.8]} />
      </mesh>
      <mesh position={[0, bh + 3.6, 0]} rotation={[0, Math.PI / 4, 0]} castShadow material={lib.brass}>
        <coneGeometry args={[bw * 0.82, 5.2, 4]} />
      </mesh>
      <group position={[0, CLOCK_TOWER.faceY, bd / 2 + 0.06]}>
        <mesh material={lib.brass}>
          <cylinderGeometry args={[CLOCK_TOWER.faceR + 0.22, CLOCK_TOWER.faceR + 0.22, 0.16, 32]} />
        </mesh>
        <mesh position={[0, 0, 0.10]} material={lib.glassLit}>
          <circleGeometry args={[CLOCK_TOWER.faceR, 40]} />
        </mesh>
        <mesh position={[0, 0, 0.13]} rotation={[0, 0, -hour]} material={lib.shoe}>
          <boxGeometry args={[0.14, 0.95, 0.05]} />
        </mesh>
        <mesh position={[0, 0, 0.13]} rotation={[0, 0, -minute]} material={lib.shoe}>
          <boxGeometry args={[0.11, 1.38, 0.05]} />
        </mesh>
      </group>
    </group>
  );
};

/**
 * The DevOps tower: a glass curtain wall over a concrete core, with one lit
 * window near the top. That window is the whole attack.
 */
const DevTower: React.FC<{frame: number}> = ({frame}) => {
  const lib = getMaterials();
  const glow = 0.55 + 0.12 * Math.sin((frame / 30) * 3.1);
  const [bw, bh, bd] = DEV_TOWER.body;
  const [ww, wh] = DEV_TOWER.windowSize;
  const faceZ = bd / 2 + 0.06;
  const bands = Math.floor(bh / 2.1);
  return (
    <group position={DEV_TOWER.pos}>
      {/* core */}
      <mesh position={[0, bh / 2, 0]} castShadow receiveShadow material={lib.concrete}>
        <boxGeometry args={[bw - 0.35, bh, bd - 0.35]} />
      </mesh>
      {/* curtain wall */}
      <mesh position={[0, bh / 2, 0]} castShadow receiveShadow material={lib.glass}>
        <boxGeometry args={[bw, bh, bd]} />
      </mesh>
      {/* mullions / slab bands */}
      {Array.from({length: bands}, (_, k) => (
        <mesh
          key={k}
          position={[0, 1.2 + k * 2.1, 0]}
          castShadow
          material={lib.steel}
        >
          <boxGeometry args={[bw + 0.10, 0.26, bd + 0.10]} />
        </mesh>
      ))}
      {/* crown */}
      <mesh position={[0, bh + 0.7, 0]} castShadow material={lib.steel}>
        <boxGeometry args={[bw + 0.5, 1.4, bd + 0.5]} />
      </mesh>

      {/* the lit window */}
      <mesh position={[0, DEV_TOWER.windowY, faceZ]} material={lib.glassLit}>
        <planeGeometry args={[ww, wh]} />
      </mesh>
      <pointLight
        position={[0, DEV_TOWER.windowY, faceZ + 1.8]}
        intensity={glow * 13}
        distance={20}
        decay={2}
        color={PALETTE.glassLit}
      />
      {/* desk + laptop, silhouetted in the window */}
      <mesh position={[0, DEV_TOWER.windowY - wh / 2 + 0.10, faceZ + 0.30]} castShadow material={lib.shoe}>
        <boxGeometry args={[2.6, 0.12, 0.9]} />
      </mesh>
      <mesh
        position={[0, DEV_TOWER.windowY - wh / 2 + 0.52, faceZ + 0.34]}
        rotation={[-0.34, 0, 0]}
        castShadow
        material={lib.steel}
      >
        <boxGeometry args={[1.05, 0.70, 0.07]} />
      </mesh>
      <mesh
        position={[0, DEV_TOWER.windowY - wh / 2 + 0.52, faceZ + 0.40]}
        rotation={[-0.34, 0, 0]}
        material={lib.glassLit}
      >
        <planeGeometry args={[0.92, 0.56]} />
      </mesh>
    </group>
  );
};

const Bridges: React.FC = () => {
  const lib = getMaterials();
  return (
    <group>
      {BRIDGE_LANES.map((lane) => {
        const cx = lane.startX + lane.length / 2;
        return (
          <group key={lane.key}>
            <mesh position={[cx, lane.y, lane.z]} castShadow receiveShadow material={lib.concrete}>
              <boxGeometry args={[lane.length, 0.5, 2.4]} />
            </mesh>
            <mesh position={[cx, lane.y + 0.55, lane.z - 1.25]} castShadow material={lib.steel}>
              <boxGeometry args={[lane.length, 0.30, 0.16]} />
            </mesh>
            <mesh position={[cx, lane.y + 0.55, lane.z + 1.25]} castShadow material={lib.steel}>
              <boxGeometry args={[lane.length, 0.30, 0.16]} />
            </mesh>
            {[0.12, 0.5, 0.88].map((f) => (
              <mesh
                key={f}
                position={[lane.startX + lane.length * f, lane.y / 2, lane.z]}
                castShadow
                receiveShadow
                material={lib.concrete}
              >
                <boxGeometry args={[0.5, lane.y, 0.5]} />
              </mesh>
            ))}
          </group>
        );
      })}
    </group>
  );
};

/* ----------------------------------------------------------------- coins */
const Coins: React.FC<{frame: number}> = ({frame}) => {
  const lib = getMaterials();
  const ref = useRef<InstancedMesh>(null);
  const dummy = useMemo(() => new Object3D(), []);
  const geo = useMemo(() => {
    const g = new CylinderGeometry(0.44, 0.44, 0.15, 20);
    g.rotateX(Math.PI / 2); // stand the disc up so it rolls out of the vault
    return g;
  }, []);
  const base = useMemo(() => new Color(PALETTE.brass), []);
  const ice = useMemo(() => new Color(PALETTE.ice), []);
  const tmp = useMemo(() => new Color(), []);

  useLayoutEffect(() => {
    const mesh = ref.current;
    if (!mesh) return;
    const t = frame / 30;
    for (let i = 0; i < COIN_COUNT; i += 1) {
      const tr = coinTransform(i, t);
      dummy.position.set(tr.pos[0], tr.pos[1], tr.pos[2]);
      dummy.rotation.set(0, 0, tr.rot);
      dummy.scale.setScalar(tr.scale);
      dummy.updateMatrix();
      mesh.setMatrixAt(i, dummy.matrix);
      tmp.copy(base).lerp(ice, tr.frozen);
      mesh.setColorAt(i, tmp);
    }
    mesh.instanceMatrix.needsUpdate = true;
    if (mesh.instanceColor) mesh.instanceColor.needsUpdate = true;
  }, [frame, dummy, base, ice, tmp]);

  return (
    <instancedMesh
      ref={ref}
      args={[geo, lib.brass, COIN_COUNT]}
      castShadow
      frustumCulled={false}
    />
  );
};

/* ------------------------------------------------------------ characters */
type Actor = {
  who: CharacterKey;
  /** Centre of the figure; feet land at y − height / 2. */
  pos: [number, number, number];
  height: number;
  faceCamera: boolean;
  yawOffset?: number;
  action: (shot: Shot) => string;
  frozen?: (shot: Shot) => number;
};

const ACTORS: Actor[] = [
  {
    who: 'guard',
    pos: [-5.0, 2.1, 3.8],
    height: 4.2,
    faceCamera: true,
    yawOffset: 0.30,
    action: (s) => s.action,
    frozen: (s) => (s.id === 5 ? 0.6 : 0),
  },
  {
    who: 'hacker',
    pos: [15, 1.9, -4.5],
    height: 3.8,
    faceCamera: true,
    action: (s) =>
      s.id >= 3 && s.id <= 5 ? 'march' : s.id === 6 || s.id === 7 ? 'type' : 'idle',
    frozen: (s) => (s.id === 5 ? 0.8 : 0),
  },
  {
    // standing at the lit window — the legs are below the sill line
    who: 'engineer',
    pos: [DEV_TOWER.pos[0], DEV_TOWER.windowY - 0.30, DEV_TOWER.pos[2] + DEV_TOWER.body[2] / 2 + 0.62],
    height: 2.9,
    faceCamera: false,
    action: (s) => (s.id === 6 || s.id === 7 ? 'type' : 'idle'),
  },
];

const CROWD: Array<{p: [number, number, number]; who: CharacterKey; yaw: number}> = [
  {p: [-14, 1.6, 6.5], who: 'townA', yaw: 0.4},
  {p: [-11.5, 1.6, -7.5], who: 'townB', yaw: -0.5},
  {p: [8.5, 1.6, 9.5], who: 'townB', yaw: 0.2},
  {p: [-19, 1.6, -3.5], who: 'townA', yaw: -0.3},
];

const Cast: React.FC<{frame: number; cameraPos: [number, number, number]}> = ({frame, cameraPos}) => {
  const shot = shotAt(frame);
  const prevShot = SHOTS[Math.max(0, shot.id - 2)] ?? shot;
  const blend = Math.min(1, (frame - shot.start) / 14);

  return (
    <group>
      {ACTORS.map((a) => (
        <Character
          key={a.who}
          who={a.who}
          frame={frame}
          action={a.action(shot)}
          prevAction={a.action(prevShot)}
          actionBlend={blend}
          position={a.pos}
          height={a.height}
          faceCamera={a.faceCamera}
          yawOffset={a.yawOffset ?? 0}
          frozen={a.frozen?.(shot) ?? 0}
          cameraPos={cameraPos}
        />
      ))}

      {CROWD.map((c, i) => (
        <Character
          key={`crowd${i}`}
          who={c.who}
          frame={frame}
          action={shot.id >= 4 && shot.id <= 5 ? 'scared' : 'idle'}
          prevAction={prevShot.id >= 4 && prevShot.id <= 5 ? 'scared' : 'idle'}
          actionBlend={blend}
          position={c.p}
          height={3.2}
          yawOffset={c.yaw}
          frozen={shot.id === 5 ? 0.35 : 0}
          cameraPos={cameraPos}
        />
      ))}
    </group>
  );
};

/* ----------------------------------------------------------------- scene */
const Scene: React.FC<{
  frame: number;
  cameraPos: [number, number, number];
  noSky?: boolean;
  noFog?: boolean;
  noTown?: boolean;
  noGround?: boolean;
}> = ({frame, cameraPos, noSky, noFog, noTown, noGround}) => {
  const lib: MaterialLibrary = getMaterials();
  return (
    <>
      <SkyEnvironment noSky={noSky} />
      {noFog ? null : <fogExp2 attach="fog" args={[ATMOSPHERE.color, ATMOSPHERE.density]} />}

      {/* Dusk rig: low warm key, cool rim from behind, sky hemisphere fill,
          and the environment map carrying the ambient. */}
      <hemisphereLight
        args={[LIGHT.hemiSky, LIGHT.hemiGround, LIGHT.hemiIntensity]}
      />
      <ambientLight intensity={LIGHT.ambient} />

      <directionalLight
        position={LIGHT.keyPosition}
        intensity={LIGHT.keyIntensity}
        color={LIGHT.keyColor}
        castShadow
        shadow-mapSize={[LIGHT.shadowMapSize, LIGHT.shadowMapSize]}
        shadow-camera-left={-75}
        shadow-camera-right={75}
        shadow-camera-top={75}
        shadow-camera-bottom={-75}
        shadow-camera-near={1}
        shadow-camera-far={260}
        shadow-bias={LIGHT.shadowBias}
        shadow-normalBias={0.03}
      />
      <directionalLight
        position={[-34, 20, -26]}
        intensity={LIGHT.rimIntensity}
        color={LIGHT.rimColor}
      />
      <directionalLight
        position={[-12, 14, 40]}
        intensity={LIGHT.fillIntensity}
        color={LIGHT.fillColor}
      />

      {noGround ? null : (
        <mesh
          rotation={[-Math.PI / 2, 0, 0]}
          position={[0, 0, 0]}
          receiveShadow
          material={lib.ground}
        >
          <planeGeometry args={[900, 900]} />
        </mesh>
      )}

      {noTown ? null : <Town />}
      <Vault />
      <ClockTower />
      <DevTower frame={frame} />
      <Bridges />
      <StreetKit />
      <Coins frame={frame} />
      <Cast frame={frame} cameraPos={cameraPos} />
    </>
  );
};

/* -------------------------------------------------------------- overlays */
const Caption: React.FC<{text: string; frame: number; start: number}> = ({text, frame, start}) => {
  const local = frame - start;
  const enter = interpolate(local, [0, 7], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });
  return (
    <div
      style={{
        position: 'absolute',
        left: 0,
        right: 0,
        bottom: 0,
        height: 620,
        background:
          'linear-gradient(to top, rgba(8,7,12,0.78) 0%, rgba(8,7,12,0.44) 34%, rgba(8,7,12,0) 100%)',
        pointerEvents: 'none',
        opacity: enter,
      }}
    >
      <div
        style={{
          position: 'absolute',
          left: 76,
          right: 76,
          bottom: 232,
          textAlign: 'center',
          fontFamily: DISPLAY,
          fontSize: 60,
          lineHeight: 1.08,
          fontWeight: 600,
          letterSpacing: -1.2,
          color: PALETTE.paper,
          transform: `translateY(${(1 - enter) * 24}px)`,
          textShadow: '0 2px 18px rgba(0,0,0,0.9), 0 1px 4px rgba(0,0,0,0.85)',
        }}
      >
        {text}
      </div>
    </div>
  );
};

const NumberCard: React.FC<{label: string; frame: number; start: number; end: number}> = ({
  label, frame, start, end,
}) => {
  const p = interpolate(frame, [start, start + 10, end - 8, end], [0, 1, 1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const scale = 0.90 + 0.10 * Easing.out(Easing.cubic)(p);
  return (
    <div
      style={{
        position: 'absolute',
        top: 300,
        left: 0,
        right: 0,
        display: 'flex',
        justifyContent: 'center',
        opacity: p,
      }}
    >
      <div
        style={{
          transform: `scale(${scale})`,
          padding: '16px 32px',
          borderRadius: 14,
          background: 'rgba(12,14,20,0.66)',
          border: '1px solid rgba(244,241,234,0.16)',
          boxShadow: '0 20px 50px rgba(0,0,0,0.45), inset 0 1px 0 rgba(255,255,255,0.08)',
          fontFamily: MONO,
          fontSize: 46,
          letterSpacing: 2,
          color: '#FFD9A0',
          textShadow: '0 2px 16px rgba(255,180,110,0.35)',
        }}
      >
        {label}
      </div>
    </div>
  );
};

/* ----------------------------------------------------------- composition */
export type Binance63BProps = {
  /** QA switches — all default to the shipped look. */
  noSky?: boolean;
  noFog?: boolean;
  noDof?: boolean;
  noTown?: boolean;
  noGround?: boolean;
  cameraOverride?: [number, number, number];
  lookOverride?: [number, number, number];
  bokehScale?: number;
  exposure?: number;
};

export const Binance63B: React.FC<Binance63BProps> = ({
  noSky = false, noFog = false, noDof = false, noTown = false, noGround = false,
  cameraOverride, lookOverride, bokehScale, exposure,
}) => {
  const frame = useCurrentFrame();
  const {width, height} = useVideoConfig();

  const state = getCameraState(frame);
  const shot = shotAt(frame);
  const progress = shotProgress(frame);

  // 5 % parallax between the cast and the town behind them.
  const anchor = shot.camera.pos;
  const cameraPos = useMemo<[number, number, number]>(
    () => [
      state.position.x + (anchor[0] - state.position.x) * CAMERA.parallax,
      state.position.y + (anchor[1] - state.position.y) * CAMERA.parallax,
      state.position.z + (anchor[2] - state.position.z) * CAMERA.parallax,
    ],
    [anchor, state.position],
  );

  const bokeh = lensPxForAperture(LENS.aperture, LENS.dofHeight, HEIGHT);
  const focusWorld = Math.max(2, state.distance - LENS.focusDistance);

  return (
    <AbsoluteFill style={{backgroundColor: PALETTE.zenith}}>
      <style>{FONTS}</style>

      {/* --- WebGL layer ------------------------------------------------ */}
      <AbsoluteFill
        style={{
          // Filmic grade: gentle contrast lift, a touch of saturation.
          filter: `contrast(${1 + GRADE.contrast / 100}) saturate(${GRADE.saturate})`,
        }}
      >
        <ThreeCanvas
          width={width}
          height={height}
          style={{width, height}}
          camera={{
            fov: CAMERA.fov,
            near: CAMERA.near,
            far: CAMERA.far,
            position: [0, 6, 30],
          }}
          gl={{antialias: false, powerPreference: 'high-performance'}}
          shadows
        >
          <RendererSettings exposure={exposure ?? LIGHT.exposure} />
          <CameraRig frame={frame} cameraOverride={cameraOverride} lookOverride={lookOverride} />
          <Scene
            frame={frame}
            cameraPos={cameraPos}
            noSky={noSky}
            noFog={noFog}
            noTown={noTown}
            noGround={noGround}
          />
          {noDof ? null : (
            <LensBlur
              focusWorld={focusWorld}
              range={LENS.worldFocusRange}
              backgroundPx={bokehScale ?? LENS.backgroundBlurPx}
              foregroundPx={LENS.foregroundBlurPx}
              exposure={exposure ?? LIGHT.exposure}
            />
          )}
        </ThreeCanvas>
      </AbsoluteFill>

      {/* --- vignette ---------------------------------------------------- */}
      <AbsoluteFill
        style={{
          background: `radial-gradient(ellipse at 50% 44%, rgba(${GRADE.vignetteColor},0) 36%, rgba(${GRADE.vignetteColor},${GRADE.vignette}) 74%, rgba(${GRADE.vignetteColor},${GRADE.vignette * 2.4}) 100%)`,
        }}
      />

      {/* --- text -------------------------------------------------------- */}
      {shot.overlay ? (
        <NumberCard label={shot.overlay} frame={frame} start={shot.start} end={shot.end} />
      ) : null}
      <Caption text={shot.caption} frame={frame} start={shot.start} />

      {/* beat marker */}
      <div
        style={{
          position: 'absolute',
          left: 70,
          right: 70,
          bottom: 150,
          height: 5,
          borderRadius: 3,
          background: 'rgba(244,241,234,0.18)',
          overflow: 'hidden',
        }}
      >
        <div
          style={{
            width: `${progress * 100}%`,
            height: '100%',
            background: '#FFD9A0',
          }}
        />
      </div>
    </AbsoluteFill>
  );
};
