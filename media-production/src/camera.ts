import {CatmullRomCurve3, Vector3} from 'three';
import {CAMERA, DURATION_IN_FRAMES, FPS} from './theme';
import {SHOTS, shotAt} from './story';

/**
 * One continuous glide. Every shot contributes a waypoint; the camera never cuts.
 *
 * Pacing: each waypoint-to-waypoint leg is eased (smoothstep) so the camera
 * settles on a beat and then accelerates into the next one — that is what reads
 * as "2–3 second glides" instead of one long drift.
 */

const v = (p: [number, number, number]) => new Vector3(p[0], p[1], p[2]);

const positions = SHOTS.map((s) => v(s.camera.pos));
const targets = SHOTS.map((s) => v(s.camera.lookAt));

// Catmull-Rom through every waypoint. `tension` low = lazy, cinematic arcs.
export const posCurve = new CatmullRomCurve3(positions, false, 'catmullrom', 0.4);
export const lookCurve = new CatmullRomCurve3(targets, false, 'catmullrom', 0.4);

const smoothstep = (t: number) => t * t * (3 - 2 * t);

/** Eased 0→1 parameter along the whole spline for a given frame. */
export const splineU = (frame: number): number => {
  const legs = SHOTS.length - 1;
  const shot = shotAt(frame);
  const i = shot.id - 1; // SHOTS ids are 1-based and contiguous

  if (i >= legs) return 1;

  const legStart = SHOTS[i].start;
  const legEnd = SHOTS[i + 1].start;
  const local = Math.min(1, Math.max(0, (frame - legStart) / (legEnd - legStart)));
  return (i + smoothstep(local)) / legs;
};

export type CameraState = {
  position: Vector3;
  lookAt: Vector3;
  /** Distance from camera to the subject — feeds the DOF focus + ink weight. */
  distance: number;
};

const tmpPos = new Vector3();
const tmpLook = new Vector3();

export const getCameraState = (frame: number): CameraState => {
  const u = splineU(frame);
  posCurve.getPoint(u, tmpPos);
  lookCurve.getPoint(u, tmpLook);

  const t = frame / FPS;

  // Slow orbital drift (2 deg/s) on a small radius, so the glide never feels
  // like it is running on rails.
  const orbit = (CAMERA.orbitDegPerSec * Math.PI) / 180;
  const ox = Math.cos(t * orbit) * CAMERA.orbitRadius;
  const oz = Math.sin(t * orbit) * CAMERA.orbitRadius;

  const position = new Vector3(tmpPos.x + ox, tmpPos.y + Math.sin(t * 0.27) * 0.28, tmpPos.z + oz);
  const lookAt = new Vector3(tmpLook.x, tmpLook.y, tmpLook.z);

  // Exponential smoothing on the look-at (style-bible lerp 0.08) so the framing
  // settles rather than snapping at each waypoint.
  lookAt.lerp(tmpLook, 1 - CAMERA.lerp);

  return {position, lookAt, distance: position.distanceTo(lookAt)};
};

/** Total path length in world units — used to report units/second. */
export const pathLength = posCurve.getLength();

/** Dolly rate actually achieved by this path. */
export const dollyUnitsPerSecond = pathLength / (DURATION_IN_FRAMES / FPS);
