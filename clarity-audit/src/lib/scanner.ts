// Instant Website Clarity Audit — deterministic scoring engine.
// Evidence-based: every finding cites what was actually found in the fetched HTML.
// No hallucinated facts. Rubric weights documented in /methodology.

export type CheckStatus = "pass" | "warn" | "fail";
export type Impact = "high" | "medium" | "low";

export interface CheckResult {
  id: string;
  category: string;
  label: string;
  status: CheckStatus;
  points: number;
  maxPoints: number;
  impact: Impact;
  evidence: string; // what was literally found on the page
  fix: string; // concrete, copyable fix guidance
}

export interface ScanReport {
  url: string;
  finalUrl: string;
  fetchedAt: string;
  score: number; // 0–100
  grade: string;
  gradeNote: string;
  checks: CheckResult[];
  topIssues: CheckResult[];
  quickWin: CheckResult | null;
  lockedFindings: number; // findings reserved for the paid report (depth, not hidden basics)
  pageFacts: {
    title: string;
    metaDescription: string;
    h1: string;
    wordCount: number;
    ctaCount: number;
    formCount: number;
    imageCount: number;
    htmlBytes: number;
    responseMs: number;
    https: boolean;
  };
}

export const CATEGORIES = [
  "Message clarity",
  "CTA & next step",
  "Trust & proof",
  "Offer transparency",
  "Form friction",
  "Mobile & basics",
] as const;

// ---------- HTML extraction helpers (dependency-free, defensive) ----------

function stripTags(html: string): string {
  return html
    .replace(/<script[\s\S]*?<\/script>/gi, " ")
    .replace(/<style[\s\S]*?<\/style>/gi, " ")
    .replace(/<noscript[\s\S]*?<\/noscript>/gi, " ")
    .replace(/<!--[\s\S]*?-->/g, " ")
    .replace(/<[^>]+>/g, " ")
    .replace(/&nbsp;/g, " ")
    .replace(/&amp;/g, "&")
    .replace(/\s+/g, " ")
    .trim();
}

function allMatches(html: string, re: RegExp): string[] {
  return Array.from(html.matchAll(re)).map((m) => (m[1] ?? "").trim());
}

function firstText(html: string, tag: string): string {
  const m = html.match(new RegExp(`<${tag}[^>]*>([\\s\\S]*?)<\\/${tag}>`, "i"));
  return m ? stripTags(m[1]) : "";
}

function meta(html: string, name: string): string {
  const m =
    html.match(new RegExp(`<meta[^>]+(?:name|property)=["']${name}["'][^>]+content=["']([^"']*)["']`, "i")) ||
    html.match(new RegExp(`<meta[^>]+content=["']([^"']*)["'][^>]+(?:name|property)=["']${name}["']`, "i"));
  return m ? m[1].trim() : "";
}

const CTA_VERBS =
  /\b(book|start|get|buy|join|enroll|register|download|claim|schedule|apply|try|order|reserve|sign up|get started|work with|talk to|grab|unlock|access)\b/i;
const WEAK_CTA = /^(click here|submit|send|learn more|more info|read more|go|here)$/i;
const OUTCOME_WORDS =
  /\b(get|gain|grow|build|learn|master|achieve|stop|finally|without|so you can|results?|outcome|transform|increase|reduce|save|earn|launch|scale|confident|clarity)\b/i;
const AUDIENCE_WORDS =
  /\b(for|helping|designed for)\s+(coaches|creators|consultants|founders|freelancers|agencies|business owners|entrepreneurs|you who|women|men|parents|marketers|designers|writers|speakers|students|professionals|teams|[a-z]+s who)\b/i;
const PROOF_WORDS =
  /\b(testimonial|review|★|stars?|clients? (say|love)|as (seen|featured) in|case stud|results from|students?|members?|rated)\b/i;

function extractCtas(html: string): { text: string; index: number }[] {
  const out: { text: string; index: number }[] = [];
  const re = /<(a|button)\b[^>]*>([\s\S]*?)<\/\1>/gi;
  let m: RegExpExecArray | null;
  while ((m = re.exec(html)) !== null) {
    const text = stripTags(m[2]).slice(0, 60);
    if (text.length >= 2 && text.length <= 40 && CTA_VERBS.test(text)) {
      out.push({ text, index: m.index });
    }
  }
  return out;
}

