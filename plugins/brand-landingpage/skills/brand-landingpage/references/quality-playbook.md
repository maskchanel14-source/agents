# Landing-page quality playbook

Use this after the visual generator or first local draft returns HTML and before calling a page “finished” or “deployment-ready.” Generated markup is a starting point, not a substitute for content verification, responsive implementation, accessibility, motion design, or browser QA.

## Definition of done

A landing page is ready for user review only when:

1. **The message is specific.** A visitor can identify the offer, audience, main benefit and next step without decoding jargon. Use one primary CTA; keep secondary actions visually quieter.
2. **The content is true.** Use only facts, prices, addresses, hours, testimonials, statistics, guarantees, credentials and customer logos that the user verified or supplied. If a fact is unknown, omit it or label it as a placeholder for review. Never invent social proof.
3. **The composition has a point of view.** Match the visual route to the brand and category. Use intentional hierarchy, contrast, whitespace, image crop and section rhythm; avoid repeating the same generic three-card grid in every section.
4. **The page works at desktop and mobile sizes.** Deliver one responsive page by default, not two disconnected production pages. The mobile variant is a design/reference input; merge its useful decisions into the responsive HTML/CSS.
5. **Interactions work.** Every CTA has a real destination or a clearly disclosed placeholder. Do not ship `href="#"`, inert buttons, pretend forms, fake booking flows or contact details that were not verified.
6. **Accessibility has been checked.** Use semantic landmarks, a logical heading hierarchy, accessible names, visible keyboard focus, meaningful image alternatives, labelled fields, sufficient contrast and a usable reduced-motion mode.
7. **Performance and metadata are reasonable.** Size images, prevent layout shift, prioritize the hero asset, lazy-load below-the-fold media, use descriptive title/description, and avoid third-party trackers by default.
8. **A real browser preview was inspected.** Check desktop and mobile in an actual browser where available. A generated canvas/Pillow render is a design render, not a browser screenshot. If browser QA cannot run, state exactly what remains unverified and do not claim deployment readiness.

## Visual hierarchy and conversion

- Keep the first viewport focused: recognizable brand, one clear headline, one explanatory sentence, primary CTA and a relevant visual.
- Make the headline promise concrete. Avoid generic filler such as “Elevate your experience” unless it is made specific by the supporting copy.
- Put proof next to the claim it supports. Use real proof only; otherwise replace testimonials and metrics with specific service/process information.
- Use a deliberate page rhythm: alternate dense and open sections, vary composition where it helps comprehension, and keep body-copy line length comfortable.
- Keep navigation short and task-oriented. A small local business usually needs service/menu, location or service area, hours if verified, and one enquiry route—not a SaaS feature taxonomy.
- Repeat the main action at a natural decision point, not after every section. Use consistent CTA wording.
- Use real, licensed or owner-approved imagery for production. Clearly label generated or placeholder imagery in private review materials; never imply an AI image depicts a real product, venue, person or customer.

## Motion choreography

Motion should explain hierarchy or state, not decorate every element. Make the page fully readable and usable before any animation runs.

| Moment | Recommended treatment | Avoid |
|---|---|---|
| Initial load | Show content immediately; optionally reveal a small hero group with a single 250–450 ms opacity/8–16 px translate. Stagger only closely related items by about 50–90 ms. | Hiding core copy until JavaScript runs; long entrance sequences; moving the whole page. |
| Scroll entry | Optional one-time 180–320 ms reveal for nonessential section visuals. Use IntersectionObserver as progressive enhancement; leave content visible if JS/API is unavailable. | Scroll-jacking, parallax as a default, repeating reveal on every scroll, or animating every paragraph/card. |
| Hover/press | Short 120–200 ms color/opacity change or a subtle 1–2 px lift. Keep layout dimensions stable. | Large scaling, bouncing, flashing, or motion that changes neighboring layout. |
| Focus | Keep focus visible immediately and clearly; do not delay or animate it away. | Removing outlines or relying on color alone. |
| Carousels/media | Prefer static content; if motion is necessary, provide pause/controls and never force autoplay for essential information. | Autoplay, infinite marquees, flashing, or motion that cannot be stopped. |

For any CSS animation, transition or smooth scrolling, provide a `@media (prefers-reduced-motion: reduce)` override. Remove transforms and smooth scrolling in that mode; do not merely shorten a long animation. Use progressive enhancement (for example, add an animation-enabled class only after JavaScript initializes). Avoid adding motion if the page remains clearer without it.

## Responsive and accessibility QA

Inspect the page in a browser at **320, 375/390, 768, 1024 and 1440 CSS px** when tooling permits. At each width, verify:

- no horizontal overflow, clipped text, overlapping controls or unexpected fixed-width blocks;
- headline wraps naturally; buttons and navigation remain usable; image crops preserve the subject;
- content order still makes sense when columns stack; no critical content is hidden on mobile;
- keyboard order follows visual/reading order; skip link, landmarks and focus indicators work;
- all controls have clear names and all form fields have programmatic labels;
- decorative images use empty alt text; informative images have concise, factual alt text;
- text contrast meets WCAG AA targets (4.5:1 for normal text; 3:1 for large text and relevant UI graphics), with no color-only status cues;
- touch targets are at least WCAG 2.2 minimums where applicable and preferably around 44 × 44 CSS px for primary mobile actions;
- reduced-motion mode preserves content and interaction without unwanted movement.

Run the bundled structural check from the plugin root:

```bash
python scripts/validate_landing_page.py path/to/index.html
python scripts/validate_landing_page.py path/to/index.html --strict
```

The validator checks common HTML structure, landmark/headings, labels and accessible names, images, fragment links, placeholder links, external-link `rel`, linked CSS motion and reduced-motion overrides. It cannot prove visual contrast, responsive behavior, keyboard usability, browser compatibility, form delivery or performance; those need browser/manual checks.

## Metadata, privacy and launch

- Add a unique title and concise description. Add Open Graph metadata when the page is intended to be shared. Only add a canonical URL when the real production domain is known.
- Preview-only concepts should be clearly marked, remain private, and use `noindex`/`nofollow` until the owner approves publication. Do not publish an unsolicited concept or expose a public preview link without explicit instruction.
- Do not collect personal data without a functioning, secured destination, purpose-specific privacy notice and appropriate consent/retention handling. If no backend exists, use a verified `mailto:`, `tel:`, booking page or messaging link rather than a fake form.
- Avoid analytics, pixels, embedded third-party widgets and unnecessary external scripts by default. Explain any that are required.
- Keep legal, pricing, hours, delivery, accessibility and availability statements factual and locally verified.

## Honest completion labels

Use the most accurate status:

- **Design draft:** visual/content direction exists; behavior and browser compatibility are not yet checked.
- **Browser-reviewed:** responsive layouts and key interactions were inspected in a real browser; remaining gaps are listed.
- **Ready for owner review:** facts, visuals, CTA destinations and desktop/mobile presentation are assembled, but owner approval/publication is still pending.
- **Deployment-ready:** static QA passes, actual browser and responsive/accessibility checks are complete, every link/form has a verified destination, production metadata and privacy requirements are addressed, and no placeholders remain.

Never use “deployment-ready” to describe a static generated mockup or a render-only preview.
