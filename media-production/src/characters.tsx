import React, {useMemo} from 'react';
import {
  BoxGeometry,
  CapsuleGeometry,
  Color,
  DoubleSide,
  MeshStandardMaterial,
  PlaneGeometry,
  SphereGeometry,
} from 'three';
import {FPS, PALETTE, clamp01, lerp} from './theme';
import {getMaterials} from './materials';
import {mulberry32} from './world';

/**
 * Characters — REVISION 2.
 *
 * These used to be camera-facing planes carrying a drawn sprite. They are now
 * actual jointed 3D figures: a hip pivot with two legs (thigh → shin → foot) and
 * a spine that carries the chest, head and two arms (upper → forearm → hand).
 *
 * Everything is built in **unit space** — feet at y = 0, top of head at y = 1 —
 * and the root group is scaled by `height`. So a 2.9-unit guard and a 3.2-unit
 * townsman share one rig.
 *
 * Proportions are real (~7.5 heads, hip at 53 % of height, knee at 28.5 %),
 * which is what separates "semi-realist" from the old chibi billboards.
 *
 * Joint conventions (all radians):
 *   armL / armR   > 0 swings the arm forward
 *   elbowL / R    > 0 flexes the elbow
 *   legL / legR   > 0 swings the thigh forward
 *   kneeL / kneeR > 0 flexes the knee (heel toward the back)
 *   spine         > 0 leans the torso forward
 *   headX         > 0 tips the chin down
 */

export type Pose =
  | 'idle' | 'walk' | 'march' | 'scared' | 'freeze' | 'type' | 'salute';

export type Joints = {
  spine: number;
  headX: number;
  headY: number;
  armL: number; armLZ: number; elbowL: number; elbowLZ: number;
  armR: number; armRZ: number; elbowR: number; elbowRZ: number;
  legL: number; kneeL: number;
  legR: number; kneeR: number;
  crouch: number;
  bob: number;
};

const ZERO: Joints = {
  spine: 0, headX: 0, headY: 0,
  armL: 0, armLZ: 0, elbowL: 0, elbowLZ: 0,
  armR: 0, armRZ: 0, elbowR: 0, elbowRZ: 0,
  legL: 0, kneeL: 0, legR: 0, kneeR: 0,
  crouch: 0, bob: 0,
};

/* --------------------------------------------------------------- the poses */

const WALK_W = 5.6; // rad/s — ~110 steps/min
const MARCH_W = 5.24; // 100 BPM, matching the score

const poseWalk = (t: number, phase: number, gain: number, march: boolean): Joints => {
  const p = t * (march ? MARCH_W : WALK_W) + phase;
  const swing = march ? 0.78 : 0.52;
  const armSwing = march ? 0.88 : 0.44;
  const kneeMax = march ? 1.30 : 1.02;
  const bend = march ? 0.22 : 0.10;

  return {
    ...ZERO,
    spine: march ? -0.04 : 0.045,
    headX: march ? -0.02 : -0.03,
    headY: Math.sin(p) * 0.03,
    armL: Math.sin(p + Math.PI) * armSwing,
    armR: Math.sin(p) * armSwing,
    armLZ: 0.09,
    armRZ: -0.09,
    elbowL: (march ? 0.85 : 0.26) + Math.max(0, Math.sin(p + Math.PI)) * 0.28,
    elbowR: (march ? 0.85 : 0.26) + Math.max(0, Math.sin(p)) * 0.28,
    elbowLZ: 0.05,
    elbowRZ: -0.05,
    legL: Math.sin(p) * swing,
    legR: Math.sin(p + Math.PI) * swing,
    kneeL: bend + Math.max(0, Math.cos(p)) * kneeMax,
    kneeR: bend + Math.max(0, Math.cos(p + Math.PI)) * kneeMax,
    bob: (Math.abs(Math.sin(p)) - 0.5) * (march ? 0.030 : 0.018) * gain,
  };
};

const poseIdle = (t: number, phase: number): Joints => {
  const b = Math.sin(t * 1.15 + phase); // breathing
  return {
    ...ZERO,
    spine: 0.018 + b * 0.014,
    headX: -0.02 + Math.sin(t * 0.71 + phase) * 0.025,
    headY: Math.sin(t * 0.43 + phase) * 0.12,
    armL: 0.05 + b * 0.02,
    armR: 0.05 - b * 0.02,
    armLZ: 0.115,
    armRZ: -0.115,
    elbowL: 0.20 + b * 0.03,
    elbowR: 0.20 - b * 0.03,
    legL: 0.012,
    legR: -0.012,
    kneeL: 0.03,
    kneeR: 0.03,
    bob: b * 0.005,
  };
};

