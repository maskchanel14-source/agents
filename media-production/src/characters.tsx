import React, {useMemo, useRef} from 'react';
import {
  CanvasTexture, DoubleSide, LinearFilter, Mesh, PerspectiveCamera,
  ShaderMaterial, SRGBColorSpace, Vector3,
} from 'three';
import {FPS, INK, PALETTE, hexToRgb} from './theme';

const _worldPos = new Vector3();

/**
 * Characters are 2D planes living in the 3D world.
 *
 *  - one procedural canvas atlas holds every pose of every character
 *  - a ShaderMaterial picks the pose tile and boils the ink every frame:
 *      float jitter = sin(uTime * 10.0 + position.x * 5.0) * 0.008;
 *  - outline weight is dilated in screen pixels (2.5 px far → 4 px near)
 */

export type PoseName =
  | 'idle' | 'walkA' | 'walkB' | 'marchA' | 'marchB'
  | 'scared' | 'freeze' | 'type' | 'salute';

export const POSES: PoseName[] = [
  'idle', 'walkA', 'walkB', 'marchA', 'marchB',
  'scared', 'freeze', 'type', 'salute',
];

export type CharacterSpec = {
  key: string;
  skin: string;
  shirt: string;
  pants: string;
  accent: string;
  hooded?: boolean;
};

export const CHARACTERS = {
  guard: {
    key: 'guard',
    skin: PALETTE.paper,
    shirt: PALETTE.town,
    pants: PALETTE.shadow,
    accent: PALETTE.sun,
  },
  engineer: {
    key: 'engineer',
    skin: PALETTE.paper,
    shirt: PALETTE.pop,
    pants: PALETTE.shadow,
    accent: PALETTE.sky,
  },
  hacker: {
    key: 'hacker',
    skin: PALETTE.sun,
    shirt: PALETTE.shadow,
    pants: PALETTE.shadow,
    accent: PALETTE.sun,
    hooded: true,
  },
} satisfies Record<string, CharacterSpec>;

export type CharacterKey = keyof typeof CHARACTERS;

const TILE_W = 256;
const TILE_H = 512;
const OUTLINE_TILE_PX = 6; // ≈2.8 screen px at normal framing before dilation

type Limbs = {
  armL: number; // radians, 0 = straight down, + = forward
  armR: number;
  legL: number;
  legR: number;
  lean: number; // torso tilt
  headTilt: number;
  crouch: number; // vertical squash
};

const POSE_LIMBS: Record<PoseName, Limbs> = {
  idle:   {armL: 0.10, armR: -0.10, legL: 0.03, legR: -0.03, lean: 0.0,  headTilt: 0.0,  crouch: 0},
  walkA:  {armL: 0.55, armR: -0.45, legL: 0.45, legR: -0.40, lean: 0.04, headTilt: 0.02, crouch: 0.03},
  walkB:  {armL: -0.45, armR: 0.55, legL: -0.40, legR: 0.45, lean: 0.04, headTilt: -0.02, crouch: 0.03},
  marchA: {armL: 1.05, armR: -0.35, legL: 0.85, legR: -0.15, lean: -0.05, headTilt: 0.0, crouch: 0.02},
  marchB: {armL: -0.35, armR: 1.05, legL: -0.15, legR: 0.85, lean: -0.05, headTilt: 0.0, crouch: 0.02},
  scared: {armL: -1.35, armR: 1.35, legL: 0.12, legR: -0.12, lean: -0.14, headTilt: -0.12, crouch: 0.10},
  freeze: {armL: -1.15, armR: 1.15, legL: 0.05, legR: -0.05, lean: -0.06, headTilt: -0.06, crouch: 0.06},
  type:   {armL: -0.95, armR: 0.95, legL: 0.08, legR: -0.08, lean: 0.22, headTilt: 0.16, crouch: 0.05},
  salute: {armL: 0.05, armR: -2.25, legL: 0.02, legR: -0.02, lean: -0.03, headTilt: 0.0, crouch: 0},
};

// ---------------------------------------------------------------------------
// Procedural sprite drawing
// ---------------------------------------------------------------------------
const roundRect = (
  ctx: CanvasRenderingContext2D,
  x: number, y: number, w: number, h: number, r: number,
) => {
  const rr = Math.min(r, w / 2, h / 2);
  ctx.beginPath();
  ctx.moveTo(x + rr, y);
  ctx.arcTo(x + w, y, x + w, y + h, rr);
  ctx.arcTo(x + w, y + h, x, y + h, rr);
  ctx.arcTo(x, y + h, x, y, rr);
  ctx.arcTo(x, y, x + w, y, rr);
  ctx.closePath();
};

