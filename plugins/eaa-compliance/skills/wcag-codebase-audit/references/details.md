# WCAG Codebase Audit — Reference Detail

Loaded on demand from `../SKILL.md`. Framework-specific patterns and fixes, the findings JSON schema, test and CI patterns, the platform ownership matrix, and the manual-test protocol.

## Findings JSON schema

Emit `eaa-audit-findings.json` in exactly this shape so the documentation stage can consume it without re-parsing prose:

```json
{
  "meta": {
    "project": "string",
    "framework": "string",
    "frameworkVersion": "string",
    "renderModel": "ssr | ssg | csr | hydrated",
    "standard": "WCAG 2.1 AA",
    "en301549Version": "v3.2.1",
    "auditedAt": "ISO-8601",
    "auditor": "string",
    "routesExamined": ["string"],
    "excluded": [{ "path": "string", "reason": "string" }],
    "method": "static-source-analysis"
  },
  "journeys": [
    {
      "journey": "checkout",
      "verdict": "BLOCKED | DEGRADED | USABLE | NOT_ASSESSED",
      "critical": 0, "serious": 0, "moderate": 0, "minor": 0
    }
  ],
  "findings": [
    {
      "id": "CO-01",
      "journey": "checkout",
      "wcag": { "sc": "3.3.2", "name": "Labels or Instructions", "level": "A" },
      "en301549": "9.1.3.3.2",
      "severity": "critical | serious | moderate | minor",
      "file": "string",
      "line": 0,
      "instances": 0,
      "defect": "string — what was observed",
      "fix": "string — the corrected code for this framework",
      "effort": "S | M | L",
      "manualRequired": false,
      "owner": "client | third-party | platform",
      "closed": false
    }
  ],
  "manualRequired": [
    { "wcag": "2.4.3", "name": "Focus Order", "test": "keyboard-only walkthrough of the checkout route" }
  ]
}
```

Use `id` prefixes by journey — `HO` home, `SE` search, `CA` category, `PD` product, `CT` cart, `CO` checkout, `PY` payment, `AU` auth, `GL` global. Stable IDs let the remediation plan, the ACR remarks, and the evidence log all reference the same finding.

Set `closed` when a fix is implemented and verified, and update the JSON in place so the ACR can be regenerated from accurate data rather than re-audited.

## Next.js and React

**Metadata and document language.** `lang` is set once, in the root layout, and is frequently wrong or missing in the App Router:

```tsx
// app/layout.tsx — lang must match the served locale, not be hardcoded for a multi-locale site
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang={locale}>   {/* not lang="en" on an i18n route */}
      <body>{children}</body>
    </html>
  );
}
```

Per-route titles come from the metadata export or `generateMetadata`. A templated title with an undefined segment renders as the site name on every page — SC 2.4.2 failure, and invisible in the source unless you check the dynamic path.

**The icon-only button.** The single most common defect in React component libraries:

```tsx
// Defect: accessible name is empty; screen reader announces "button"
<button onClick={close}><XIcon /></button>

// Fix
<button type="button" onClick={close} aria-label="Close dialog">
  <XIcon aria-hidden="true" focusable="false" />
</button>
```

`aria-hidden` on the SVG matters, and so does `focusable="false"` for legacy IE/Edge SVG focus. Find the shared icon-button primitive and count its usages — this is usually one fix closing dozens of instances.

**Focus style suppression.** Tailwind resets and `outline-none` without a replacement:

```css
/* Defect: SC 2.4.7 Focus Visible */
:focus { outline: none; }

/* Fix: remove the outline only when a visible alternative exists */
:focus-visible { outline: 2px solid var(--focus); outline-offset: 2px; }
```

Search for `outline-none`, `outline: 0`, `outline: none`, and Tailwind `focus:outline-none` with no paired `focus-visible:ring-*`. Report as one finding against the stylesheet, with the count of affected components.

**Client-rendered state changes.** A result list, a cart total, or a form error updated in state is invisible to a screen reader unless the region is live:

```tsx
// Fix: SC 4.1.3 Status Messages
<p role="status" aria-live="polite">{`${count} results`}</p>
<div role="alert" id="email-error">{error}</div>
<input aria-invalid={!!error} aria-describedby={error ? "email-error" : undefined} />
```

`role="alert"` is assertive and interrupts; use `role="status"` for anything that is not an error. Applying `aria-live` to a large frequently-updated container makes the product unusable — scope the live region tightly and say so in the finding.

