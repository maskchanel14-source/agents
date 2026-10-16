# State Management, Pitfalls & Templates

## metadata.json Schema

```json
{
  "projectId": "",
  "projectTitle": "",
  "designSystemId": "",
  "screens": {
    "desktop": {
      "current": "",
      "history": []
    },
    "mobile": {
      "current": "",
      "history": []
    }
  },
  "interview": {
    "projectName": "",
    "description": "",
    "targetUsers": "",
    "cta": "",
    "brandFeel": [],
    "colorMode": "",
    "primaryColor": "",
    "colorVariant": "",
    "headlineFont": "",
    "bodyFont": "",
    "roundness": ""
  },
  "iterationCount": 0,
  "assumptions": [],
  "qa": {
    "staticValidator": "not_run",
    "browserReviewed": false,
    "testedViewports": [],
    "knownLimitations": []
  },
  "status": "briefing"
}
```

## State Management Rules

- Create `.stitch/` directory at project start.
- Write `metadata.json` after every state-changing operation (project creation, design system creation, screen generation, edit, variant selection, approval).
- **Status flow:** `briefing` (or legacy `interview`) --> `designing` --> `qa` --> `ready_for_review` --> `approved` --> `delivered`.
- Persist assumptions, static-validator result, tested viewports and known limitations in the `assumptions` and `qa` fields; never mark an unrun check as passed.
- If `metadata.json` exists when the skill starts:
  - `briefing` / `interview`: extract known inputs and ask only for material unknowns.
  - `designing`: open the latest saved HTML where possible and continue local refinement.
  - `qa`: resume the missing static/browser checks and update their recorded status.
  - `ready_for_review`: present the preview and concise QA summary; do not redo completed checks.
  - `approved`: prepare the delivery bundle.
  - `delivered`: report the existing bundle and revise only if requested.

---

## Common Pitfalls

| Pitfall | Wrong | Right |
|---------|-------|-------|
| Blocking an immediate build on a long interview | Requiring every brand preference before drafting | Extract supplied facts, use documented defaults, and ask only for material unknowns |
| Asking for image uploads | "Can you share your logo?" | Never ask. If user sends one, extract style and save original. |
| Translating CSS feedback literally | Passing "add padding-top: 40px" to Stitch | Translate to design intent: "Add more breathing room above the headline" |
| Overloading prompts | 500-word generation prompt | 6-8 sentences. One sentence per section. |
| Skipping browser preview | Describing the result in text | Open the actual HTML in a browser where available; if unavailable, state that the page is not browser-reviewed. |
| Retrying slow generation | Calling generate again after 30 seconds | Wait. Use `get_screen` to check if it completed. |
| Skipping update_design_system | Only calling create_design_system | Must call update immediately after create. |
| Hardcoding tool names | `create_project(...)` | Discover namespace via `list_tools` first. |
| Ignoring output_components | Skipping Stitch suggestions | Present any generation suggestions to the user. |
| Too many interview questions | Fixed survey or repeated approval checks | Ask once for critical missing facts; proceed on reversible design choices using recorded assumptions. |
| Desktop-only by default | Treating the mobile screen as optional | Generate a mobile counterpart and merge its decisions into one responsive page. |
| Generic conversion filler | Inventing testimonials, metrics or urgency | Use verified evidence or omit the claim. |
| Motion without an exit | Adding entrance/scroll animation only | Respect `prefers-reduced-motion`; content must remain visible without JavaScript. |
| Claiming launch readiness too early | Trusting generated HTML or a design render | Run static QA and browser checks; report unverified items honestly. |
| Fake form or CTA | Styling a control with no destination/handler | Wire a verified action or label it as a placeholder; never imply submission succeeded. |

---

## DEPLOY.md Template

Use this template when generating the deployment checklist. Keep the status truthful and update every item to match the actual bundle:

```markdown
# {Project Name} — Landing Page

## Bundle contents
- `index.html` — one responsive page
- `design/DESIGN.md` — brand system and rationale
- `design/color-tokens.json` — design tokens
- `assets/` — approved/licensed assets only

## QA status
- Static validator: {pass / warnings / not run}
- Real browser reviewed: {yes / no}
- Viewports checked: {list or not checked}
- Keyboard/interaction review: {status}
- Forms and CTA destinations: {verified details or placeholder warning}
- Known limitations: {list; write “none known” only if checked}
- Owner approval/publication: {pending / approved / not applicable}

## Design tokens
- Primary color: {name} ({hex})
- Headline/body font: {pairing}
- Border radius: {description}
- Color mode: {light/dark}

## Before deployment
1. Replace any explicitly marked placeholder with verified, owner-approved content.
2. Confirm all CTA links, phone/email/booking routes and form handlers work.
3. Confirm image rights, alt text, loading behavior and responsive crops.
4. Recheck title, description, social metadata, canonical URL and indexability for the real domain.
5. Review privacy notice, data collection, third-party scripts and analytics; do not add tracking by default.
6. Run the static validator and browser checks listed above; record failures and unresolved items.
7. Obtain any owner authorization required for publication and confirm the deployment target.

## Design decisions
{2–3 sentences explaining the key choices and any assumptions}
```

Do not call a bundle deployment-ready while required QA or owner-approved facts remain outstanding.
