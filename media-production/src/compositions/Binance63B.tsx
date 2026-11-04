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
import {
  BackSide,
  Color,
  CylinderGeometry,
  InstancedMesh,
  Object3D,
  PerspectiveCamera,
  ShaderMaterial,
  Vector3,
  NeutralToneMapping,
  PCFSoftShadowMap,
} from 'three';
import {useThree} from '@react-three/fiber';

import {getCameraState} from '../camera';
import {shotAt, shotProgress, type Shot} from '../story';
import {Character} from '../characters';
import {
  BRIDGE_LANES,
  CLOCK_TOWER,
  COIN_COUNT,
  coinTransform,
  DEV_TOWER,
  TOWN_BUILDINGS,
  VAULT,
  usePaintedMaterials,
} from '../world';
import {
  CAMERA,
  FPS,
  GRADE,
  HEIGHT,
  LENS,
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

/* ------------------------------------------------------------------ sky */
const SkyDome: React.FC = () => {
  const material = useMemo(
    () =>
      new ShaderMaterial({
        side: BackSide,
        depthWrite: false,
        uniforms: {
          // Bright at the zenith, teal down at the horizon so it blends into
          // the ground plane and the fog instead of banding against them.
          uTop: {value: new Color(PALETTE.paper)},
          uBottom: {value: new Color(PALETTE.sky)},
        },
        vertexShader: `varying float vY;
          void main(){ vY = normalize(position).y;
            gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }`,
        fragmentShader: `uniform vec3 uTop; uniform vec3 uBottom; varying float vY;
          void main(){ gl_FragColor = vec4(mix(uBottom, uTop, smoothstep(-0.05, 0.55, vY)), 1.0); }`,
      }),
    [],
  );
  return (
    <mesh material={material} scale={[1, 1, 1]}>
      <sphereGeometry args={[150, 24, 16]} />
    </mesh>
  );
};

/* --------------------------------------------------- renderer settings */
/** Tone mapping has to be set on the renderer instance — R3F passes the `gl`
 *  object straight to the WebGLRenderer constructor, which ignores it. */
const RendererSettings: React.FC<{exposure: number}> = ({exposure}) => {
  const gl = useThree((s) => s.gl);
  gl.toneMapping = NeutralToneMapping;
  gl.toneMappingExposure = exposure;
  gl.shadowMap.type = PCFSoftShadowMap;
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

/* ----------------------------------------------------------------- town */
const Town: React.FC = () => {
  const mats = usePaintedMaterials();
  return (
    <group>
      {TOWN_BUILDINGS.map((b) => (
        <group key={b.key} position={b.pos} rotation={[0, b.rot, 0]}>
          <mesh castShadow receiveShadow material={mats[b.mat].color}>
            <boxGeometry args={b.size} />
          </mesh>
          {b.roof === 'gable' ? (
            <mesh
              position={[0, b.size[1] / 2 + 0.7, 0]}
              rotation={[0, Math.PI / 4, 0]}
              castShadow
              material={mats.pop.color}
            >
              <coneGeometry args={[b.size[0] * 0.82, 1.6, 4]} />
            </mesh>
          ) : null}
          {b.roof === 'tower' ? (
            <mesh
              position={[0, b.size[1] / 2 + 1.6, 0]}
              castShadow
              material={mats.sun.color}
            >
              <coneGeometry args={[b.size[0] * 0.85, 3.4, 4]} />
            </mesh>
          ) : null}
        </group>
      ))}
    </group>
  );
};

/* ------------------------------------------------------------- landmarks */
const Vault: React.FC = () => {
  const mats = usePaintedMaterials();
  return (
    <group position={VAULT.pos}>
      {/* plaza */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.02, 0]} receiveShadow material={mats.paper.color}>
        <circleGeometry args={[13, 40]} />
      </mesh>
      {/* steps */}
      <mesh position={[0, 0.3, 6.4]} castShadow receiveShadow material={mats.paper.color}>
        <boxGeometry args={[7, 0.6, 2.6]} />
      </mesh>
      {/* body */}
      <mesh position={[0, 5.5, 0]} castShadow receiveShadow material={mats.sun.color}>
        <boxGeometry args={VAULT.body} />
      </mesh>
      {/* roof */}
      <mesh position={[0, 13.4, 0]} rotation={[0, Math.PI / 4, 0]} castShadow material={mats.pop.color}>
        <coneGeometry args={[7.4, 4.6, 4]} />
      </mesh>
      {/* door */}
      <mesh position={[0, 3.2, 4.6]} castShadow receiveShadow material={mats.shadow.color}>
        <boxGeometry args={VAULT.doorSize} />
      </mesh>
      {/* dial */}
      <mesh position={[0, 3.4, 5.0]} rotation={[Math.PI / 2, 0, 0]} castShadow material={mats.paper.color}>
        <cylinderGeometry args={[1.5, 1.5, 0.35, 24]} />
      </mesh>
    </group>
  );
};

const ClockTower: React.FC = () => {
  const mats = usePaintedMaterials();
  // 20:05 → hour hand at 242.5°, minute hand at 30° (clockwise from 12).
  const hour = ((8 + 5 / 60) / 12) * Math.PI * 2;
  const minute = (5 / 60) * Math.PI * 2;
  return (
    <group position={CLOCK_TOWER.pos}>
      <mesh position={[0, CLOCK_TOWER.body[1] / 2, 0]} castShadow receiveShadow material={mats.town.color}>
        <boxGeometry args={CLOCK_TOWER.body} />
      </mesh>
      <mesh position={[0, CLOCK_TOWER.body[1] + 2.2, 0]} rotation={[0, Math.PI / 4, 0]} castShadow material={mats.pop.color}>
        <coneGeometry args={[3.4, 4.4, 4]} />
      </mesh>
      <group position={[0, CLOCK_TOWER.faceY, CLOCK_TOWER.body[2] / 2 + 0.06]}>
        <mesh material={mats.paper.color}>
          <circleGeometry args={[CLOCK_TOWER.faceR, 32]} />
        </mesh>
        <mesh position={[0, 0, 0.05]} rotation={[0, 0, -hour]} material={mats.shadow.color}>
          <boxGeometry args={[0.16, 1.0, 0.06]} />
        </mesh>
        <mesh position={[0, 0, 0.05]} rotation={[0, 0, -minute]} material={mats.shadow.color}>
          <boxGeometry args={[0.12, 1.45, 0.06]} />
        </mesh>
      </group>
    </group>
  );
};

const DevTower: React.FC<{frame: number}> = ({frame}) => {
  const mats = usePaintedMaterials();
  const glow = 0.55 + 0.12 * Math.sin(frame / FPS * 3.1);
  const [ww, wh] = DEV_TOWER.windowSize;
  const faceZ = DEV_TOWER.body[2] / 2 + 0.05;
  return (
    <group position={DEV_TOWER.pos}>
      <mesh position={[0, DEV_TOWER.body[1] / 2, 0]} castShadow receiveShadow material={mats.town.color}>
        <boxGeometry args={DEV_TOWER.body} />
      </mesh>
      <mesh position={[0, DEV_TOWER.body[1] + 1.4, 0]} rotation={[0, Math.PI / 4, 0]} castShadow material={mats.sky.color}>
        <coneGeometry args={[4.3, 2.8, 4]} />
      </mesh>
      {/* the lit window — the whole attack happened behind this rectangle */}
      <mesh position={[0, DEV_TOWER.windowY, faceZ]} material={mats.sun.color}>
        <planeGeometry args={[ww, wh]} />
      </mesh>
      <pointLight
        position={[0, DEV_TOWER.windowY, faceZ + 1.6]}
        intensity={glow * 22}
        distance={16}
        color={PALETTE.sun}
      />
      {/* laptop on the desk, screen facing out */}
      <mesh position={[0, DEV_TOWER.windowY - 0.95, faceZ + 0.16]} rotation={[-0.35, 0, 0]} castShadow material={mats.shadow.color}>
        <boxGeometry args={[1.05, 0.7, 0.08]} />
      </mesh>
      <mesh position={[0, DEV_TOWER.windowY - 0.95, faceZ + 0.21]} rotation={[-0.35, 0, 0]} material={mats.sky.color}>
        <planeGeometry args={[0.92, 0.58]} />
      </mesh>
    </group>
  );
};

const Bridges: React.FC = () => {
  const mats = usePaintedMaterials();
  return (
    <group>
      {BRIDGE_LANES.map((lane) => {
        const railMat = lane.freezable ? mats.sky.color : mats.pop.color;
        const cx = lane.startX + lane.length / 2;
        return (
          <group key={lane.key}>
            <mesh position={[cx, lane.y, lane.z]} castShadow receiveShadow material={mats.paper.color}>
              <boxGeometry args={[lane.length, 0.5, 2.4]} />
            </mesh>
            <mesh position={[cx, lane.y + 0.55, lane.z - 1.25]} castShadow material={railMat}>
              <boxGeometry args={[lane.length, 0.36, 0.22]} />
            </mesh>
            <mesh position={[cx, lane.y + 0.55, lane.z + 1.25]} castShadow material={railMat}>
              <boxGeometry args={[lane.length, 0.36, 0.22]} />
            </mesh>
            {[0.12, 0.5, 0.88].map((f) => (
              <mesh
                key={f}
                position={[lane.startX + lane.length * f, lane.y / 2, lane.z]}
                castShadow
                material={mats.town.color}
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
  const mats = usePaintedMaterials();
  const ref = useRef<InstancedMesh>(null);
  const dummy = useMemo(() => new Object3D(), []);
  const geo = useMemo(() => {
    const g = new CylinderGeometry(0.44, 0.44, 0.15, 18);
    g.rotateX(Math.PI / 2); // stand the disc up so it rolls out of the vault
    return g;
  }, []);
  const base = useMemo(() => new Color(PALETTE.sun), []);
  const ice = useMemo(() => new Color(PALETTE.sky), []);
  const tmp = useMemo(() => new Color(), []);

  useLayoutEffect(() => {
    const mesh = ref.current;
    if (!mesh) return;
    const t = frame / FPS;
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
      args={[geo, mats.sun.color, COIN_COUNT]}
      castShadow
      frustumCulled={false}
    />
  );
};

/* ------------------------------------------------------------ characters */
type Actor = {
  who: 'guard' | 'engineer' | 'hacker';
  pos: [number, number, number];
  height: number;
  faceCamera: boolean;
  action: (shot: Shot) => string;
  frozen?: (shot: Shot) => number;
  opacity?: (shot: Shot, frame: number) => number;
  bob?: number;
};

const ACTORS: Actor[] = [
  {
    who: 'guard',
    pos: [-6.2, 1.45, 3.8],
    height: 2.9,
    faceCamera: true,
    action: (s) => s.action,
    frozen: (s) => (s.id === 5 ? 0.6 : 0),
  },
  {
    who: 'hacker',
    pos: [15, 3.2, -4.5],
    height: 2.7,
    faceCamera: true,
    action: (s) => (s.id >= 3 && s.id <= 5 ? 'march' : s.id === 6 || s.id === 7 ? 'type' : 'idle'),
    frozen: (s) => (s.id === 5 ? 0.8 : 0),
  },
  {
    who: 'engineer',
    pos: [DEV_TOWER.pos[0], DEV_TOWER.windowY - 1.05, DEV_TOWER.pos[2] + DEV_TOWER.body[2] / 2 + 0.55],
    height: 1.8,
    faceCamera: false,
    action: (s) => (s.id === 6 || s.id === 7 ? 'type' : 'idle'),
    bob: 0,
  },
];

const Cast: React.FC<{frame: number; cameraPos: Vector3}> = ({frame, cameraPos}) => {
  const shot = shotAt(frame);
  return (
    <group>
      {ACTORS.map((a) => (
        <Character
          key={a.who}
          who={a.who}
          frame={frame}
          action={a.action(shot)}
          position={a.pos}
          height={a.height}
          faceCamera={a.faceCamera}
          frozen={a.frozen?.(shot) ?? 0}
          bob={a.bob ?? 1}
          cameraPos={[cameraPos.x, cameraPos.y, cameraPos.z]}
          fov={CAMERA.fov}
        />
      ))}

      {/* townsfolk — the crowd that watches the money leave */}
      {[
        {p: [-14, 1.15, 6.5] as [number, number, number], h: 2.3},
        {p: [-11.5, 1.15, -7.5] as [number, number, number], h: 2.3},
        {p: [8.5, 1.15, 9.5] as [number, number, number], h: 2.3},
        {p: [-19, 1.15, -3.5] as [number, number, number], h: 2.3},
      ].map((c, i) => (
        <Character
          key={`crowd${i}`}
          who={i % 2 === 0 ? 'guard' : 'engineer'}
          frame={frame}
          action={shot.id >= 4 && shot.id <= 5 ? 'scared' : 'idle'}
          position={c.p}
          height={c.h}
          frozen={shot.id === 5 ? 0.35 : 0}
          cameraPos={[cameraPos.x, cameraPos.y, cameraPos.z]}
          fov={CAMERA.fov}
        />
      ))}
    </group>
  );
};

/* ----------------------------------------------------------------- scene */
const Scene: React.FC<{
  frame: number; cameraPos: Vector3; distance: number;
  noSky?: boolean; noFog?: boolean; noTown?: boolean; noGround?: boolean;
}> = ({frame, cameraPos, noSky, noFog, noTown, noGround}) => {
  const mats = usePaintedMaterials();
  return (
    <>
      <color attach="background" args={[PALETTE.sky]} />
      {noFog ? null : <fog attach="fog" args={[PALETTE.sky, 120, 340]} />}

      {/* warm key + cool fill, plus a shadow-coloured floor so unlit faces
          land on #2A2E6B instead of crushing to black */}
      <hemisphereLight args={[PALETTE.paper, PALETTE.sky, 0.60]} />
      <ambientLight intensity={1.25} color="#8FD6FF" />
      <ambientLight intensity={0.42} color={PALETTE.shadow} />
      <directionalLight
        position={[14, 28, 16]}
        intensity={1.05}
        color="#FFE3A8"
        castShadow
        shadow-mapSize={[1024, 1024]}
        shadow-camera-left={-70}
        shadow-camera-right={70}
        shadow-camera-top={70}
        shadow-camera-bottom={-70}
        shadow-camera-far={160}
        shadow-bias={-0.0008}
      />
      <directionalLight position={[-22, 12, -14]} intensity={0.4} color="#8FD6FF" />

      {noSky ? null : <SkyDome />}

      {noGround ? null : (
        <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0, 0]} receiveShadow material={mats.town.color}>
          <planeGeometry args={[900, 900]} />
        </mesh>
      )}

      {noTown ? null : <Town />}
      <Vault />
      <ClockTower />
      <DevTower frame={frame} />
      <Bridges />
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
        left: 70,
        right: 70,
        bottom: 250,
        textAlign: 'center',
        fontFamily: DISPLAY,
        fontSize: 62,
        lineHeight: 1.06,
        fontWeight: 700,
        letterSpacing: -1.6,
        color: PALETTE.paper,
        opacity: enter,
        transform: `translateY(${(1 - enter) * 26}px)`,
        textShadow: `0 6px 0 ${PALETTE.shadow}, 0 10px 30px rgba(42,46,107,0.55)`,
        WebkitTextStroke: `3px ${PALETTE.shadow}`,
        paintOrder: 'stroke fill',
      }}
    >
      {text}
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
  const scale = 0.86 + 0.14 * Easing.out(Easing.cubic)(p);
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
          padding: '18px 34px',
          borderRadius: 18,
          background: 'rgba(26,83,92,0.82)',
          border: `4px solid ${PALETTE.sun}`,
          fontFamily: MONO,
          fontSize: 52,
          letterSpacing: 1.5,
          color: PALETTE.sun,
          textShadow: `0 4px 18px rgba(42,46,107,0.6)`,
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
};

export const Binance63B: React.FC<Binance63BProps> = ({
  noSky = false, noFog = false, noDof = false, noTown = false, noGround = false,
  cameraOverride, lookOverride, bokehScale,
}) => {
  const frame = useCurrentFrame();
  const {width, height} = useVideoConfig();

  const state = getCameraState(frame);
  const shot = shotAt(frame);
  const progress = shotProgress(frame);

  // 5 % parallax between the character planes and the town behind them.
  const anchor = shot.camera.pos;
  const parallax = useMemo(
    () => new Vector3(
      (anchor[0] - state.position.x) * CAMERA.parallax,
      (anchor[1] - state.position.y) * CAMERA.parallax,
      (anchor[2] - state.position.z) * CAMERA.parallax,
    ),
    [anchor, state.position],
  );
  const cameraPos = useMemo(
    () => new Vector3(
      state.position.x + parallax.x,
      state.position.y + parallax.y,
      state.position.z + parallax.z,
    ),
    [state.position, parallax],
  );

  const bokeh = lensPxForAperture(LENS.aperture, LENS.dofHeight, HEIGHT);
  const focusWorld = Math.max(2, state.distance - LENS.focusDistance);

  return (
    <AbsoluteFill style={{backgroundColor: PALETTE.sky}}>
      <style>{FONTS}</style>

      {/* --- WebGL layer ------------------------------------------------ */}
      <AbsoluteFill
        style={{
          // Grade: warm temperature +5, contrast +10
          filter: `contrast(${1 + GRADE.contrast / 100}) saturate(1.06) sepia(0.055)`,
        }}
      >
        <ThreeCanvas
          width={width}
          height={height}
          style={{width, height}}
          camera={{fov: CAMERA.fov, near: CAMERA.near, far: CAMERA.far, position: [0, 6, 30]}}
          gl={{antialias: false, powerPreference: 'high-performance'}}
          shadows
        >
          <RendererSettings exposure={1.35} />
          <CameraRig frame={frame} cameraOverride={cameraOverride} lookOverride={lookOverride} />
          <Scene
            frame={frame}
            cameraPos={cameraPos}
            distance={state.distance}
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
            />
          )}
        </ThreeCanvas>
      </AbsoluteFill>

      {/* --- vignette 0.15 in the palette shadow colour ------------------ */}
      <AbsoluteFill
        style={{
          background: `radial-gradient(ellipse at 50% 44%, rgba(42,46,107,0) 34%, rgba(42,46,107,${GRADE.vignette}) 72%, rgba(42,46,107,${GRADE.vignette * 2.6}) 100%)`,
        }}
      />

      {/* --- text -------------------------------------------------------- */}
      {shot.overlay ? (
        <NumberCard label={shot.overlay} frame={frame} start={shot.start} end={shot.end} />
      ) : null}
      <Caption text={shot.caption} frame={frame} start={shot.start} />

      {/* loop marker so the editor can see where the beat lands */}
      <div
        style={{
          position: 'absolute',
          left: 70,
          right: 70,
          bottom: 150,
          height: 6,
          borderRadius: 3,
          background: 'rgba(247,255,247,0.22)',
          overflow: 'hidden',
        }}
      >
        <div
          style={{
            width: `${progress * 100}%`,
            height: '100%',
            background: PALETTE.sun,
          }}
        />
      </div>
    </AbsoluteFill>
  );
};
