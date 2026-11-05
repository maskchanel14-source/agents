import React, {useMemo} from 'react';
import {useFrame, useThree} from '@react-three/fiber';
import {
  DepthTexture,
  HalfFloatType,
  LinearFilter,
  Mesh,
  OrthographicCamera,
  PlaneGeometry,
  RGBAFormat,
  Scene,
  ShaderMaterial,
  UnsignedIntType,
  Vector2,
  WebGLRenderTarget,
} from 'three';

/**
 * Lens blur — a self-contained depth-of-field pass.
 *
 * Why not `@react-three/postprocessing`'s <DepthOfField/>? Its EffectComposer
 * renders nothing at all under a software GL stack (SwiftShader), which is what
 * CI and headless renderers use. This pass is plain three.js: render the scene
 * into a target with a depth texture, then resolve it through a fullscreen quad
 * that blurs by circle-of-confusion. It behaves identically on a real GPU.
 *
 * Style-bible mapping (see theme.ts):
 *   focusDistance 2.5  → focal plane sits 2.5 world units in front of the subject
 *   aperture 0.05      → 10 px background blur (LENS.backgroundBlurPx)
 *   foreground blur    → 4 px for anything nearer than the focal plane
 */

const FRAG = /* glsl */ `
  precision highp float;

  uniform sampler2D uColor;
  uniform sampler2D uDepth;
  uniform vec2  uTexel;        // 1 / drawing-buffer size
  uniform float uNear;
  uniform float uFar;
  uniform float uFocus;        // world units from the camera
  uniform float uRange;        // world units either side of focus that stay sharp
  uniform float uBgPx;         // max background blur, px
  uniform float uFgPx;         // max foreground blur, px
  uniform float uExposure;

  varying vec2 vUv;

  // ---------------------------------------------------------------------
  // Tone mapping has to live HERE, not on the renderer.
  //
  // WebGLRenderer skips tone mapping entirely when the draw target is a
  // render target (WebGLRenderer.js: "if ( _currentRenderTarget === null ||
  // isXRRenderTarget )"), which is exactly the case for this pass — so
  // renderer.toneMapping and renderer.toneMappingExposure were both silently
  // ignored and every frame came out flat and untonemapped.
  //
  // Verbatim port of three's ACESFilmicToneMapping, renamed: three injects
  // tonemapping_pars_fragment into every non-raw ShaderMaterial, so the stock
  // names would collide and fail to compile.
  // ---------------------------------------------------------------------
  vec3 lensRRT( vec3 v ) {
    vec3 a = v * ( v + 0.0245786 ) - 0.000090537;
    vec3 b = v * ( 0.983729 * v + 0.4329510 ) + 0.238081;
    return a / b;
  }

  vec3 lensACES( vec3 color ) {
    const mat3 ACESInputMat = mat3(
      vec3( 0.59719, 0.07600, 0.02840 ),
      vec3( 0.35458, 0.90834, 0.13383 ),
      vec3( 0.04823, 0.01566, 0.83777 )
    );
    const mat3 ACESOutputMat = mat3(
      vec3(  1.60475, -0.10208, -0.00327 ),
      vec3( -0.53108,  1.10813, -0.07276 ),
      vec3( -0.07367, -0.00605,  1.07602 )
    );
    color *= uExposure / 0.6;
    color = ACESInputMat * color;
    color = lensRRT( color );
    color = ACESOutputMat * color;
    return clamp( color, 0.0, 1.0 );
  }

  // The scene is rendered into a *linear* target, so the blur happens in linear
  // light and this pass owns the sRGB encode on the way out.
  vec3 lensToSRGB(vec3 c) {
    c = max(c, vec3(0.0));
    return mix(1.055 * pow(c, vec3(1.0 / 2.4)) - 0.055, c * 12.92, step(c, vec3(0.0031308)));
  }

  float viewZ(float d) {
    float z = d * 2.0 - 1.0;                 // NDC
    return (2.0 * uNear * uFar) / (uFar + uNear - z * (uFar - uNear));
  }

  void main() {
    float dist   = viewZ(texture2D(uDepth, vUv).x);
    float signed = dist - uFocus;
    float coc    = clamp(abs(signed) / uRange, 0.0, 1.0);
    float radius = coc * (signed < 0.0 ? uFgPx : uBgPx);

    vec4 centre = texture2D(uColor, vUv);
    if (radius < 0.6) {
      gl_FragColor = vec4(lensToSRGB(lensACES(centre.rgb)), centre.a);
      return;
    }

    // 16-tap golden-angle disc. Cheap enough for software GL, smooth enough
    // that the bokeh does not read as a box blur.
    const int TAPS = 16;
    const float GOLDEN = 2.39996323;
    vec3 sum = centre.rgb * 1.6;
    float wsum = 1.6;

    for (int i = 0; i < TAPS; i++) {
      float fi = float(i);
      float a = fi * GOLDEN;
      float r = sqrt((fi + 0.5) / float(TAPS)) * radius;
      vec2 uv = vUv + vec2(cos(a), sin(a)) * r * uTexel;

      // Do not drag a sharp foreground pixel into a blurred background.
      float dz = viewZ(texture2D(uDepth, uv).x);
      float w = (dz >= uFocus - uRange * 0.5) ? 1.0 : 0.22;

      sum += texture2D(uColor, uv).rgb * w;
      wsum += w;
    }

    gl_FragColor = vec4(lensToSRGB(lensACES(sum / wsum)), centre.a);
  }
`;