export interface PageInput {
  url: string;
  finalUrl: string;
  html: string;
  responseMs: number;
  htmlBytes: number;
  fetchedAt?: string; // injectable for deterministic fixtures (sample report)
}

export function analyzePage(input: PageInput): ScanReport {
  const { html } = input;
  const lower = html.toLowerCase();
  const text = stripTags(html);
  const title = firstText(html, "title");
  const h1 = firstText(html, "h1");
  const metaDescription = meta(html, "description");
  const heroText = stripTags(html.slice(0, Math.min(html.length, 12000))); // top-of-page proxy
  const ctas = extractCtas(html);
  const forms = allMatches(html, /(<form\b)/gi).length;
  const requiredFields = (html.match(/\brequired\b/gi) ?? []).length;
  const inputs = (html.match(/<(input|textarea|select)\b/gi) ?? []).length;
  const images = html.match(/<img\b[^>]*>/gi) ?? [];
  const imagesWithAlt = images.filter((t) => /alt=["'][^"']+["']/i.test(t)).length;
  const https = input.finalUrl.startsWith("https://");
  const wordCount = text ? text.split(/\s+/).length : 0;

  const checks: CheckResult[] = [];
  const add = (c: CheckResult) => checks.push(c);

  // ---- Message clarity (25) ----
  add({
    id: "h1-present", category: "Message clarity", label: "A single clear headline (H1)",
    status: h1 ? "pass" : "fail", points: h1 ? 6 : 0, maxPoints: 6, impact: "high",
    evidence: h1 ? `H1 found: “${h1.slice(0, 80)}”` : "No <h1> found in the page HTML.",
    fix: "Add one H1 that states who it is for and the outcome. Template: “I help [audience] [outcome] without [pain].”",
  });
  const h1Len = h1.length;
  add({
    id: "h1-length", category: "Message clarity", label: "Headline readable in one glance",
    status: !h1 ? "fail" : h1Len >= 20 && h1Len <= 90 ? "pass" : "warn",
    points: !h1 ? 0 : h1Len >= 20 && h1Len <= 90 ? 4 : 2, maxPoints: 4, impact: "medium",
    evidence: h1 ? `Headline is ${h1Len} characters.` : "No headline to measure.",
    fix: "Aim for 20–90 characters. Move detail into a subheadline instead of stretching the H1.",
  });
  const outcome = OUTCOME_WORDS.test(h1) || OUTCOME_WORDS.test(heroText.slice(0, 600));
  add({
    id: "outcome-language", category: "Message clarity", label: "Outcome named above the fold",
    status: outcome ? "pass" : "fail", points: outcome ? 5 : 0, maxPoints: 5, impact: "high",
    evidence: outcome ? "Outcome/benefit language detected in the headline or hero copy." : "No outcome language (e.g. “get”, “build”, “without”, “so you can”) found near the top of the page.",
    fix: "Name the result, not the format. “6-week course” → “Launch your course in 6 weeks, without a team.”",
  });
  const audience = AUDIENCE_WORDS.test(heroText);
  add({
    id: "audience-named", category: "Message clarity", label: "Audience named explicitly",
    status: audience ? "pass" : "warn", points: audience ? 5 : 1, maxPoints: 5, impact: "high",
    evidence: audience ? "Audience language (“for …”, “helping …”) detected near the top." : "The hero does not clearly say who this is for.",
    fix: "Add “For [specific audience] who [specific situation]” in the hero. Specificity beats breadth for trust.",
  });
  const titleWords = new Set(title.toLowerCase().split(/\W+/).filter((w) => w.length > 3));
  const overlap = h1.toLowerCase().split(/\W+/).filter((w) => titleWords.has(w)).length;
  add({
    id: "title-h1-alignment", category: "Message clarity", label: "Page title matches headline promise",
    status: title && h1 && overlap >= 2 ? "pass" : title && h1 ? "warn" : "fail",
    points: title && h1 && overlap >= 2 ? 5 : title && h1 ? 2 : 0, maxPoints: 5, impact: "medium",
    evidence: `Title: “${title.slice(0, 60) || "(missing)"}” · H1: “${h1.slice(0, 60) || "(missing)"}”`,
    fix: "Keep the search-result title and the on-page headline making the same promise, so clicks feel confirmed, not baited.",
  });

  // ---- CTA & next step (20) ----
  add({
    id: "cta-present", category: "CTA & next step", label: "A clear call to action exists",
    status: ctas.length > 0 ? "pass" : "fail", points: ctas.length > 0 ? 7 : 0, maxPoints: 7, impact: "high",
    evidence: ctas.length ? `${ctas.length} action-oriented button/link found (e.g. “${ctas[0].text}”).` : "No button or link with an action verb (book, start, get, buy…) found.",
    fix: "Add one primary CTA in the hero. Use verb + object + outcome: “Book my free clarity call.”",
  });
  const ctaEarly = ctas.length > 0 && ctas[0].index < 15000;
  add({
    id: "cta-above-fold", category: "CTA & next step", label: "CTA visible without scrolling far",
    status: ctaEarly ? "pass" : "fail", points: ctaEarly ? 5 : 0, maxPoints: 5, impact: "high",
    evidence: ctas.length ? (ctaEarly ? "First CTA appears in the top ~15 KB of HTML (above-the-fold proxy)." : "First CTA appears deep in the page HTML.") : "No CTA found.",
    fix: "Place the primary CTA in the hero, next to the headline. Visitors who are ready should not have to hunt.",
  });
  const weak = ctas.filter((c) => WEAK_CTA.test(c.text.trim()));
  add({
    id: "cta-specific", category: "CTA & next step", label: "CTA says what happens next",
    status: ctas.length && weak.length === 0 ? "pass" : ctas.length ? "warn" : "fail",
    points: ctas.length && weak.length === 0 ? 4 : ctas.length ? 2 : 0, maxPoints: 4, impact: "medium",
    evidence: weak.length ? `Generic CTA text found: “${weak[0].text}”.` : ctas.length ? "CTAs use specific action language." : "No CTA found.",
    fix: "Replace “Learn more / Submit” with the actual next step: “See the curriculum”, “Get my audit”.",
  });
  add({
    id: "cta-repeated", category: "CTA & next step", label: "CTA repeats after proof sections",
    status: ctas.length >= 2 ? "pass" : "warn", points: ctas.length >= 2 ? 4 : 1, maxPoints: 4, impact: "medium",
    evidence: `${ctas.length} CTA occurrence(s) on the page.`,
    fix: "Repeat the same primary CTA after each major proof block (testimonials, curriculum, FAQ). Consistency, not variety.",
  });

  // ---- Trust & proof (15) ----
  const proof = PROOF_WORDS.test(text);
  add({
    id: "social-proof", category: "Trust & proof", label: "Social proof present",
    status: proof ? "pass" : "fail", points: proof ? 5 : 0, maxPoints: 5, impact: "high",
    evidence: proof ? "Proof language (reviews/testimonials/results) detected." : "No testimonials, reviews, ratings, or case-study language detected.",
    fix: "Add 2–3 real, specific testimonials with names/roles. If you have none yet, use a methodology/sample section instead — never invent quotes.",
  });
  const contact = /@|mailto:|contact|support@|\+?\d[\d\s().-]{7,}/i.test(text) || lower.includes("contact");
  add({
    id: "contact-path", category: "Trust & proof", label: "A human is reachable",
    status: contact ? "pass" : "fail", points: contact ? 4 : 0, maxPoints: 4, impact: "medium",
    evidence: contact ? "Contact path (email/phone/contact link) detected." : "No contact information or contact link detected.",
    fix: "Add a visible support email or contact link in the footer. Reachability is a top trust signal for first-time buyers.",
  });
  const privacy = lower.includes("privacy");
  add({
    id: "privacy-link", category: "Trust & proof", label: "Privacy policy linked",
    status: privacy ? "pass" : "fail", points: privacy ? 3 : 0, maxPoints: 3, impact: "low",
    evidence: privacy ? "A “privacy” reference/link was found." : "No privacy policy reference found.",
    fix: "Link Privacy, Terms, and Refund policies in the footer. Missing legal pages quietly kill checkout confidence.",
  });
  const face = /about|meet |hi, i|i'm |my name|founder|coach\b.*photo|headshot/i.test(text) || images.length > 0;
  add({
    id: "human-presence", category: "Trust & proof", label: "A real person/brand is visible",
    status: face ? "pass" : "warn", points: face ? 3 : 1, maxPoints: 3, impact: "medium",
    evidence: face ? "About/introduction language or imagery detected." : "No about/intro section or imagery detected.",
    fix: "Show a face and 2–3 lines of story near the offer. People buy from people, especially coaches and consultants.",
  });

  // ---- Offer transparency (15) ----
  const price = /\$\s?\d|£\s?\d|€\s?\d|USD\s?\d|free\b.*trial|pricing/i.test(text);
  add({
    id: "price-visible", category: "Offer transparency", label: "Price or pricing path visible",
    status: price ? "pass" : "warn", points: price ? 5 : 1, maxPoints: 5, impact: "high",
    evidence: price ? "Price/pricing language detected on the page." : "No price, currency amount, or pricing reference detected.",
    fix: "Show the price (or “from $X”) before checkout. Hidden pricing is the #1 silent conversion killer for services.",
  });
  const deliverables = (html.match(/<li\b/gi) ?? []).length;
  add({
    id: "deliverables-listed", category: "Offer transparency", label: "Deliverables listed concretely",
    status: deliverables >= 4 ? "pass" : "warn", points: deliverables >= 4 ? 5 : 1, maxPoints: 5, impact: "medium",
    evidence: `${deliverables} list items found (proxy for “what you get” detail).`,
    fix: "Add a “What's included” checklist: modules, sessions, templates, support, timeline. Concreteness sells.",
  });
  const faq = /faq|frequently asked|questions\?/i.test(text) || lower.includes('"@type": "faqpage"') || lower.includes('"@type":"faqpage"');
  add({
    id: "faq-present", category: "Offer transparency", label: "FAQ answers objections",
    status: faq ? "pass" : "warn", points: faq ? 3 : 0, maxPoints: 3, impact: "medium",
    evidence: faq ? "FAQ section/language detected." : "No FAQ section detected.",
    fix: "Add 5 FAQs: time required, fit/not-fit, delivery format, tech needs, refund. Each unanswered objection is a lost sale.",
  });
  const guarantee = /guarantee|refund|money[- ]back|risk[- ]free/i.test(text);
  add({
    id: "risk-reversal", category: "Offer transparency", label: "Risk reversal stated",
    status: guarantee ? "pass" : "warn", points: guarantee ? 2 : 0, maxPoints: 2, impact: "medium",
    evidence: guarantee ? "Guarantee/refund language detected." : "No guarantee or refund language detected.",
    fix: "State an honest policy, e.g. “If the report is missing agreed sections, we revise or refund.” Do not promise results.",
  });

  // ---- Form friction (10) ----
  const hasForm = forms > 0 || /calendly|cal\.com|tidycal|book/i.test(html);
  add({
    id: "form-exists", category: "Form friction", label: "A way to act (form/booking) exists",
    status: hasForm ? "pass" : "fail", points: hasForm ? 4 : 0, maxPoints: 4, impact: "high",
    evidence: hasForm ? `${forms} form(s) / booking reference detected.` : "No form or booking link detected.",
    fix: "Give the CTA somewhere real to go: booking link, checkout, or a short form. A CTA to nowhere destroys trust.",
  });
  const lowFriction = requiredFields <= 5 && inputs <= 8;
  add({
    id: "form-short", category: "Form friction", label: "Form asks for little, early",
    status: !hasForm ? "fail" : lowFriction ? "pass" : "warn",
    points: !hasForm ? 0 : lowFriction ? 4 : 2, maxPoints: 4, impact: "medium",
    evidence: hasForm ? `${inputs} input field(s), ~${requiredFields} marked required.` : "No form to measure.",
    fix: "Keep the first step to name + email (or email only). Ask qualifying questions after commitment, not before.",
  });
  const emailCapture = /type=["']email["']/i.test(html);
  add({
    id: "email-capture", category: "Form friction", label: "Email capture for non-buyers",
    status: emailCapture ? "pass" : "warn", points: emailCapture ? 2 : 0, maxPoints: 2, impact: "low",
    evidence: emailCapture ? "An email input exists (lead capture possible)." : "No email input found — non-buyers have no lower-commitment step.",
    fix: "Offer a free checklist/sample in exchange for email (with consent + unsubscribe). Most visitors need a smaller first yes.",
  });

  // ---- Mobile & basics (15) ----
  const viewport = /<meta[^>]+name=["']viewport["']/i.test(html);
  add({
    id: "viewport", category: "Mobile & basics", label: "Mobile viewport configured",
    status: viewport ? "pass" : "fail", points: viewport ? 4 : 0, maxPoints: 4, impact: "high",
    evidence: viewport ? "Viewport meta tag present." : "No viewport meta tag — page likely renders zoomed-out on phones.",
    fix: "Add <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">. Most landing-page traffic is mobile.",
  });
  const sizeOk = input.htmlBytes <= 500_000;
  add({
    id: "html-size", category: "Mobile & basics", label: "Page weight is reasonable",
    status: sizeOk ? "pass" : "warn", points: sizeOk ? 4 : 1, maxPoints: 4, impact: "medium",
    evidence: `HTML document is ${(input.htmlBytes / 1024).toFixed(0)} KB (before images/scripts).`,
    fix: "Trim heavy page-builder bloat. Every extra 100 KB of HTML slows first paint on mobile connections.",
  });
  const altOk = images.length === 0 || imagesWithAlt / Math.max(images.length, 1) >= 0.7;
  add({
    id: "image-alt", category: "Mobile & basics", label: "Images have alt text",
    status: altOk ? "pass" : "warn", points: altOk ? 3 : 1, maxPoints: 3, impact: "low",
    evidence: images.length ? `${imagesWithAlt}/${images.length} images have non-empty alt text.` : "No <img> tags found.",
    fix: "Add descriptive alt text to content images — accessibility, SEO, and broken-image resilience in one move.",
  });
  add({
    id: "https", category: "Mobile & basics", label: "Served over HTTPS",
    status: https ? "pass" : "fail", points: https ? 2 : 0, maxPoints: 2, impact: "high",
    evidence: https ? "Final URL uses HTTPS." : "Final URL is plain HTTP.",
    fix: "Enable HTTPS (free via your host/Cloudflare). Browsers label HTTP pages “Not secure” — fatal at checkout.",
  });
  const fast = input.responseMs <= 3000;
  add({
    id: "response-time", category: "Mobile & basics", label: "Server responds quickly",
    status: fast ? "pass" : "warn", points: fast ? 2 : 0, maxPoints: 2, impact: "medium",
    evidence: `HTML fetched in ${input.responseMs} ms from the scanner.`,
    fix: "Aim for HTML in under ~1s. Check hosting region, caching, and redirect chains (each redirect adds a round trip).",
  });

  const score = checks.reduce((s, c) => s + c.points, 0);
  const grade =
    score >= 80 ? "Clear" : score >= 60 ? "Nearly there" : score >= 40 ? "Foggy" : "Unclear";
  const gradeNote =
    score >= 80
      ? "Visitors can likely tell what this is, who it is for, and what to do next within seconds."
      : score >= 60
        ? "The core message lands, but a few fixable gaps are likely costing clicks."
        : score >= 40
          ? "A first-time visitor has to work too hard to understand the offer. The fixes below are high-leverage."
          : "Most first-time visitors will leave before they understand the offer. Start with the quick win — it is genuinely quick.";

  const impactRank: Record<Impact, number> = { high: 0, medium: 1, low: 2 };
  const problems = checks
    .filter((c) => c.status !== "pass")
    .sort((a, b) => impactRank[a.impact] - impactRank[b.impact] || b.maxPoints - b.points - (a.maxPoints - a.points));
  const topIssues = problems.slice(0, 3);
  const quickWin = problems.find((c) => c.impact === "high") ?? problems[0] ?? null;

  return {
    url: input.url,
    finalUrl: input.finalUrl,
    fetchedAt: input.fetchedAt ?? new Date().toISOString(),
    score,
    grade,
    gradeNote,
    checks,
    topIssues,
    quickWin,
    // Paid depth = per-issue rewrite examples, section-by-section annotated review,
    // and a 7-day plan. We surface the count of remaining findings honestly.
    lockedFindings: Math.max(0, problems.length - 3),
    pageFacts: {
      title, metaDescription, h1, wordCount,
      ctaCount: ctas.length, formCount: forms, imageCount: images.length,
      htmlBytes: input.htmlBytes, responseMs: input.responseMs, https,
    },
  };
}

export function scoreColor(score: number): string {
  if (score >= 80) return "#15803d";
  if (score >= 60) return "#b45309";
  if (score >= 40) return "#c2410c";
  return "#b91c1c";
}