const poseScared = (t: number, phase: number): Joints => {
  const shake = Math.sin(t * 21 + phase) * 0.014;
  return {
    ...ZERO,
    spine: -0.17 + shake,
    headX: -0.13,
    headY: shake * 0.6,
    armL: -0.30,
    armR: -0.30,
    armLZ: 0.62,
    armRZ: -0.62,
    elbowL: 1.55 + shake,
    elbowR: 1.55 - shake,
    elbowLZ: 0.22,
    elbowRZ: -0.22,
    legL: 0.09,
    legR: -0.09,
    kneeL: 0.34,
    kneeR: 0.34,
    crouch: 0.15,
    bob: shake * 0.2,
  };
};

const poseFreeze = (t: number, phase: number): Joints => {
  const shiver = Math.sin(t * 17 + phase) * 0.008;
  return {
    ...ZERO,
    spine: -0.05 + shiver,
    headX: -0.04,
    armL: -0.12,
    armR: -0.12,
    armLZ: 0.30,
    armRZ: -0.30,
    elbowL: 0.42,
    elbowR: 0.42,
    legL: 0.05,
    legR: -0.05,
    kneeL: 0.24,
    kneeR: 0.24,
    crouch: 0.10,
    bob: shiver * 0.3,
  };
};

const poseType = (t: number, phase: number): Joints => {
  // Seated at a desk: torso pitched in, forearms out flat, fingers busy.
  const f = Math.sin(t * 9.5 + phase);
  const g = Math.sin(t * 9.5 + phase + 1.9);
  return {
    ...ZERO,
    spine: 0.30,
    headX: 0.24,
    headY: Math.sin(t * 0.5 + phase) * 0.05,
    armL: 0.72 + f * 0.03,
    armR: 0.72 + g * 0.03,
    armLZ: 0.20,
    armRZ: -0.20,
    elbowL: 1.18 + f * 0.06,
    elbowR: 1.18 + g * 0.06,
    legL: 0.14,
    legR: -0.14,
    kneeL: 0.06,
    kneeR: 0.06,
    crouch: 0.10,
    bob: 0,
  };
};

const poseSalute = (t: number, phase: number): Joints => {
  const b = Math.sin(t * 1.1 + phase) * 0.012;
  return {
    ...ZERO,
    spine: -0.03 + b,
    headX: -0.02,
    headY: 0.04,
    armL: 0.04,
    armR: -0.14,
    armLZ: 0.10,
    armRZ: -0.58,
    elbowL: 0.16,
    elbowR: 2.40,
    elbowLZ: 0.04,
    elbowRZ: 0.52,
    legL: 0.02,
    legR: -0.02,
    kneeL: 0.03,
    kneeR: 0.03,
    bob: b * 0.4,
  };
};

const POSE_FN: Record<Pose, (t: number, phase: number) => Joints> = {
  idle: poseIdle,
  walk: (t, p) => poseWalk(t, p, 1, false),
  march: (t, p) => poseWalk(t, p, 1, true),
  scared: poseScared,
  freeze: poseFreeze,
  type: poseType,
  salute: poseSalute,
};

export const jointsFor = (pose: Pose, t: number, phase: number): Joints =>
  POSE_FN[pose](t, phase);

/** Blend two joint sets — used to cross-fade an action change at a shot cut. */
const blendJoints = (a: Joints, b: Joints, k: number): Joints => {
  if (k >= 1) return b;
  if (k <= 0) return a;
  const out = {...a};
  (Object.keys(a) as Array<keyof Joints>).forEach((key) => {
    out[key] = lerp(a[key], b[key], k);
  });
  return out;
};

/* ------------------------------------------------------------- geometries */

type Geo = {
  sphere: SphereGeometry;
  sphereLow: SphereGeometry;
  box: BoxGeometry;
  plane: PlaneGeometry;
  upperArm: CapsuleGeometry;
  forearm: CapsuleGeometry;
  thigh: CapsuleGeometry;
  shin: CapsuleGeometry;
  neck: CapsuleGeometry;
  hood: SphereGeometry;
  hair: SphereGeometry;
  cap: SphereGeometry;
};

let GEO: Geo | null = null;

