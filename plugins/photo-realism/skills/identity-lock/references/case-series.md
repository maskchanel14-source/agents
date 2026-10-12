# Case series: one cat, three generations, two anchors tested

Recorded because the middle generation fails in the most instructive way available: it does
everything right and still loses the subject.

## Goal

A believable phone snapshot of a tabby cat asleep on a sofa (the same subject as the plugin's
first case study), iterated under the director loop: brief, prompt, generate, inspect pixels,
diagnose, fix one field. The series doubles as an identity experiment — the identity block was
frozen from generation 1 onward, so any change in the cat is the method's fault, not the
prompt's.

## The frozen identity block

```text
ordinary tabby cat: dark grey-brown stripes, a white chest patch, a small notch in the left
ear tip
```

Plus the realism locks: casual 4:3 in the opening sentence, one-handed shooting logic, flat
grey-yellow cast, plain beige slipcover declared intact (damage prior), one causal
imperfection, closing negations.

## Generation 1 — realism lands, one physical-evidence failure

The brief's causal imperfection was assigned to the tail: `the tail flicked once right before
the shutter, so slight motion softness is limited to the tail tip only`.

**Result:** the aesthetic and the imperfection both landed — motion softness confined to the
lower tail while face and body stayed sharp; slipcover clean and uniform; paw hanging off the
cushion; residual color-temperature split between cool window light and warm lamp.

**One defect:** the phone charger rendered **standing upright** on the cushion with its cable
loop floating slightly above the fabric — no plausible contact. Physical evidence was the
weakest layer in the frame.

## Generation 2 — one field fixed by regeneration; identity lost

Prompt identical except the charger field, rewritten with contact language:
`a black phone charger adapter lying flat on the cushion with its cable resting along the
fabric in a loose loop, both pressing the cloth slightly and casting soft contact shadows`.
No reference image supplied — deliberately, to test the frozen text block as the only anchor.

**Result:**

- **Charger fixed.** Flat adapter, cable following the cloth, contact shadows present.
- **Identity lost.** The output cat is a different individual: cooler silver-grey coat,
  classic blotched pattern instead of mackerel stripes, white chest patch weakened, ear notch
  absent. Same *type*, different *cat*.
- The whole scene also re-rolled (different room, sofa, pose) — expected from a full
  regeneration, and the reason field fixes do not belong there.

**The finding:**

> A frozen text identity block locks the type, not the individual. Independent generations
> from the same block sample different members of the described category. Individual-level
> consistency requires a visual anchor.

This matches, in a new domain, the plugin's damage-prior lesson: the mechanism is not the
model forgetting the words, it is the model sampling from somewhere the words point at.

## Generation 3 — the repair path locks identity and fixes the field

Framed as an edit, not a regeneration: generation 1 passed as base image in slot 1, prompt
opened with `You are performing a SINGLE, TARGETED EDIT on IMAGE 1 ... this is a repair edit,
not a regeneration and not a retouch`, named the one edit (charger flat with contact shadows),
then an explicit preserve-list: same cat, same pose, same markings, same notch, same tail
softness, same slipcover, same clutter, same cast, same noise, `do not beautify, do not
sharpen, do not brighten`.

**Result:**

- **Charger fixed** and **identity preserved** — same individual as generation 1, markings and
  notch intact, tail softness intact.
- **Repair creep:** the frame came back slightly brighter and cleaner than the base — the
  slipcover shifted toward white, noise reduced — despite the explicit prohibition. Edits
  re-render through a quality prior; the preserve-list narrows the creep but does not close
  it. Recorded as a failure mode in `smartphone-realism` `references/failure-modes.md`.

## Transferable rules

1. **Text identity blocks are type anchors.** Use them to keep a series coherent in palette
   and marking class; do not promise a user the same individual from text alone.
2. **Field fixes belong to edits, not regenerations.** Regeneration re-rolls the scene; an
   edit with the base in slot 1 changes one field in place.
3. **The preserve-list must include the ugly parts.** Color cast, noise level, and softness
   are exactly what an edit silently "improves"; name them or lose them.
4. **Assign imperfections a cause and a boundary.** `motion softness limited to the tail tip
   because the tail moved` survived all three generations; scatter-shot noise language would
   not have. (Prior art for causal imperfection: `aidenli/krea2-photography-prompt-skills`,
   unlicensed — idea referenced, no text copied.)
5. **Verify per field, per generation.** Generation 2's tool response reported success while
   the subject quietly changed species-of-one.

## What this series does not establish

- Whether a visual anchor holds identity across a *different* generator; all three runs used
  one image tool.
- Quantitative identity scores; the drift verdict here is human inspection of markings, not
  an embedding number (see `measuring.md` for the instrumented version).
- Whether the repair creep magnitude is model-specific. It was observed once, explicitly
  forbidden, and still present; treat the direction as general and the size as unmeasured.
