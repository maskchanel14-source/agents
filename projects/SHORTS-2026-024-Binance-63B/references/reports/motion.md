# AGENT 1 — motion

**Question:** is the camera gliding smoothly, with no hard cuts?

## Method
`src/camera.ts` builds one `CatmullRomCurve3` through all 9 shot waypoints and
samples it by an eased global parameter. Measured by walking all 2010 frames
(`src/_camstats.ts` during QA):

| Metric | Measured | Style bible | Verdict |
| --- | --- | --- | --- |
| Hard cuts | **0** in 2010 frames | 0 | PASS |
| Path length | 180.5 units | — | — |
| Dolly rate | **2.694 u/s** | 0.8 u/s | **MISS (3.4×)** |
| Max per-frame step | 0.4588 u | — | smooth (≈ 13.8 u/s peak) |
| Max look-at swing | 1.095 °/frame (32.9 °/s) | — | peak only, at waypoint transitions |
| Look-at smoothing | `lerp 0.08` | 0.08 | PASS |
| Orbit | 2 °/s on a 1.15 u radius | 2 °/s | PASS |
| Parallax | 5 % between planes and town | 5 % | PASS |

Per-shot travel:

```
shot 1   f0-200    dist 71.4 -> 33.9   travel 19.8 u
shot 2   f200-455  dist 33.9 -> 42.0   travel 20.9 u
shot 3   f455-705  dist 42.0 -> 32.5   travel 28.6 u
shot 4   f705-910  dist 32.5 -> 14.7   travel 18.3 u
shot 5   f910-1060 dist 14.7 -> 19.1   travel 16.8 u
shot 6   f1060-1400 dist 19.1 -> 8.0   travel 11.4 u
shot 7   f1400-1530 dist 8.0 -> 24.7   travel 20.5 u
shot 8   f1530-1685 dist 24.7 -> 59.5  travel 40.8 u
shot 9   f1685-2010 dist 59.5 -> 59.2  travel 0.5 u
```

## Findings

1. **The glide is genuinely continuous.** Position and look-at are both spline
   samples, so there is no discontinuity anywhere in 2010 frames. Max per-frame
   step of 0.46 u is well under 1 % of the shot distance — no visible jumps.

2. **Dolly rate misses the bible by 3.4×.** 0.8 u/s over 67 s is 54 units of
   travel total, but the 9 beats are spread across a town that is ~110 units
   wide, so the path is 180.5 u. The camera is not "fast" per frame — it is
   covering more ground than a 0.8 u/s short ever could.

3. **Shot 9 barely moves** (0.5 u over 10.8 s). It is the final hold on the
   payoff card; fine as a deliberate settle, but note it is the only static beat.

## FIX

- **F1 (real fix, needs re-render):** compress the world so the same 9 beats fit
  in ~60–70 units of travel — move the clock tower from x −30 to x −14, the dev
  tower from z −11 to z −6, and shrink the bridge fan from 26 u to 16 u. That
  lands dolly at ≈ 1.0 u/s without changing any framing.
- **F2 (cheap):** keep the path but raise `DURATION_IN_FRAMES` — at 2010 frames
  the rate is fixed by path length, so only a shorter path or a longer runtime
  moves it.
- **F3:** the look-at peak of 32.9 °/s happens exactly at waypoint transitions.
  Widen the smoothstep (currently `t²(3−2t)`) to a smootherstep `t³(6t²−15t+10)`
  if any transition reads as a whip pan on a real display.