**Hydration and `suppressHydrationWarning`.** A component that renders differently on server and client can produce a DOM the audit never saw in source. Flag any `suppressHydrationWarning` on a semantic element as requiring runtime verification.

## Vue, Svelte, Angular

**Vue** — `v-html` content bypasses template authoring and is a common source of unlabelled markup and heading-level damage from CMS HTML. Audit what goes into it, not just the template. Bind `:lang` on the root element for i18n routes.

**Svelte** — the `svelte-a11y` compiler warnings are suppressed per-line with `<!-- svelte-ignore a11y-click-events-have-key-events -->`. **Search for `svelte-ignore a11y-` and report every instance**: each one is a developer who saw an accessibility warning and dismissed it. These are high-confidence findings with a documented intent trail.

**Angular** — templates are compiled and checked, but `innerHTML` bindings behave like Vue's `v-html`. Angular CDK's `cdkTrapFocus`, `cdkA11yModule`, and `LiveAnnouncer` are the correct primitives; report hand-rolled modal or live-region implementations that bypass them.

## Shopify Liquid

Merchant-owned surface versus platform-owned surface is the whole audit here.

**Merchant-owned, fixable:** theme templates and sections; section schemas; product and collection templates; the cart; product images and alt text (populated from the admin, so alt-text failures are a **content** problem needing a process fix, not a code fix); app embeds the merchant chose to install.

```liquid
{%- comment -%} Defect: alt empty on every product image {%- endcomment -%}
<img src="{{ image | image_url: width: 800 }}" alt="">

{%- comment -%} Fix: use the admin-entered alt, with a sane fallback {%- endcomment -%}
<img
  src="{{ image | image_url: width: 800 }}"
  alt="{{ image.alt | escape | default: product.title | escape }}"
  width="{{ image.width }}" height="{{ image.height }}" loading="lazy">
```

**Platform-owned, not fixable:** the checkout extensibility surface. Merchants cannot modify checkout markup directly — only through sanctioned extension points. A merchant whose checkout fails SC 3.3.2 cannot remediate it in theme code. Record `owner: "platform"`, name the limitation, and route it to the statement's known-limitations section and the ACR remark. **Do not put platform-owned failures in the client's remediation plan as client work** — that is how plans stall in week two.

**Third-party apps:** review widgets, chat bubbles, upsell popups, cookie banners, and payment-frame injectors each render markup the merchant does not control. Record `owner: "third-party"` with the app name, and advise a written remediation request to the vendor plus evaluation of a replacement where the vendor is unresponsive.

Note that Shopify requires Theme Store themes to average at least 90 on Lighthouse's accessibility audit — useful context, but a Theme Store theme is a **starting point**, not a conformance claim, and app-injected markup sits outside it entirely.

## WordPress and WooCommerce

**Theme templates** — check `header.php` for `language_attributes()` and the document title; `footer.php` for the skip-link target and landmark closure; template parts for heading order.

**Block markup** — Gutenberg blocks produce varying quality. Core blocks are generally sound; page-builder plugins (Elementor, WPBakery, Divi) frequently emit `div` soup with heading-level damage, empty links, and click handlers on non-interactive elements. Identify the page builder early — it determines whether fixes are code changes or editor-content changes, and editor-content changes need a process fix and training rather than a patch.

**WooCommerce-specific:**

- product gallery images and alt text — admin-entered, so a content-process problem
- the add-to-cart form: quantity input without an accessible name; variation selects without labels
- cart and checkout: coupon and error messages not exposed as live regions; validation errors shown only in red (SC 1.4.1 and SC 3.3.1 together)
- the payment step where a gateway iframe or hosted redirect moves the customer off-site — establish the ownership boundary in writing before making any conformance claim about checkout

**Plugins** render markup the site owner does not control. `owner: "third-party"` with the plugin named. A cookie-consent plugin that traps keyboard focus is a common and severe finding, and it is rarely the site owner's code.

## Astro, and static or hand-authored HTML

Islands architecture means only hydrated components carry client behaviour — audit the island boundaries, because a static page with one interactive island concentrates all keyboard and live-region risk in that island. Check the document shell for `lang`, a real `<title>`, landmarks, and a skip link. For hand-authored HTML, the highest-yield searches are `<div onclick`, `<span onclick`, `tabindex="1"`, `outline:none`, `alt=""` on informative images, and `<a href="#">`.

## Component tests

Add coverage for what you fix, so the defect cannot silently return.