const VERT = /* glsl */ `
  varying vec2 vUv;
  void main() {
    vUv = uv;
    gl_Position = vec4(position.xy, 0.0, 1.0);
  }
`;

export type LensBlurProps = {
  /** World-space distance from the camera to the focal plane. */
  focusWorld: number;
  /** Depth-of-field sharp band, in world units. */
  range?: number;
  /** Background blur in frame pixels (style bible: 8–12). */
  backgroundPx?: number;
  /** Foreground blur in frame pixels (style bible: 4). */
  foregroundPx?: number;
  /** ACES exposure applied on resolve (three skips it for render targets). */
  exposure?: number;
};

export const LensBlur: React.FC<LensBlurProps> = ({
  focusWorld,
  range = 12,
  backgroundPx = 10,
  foregroundPx = 4,
  exposure = 1,
}) => {
  const {gl, scene, camera, size} = useThree();

  const rig = useMemo(() => {
    const buf = gl.getDrawingBufferSize(new Vector2());
    const w = Math.max(2, Math.floor(buf.x));
    const h = Math.max(2, Math.floor(buf.y));

    const depth = new DepthTexture(w, h);
    depth.type = UnsignedIntType;
    depth.minFilter = LinearFilter;
    depth.magFilter = LinearFilter;

    // Half-float: the scene render is untonemapped linear, so sunlit surfaces
    // and the sky blow well past 1.0. An 8-bit target clipped them before the
    // ACES curve ever saw them, and banded everything below 0.05.
    const target = new WebGLRenderTarget(w, h, {
      format: RGBAFormat,
      type: HalfFloatType,
      minFilter: LinearFilter,
      magFilter: LinearFilter,
      depthBuffer: true,
      stencilBuffer: false,
      depthTexture: depth,
    });

    const material = new ShaderMaterial({
      vertexShader: VERT,
      fragmentShader: FRAG,
      depthTest: false,
      depthWrite: false,
      uniforms: {
        uColor: {value: target.texture},
        uDepth: {value: depth},
        uTexel: {value: new Vector2(1 / w, 1 / h)},
        uNear: {value: 0.1},
        uFar: {value: 220},
        uFocus: {value: 10},
        uRange: {value: range},
        uBgPx: {value: backgroundPx},
        uFgPx: {value: foregroundPx},
        uExposure: {value: exposure},
      },
    });

    const quadScene = new Scene();
    const quad = new Mesh(new PlaneGeometry(2, 2), material);
    quad.frustumCulled = false;
    quadScene.add(quad);

    const quadCamera = new OrthographicCamera(-1, 1, 1, -1, 0, 1);

    return {target, material, quadScene, quadCamera, depth};
  }, [gl, size.width, size.height, range, backgroundPx, foregroundPx]);

  const cam = camera as {near: number; far: number};
  rig.material.uniforms.uFocus.value = focusWorld;
  rig.material.uniforms.uExposure.value = exposure;
  rig.material.uniforms.uNear.value = cam.near;
  rig.material.uniforms.uFar.value = cam.far;

  useFrame(() => {
    gl.setRenderTarget(rig.target);
    gl.render(scene, camera);
    gl.setRenderTarget(null);
    gl.render(rig.quadScene, rig.quadCamera);
  }, 1);

  return null;
};
