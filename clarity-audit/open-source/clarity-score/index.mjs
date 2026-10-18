/**
 * clarity-score (open core) — MIT
 * Score a landing page's HTML against a transparent 25-check / 100-point
 * clarity rubric. Pure function: HTML string in, findings out. No network,
 * no dependencies. The hosted Clarity Audit adds the SSRF-safe fetcher,
 * result pages, badges, and paid rewrite reports on top of this engine.
 *
 * @param {string} html Raw HTML of the page
 * @param {{url?: string, responseMs?: number, finalUrl?: string}} [opts]
 * @returns {{score:number, checks:Array, pageFacts:Object}}
 */
const stripTags = (h) => h.replace(/<script[\s\S]*?<\/script>/gi, " ").replace(/<style[\s\S]*?<\/style>/gi, " ")
  .replace(/<!--[\s\S]*?-->/g, " ").replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim();
const firstText = (h, tag) => { const m = h.match(new RegExp(`<${tag}[^>]*>([\\s\\S]*?)<\\/${tag}>`, "i")); return m ? stripTags(m[1]) : ""; };

export function analyzeHtml(html, opts = {}) {
  const lower = html.toLowerCase();
  const text = stripTags(html);
  const title = firstText(html, "title");
  const h1 = firstText(html, "h1");
  const hero = stripTags(html.slice(0, 12000));
  const CTA = /\b(book|start|get|buy|join|enroll|register|download|claim|schedule|apply|try|order|reserve|sign up|get started|grab|unlock|access)\b/i;
  const ctas = [];
  const re = /<(a|button)\b[^>]*>([\s\S]*?)<\/\1>/gi; let m;
  while ((m = re.exec(html)) !== null) { const t = stripTags(m[2]).slice(0, 60); if (t.length >= 2 && t.length <= 40 && CTA.test(t)) ctas.push({ text: t, index: m.index }); }
  const forms = (html.match(/<form\b/gi) || []).length;
  const req = (html.match(/\brequired\b/gi) || []).length;
  const inputs = (html.match(/<(input|textarea|select)\b/gi) || []).length;
  const imgs = html.match(/<img\b[^>]*>/gi) || [];
  const alt = imgs.filter((t) => /alt=["'][^"']+["']/i.test(t)).length;
  const bytes = Buffer.byteLength(html, "utf8");
  const https = (opts.finalUrl || opts.url || "").startsWith("https://");
  const ms = opts.responseMs ?? 0;

  const C = [];
  const add = (id, category, label, status, points, maxPoints, impact, evidence, fix) =>
    C.push({ id, category, label, status, points, maxPoints, impact, evidence, fix });

  add("h1-present", "Message clarity", "A single clear headline (H1)", h1 ? "pass" : "fail", h1 ? 6 : 0, 6, "high",
    h1 ? `H1: "${h1.slice(0, 80)}"` : "No <h1> found.", "Add one H1: audience + outcome + without-the-pain.");
  const lenOk = h1.length >= 20 && h1.length <= 90;
  add("h1-length", "Message clarity", "Headline readable in one glance", !h1 ? "fail" : lenOk ? "pass" : "warn", !h1 ? 0 : lenOk ? 4 : 2, 4, "medium",
    `${h1.length} characters`, "Aim for 20–90 characters; detail goes in the subheadline.");
  const outcome = /\b(get|gain|grow|build|learn|master|achieve|stop|finally|without|so you can|results?|transform|increase|reduce|save|earn|launch|scale)\b/i.test(h1 + " " + hero.slice(0, 600));
  add("outcome-language", "Message clarity", "Outcome named above the fold", outcome ? "pass" : "fail", outcome ? 5 : 0, 5, "high",
    outcome ? "Outcome language found near top." : "No outcome language near top.", "Name the result, not the format.");
  const audience = /\b(for|helping|designed for)\s+(coaches|creators|consultants|founders|freelancers|agencies|owners|entrepreneurs|women|men|parents|marketers|designers|writers|students|professionals|teams|[a-z]+s who)\b/i.test(hero);
  add("audience-named", "Message clarity", "Audience named explicitly", audience ? "pass" : "warn", audience ? 5 : 1, 5, "high",
    audience ? "Audience language found." : "Hero doesn't say who it's for.", 'Add "For [audience] who [situation]".');
  const tw = new Set(title.toLowerCase().split(/\W+/).filter((w) => w.length > 3));
  const overlap = h1.toLowerCase().split(/\W+/).filter((w) => tw.has(w)).length;
  add("title-h1-alignment", "Message clarity", "Page title matches headline promise", title && h1 && overlap >= 2 ? "pass" : title && h1 ? "warn" : "fail",
    title && h1 && overlap >= 2 ? 5 : title && h1 ? 2 : 0, 5, "medium", `Title: "${title.slice(0, 60)}" · H1: "${h1.slice(0, 60)}"`, "Same promise in tab title and headline.");

  add("cta-present", "CTA & next step", "A clear call to action exists", ctas.length ? "pass" : "fail", ctas.length ? 7 : 0, 7, "high",
    ctas.length ? `${ctas.length} CTA(s), e.g. "${ctas[0].text}"` : "No action-verb CTA found.", "Verb + object + outcome in the hero.");
  const early = ctas.length > 0 && ctas[0].index < 15000;
  add("cta-above-fold", "CTA & next step", "CTA visible without scrolling far", early ? "pass" : "fail", early ? 5 : 0, 5, "high",
    early ? "First CTA in top ~15KB." : "First CTA is deep/absent.", "Primary CTA belongs in the hero.");
  const weak = ctas.filter((c) => /^(click here|submit|send|learn more|more info|read more|go|here)$/i.test(c.text.trim()));
  add("cta-specific", "CTA & next step", "CTA says what happens next", ctas.length && !weak.length ? "pass" : ctas.length ? "warn" : "fail",
    ctas.length && !weak.length ? 4 : ctas.length ? 2 : 0, 4, "medium", weak.length ? `Generic: "${weak[0].text}"` : "Specific CTA language.", 'Replace "Submit" with the actual next step.');
  add("cta-repeated", "CTA & next step", "CTA repeats after proof sections", ctas.length >= 2 ? "pass" : "warn", ctas.length >= 2 ? 4 : 1, 4, "medium",
    `${ctas.length} CTA occurrence(s).`, "Repeat the same CTA after each proof block.");

  const proof = /\b(testimonial|review|stars?|clients? (say|love)|as (seen|featured) in|case stud|rated)\b/i.test(text);
  add("social-proof", "Trust & proof", "Social proof present", proof ? "pass" : "fail", proof ? 5 : 0, 5, "high",
    proof ? "Proof language found." : "No testimonials/reviews language.", "Add real, specific testimonials — never invented ones.");
  const contact = /mailto:|@|contact/i.test(text) || lower.includes("contact");
  add("contact-path", "Trust & proof", "A human is reachable", contact ? "pass" : "fail", contact ? 4 : 0, 4, "medium",
    contact ? "Contact path found." : "No contact path found.", "Visible support email/contact link in the footer.");
  add("privacy-link", "Trust & proof", "Privacy policy linked", lower.includes("privacy") ? "pass" : "fail", lower.includes("privacy") ? 3 : 0, 3, "low",
    lower.includes("privacy") ? "Privacy reference found." : "No privacy reference.", "Link Privacy/Terms/Refund in the footer.");
  const face = /about|meet |hi, i|i'm |my name|founder/i.test(text) || imgs.length > 0;
  add("human-presence", "Trust & proof", "A real person/brand is visible", face ? "pass" : "warn", face ? 3 : 1, 3, "medium",
    face ? "Intro/imagery found." : "No intro section/imagery.", "Face + two lines of story near the offer.");

  const price = /\$\s?\d|£\s?\d|€\s?\d|USD\s?\d|pricing/i.test(text);
  add("price-visible", "Offer transparency", "Price or pricing path visible", price ? "pass" : "warn", price ? 5 : 1, 5, "high",
    price ? "Pricing language found." : "No price/pricing reference.", 'Show the price or "from $X" before checkout.');
  const lis = (html.match(/<li\b/gi) || []).length;
  add("deliverables-listed", "Offer transparency", "Deliverables listed concretely", lis >= 4 ? "pass" : "warn", lis >= 4 ? 5 : 1, 5, "medium",
    `${lis} list items.`, 'Add a "What\'s included" checklist.');
  const faq = /faq|frequently asked/i.test(text) || lower.includes('"@type":"faqpage"') || lower.includes('"@type": "faqpage"');
  add("faq-present", "Offer transparency", "FAQ answers objections", faq ? "pass" : "warn", faq ? 3 : 0, 3, "medium",
    faq ? "FAQ detected." : "No FAQ detected.", "Answer fit, time, delivery, tech, refund.");
  const guar = /guarantee|refund|money[- ]back/i.test(text);
  add("risk-reversal", "Offer transparency", "Risk reversal stated", guar ? "pass" : "warn", guar ? 2 : 0, 2, "medium",
    guar ? "Guarantee/refund language found." : "No risk-reversal language.", "State an honest revise-or-refund style policy.");

  const hasForm = forms > 0 || /calendly|cal\.com|tidycal/i.test(html);
  add("form-exists", "Form friction", "A way to act (form/booking) exists", hasForm ? "pass" : "fail", hasForm ? 4 : 0, 4, "high",
    hasForm ? `${forms} form(s)/booking found.` : "No form/booking found.", "Give the CTA somewhere real to go.");
  const lowF = req <= 5 && inputs <= 8;
  add("form-short", "Form friction", "Form asks for little, early", !hasForm ? "fail" : lowF ? "pass" : "warn", !hasForm ? 0 : lowF ? 4 : 2, 4, "medium",
    hasForm ? `${inputs} inputs, ~${req} required.` : "No form.", "Name + email first; qualify later.");
  const emailCap = /type=["']email["']/i.test(html);
  add("email-capture", "Form friction", "Email capture for non-buyers", emailCap ? "pass" : "warn", emailCap ? 2 : 0, 2, "low",
    emailCap ? "Email input found." : "No email input.", "Offer a smaller first yes (checklist/sample).");

  const vp = /<meta[^>]+name=["']viewport["']/i.test(html);
  add("viewport", "Mobile & basics", "Mobile viewport configured", vp ? "pass" : "fail", vp ? 4 : 0, 4, "high",
    vp ? "Viewport meta present." : "No viewport meta.", 'Add <meta name="viewport" …>.');
  add("html-size", "Mobile & basics", "Page weight is reasonable", bytes <= 500_000 ? "pass" : "warn", bytes <= 500_000 ? 4 : 1, 4, "medium",
    `${(bytes / 1024).toFixed(0)} KB HTML.`, "Trim builder bloat.");
  const altOk = imgs.length === 0 || alt / Math.max(imgs.length, 1) >= 0.7;
  add("image-alt", "Mobile & basics", "Images have alt text", altOk ? "pass" : "warn", altOk ? 3 : 1, 3, "low",
    imgs.length ? `${alt}/${imgs.length} with alt.` : "No <img> tags.", "Descriptive alt text on content images.");
  add("https", "Mobile & basics", "Served over HTTPS", https ? "pass" : "fail", https ? 2 : 0, 2, "high",
    https ? "HTTPS." : "Not HTTPS / unknown.", "Enable HTTPS.");
  add("response-time", "Mobile & basics", "Server responds quickly", ms > 0 && ms <= 3000 ? "pass" : ms === 0 ? "warn" : "warn", ms > 0 && ms <= 3000 ? 2 : 0, 2, "medium",
    ms ? `${ms} ms.` : "Not measured (pass responseMs).", "Aim for HTML < ~1s.");

  const score = C.reduce((s, c) => s + c.points, 0);
  return { score, checks: C, pageFacts: { title, h1, wordCount: text ? text.split(/\s+/).length : 0, ctaCount: ctas.length, formCount: forms, imageCount: imgs.length, htmlBytes: bytes, https } };
}