/** Stroke-then-fill so every shape carries its own ink line. */
const ink = (
  ctx: CanvasRenderingContext2D,
  fill: string,
  draw: () => void,
) => {
  draw();
  ctx.fillStyle = fill;
  ctx.fill();
  ctx.lineWidth = OUTLINE_TILE_PX;
  ctx.strokeStyle = PALETTE.shadow;
  ctx.lineJoin = 'round';
  ctx.lineCap = 'round';
  ctx.stroke();
};

const limb = (
  ctx: CanvasRenderingContext2D,
  x: number, y: number, len: number, thick: number, angle: number, fill: string,
) => {
  ctx.save();
  ctx.translate(x, y);
  ctx.rotate(angle);
  ink(ctx, fill, () => roundRect(ctx, -thick / 2, 0, thick, len, thick * 0.45));
  ctx.restore();
};

const drawCharacter = (
  ctx: CanvasRenderingContext2D,
  ox: number, oy: number,
  spec: CharacterSpec,
  pose: PoseName,
) => {
  const L = POSE_LIMBS[pose];
  const cx = ox + TILE_W / 2;
  const groundY = oy + TILE_H * 0.965;

  const scale = 1 - L.crouch;
  const headR = TILE_W * 0.165;
  const torsoH = TILE_H * 0.30 * scale;
  const torsoW = TILE_W * 0.36;
  const legLen = TILE_H * 0.30 * scale;
  const armLen = TILE_H * 0.26 * scale;

  const hipY = groundY - legLen;
  const shoulderY = hipY - torsoH;
  const headCY = shoulderY - headR * 1.02;

  ctx.save();
  ctx.translate(cx, groundY);
  ctx.rotate(L.lean);
  ctx.translate(-cx, -groundY);

  // --- legs
  limb(ctx, cx - torsoW * 0.24, hipY, legLen, torsoW * 0.30, L.legL, spec.pants);
  limb(ctx, cx + torsoW * 0.24, hipY, legLen, torsoW * 0.30, L.legR, spec.pants);

  // --- torso
  ink(ctx, spec.shirt, () =>
    roundRect(ctx, cx - torsoW / 2, shoulderY, torsoW, torsoH, torsoW * 0.34));

  // --- accent (guard badge / engineer lanyard)
  ink(ctx, spec.accent, () =>
    roundRect(ctx, cx - torsoW * 0.12, shoulderY + torsoH * 0.18, torsoW * 0.24, torsoH * 0.20, 4));

  // --- arms
  limb(ctx, cx - torsoW * 0.52, shoulderY + torsoH * 0.06, armLen, torsoW * 0.24, L.armL, spec.shirt);
  limb(ctx, cx + torsoW * 0.52, shoulderY + torsoH * 0.06, armLen, torsoW * 0.24, L.armR, spec.shirt);

  // hands
  ink(ctx, spec.skin, () => {
    ctx.beginPath();
    ctx.arc(
      cx - torsoW * 0.52 + Math.sin(L.armL) * armLen,
      shoulderY + torsoH * 0.06 + Math.cos(L.armL) * armLen,
      torsoW * 0.13, 0, Math.PI * 2);
  });
  ink(ctx, spec.skin, () => {
    ctx.beginPath();
    ctx.arc(
      cx + torsoW * 0.52 + Math.sin(L.armR) * armLen,
      shoulderY + torsoH * 0.06 + Math.cos(L.armR) * armLen,
      torsoW * 0.13, 0, Math.PI * 2);
  });

  // --- head
  ctx.save();
  ctx.translate(cx, headCY);
  ctx.rotate(L.headTilt);

  if (spec.hooded) {
    // Hood: a big shadow-coloured cowl with the face lost inside it.
    ink(ctx, spec.shirt, () => {
      ctx.beginPath();
      ctx.moveTo(0, -headR * 1.45);
      ctx.bezierCurveTo(headR * 1.35, -headR * 1.30, headR * 1.22, headR * 0.55, 0, headR * 1.05);
      ctx.bezierCurveTo(-headR * 1.22, headR * 0.55, -headR * 1.35, -headR * 1.30, 0, -headR * 1.45);
      ctx.closePath();
    });
    // Face void
    ink(ctx, PALETTE.shadow, () => {
      ctx.beginPath();
      ctx.ellipse(0, -headR * 0.05, headR * 0.62, headR * 0.78, 0, 0, Math.PI * 2);
    });
  } else {
    ink(ctx, spec.skin, () => {
      ctx.beginPath();
      ctx.arc(0, 0, headR, 0, Math.PI * 2);
    });
  }

  // Eyes: diameter = 12 % of head diameter → radius = 0.12 * headR.
  const eyeR = headR * 0.12;
  const eyeY = spec.hooded ? -headR * 0.12 : -headR * 0.10;
  const eyeX = headR * (spec.hooded ? 0.26 : 0.32);
  ctx.fillStyle = PALETTE.shadow;
  ctx.beginPath();
  ctx.arc(-eyeX, eyeY, eyeR, 0, Math.PI * 2);
  ctx.fill();
  ctx.beginPath();
  ctx.arc(eyeX, eyeY, eyeR, 0, Math.PI * 2);
  ctx.fill();

  ctx.restore();
  ctx.restore();
};