```tsx
// jest-axe against a rendered component
import { render } from "@testing-library/react";
import { axe, toHaveNoViolations } from "jest-axe";

expect.extend(toHaveNoViolations);

it("CloseButton exposes an accessible name", async () => {
  const { container } = render(<CloseButton onClick={() => {}} />);
  expect(await axe(container)).toHaveNoViolations();
});
```

```ts
// Playwright: keyboard reachability and focus visibility on a real route
await page.goto("/checkout");
await page.keyboard.press("Tab");
const focused = await page.evaluate(() => {
  const el = document.activeElement as HTMLElement;
  const s = getComputedStyle(el);
  return { tag: el.tagName, outline: s.outlineStyle, boxShadow: s.boxShadow };
});
expect(focused.outline).not.toBe("none");
```

Name-based assertions catch what axe cannot: assert that `getByRole("button", { name: /close dialog/i })` resolves, which fails on an unnamed icon button even when the automated scan passes.

## CI gate

Adopt a **fail-on-regression** rule, not fail-on-any-violation, so the gate can be added to a non-compliant codebase without blocking every merge:

```yaml
- name: Accessibility regression gate
  run: |
    npx axe-cli --tags wcag2a,wcag2aa,wcag21a,wcag21aa \
      --rules-file .a11y-baseline.json \
      --exit --reporter cli "$ROUTE_LIST"
```

`.a11y-baseline.json` records known legacy violations so new ones fail the build. Reduce the baseline as remediation lands, and treat a growing baseline as a process failure worth escalating.

State the gate's limit honestly in every report: automated scanning detects roughly a quarter to a third of WCAG issues. A green CI run is a regression guard, **not a conformance claim**, and must never be presented to a buyer as evidence of compliance.

## Platform ownership matrix

| Surface | Typical owner | Consequence |
|---|---|---|
| Theme templates and components | `client` | Fixable in code |
| Admin-entered alt text and content | `client` | Needs a process and training fix, not a patch |
| Shopify checkout extensibility surface | `platform` | Not fixable by the merchant; document as a limitation |
| WooCommerce payment gateway iframe or hosted redirect | `third-party` | Off-site boundary; no conformance claim without the provider's own ACR |
| Cookie-consent, chat, review, upsell widgets | `third-party` | Written remediation request; evaluate replacement if unresponsive |
| Page-builder output | `client` | Fix in the editor; needs training and a content standard |
| CMS content in headless setups | `third-party` | CMS owns content accessibility; frontend owns markup |
| CDN or edge-injected scripts | `platform` | Establish before claiming coverage |

Every client-facing document must state these boundaries. A conformance claim that silently includes a surface the client does not control is the specific misrepresentation that causes an ACR to be withdrawn.

## Manual-test protocol — closing `MANUAL REQUIRED`

The protocol that converts a static audit into evidence sufficient for a conformance level. Record each run in `eaa-evidence-log.md` with date, tester, method, environment (browser, OS, assistive technology and version), steps performed, observed result, and artefact reference.

**Keyboard-only pass, per revenue journey:**

1. Load the route with no pointer input. Tab through the entire journey.
2. Record the focus order and check it matches the visual and logical reading order (SC 2.4.3).
3. Confirm every interactive element is reachable and operable with Enter or Space (SC 2.1.1).
4. Confirm a visible focus indicator on every element (SC 2.4.7).
5. Confirm no trap: you can always leave any component, including modals, carousels, and chat widgets (SC 2.1.2).
6. Confirm Escape closes overlays and focus returns to the triggering control.
7. Confirm the skip link appears on first Tab and targets the main landmark (SC 2.4.1).

**One screen reader, per journey.** NVDA with Firefox on Windows, or VoiceOver with Safari on macOS. Read the journey start to finish and record: does the accessible name of each control describe its action; are form errors announced and does focus move to them; are status changes announced; are headings and landmarks navigable; is the announcement order usable.

**Contrast and zoom:** verify computed contrast against rendered backgrounds including gradients and images (SC 1.4.3, 1.4.11); reflow at 400% zoom and 320 CSS pixels with no loss of content or function and no two-dimensional scrolling (SC 1.4.10); resize text to 200% (SC 1.4.4); apply text-spacing overrides (SC 1.4.12).

**Timing and media:** session-timeout warning (SC 2.2.1); autoplaying content that can be paused, stopped, or hidden (SC 2.2.2); captions on prerecorded video (SC 1.2.2).

Only after a criterion is closed by one of these tests may it carry `Supports` in an ACR. Until then it is **Not Evaluated** with the closing test named and dated.