const getGeom = (): Geo => {
  if (GEO) return GEO;
  GEO = {
    sphere: new SphereGeometry(0.5, 18, 12),
    sphereLow: new SphereGeometry(0.5, 12, 8),
    box: new BoxGeometry(1, 1, 1),
    plane: new PlaneGeometry(1, 1),
    // CapsuleGeometry(radius, length, capSegments, radialSegments)
    upperArm: new CapsuleGeometry(0.030, 0.105, 4, 10),
    forearm: new CapsuleGeometry(0.026, 0.108, 4, 10),
    thigh: new CapsuleGeometry(0.042, 0.161, 4, 10),
    shin: new CapsuleGeometry(0.034, 0.172, 4, 10),
    neck: new CapsuleGeometry(0.026, 0.038, 4, 8),
    // partial spheres: phiLength < π leaves the face open
    hood: new SphereGeometry(0.5, 18, 12, 0, Math.PI * 2, 0, Math.PI * 0.58),
    hair: new SphereGeometry(0.5, 16, 10, 0, Math.PI * 2, 0, Math.PI * 0.52),
    cap: new SphereGeometry(0.5, 16, 8, 0, Math.PI * 2, 0, Math.PI * 0.46),
  };
  return GEO;
};

/* -------------------------------------------------------------- body plan */

/**
 * Landmarks as a fraction of total height. Real human proportions, so the
 * figure reads as a person and not a toy.
 */
const P = {
  headY: 0.935,
  headRX: 0.056,
  headRY: 0.068,
  headRZ: 0.061,
  neckY: 0.850,
  shoulderY: 0.800,
  shoulderX: 0.115,
  chestY: 0.755,
  abdomenY: 0.635,
  pelvisY: 0.515,
  hipY: 0.530,
  hipX: 0.075,
  upperArmLen: 0.186, // real: 0.186 · height
  forearmLen: 0.146, // real: 0.146 · height (wrist lands at 0.468)
  thighLen: 0.245,
  shinLen: 0.240,
  ankleY: 0.045,
};

/* --------------------------------------------------------------- wardrobe */

export type CharacterKey = 'guard' | 'engineer' | 'hacker' | 'townA' | 'townB';

type Wardrobe = {
  skin: MeshStandardMaterial;
  shirt: MeshStandardMaterial;
  pants: MeshStandardMaterial;
  shoe: MeshStandardMaterial;
  hair: MeshStandardMaterial;
  accent: MeshStandardMaterial;
  hooded: boolean;
  capped: boolean;
};

const ICE = new Color(PALETTE.ice);

/**
 * Per-character material clones. Cloning (rather than mutating the library
 * materials) is what lets one character freeze to ice while its neighbour
 * does not.
 */
const useWardrobe = (who: CharacterKey): Wardrobe =>
  useMemo(() => {
    const lib = getMaterials();
    const spec: Record<CharacterKey, {
      skin: MeshStandardMaterial; shirt: MeshStandardMaterial;
      pants: MeshStandardMaterial; hair: MeshStandardMaterial;
      accent: MeshStandardMaterial; hooded: boolean; capped: boolean;
    }> = {
      guard: {
        skin: lib.skin, shirt: lib.cloth, pants: lib.cloth,
        hair: lib.hair, accent: lib.brass, hooded: false, capped: true,
      },
      engineer: {
        skin: lib.skinDeep, shirt: lib.clothWarm, pants: lib.slate,
        hair: lib.hair, accent: lib.brass, hooded: false, capped: false,
      },
      hacker: {
        skin: lib.skin, shirt: lib.hoodie, pants: lib.hoodie,
        hair: lib.hair, accent: lib.steel, hooded: true, capped: false,
      },
      townA: {
        skin: lib.skin, shirt: lib.cloth, pants: lib.slate,
        hair: lib.hair, accent: lib.brass, hooded: false, capped: false,
      },
      townB: {
        skin: lib.skinDeep, shirt: lib.plaster, pants: lib.brick,
        hair: lib.hair, accent: lib.brass, hooded: false, capped: false,
      },
    };
    const s = spec[who];
    const clone = (m: MeshStandardMaterial) => {
      const c = m.clone();
      if (who === 'hacker' && m === lib.hoodie) c.side = DoubleSide;
      return c;
    };
    return {
      skin: clone(s.skin),
      shirt: clone(s.shirt),
      pants: clone(s.pants),
      shoe: clone(lib.shoe),
      hair: clone(s.hair),
      accent: clone(s.accent),
      hooded: s.hooded,
      capped: s.capped,
    };
  }, [who]);

/* ------------------------------------------------------------- components */