/** One atlas: columns = poses, rows = characters. */
export const buildCharacterAtlas = (): CanvasTexture => {
  const rows = Object.values(CHARACTERS) as CharacterSpec[];
  const c = document.createElement('canvas');
  c.width = TILE_W * POSES.length;
  c.height = TILE_H * rows.length;
  const ctx = c.getContext('2d')!;
  ctx.clearRect(0, 0, c.width, c.height);

  rows.forEach((spec, r) => {
    POSES.forEach((pose, p) => {
      drawCharacter(ctx, p * TILE_W, r * TILE_H, spec, pose);
    });
  });

  const tex = new CanvasTexture(c);
  tex.colorSpace = SRGBColorSpace;
  tex.minFilter = LinearFilter;
  tex.magFilter = LinearFilter;
  tex.generateMipmaps = false;
  return tex;
};

// ---------------------------------------------------------------------------
// Ink material — boiling outline, pose tile, distance-scaled line weight
// ---------------------------------------------------------------------------
const VERT = /* glsl */ `
  varying vec2 vUv;
  void main() {
    vUv = uv;
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
  }
`;

const FRAG = /* glsl */ `
  precision highp float;
  uniform sampler2D uAtlas;
  uniform vec2  uTile;        // (col, row) of the current pose
  uniform vec2  uTileCount;   // (cols, rows)
  uniform float uTime;
  uniform float uPxToUvY;     // 1 / on-screen height in px
  uniform float uInkWidth;    // 2.5 .. 4.0 screen px
  uniform float uFrozen;      // 0..1 ice tint
  uniform float uOpacity;
  uniform vec3  uIceColor;
  varying vec2 vUv;

  vec4 tile(vec2 uv) {
    return texture2D(uAtlas, (clamp(uv, 0.0, 1.0) + uTile) / uTileCount);
  }

  void main() {
    // ---- ink boiling: the classic hand-drawn line wobble -------------------
    // spec: float jitter = sin(uTime * 10.0 + position.x * 5.0) * 0.008;
    float jitter = sin(uTime * ${INK.boilSpeed.toFixed(1)} + vUv.x * ${INK.boilSpread.toFixed(1)})
                 * ${INK.boilAmount.toFixed(3)};

    // ...rescaled so the wobble measures 0.3–0.8 px on screen, not in UV.
    float boilPx = mix(${INK.boilMinPx}, ${INK.boilMaxPx},
                       0.5 + 0.5 * sin(uTime * 3.0 + vUv.y * 9.0));
    vec2 uv = vUv + vec2(jitter * 0.35, jitter) + vec2(boilPx * uPxToUvY * 0.5);

    // ---- distance-scaled outline weight -----------------------------------
    float extraPx = clamp((uInkWidth - ${INK.minPx.toFixed(1)}) / (${INK.maxPx.toFixed(1)} - ${INK.minPx.toFixed(1)}), 0.0, 1.0) * 1.2;
    float d = extraPx * uPxToUvY;
    vec4 t = tile(uv);
    float a = t.a;
    a = max(a, tile(uv + vec2( d, 0.0)).a);
    a = max(a, tile(uv + vec2(-d, 0.0)).a);
    a = max(a, tile(uv + vec2(0.0,  d)).a);
    a = max(a, tile(uv + vec2(0.0, -d)).a);

    if (a < 0.02) discard;

    vec3 col = t.rgb;
    col = mix(col, uIceColor, uFrozen * 0.72);
    gl_FragColor = vec4(col, a * uOpacity);
  }
`;

