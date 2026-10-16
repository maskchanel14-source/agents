# Brand Brief and Feedback Framework

## Briefing Philosophy

- Extract product name, audience, offer, market/language, CTA and brand cues from the request and project files before asking anything.
- Ask only for facts that affect truth, function, legal text or the primary user action. If the user says to proceed, document assumptions and build rather than blocking on preferences.
- Cosmetic preferences (adjectives, fonts, light/dark, roundness) are optional. Infer a restrained, readable default and record it.
- If clarification is essential, ask one concise, consolidated question rather than running a fixed questionnaire. Do not repeat answered questions.
- Use examples only when they help the user decide; never require a design vocabulary lesson.
- Treat the brief as a working record, not an approval ceremony. Do not ask permission for reversible design decisions or tool calls.
- The user may directly edit HTML/CSS; support local changes rather than forcing a regeneration cycle.

---

## Phase A: Product & Purpose

**Goal:** Understand what the product does, who it's for, and what action the landing page should drive.

### Core Questions (ask in order, skip any already answered)

1. "What's your project called?"
   - Extract exact spelling, capitalization, and any tagline they mention.

2. "Give me the elevator pitch -- what does it do and why should someone care?"
   - If too technical: "Imagine explaining this to someone who might use it but isn't a developer. What problem does it solve for them?"
   - If overly broad: "If you had to pick the one thing that makes this worth checking out, what is it?"

3. "Who are your target users? Developers? Designers? Non-technical teams? Everyone?"
   - If they say "developers": "What kind -- frontend, backend, DevOps, data? What stack or ecosystem?"
   - If they say "everyone": "Who's shown the most interest so far, or who would you pitch to first?"
   - If they have no users yet: "Who did you build this for originally? Whose problem were you solving?"

4. "What's the primary action you want a visitor to take? For example: sign up, start a free trial, join the waitlist, book a demo, star the repo, or try a live demo."
   - If they list multiple: "Which one matters most right now -- the one you'd put on the biggest button?"
   - Map their answer to button text internally (e.g., "try it out" --> "Try It Free").

### What to Extract From Phase A

| Field | Example |
|-------|---------|
| Project name (exact spelling) | "Railtrack" |
| Elevator pitch (1-2 sentences) | "Open-source deployment pipeline that catches breaking changes before they hit production" |
| Target users | "Backend engineers working with Kubernetes, mostly at mid-size companies" |
| Primary CTA | "Start free trial" --> button text "Start Free Trial" |
| Bonus (if volunteered) | Repo URL, existing docs, tech stack, pricing model |

### Transition Rule

Prefer a project name, one-sentence offer, target audience and primary CTA. If some are unknown, use a clearly marked placeholder where safe; ask only if the missing answer would change the page's truth or make its main action impossible. When the user asks for a fast build, extract what is available and proceed with documented defaults.

---

## Phase B: Brand Feel

**Goal:** Choose a coherent emotional direction. Use these as optional signals only when the brief/project files do not already provide them.

### Optional Signals

1. "Pick 3 words that describe how your product should come across to visitors."
   - Offer a menu if they hesitate:
     > Some options: bold, clean, minimal, technical, friendly, trustworthy, modern, playful, fast, precise, approachable, sophisticated, sharp, innovative, reliable, developer-friendly, premium, fun, lightweight, serious
   - Accept any 3 words, even ones not on the list.
   - If they say "I don't know" or "I haven't thought about it": "Think about the products you respect most. When you land on Stripe's page, or Linear's, or Tailwind's -- what feeling do you get? What's the equivalent for your product?"

2. "Name a product or site whose landing page you admire. Doesn't have to be in your space."
   - If they name one: "What specifically do you like about it -- the colors, the layout, the overall vibe, the copy?"
   - If they can't think of one: skip and move on. Don't push.
   - Common developer references and what they imply:
     - Stripe: clean, premium, lots of whitespace, subtle gradients
     - Linear: dark, minimal, fast-feeling, sharp
     - Vercel: dark/light contrast, geometric, developer-focused
     - Tailwind: bright, colorful, friendly, well-structured
     - Supabase: dark, green accent, technical but approachable
     - Raycast: dark, polished, product-focused

3. "Light theme or dark theme?"
   - This maps directly to colorMode (LIGHT vs DARK).
   - Developers building dev tools tend toward dark. Products targeting non-technical users tend toward light. Note this to the user if they're unsure: "Dev tools usually go dark, consumer-facing products usually go light. What fits your audience?"

### Follow-Up Triggers

- **Contradictory adjectives** (e.g., "playful" + "serious"): "Interesting combination. If they conflict, which wins -- the approachable side or the authoritative side?"
- **All-technical** (e.g., "fast, reliable, scalable"): "Those describe the product. Now think about the page itself -- when someone sees it for the first time, what impression should it leave?"
- **"Just make it look professional"**: "Professional covers a lot of ground -- Stripe-professional or IBM-professional? Clean and spacious, or dense and information-rich?"

### Adjective Interpretation

Map the user's 3 adjectives to a Stitch `colorVariant` using the Color Variant Decision Tree in `references/stitch-architecture.md`. That file contains the full mapping table with rationale and example products.

### Transition Rule

Brand adjectives, reference products and light/dark preferences are not blockers. If absent, infer a restrained direction from the audience and category; note the assumption and continue.

---

## Phase C: Visual Preferences

**Goal:** Use existing brand tokens when supplied; otherwise choose accessible, readable defaults appropriate to the business.

### Optional Signals

