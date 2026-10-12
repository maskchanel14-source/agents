# Visual brief schema reference

Derived from the `banana.visual-brief.v1` contract in
`AgriciDaniel/banana-claude` (`skills/banana/references/prompt-engineering.md`, MIT), adapted to
be generator-neutral.

Source: https://github.com/AgriciDaniel/banana-claude

## Full field reference

| Field | Type | Required | Purpose |
|---|---|---|---|
| `schema_version` | string | yes | Contract identifier. `banana.visual-brief.v1` |
| `revision` | int | on revision | Increments when a governing field changes |
| `supersedes` | string | on revision | The prior brief's hash |
| `change_log` | array | on revision | `{field, was, now, reason}` per change |
| `goal` | string | yes | What the image must communicate, one sentence |
| `facts` | string[] | yes | Claims that cannot change |
| `locks` | string[] | yes | Elements preserved exactly, each checkable by looking |
| `freedoms` | string[] | yes | What may vary |
| `direction` | object | yes | `mode`, `thesis`, `signature`, `avoid` |
| `composition` | string[] | yes | Framing, placement, negative-space assignment |
| `rendering` | string[] | yes | Light, material, optics, finish |
| `typography` | object | when text | `exact_copy`, `instructions` |
| `references` | array | when supplied | Role, purpose, subject_id per reference |

### `direction.mode`

- `creative` — the image should communicate an idea. The model may interpret.
- `preserve` — the image must reproduce supplied material. Interpretation is a defect.

### `direction.signature`

One concrete detail that no generic image would contain. Test: could this phrase appear in a
prompt for a different, unrelated image? If yes, it is not a signature.

| Weak | Strong |
|---|---|
| `warm lighting` | `one narrow stripe of dawn light crosses the front dial` |
| `interesting texture` | `two or three crumbs and a single loose hair on the cushion` |
| `moody atmosphere` | `the exact center of the frame falls on empty upholstery` |

## Writing locks that actually enforce

A lock must make the wrong outcome a **failure**, not merely a preference.

| Lock written | Why it fails to enforce |
|---|---|
| `subject should be off-center` | nothing makes a centered result a violation |
| `keep the mood consistent` | not checkable by looking |
| `preserve the product` | no criterion for what counts as preserved |

| Lock written | Why it enforces |
|---|---|
| `the subject is NOT in the center of the frame` | checkable, binary |
| `the sofa is upholstered in neutral linen, not glossy leather` | names both sides |
| `the light comes from a window, not flash` | names both sides |

**Also assign the leftover space a purpose.** Forbidding a centered subject without saying what
fills the rest of the frame leaves the model nowhere to put its attention, and the subject drifts
back. `the upper-left third belongs to the room, not the subject` closes that gap.

## Revision and change log

```json
{
  "schema_version": "banana.visual-brief.v1",
  "revision": 2,
  "supersedes": "<hash of revision 1>",
  "change_log": [
    {
      "field": "locks",
      "was": "(no lock about centering)",
      "now": "The subject is NOT in the center of the frame",
      "reason": "Revision 1 produced a centered subject. The old composition field said 'off-center' but no lock made centering a failure, so the deviation was noted without consequence."
    },
    {
      "field": "composition",
      "was": "(no negative-space assignment)",
      "now": "The upper-left third is given to window light and an out-of-focus houseplant",
      "reason": "Gives the model a purpose for the area the subject vacates. Without it, forbidding a centered subject alone caused it to drift back."
    }
  ]
}
```

The `reason` field is the point of the log. A future reader must be able to tell whether a field
is deliberate or accidental.

## Canonical hashing

The hash must be stable across formatting, editors, and line endings, so it is computed over a
**canonical** serialization, not the raw file:

```python
import json, hashlib
obj = json.load(open("brief.json"))
canonical = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
brief_sha256 = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
```

Sorted keys, no whitespace, UTF-8, non-ASCII preserved. Bind `brief_sha256` into every artifact
sidecar so a regenerated image can be traced to the exact brief that produced it.

## Artifact sidecar

Record alongside each generated artifact:

| Field | Purpose |
|---|---|
| `artifact_sha256` | Identify the exact bytes reviewed |
| `brief_sha256` | Identify the exact brief used |
| `supersedes_brief_sha256` | Revision lineage |
| `route`, `generator`, `reference_images` | How it was produced |
| `visual_review_status` | `pass`, `pass_with_notes`, `needs_review`, `blocked` |
| `p0_checks` | One entry per lock and fact, with the observed result |
| `open_deviations` | Misses that remain, or empty |
| `residual_notes` | Accepted imperfections and why they were accepted |

**Verification without pixels is not verification.** A successful tool response carries no
information about whether the image satisfies the brief. Record review status only after
inspecting the returned image, and list deviations even when the overall result passes — a
sidecar that only records successes is not a record.

## Worked example, minimal

```json
{
  "schema_version": "banana.visual-brief.v1",
  "goal": "A phone snapshot of an ordinary apartment, believable rather than attractive.",
  "facts": [
    "One adult tabby cat, asleep",
    "The room is genuinely lived in"
  ],
  "locks": [
    "The cat is NOT in the center of the frame",
    "The light is ambient overhead, not directional or dramatic"
  ],
  "freedoms": ["The exact clutter on the table", "The cat's pose within the right half"],
  "direction": {
    "mode": "creative",
    "thesis": "A boring photo taken by accident",
    "signature": "A charger cable running from a wall outlet to a phone on the cushion",
    "avoid": "Rule-of-thirds composition, soft window light, tidy staging"
  },
  "composition": [
    "Casual 4:3 horizontal, frame slightly tilted",
    "The right-hand two thirds hold the sofa; the left third holds the cluttered table",
    "Foreground object slightly out of focus for depth"
  ],
  "rendering": [
    "Flat overhead ambient light, open shadow, no interesting shadows",
    "White balance off toward yellow-green, dull low-contrast colors, low saturation",
    "Plain beige cotton slipcover, evenly colored and clean, soft creases from sitting",
    "Slight digital noise, soft details, average resolution"
  ]
}
```