export type CharacterProps = {
  who: CharacterKey;
  action: string;
  /** Action of the previous shot — cross-faded so an action change never pops. */
  prevAction?: string;
  /** 0 → 1 blend from `prevAction` into `action`. */
  actionBlend?: number;
  position: [number, number, number]; // centre of the figure, as before
  /** Full standing height in world units. */
  height?: number;
  frozen?: number;
  faceCamera?: boolean;
  /** Y-rotation offset, in radians, on top of the facing. */
  yawOffset?: number;
  frame: number;
  cameraPos: [number, number, number];
};

export const Character: React.FC<CharacterProps> = ({
  who, action, prevAction, actionBlend = 1, position,
  height = 2.9, frozen = 0, faceCamera = true, yawOffset = 0,
  frame, cameraPos,
}) => {
  const G = getGeom();
  const lib = getMaterials();
  const w = useWardrobe(who);

  const t = frame / FPS;
  // Deterministic per-character phase so a crowd never marches in lockstep.
  const phase = useMemo(() => mulberry32(who.charCodeAt(0) * 977 + who.length)() * 6.283, [who]);

  const j = useMemo(() => {
    const a = (action in POSE_FN ? action : 'idle') as Pose;
    const b = (prevAction && prevAction in POSE_FN ? prevAction : a) as Pose;
    return blendJoints(jointsFor(b, t, phase), jointsFor(a, t, phase), actionBlend);
  }, [action, prevAction, actionBlend, t, phase]);

  // --- the freeze: lerp the wardrobe toward ice -----------------------------
  const f = clamp01(frozen);
  useMemo(() => {
    const k = f * 0.8;
    [w.skin, w.shirt, w.pants, w.shoe, w.hair].forEach((m) => {
      m.color.lerp(ICE, k * 0.55);
      m.roughness = lerp(m.roughness, 0.18, k);
      m.metalness = lerp(m.metalness, 0.05, k);
    });
    return null;
  }, [f, w]);

  const feetY = position[1] - height / 2;
  const yaw = faceCamera
    ? Math.atan2(cameraPos[0] - position[0], cameraPos[2] - position[2]) + yawOffset
    : yawOffset;

  // crouch compresses the whole figure and drops the hips
  const crouchScale = 1 - j.crouch * 0.16;
  const bodyY = j.bob - j.crouch * 0.03;

  const eyeR = 0.019;
  const eyeY = P.headY + 0.008;
  const eyeX = 0.021;
  const eyeZ = 0.048;

  return (
    <group position={[position[0], feetY, position[2]]} rotation={[0, yaw, 0]}>
      {/* contact shadow — the shadow map is far too coarse to catch the point
          where a foot meets the pavement, and that contact is what sells it */}
      <mesh
        geometry={G.plane}
        rotation={[-Math.PI / 2, 0, 0]}
        position={[0, 0.012, 0.02]}
        scale={[0.62 * height * 0.5, 0.62 * height * 0.5, 1]}
        renderOrder={2}
      >
        <meshBasicMaterial
          map={lib.contactShadow}
          transparent
          depthWrite={false}
          fog={false}
          color="#000000"
        />
      </mesh>

      <group scale={[height, height * crouchScale, height]}>
        <group position={[0, bodyY, 0]}>
          {/* ------------------------------------------------------ hips */}
          <group position={[0, P.hipY, 0]}>
            <mesh geometry={G.sphere} position={[0, P.pelvisY - P.hipY, 0]}
              scale={[0.170, 0.110, 0.105]} castShadow material={w.pants} />

            {/* ---- legs ---- */}
            {([-1, 1] as const).map((side) => {
              const isL = side > 0;
              const hipRot = isL ? -j.legL : -j.legR;
              const kneeRot = isL ? j.kneeL : j.kneeR;
              return (
                <group
                  key={`hip${side}`}
                  position={[P.hipX * side, 0, 0]}
                  rotation={[hipRot, 0, 0]}
                >
                  <mesh geometry={G.thigh} position={[0, -P.thighLen / 2, 0]} castShadow material={w.pants} />
                  <mesh geometry={G.sphereLow} position={[0, -P.thighLen, 0]}
                    scale={[0.072, 0.072, 0.072]} material={w.pants} />
                  <group position={[0, -P.thighLen, 0]} rotation={[kneeRot, 0, 0]}>
                    <mesh geometry={G.shin} position={[0, -P.shinLen / 2, 0]} castShadow material={w.pants} />
                    <mesh geometry={G.sphereLow} position={[0, -P.shinLen, 0]}
                      scale={[0.062, 0.062, 0.062]} material={w.pants} />
                    {/* foot: ankle sits at 0.045, sole at 0 */}
                    <mesh geometry={G.box} position={[0, -P.shinLen - 0.0225, 0.038]}
                      scale={[0.082, 0.045, 0.190]} castShadow material={w.shoe} />
                  </group>
                </group>
              );
            })}

            {/* ---- spine: chest, head and both arms ride on this ---- */}
            <group rotation={[j.spine, 0, 0]}>
              <mesh geometry={G.sphere} position={[0, P.abdomenY - P.hipY, 0]}
                scale={[0.168, 0.128, 0.104]} castShadow material={w.shirt} />
              <mesh geometry={G.sphere} position={[0, P.chestY - P.hipY, 0]}
                scale={[0.205, 0.150, 0.116]} castShadow material={w.shirt} />
              <mesh geometry={G.neck} position={[0, P.neckY - P.hipY, 0]} castShadow material={w.skin} />

              {/* shoulders */}
              {([-1, 1] as const).map((side) => (
                <mesh key={`sh${side}`} geometry={G.sphereLow}
                  position={[P.shoulderX * side, P.shoulderY - P.hipY, 0]}
                  scale={[0.082, 0.082, 0.082]} castShadow material={w.shirt} />
              ))}

              {/* badge / lanyard — the one warm accent on the figure */}
              <mesh geometry={G.box}
                position={[0.032, P.chestY - P.hipY + 0.012, 0.098]}
                scale={[0.030, 0.052, 0.008]} material={w.accent} />
              <mesh geometry={G.box}
                position={[0, P.chestY - P.hipY - 0.010, 0.104]}
                scale={[0.012, 0.115, 0.006]} material={w.accent} />

              {/* ---- head ---- */}
              <group position={[0, P.headY - P.hipY, 0]} rotation={[j.headX, j.headY, 0]}>
                <mesh geometry={G.sphere}
                  scale={[P.headRX * 2, P.headRY * 2, P.headRZ * 2]}
                  castShadow material={w.skin} />

                {w.hooded ? (
                  <mesh geometry={G.hood} position={[0, 0.010, -0.006]}
                    scale={[0.142, 0.158, 0.148]} castShadow material={w.shirt} />
                ) : (
                  <mesh geometry={G.hair} position={[0, 0.006, -0.004]}
                    scale={[0.121, 0.148, 0.129]} material={w.hair} />
                )}

                {w.capped ? (
                  <group position={[0, P.headRY * 0.86, 0]}>
                    <mesh geometry={G.cap} scale={[0.128, 0.088, 0.132]} castShadow material={w.shirt} />
                    <mesh geometry={G.box} position={[0, -0.004, 0.072]}
                      scale={[0.104, 0.010, 0.062]} castShadow material={w.shirt} />
                  </group>
                ) : null}

                {/* eyes — radius ≈ 12 % of head height */}
                <mesh geometry={G.sphereLow} position={[-eyeX, eyeY - P.headY, eyeZ]}
                  scale={[eyeR, eyeR, eyeR]} material={lib.eye} />
                <mesh geometry={G.sphereLow} position={[eyeX, eyeY - P.headY, eyeZ]}
                  scale={[eyeR, eyeR, eyeR]} material={lib.eye} />
              </group>

              {/* ---- arms ---- */}
              {([-1, 1] as const).map((side) => {
                const isL = side > 0;
                const swing = isL ? j.armL : j.armR;
                const spread = isL ? j.armLZ : j.armRZ;
                const flex = isL ? j.elbowL : j.elbowR;
                const twist = isL ? j.elbowLZ : j.elbowRZ;
                return (
                  <group
                    key={`arm${side}`}
                    position={[P.shoulderX * side, P.shoulderY - P.hipY, 0]}
                    rotation={[-swing, 0, spread]}
                  >
                    <mesh geometry={G.upperArm} position={[0, -P.upperArmLen / 2, 0]}
                      castShadow material={w.shirt} />
                    <group position={[0, -P.upperArmLen, 0]} rotation={[-flex, 0, twist]}>
                      <mesh geometry={G.sphereLow} scale={[0.058, 0.058, 0.058]} material={w.shirt} />
                      <mesh geometry={G.forearm} position={[0, -P.forearmLen / 2, 0]}
                        castShadow material={w.skin} />
                      <mesh geometry={G.sphere} position={[0, -P.forearmLen - 0.018, 0]}
                        scale={[0.034, 0.058, 0.021]} castShadow material={w.skin} />
                    </group>
                  </group>
                );
              })}
            </group>
          </group>
        </group>
      </group>
    </group>
  );
};

export default Character;