1. Color direction:
   - "Do you have existing brand colors -- maybe from your app's UI, your docs site, or your repo?"
   - If yes with a hex, Tailwind class, or CSS variable: use it directly.
   - If yes with a name ("indigo," "the GitHub green"): translate to hex.
   - If no: "What color comes to mind for your product? Or think about what feeling you want -- trust (blues), energy (oranges/reds), growth (greens), creativity (purples)."

2. Font feel:
   - "For the landing page text, do you prefer something clean and geometric (like Inter or DM Sans), or something with more character and weight (like a serif)?"
   - If they say "monospace" or reference a code font: "Monospace works in code, but on a marketing page it can feel cold. I'd recommend a clean sans-serif that has a similar technical feel -- like Space Grotesk or Geist. You good with that?"

3. Shape direction:
   - "Sharp corners or rounded? Think about the buttons in your UI -- same direction?"
   - Developers usually have a strong instinct here from their framework's defaults (Tailwind `rounded-lg`, MUI's defaults, etc.).

### Common Color Name to Hex Mapping

| User says | Hex | Notes |
|-----------|-----|-------|
| Indigo / Tailwind indigo | #4F46E5 | Common dev tool accent |
| Navy / dark blue | #1E3A5F | Professional, trust |
| Royal blue | #1E40AF | Confident, established |
| Red | #DC2626 | Energy, urgency |
| Orange | #EA580C | Warmth, friendliness |
| Green | #16A34A | Growth, open source |
| Teal / cyan | #0D9488 | Modern, fresh |
| Purple / violet | #7C3AED | Creative, premium |
| Amber / gold | #D97706 | Warmth, quality |
| Charcoal / near-black | #1F2937 | Use instead of pure #000 |

### Transition to Generation

Write a short internal brief with known facts, chosen defaults and unresolved placeholders. Tell the user what direction you are taking as you build, but do not pause for confirmation of reversible design choices. Apply corrections immediately if the user provides them.

### Edge Cases

- **User wants to skip entirely**: Extract available facts, choose safe visual defaults, mark missing copy as a placeholder and build the first draft. Do not ask extra preference questions.
- **User shares their app URL, repo, or docs**: Inspect available project files or the supplied site when permitted and useful. Reuse verified tokens/content; do not invent details. If access fails, say what could not be checked and proceed with a documented assumption.
- **User pastes a README or description**: Parse it for project name, pitch, target users, and features. Skip to the gaps.

---

## Feedback Facilitation Guide

### One Focused Review Prompt

After the responsive desktop/mobile pair and QA, present a concise preview summary and invite targeted corrections in one short prompt (for example: “The first pass is built and checked; tell me any specific change you want.”). Do not ask three separate questions after every generation or make progress wait on a response when the user asked you to complete the build. Apply any stated feedback directly.

### Guiding the User Toward Useful Feedback

Developers often give feedback in implementation terms. Redirect toward design intent:

| User says | They likely mean | Follow-up to ask |
|-----------|-----------------|-----------------|
| "I don't like it" | Overall mismatch | "Is it the colors, the layout, or the overall mood that feels off?" |
| "It's boring" / "too plain" | Low visual energy | "Would you like more color contrast, a bolder layout, or both?" |
| "It's too busy" | Visual clutter | "Which part feels most cluttered? The hero, the features section, or everything?" |
| "It looks like a template" | Generic, no personality | "What would make it feel more specific to your product? A different layout, stronger colors, more distinctive typography?" |
| "It's too marketing-y" | Over-designed, too much flair | "Should we strip it down -- less decoration, more information density, tighter layout?" |
| "The colors are off" | Palette mismatch | "Too bright, too dull, or just the wrong hue?" |
| "More whitespace" / "too cramped" | Layout density | Edit: "Add more breathing room between sections" |
| "Needs more padding" / "font-size too small" | CSS-level observation | Translate: "Which section feels too tight or hard to read?" |
| "Make it pop" | Weak visual hierarchy | "What should stand out more -- the headline, the CTA button, or the overall contrast?" |
| "I love the layout but not the colors" | Partial approval | Variant signal: keep layout, change COLOR_SCHEME only |
| "Show me something totally different" | Fundamental rethink | REIMAGINE creative range |
| "Can I just edit the HTML?" | Wants direct control | Make the local change directly, preserve a versioned backup and rerun QA. |

### Design Dimensions to Highlight for the User

When presenting a design for review, draw the user's attention to specific elements. These help non-designers evaluate design without knowing design vocabulary:

- **Message clarity**: "Can a visitor tell what your product does within 5 seconds of landing here?"
- **CTA visibility**: "How quickly did your eye find the primary button? Could you miss it?"
- **Color impression**: "Do these colors match the feel you described -- {their 3 adjectives}?"
- **Reading flow**: "When you scan top to bottom, does the section order make sense for someone discovering your product?"
- **Credibility**: "If you were evaluating this product for the first time, does this page make it look like a real, maintained project?"

### Efficient Completion

- Make one purposeful refinement pass after the initial review; continue when the user requests changes or a material QA defect remains.
- Do not force a loop of repeated approvals for cosmetic choices. Give the user the bundle and accurate QA status when work is complete.
- Public deployment is a separate, consequential action: perform it only when the user has authorized a deployment target and all required content/QA gates pass.

### Feedback Priority Framework

Help users separate critical from cosmetic:

1. **Must fix**: The page doesn't communicate what the product does, or the CTA is unclear/missing.
2. **Should improve**: The mood doesn't match the brand direction, or a section is missing/unnecessary.
3. **Nice to have**: Font weight preference, exact shade of a color, spacing tweaks.

Guide users to address category 1 first, then 2, then 3. This prevents endless loops on cosmetic details while structural problems persist.