export type InkUniforms = {
  uAtlas: {value: CanvasTexture | null};
  uTile: {value: [number, number]};
  uTileCount: {value: [number, number]};
  uTime: {value: number};
  uPxToUvY: {value: number};
  uInkWidth: {value: number};
  uFrozen: {value: number};
  uOpacity: {value: number};
  uIceColor: {value: [number, number, number]};
};

export const createInkMaterial = (atlas: CanvasTexture, row: number) =>
  new ShaderMaterial({
    vertexShader: VERT,
    fragmentShader: FRAG,
    transparent: true,
    depthWrite: true,
    side: DoubleSide,
    uniforms: {
      uAtlas: {value: atlas},
      uTile: {value: [0, row]},
      uTileCount: {value: [POSES.length, Object.keys(CHARACTERS).length]},
      uTime: {value: 0},
      uPxToUvY: {value: 1 / 300},
      uInkWidth: {value: INK.minPx},
      uFrozen: {value: 0},
      uOpacity: {value: 1},
      uIceColor: {value: hexToRgb(PALETTE.sky)},
    } as unknown as InkUniforms,
  });

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------
const ROW_OF: Record<CharacterKey, number> = {guard: 0, engineer: 1, hacker: 2};

/** Two-frame walk cycle / marching cycle for the current action. */
export const poseForAction = (action: string, t: number): PoseName => {
  const step = Math.floor(t * 3.2) % 2 === 0;
  switch (action) {
    case 'walk': return step ? 'walkA' : 'walkB';
    case 'march': return step ? 'marchA' : 'marchB';
    case 'scared': return 'scared';
    case 'freeze': return 'freeze';
    case 'type': return Math.floor(t * 5.0) % 4 === 0 ? 'type' : 'idle';
    case 'salute': return 'salute';
    default: return Math.floor(t * 1.4) % 7 === 0 ? (step ? 'walkA' : 'idle') : 'idle';
  }
};

export type CharacterProps = {
  who: CharacterKey;
  action: string;
  position: [number, number, number];
  /** World-space height of the plane in units. */
  height?: number;
  frozen?: number;
  opacity?: number;
  faceCamera?: boolean;
  bob?: number;
  /** Remotion frame — drives every animation so renders are deterministic. */
  frame: number;
  /** Live camera position, for billboarding + distance-based ink weight. */
  cameraPos: [number, number, number];
  fov?: number;
  viewportHeightPx?: number;
};

export const Character: React.FC<CharacterProps> = ({
  who, action, position, height = 2.6, frozen = 0, opacity = 1,
  faceCamera = true, bob = 1, frame, cameraPos, fov = 42, viewportHeightPx = 1920,
}) => {
  const atlas = useMemo(buildCharacterAtlas, []);
  const material = useMemo(() => createInkMaterial(atlas, ROW_OF[who]), [atlas, who]);
  const mesh = useRef<Mesh>(null);

  const t = frame / FPS;
  const pose = poseForAction(action, t);
  const u = material.uniforms as unknown as InkUniforms;

  u.uTime.value = t;
  u.uTile.value[0] = POSES.indexOf(pose);
  u.uFrozen.value = frozen;
  u.uOpacity.value = opacity;

  // Screen height of this plane → converts screen px to UV for ink + boil.
  const bobY = Math.sin(t * 3.2) * 0.045 * bob;
  const dist = Math.hypot(
    cameraPos[0] - position[0],
    cameraPos[1] - (position[1] + bobY),
    cameraPos[2] - position[2],
  );
  const worldPerPx = (2 * Math.tan((fov * Math.PI) / 360) * dist) / viewportHeightPx;
  u.uPxToUvY.value = 1 / Math.max(40, height / worldPerPx);

  // Outline weight: 4 px near → 2.5 px far.
  const near = 6;
  const far = 46;
  const k = Math.min(1, Math.max(0, (dist - near) / (far - near)));
  u.uInkWidth.value = INK.maxPx - (INK.maxPx - INK.minPx) * k;

  const rotationY = faceCamera
    ? Math.atan2(cameraPos[0] - position[0], cameraPos[2] - position[2])
    : 0;

  const width = height * (TILE_W / TILE_H);

  return (
    <mesh
      ref={mesh}
      position={[position[0], position[1] + bobY, position[2]]}
      rotation={[0, rotationY, 0]}
      material={material}
      castShadow
    >
      <planeGeometry args={[width, height]} />
    </mesh>
  );
};
