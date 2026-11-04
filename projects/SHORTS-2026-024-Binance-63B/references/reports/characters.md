# AGENT 4 — characters

**Question:** do the 2D characters read as 2D planes living in the 3D world?
Is the eye size right?

## Method
`src/characters.tsx`. One procedural canvas atlas (9 poses × 3 characters,
256×512 per tile, 2304×1536 total), sampled by a `ShaderMaterial` that picks the
pose tile and boils the ink.

| Property | Value | Style bible | Verdict |
| --- | --- | --- | --- |
| Form | 2D `planeGeometry` billboards in 3D | 2D planes in 3D | PASS |
| Eye size | `eyeR = headR × 0.12` → 12 % of head diameter | 12 % of head | PASS |
| Limbs | simple rounded rects, stroked then filled | simple | PASS |
| Poses | 9 (idle, walkA/B, marchA/B, scared, freeze, type, salute) | — | PASS |
| Billboarding | `rotation.y = atan2(camX − px, camZ − pz)`, per frame | — | PASS |
| Parallax vs town | 5 % | 5 % | PASS |

## Findings

1. **Characters compile and draw**, and the ink shader now compiles cleanly —
   the first full render crashed the browser on frame 0 because
   `${INK.maxPx}` interpolated as the integer literal `4`, giving GLSL
   `4 - 2.5` (int − float). Fixed with `.toFixed(1)` on every interpolated
   constant.

2. **They are too small to carry the frame.** On the rendered stills the
   characters occupy a few percent of frame height in every shot except the two
   tower close-ups. Measured palette coverage of `#FF6B6B` (the "char pop"
   colour that is meant to make characters pop) is **0.0 % on 8 of 9 stills**.
   The pop colour is only on the engineer's shirt, the vault roof, gable roofs
   and the Bitcoin lane rails — all of which are small or far away.

3. **Casting is thin.** Three named actors (guard, engineer, hacker) plus four
   townsfolk, but the townsfolk reuse the guard/engineer sprites at 2.3 u, so the
   crowd reads as duplicates at anything but close range.

4. The engineer in the tower window (shot 7) is the one place a character is
   properly readable — it is framed at ~1.8 u against a lit window.

## FIX

- **F1 (needs re-render):** raise character heights — guard 2.9 → 4.2 u, hacker
  2.7 → 3.8 u, townsfolk 2.3 → 3.2 u. At the current camera distances that puts
  them at roughly 8–14 % of frame height instead of 3–5 %.
- **F2:** move the guard from x −6.2 to x −5.0 so the vault-plaza shot frames
  them against the gold vault rather than against dark town.
- **F3:** give the townsfolk a fourth sprite (a `pop`-shirted variant) so the
  crowd is not two copies, and add `pop` to the guard's badge so the pop colour
  registers in the wide shots.
- **F4:** the `type` pose flickers back to `idle` on 3 of every 4 half-beats
  (`Math.floor(t * 5) % 4 === 0`). It reads as a twitch; make it a clean two-frame
  cycle like the walk.
