export interface ArticleSection { h: string; paras: string[]; list?: string[] }
export interface Article {
  slug: string; title: string; description: string; keyword: string; readMins: number;
  intro: string; sections: ArticleSection[]; faqs: { q: string; a: string }[];
}

const A = (
  slug: string, title: string, description: string, keyword: string, readMins: number,
  intro: string, sections: ArticleSection[], faqs: { q: string; a: string }[]
): Article => ({ slug, title, description, keyword, readMins, intro, sections, faqs });

export const RESOURCES: Article[] = [
  A("free-landing-page-score",
    "Free Landing Page Score: What It Measures (and What It Can't)",
    "A free landing page score grades clarity: headline, CTA, proof, pricing, and form friction. Here's how the rubric works, its limits, and how to use your score.",
    "free landing page score", 6,
    "A landing page score is a clarity check, not a fortune teller. It answers one question: could a stranger understand your offer in five seconds? This page explains exactly what our 100-point rubric measures, where automated scoring is blind, and how to act on your result.",
    [
      { h: "What the score measures", paras: ["The rubric weights six categories: message clarity (25), CTA & next step (20), trust & proof (15), offer transparency (15), form friction (10), and mobile & technical basics (15). Each check is evidence-based — the scanner reads your public HTML and reports what it literally found: your H1, your button text, whether a price appears anywhere."], list: ["Headline: does an H1 exist, is it glance-readable, does it name an outcome?", "Audience: does the hero say who this is for?", "CTA: is there an action button above the fold, and does it say what happens next?", "Proof: testimonials, ratings, or case-study language present?", "Price: is any price or pricing path visible before checkout?", "Form: how many required fields stand between interest and action?"] },
      { h: "What a score cannot tell you", paras: ["No automated tool sees your traffic quality, your offer's real demand, or how your page feels rendered on a phone in sunlight. A score of 85 does not guarantee sales; a score of 45 does not doom you. Treat the score as a pre-flight checklist: it catches the structural clarity problems that make every other marketing effort leak."] },
      { h: "How to use your score", paras: ["Fix the highest-impact failures first — usually the headline and the first CTA. Change one thing, re-scan, and watch the check flip to pass. That verify-loop is the whole point of the 5-Day Clarity Challenge. When you want rewrite options and a day-by-day plan instead of DIY, that is what the paid audit tiers add."] },
    ],
    [{ q: "Is the landing page score really free?", a: "Yes. The scanner, your score, your top 3 issues, and one quick-win fix are free with no email required. Paid tiers add rewrites and an implementation plan." },
     { q: "Does scanning my page store my data?", a: "The scanner fetches your public HTML to analyze it. Result pages can be shared by link; see the privacy policy for retention and deletion." },
     { q: "What is a good landing page score?", a: "80+ means a cold visitor can likely grasp the offer fast. 60–79 is close — usually 2–3 fixes away. Below 60, fix the headline and CTA before spending on traffic." }]),

  A("landing-page-audit-checklist",
    "Landing Page Audit Checklist: 20 Points in 15 Minutes",
    "Run this 100-point landing page audit checklist before your next launch: headline, CTA, proof, pricing, FAQ, forms, mobile. Free scanner included.",
    "landing page audit checklist", 7,
    "This is the exact checklist our scanner automates. Run it manually in 15 minutes, or paste your URL into the free scanner and get the same 25 checks scored in seconds.",
    [
      { h: "Message clarity (5 checks)", paras: ["Open your page on a phone and read only what is visible. Could you repeat the offer back?"], list: ["One H1 headline exists", "Headline is 20–90 characters (one glance)", "An outcome is named, not just a format (“launch your course”, not “6 modules”)", "The audience is named (“for coaches who…”) ", "Browser tab title and H1 make the same promise"] },
      { h: "CTA & next step (4 checks)", paras: [], list: ["A primary CTA button exists", "It is visible without scrolling", "Button text says what happens next (not “Submit” / “Learn more”)", "The same CTA repeats after proof sections"] },
      { h: "Trust, offer, forms, mobile (11 checks)", paras: [], list: ["Testimonials/reviews present (real ones only)", "A contact path is visible", "Privacy policy linked", "A real person or brand story appears", "Price or pricing path visible", "Deliverables listed as a checklist", "FAQ answers fit, time, delivery, refund", "Guarantee/refund stated honestly", "Form exists and the first step is short", "Email capture gives non-buyers a smaller yes", "Mobile viewport, HTTPS, image alt text, fast response"] },
      { h: "Scoring yourself honestly", paras: ["Give full points only when a cold visitor — not you — would find the item in under five seconds. Owners over-score because they already know the answers. When in doubt, run the free scanner: it has no ego and shows its evidence for every point."] },
    ],
    [{ q: "How often should I audit my landing page?", a: "Before every launch or ad spend, and after any redesign. Monthly is plenty for a stable page." },
     { q: "Which checklist item matters most?", a: "Headline outcome + audience. If those two fail, nothing below them gets read." }]),

  A("coaching-landing-page-mistakes",
    "7 Coaching Landing Page Mistakes That Quietly Cost You Calls",
    "The most common coaching landing page mistakes: vague outcomes, hidden pricing, generic CTAs, no FAQ. With fixes you can copy in an afternoon.",
    "coaching landing page mistakes", 7,
    "Coaching pages fail differently from product pages: the offer is intangible, so clarity has to do the heavy lifting. These are the seven patterns our rubric flags most often on coach pages — and the one-afternoon fix for each.",
    [
      { h: "1. “Transform your life” syndrome", paras: ["Transformation is true and useless. Visitors cannot picture “transformed” — they can picture “book 3 discovery calls a week” or “sleep through the night without the 3 a.m. spiral”. Name the observable outcome your clients actually report.", "Fix: “I help [audience] [observable outcome] without [the thing they dread].”"] },
      { h: "2. The biography hero", paras: ["Leading with your certifications answers a question nobody has asked yet. The hero must answer: what changes for me, and is this for someone like me? Move credentials below the first proof block."] },
      { h: "3. Pricing by interrogation", paras: ["“Book a call to learn the investment” filters for the already-convinced and repels everyone else. A “from $X” anchor or a range costs you nothing and pre-qualifies honestly."] },
      { h: "4. One lonely CTA", paras: ["A single “Book a call” at the very bottom asks cold visitors for the biggest commitment at the moment of least trust. Add a smaller step — a free resource, a sample session outline, an email checklist."] },
      { h: "5–7. Proof, FAQ, and friction", paras: [], list: ["Proof: “Sarah is amazing!” converts nobody. Specific beats glowing: who, starting point, measurable change, timeframe.", "FAQ: answer fit/not-fit, session format, time commitment, and what happens on the discovery call. The un-asked “is this a sales pitch?” question kills bookings.", "Friction: a 9-field application before a free call is a wall, not a filter. Two fields to book; qualify on the call."] },
    ],
    [{ q: "Should coaches show prices?", a: "Show at least a starting point or range. Hidden pricing mainly filters out good-fit, budget-aware buyers — the ones most likely to pay on time." },
     { q: "How many testimonials does a coaching page need?", a: "Two or three specific ones beat ten vague ones. Each should name the person's situation and a concrete change." }]),

  A("course-sales-page-audit",
    "Course Sales Page Audit: The 8 Sections Buyers Actually Read",
    "Audit your course sales page like a buyer: outcome, curriculum, proof, price anchor, FAQ. What to fix, in what order, before your next launch.",
    "course sales page audit", 7,
    "Buyers do not read course pages top to bottom. Eye-tracking and scroll-depth studies agree: they skim for outcome, curriculum, proof, price, and the refund answer. Audit those eight sections in this order.",
    [
      { h: "The skim path", paras: [], list: ["Headline: outcome + who + timeframe", "“Is this for me?” fit/not-fit block", "Curriculum: module outcomes, not module topics", "Proof: student results with starting points", "Price block: anchor, installments, what's included", "Guarantee: one honest paragraph near the price", "FAQ: time, access length, tech, refund", "Final CTA: same words as the hero CTA"] },
      { h: "Curriculum: topics vs outcomes", paras: ["“Module 3: Email Marketing” tells a buyer nothing about their future. “Module 3: Write the 5 emails that sell while you sleep (templates included)” does. Rewrite every module title as a capability the student walks away with."] },
      { h: "The price block audit", paras: ["Three questions must be answerable in ten seconds: What does it cost? What exactly do I get? What if it's not for me? If a visitor has to open checkout to learn any of the three, the block fails. Show the deliverables checklist directly above the buy button — concreteness is what the button click is made of."] },
    ],
    [{ q: "How long should a course sales page be?", a: "Long enough to answer every objection for your price point. A $49 workshop needs a screen or two; a $997 program needs the full eight sections. Length is fine — repetition without new information is not." },
     { q: "Should I show the full curriculum?", a: "Yes, as outcome-titled modules. Hiding the curriculum reads as hiding thin content." }]),

  A("consultant-website-clarity",
    "Consultant Website Clarity: From “Services” to a Bookable Offer",
    "Consultant websites list services; clarity turns them into offers. A practical framework: niche statement, productized entry offer, proof, friction-free booking.",
    "consultant website clarity", 6,
    "Most consultant sites are brochures: a list of capabilities and a contact form. Buyers do not buy capabilities — they buy a defined outcome with a defined first step. Here is the clarity upgrade path.",
    [
      { h: "Replace the services list with a ladder", paras: ["Give visitors three rungs: a free diagnostic or resource, a small fixed-scope paid first engagement (audit, roadmap, sprint), and the flagship engagement. Each rung gets its own outcome statement and price anchor. “Strategy consulting” is not an offer; “2-week pricing audit, $2,500, findings + roadmap” is."] },
      { h: "The niche sentence", paras: ["Your hero should pass the referral test: a past client could describe you in one sentence at a dinner party. “I help B2B SaaS firms under $5M fix pricing pages that leak trials.” Narrow reads as expert; broad reads as available."] },
      { h: "Booking without the gauntlet", paras: ["One calendar link, two qualifying questions max, and a line that says what the call is (“30 minutes, no pitch — you leave with a one-page diagnosis either way”). Every extra required field is a toll booth on the road to revenue."] },
    ],
    [{ q: "Should consultants publish fees?", a: "Publish the entry offer's fee exactly, and a “from” anchor for flagship work. It pre-qualifies and signals confidence." },
     { q: "What if my work is genuinely bespoke?", a: "The engagement can be bespoke; the first step cannot. Productize the diagnosis, customize the cure." }]),

  A("cta-examples",
    "40 CTA Examples That Say What Happens Next",
    "Steal these CTA examples by category — coaching, courses, consulting, lead magnets — plus the formula behind buttons that get clicked.",
    "CTA examples landing page", 6,
    "A call to action has one job: tell the visitor exactly what happens when they click. “Submit” and “Learn more” fail that test. Use the formula — verb + object + outcome — and borrow from the lists below.",
    [
      { h: "The formula", paras: ["Verb (get, book, start) + object (my audit, your plan) + outcome or ease (“in 10 minutes”, “free”). First person often outperforms second (“Start my plan” vs “Start your plan”) — test it rather than trusting folklore, including this sentence."] },
      { h: "Coaching & consulting", paras: [], list: ["Book my free clarity call", "Get my one-page diagnosis", "See if we're a fit (15 min)", "Claim a roadmap session", "Talk through my numbers"] },
      { h: "Courses & digital products", paras: [], list: ["Enroll and start Module 1", "Get instant access — $39", "Download the template kit", "Join the next cohort", "Start learning free (Lesson 1)"] },
      { h: "Lead magnets & low-commitment steps", paras: [], list: ["Send me the checklist", "Score my landing page (free)", "Email me the sample report", "Show me my 3 quick wins", "Get the 5-day challenge"] },
      { h: "What to avoid", paras: [], list: ["Submit / Send / Click here — says nothing", "Buy now!!! — urgency without information", "Maybe later → shame copy on the decline link (“No, I hate money”) — dark pattern, erodes trust", "Five different CTAs competing in one hero — pick one primary action"] },
    ],
    [{ q: "How many CTAs should a landing page have?", a: "One primary action, repeated. A secondary low-commitment option (free sample, checklist) is fine below the hero." },
     { q: "Does button color matter?", a: "Contrast matters; magic colors do not. The button must be the most visually obvious element near the decision point." }]),

  A("trust-signals-landing-page",
    "Trust Signals for Landing Pages (Without Testimonials)",
    "No testimonials yet? Build trust with method transparency, sample deliverables, honest guarantees, and reachability. Plus: what never to fake.",
    "trust signals landing page", 6,
    "New offers have a chicken-and-egg problem: no buyers, no testimonials. The answer is not inventing proof — it is substituting transparency. Here are the trust signals that work before your first review exists.",
    [
      { h: "Transparency signals", paras: [], list: ["Methodology page: show exactly how the work is done (our scanner publishes its full rubric)", "Sample deliverable: a real, labeled sample report or lesson", "Specific inclusions: “6 × 45-min sessions” beats “coaching package”", "Honest limits: “This won't fix a product nobody wants” paradoxically builds trust", "Reachable human: named person, photo, working support email", "Clear refund terms linked before checkout, not buried after"] },
      { h: "Borrowed-but-honest proof", paras: ["Beta feedback labeled as beta feedback. Results from adjacent work, attributed precisely (“from my agency clients, 2023–25”). Your own before/after using your own product. All legitimate — if the label matches the evidence."] },
      { h: "Never fake these", paras: ["Testimonials, review counts, “as seen in” logos, student numbers, countdown timers, “only 3 left” on a digital file. Fake proof is not a growth hack; it is a refund, chargeback, and reputation time bomb. One screenshot from a suspicious buyer outweighs a hundred invented stars."] },
    ],
    [{ q: "Are trust badges (secure checkout etc.) worth adding?", a: "A plain-language line near the button — what happens after you pay and how refunds work — outperforms clip-art shields." },
     { q: "When can I show aggregate stats like “average score”?", a: "Only with a real sample size behind them, stated on the page. Our own rule: no average is shown until at least 10 real scans exist." }]),

  A("headline-formulas",
    "10 Headline Formulas for Coaches, Courses & Consultants",
    "Headline formulas that name the audience and the outcome — with before/after examples and the 5-second test to validate each one.",
    "landing page headline formulas", 7,
    "Your headline is not a slogan; it is a filter and a promise. Every formula below forces the two things cold visitors need in five seconds: who it is for, and what changes.",
    [
      { h: "The formulas", paras: [], list: ["I help [audience] [outcome] without [pain]", "[Outcome] for [audience] in [timeframe]", "Stop [pain]. Start [outcome].", "The [adjective] way for [audience] to [outcome]", "[Number] [units] to [outcome] (even if [objection])", "From [before] to [after] — a [format] for [audience]", "What if [desired state] by [date/milestone]?", "[Outcome], minus the [hated part of the usual method]", "Built for [audience] who are tired of [status quo]", "[Specific mechanism]: how [audience] [outcome]"] },
      { h: "Before → after", paras: ["“Mindset Coaching for Everyone” → “I help new managers stop Sunday-night dread without quitting their job.” “Photography Course” → “Book your first paid shoot in 30 days — a course for hobbyists going pro.” Notice what changed: audience, observable outcome, removed pain. Nothing about you."] },
      { h: "The 5-second test", paras: ["Show the page to someone outside your market for five seconds, hide it, and ask: what is sold, for whom, and what do you do next? Three correct answers = clear. No volunteers handy? Run the free scanner — it checks headline presence, length, outcome language, and audience naming automatically."] },
    ],
    [{ q: "How long should a headline be?", a: "20–90 characters covers most winners. Longer can work if every word earns its place; detail belongs in the subheadline." },
     { q: "Clever or clear?", a: "Clear. Clever is a tax the visitor pays in comprehension. Spend creativity on specificity instead." }]),

  A("faq-examples-landing-page",
    "FAQ Examples: The 9 Questions Every Offer Page Must Answer",
    "Copy-ready FAQ examples for coaching, course, and consulting pages: fit, time, delivery, tech, price, and refund — answered honestly.",
    "FAQ examples landing page", 6,
    "An FAQ is not a legal appendix; it is your objection-handling closer. These nine questions cover nearly every silent reason a qualified visitor leaves without buying.",
    [
      { h: "The nine", paras: [], list: ["Who is this for — and who is it NOT for?", "How much time will this take each week?", "How is it delivered, and when do I get access?", "What exactly is included (and what is not)?", "What do I need before starting (tools, experience, budget)?", "What happens right after I pay/book?", "What if my situation is different (edge case)?", "What is the refund/reschedule policy?", "How do I contact a human with a question?"] },
      { h: "Answer like a human", paras: ["“What if it's not for me?” — “Email us within 14 days for a full refund, no exit interview.” beats three paragraphs of policy-ese. Honest not-for-you answers (“If you want done-for-you, this course will frustrate you”) raise conversion among the right buyers and lower refunds among the wrong ones."] },
      { h: "Placement", paras: ["After pricing, before the final CTA. The FAQ's job is to hand a now-unblocked reader straight back to the button. Add FAQ schema markup so search engines can surface the same answers."] },
    ],
    [{ q: "How many FAQs is too many?", a: "Five to nine. Beyond that, group them or move rare ones to a support page." },
     { q: "Should FAQs include the refund policy?", a: "Always. It is the most-searched answer on any offer page and hiding it reads as intent." }]),

  A("mobile-landing-page-issues",
    "Mobile Landing Page Issues: The 6 Checks That Matter First",
    "Most landing page traffic is mobile. Fix these six mobile issues first: viewport, tap targets, hero height, form keyboards, page weight, sticky CTA.",
    "mobile landing page issues", 6,
    "Designers review pages on desktop; buyers meet them on phones — often on mediocre connections. These six checks catch the mobile failures that cost the most.",
    [
      { h: "The six checks", paras: [], list: ["Viewport meta present (without it, the page renders as a shrunken desktop site)", "Headline + CTA visible in the first screen-height — no full-screen hero image pushing the button below the fold", "Tap targets ≥ 44px with spacing (fat-thumb rule)", "Correct input types: email/tel keyboards, autocomplete attributes", "Page weight discipline: compressed images, no auto-playing hero video on cellular", "No horizontal scroll, no hover-only interactions, no popups that cannot be closed on a small screen"] },
      { h: "The 60-second phone audit", paras: ["Open your page on your own phone with Wi-Fi off. Time to readable headline? Can you tap the CTA one-handed? Does the form summon the right keyboard? Anything over ~3 seconds to first content on 4G is a leak. Our scanner covers the automatable subset — viewport, HTTPS, HTML weight, response time, alt text — but the one-handed tap test is yours to run."] },
    ],
    [{ q: "Do I need a sticky mobile CTA?", a: "On long sales pages, a slim sticky bottom bar with the primary CTA usually helps. Test it; remove it if it covers content or annoys." },
     { q: "What page size is acceptable?", a: "Keep total initial load under ~1.5 MB where you can; HTML itself under ~200 KB is a healthy target for a landing page." }]),

  A("why-landing-page-not-converting",
    "Why Is My Landing Page Not Converting? A 10-Minute Diagnosis",
    "Traffic but no sales or bookings? Diagnose in order: clarity, trust, offer transparency, friction, then traffic quality. Free scanner runs the first four.",
    "why is my landing page not converting", 7,
    "Non-converting pages almost never have ten problems. They have one broken link in a chain of five. Diagnose in this order — each step assumes the previous one holds.",
    [
      { h: "Step 1: Can a stranger say what this is? (Clarity)", paras: ["Show the page for five seconds, hide it, ask: what's sold, for whom, what's the next click? Any wrong answer = your leak is here, at the top, and nothing below matters until it's fixed. This is the single most common cause we are built to catch."], list: ["Headline names an outcome, not a format", "Audience is named ('for coaches who…')", "One obvious primary button above the fold"] },
      { h: "Step 2: Would a stranger trust it? (Proof)", paras: ["Cold visitors look for a reachable human, specific proof, and legal basics. Missing pieces don't always kill the sale loudly — they kill it as a vague 'let me think about it' that never returns. Run the Trust Signal Checker on your copy."] },
      { h: "Step 3: Is the deal fully visible? (Transparency)", paras: ["Price discoverable only at checkout, deliverables described as vibes, no FAQ, no refund line. Each hidden answer is an exit. If a visitor must click 'buy' to learn what buying means, most won't."] },
      { h: "Step 4: How hard is yes? (Friction)", paras: ["Count required fields before the first win. Nine-field applications before a free call, account creation before checkout, phone numbers demanded without a reason. Cut the first step to email (+name) and qualify later."] },
      { h: "Step 5: Is it actually the traffic? (Fit)", paras: ["If clarity, trust, transparency, and friction all pass, the mismatch is upstream: the ad/post/referral promised something the page doesn't, or the audience was never buyers. Check that your traffic source's promise matches your headline word-for-word in spirit. And keep the honest caveat: clarity cannot rescue an offer the market doesn't want — it just stops you blaming the page for it."] },
    ],
    [{ q: "How do I know which step is broken?", a: "Run the free scanner: steps 1–4 map to its six categories with per-check evidence. Fix the earliest failing step first." },
     { q: "My page converts at 1%. Is that bad?", a: "Depends on price, traffic warmth, and the action (email vs $997 checkout). Cold-to-sale at 1% can be healthy; warm-to-free-call at 1% is a five-alarm clarity fire. Context beats benchmarks." }]),

  A("above-the-fold-checklist",
    "Above the Fold: The 6 Elements Your First Screen Must Carry",
    "What to put above the fold on a landing page: headline, subheadline, CTA, proof hint, visual, and nav discipline — with a 5-second self-test.",
    "what to put above the fold landing page", 6,
    "The fold is not magic — people scroll. But the first screen decides whether scrolling happens. These six elements earn the scroll.",
    [
      { h: "The six", paras: [], list: ["Headline: audience + outcome (20–90 characters)", "Subheadline: how it works / proof of mechanism in one line", "Primary CTA: verb + object + what happens next", "Proof hint: one specific number or name (only if true)", "Visual: the product, the person, or the result — not abstract stock fog", "Nav discipline: logo + at most 3 links (or none on campaign pages)"] },
      { h: "What to evict from the first screen", paras: ["Full-screen hero videos that push the CTA below the fold on mobile. Carousels (three messages = no message). 'Welcome to my website.' Award badges from 2019. Anything that delays the answer to 'what is this and is it for me?'"] },
      { h: "The 5-second self-test", paras: ["Screenshot the first screen on a phone. Give yourself five seconds. Could you brief a colleague on the offer from memory? If not, the fold is decoration pretending to be communication. Our scanner automates the checkable parts — H1, outcome language, audience, early CTA."] },
    ],
    [{ q: "Does fold placement matter on mobile?", a: "More, not less. The mobile first screen is smaller and the thumb is restless — headline + CTA must both fit without a scroll." },
     { q: "Should the price be above the fold?", a: "For low-ticket offers, yes. For high-ticket, a 'from $X' anchor or a visible Pricing link in nav does the job." }]),

  A("landing-page-form-best-practices",
    "Landing Page Form Best Practices: How Many Fields Is Too Many?",
    "Form friction kills more conversions than bad headlines. Field-count rules, ordering, sensitive-field timing, and the two-step pattern that fixes long forms.",
    "landing page form best practices", 6,
    "Every field is a tiny negotiation. The visitor asks: 'Is what I get worth what you're asking?' Fields that feel nosy, early, or unexplained lose that negotiation. Here is the practical rulebook.",
    [
      { h: "The field budget", paras: [], list: ["Lead magnet / email capture: 1 field (email), 2 max (+ first name)", "Free call booking: name + email (+ calendar does the rest); 2 qualifying questions max", "Paid checkout: only what the payment processor needs; account creation AFTER purchase", "Applications (high-ticket): longer is fine — friction as a filter is legitimate when capacity is truly limited; say so on the page"] },
      { h: "Ordering and honesty", paras: ["Easy first (name, email), sensitive later (phone, budget, URLs), open-ended last. Beside any sensitive field, one clause of reason: 'Phone — only if we need to reschedule.' Unexplained data requests read as data harvesting, because sometimes they are."] },
      { h: "The two-step fix", paras: ["Step 1: email (the small yes). Step 2 (thank-you page or follow-up): qualifying questions framed as personalization. Completion rates on step 2 are high precisely because commitment already happened. Check your current first step with the free Form Friction Checker."] },
    ],
    [{ q: "Is asking for a phone number always bad?", a: "No — for booked calls it's often necessary. It's bad unexplained and bad as field #1 before any value or commitment." },
     { q: "Should I use multi-step forms?", a: "For anything over ~4 fields, yes — with a progress cue and the easy questions first." }]),

  A("should-coaches-show-prices",
    "Should Coaches Show Prices on Their Website? (Yes — Here's How)",
    "Hidden coaching prices filter out your best buyers. The case for price transparency, three ways to show fees without boxing yourself in, and what to do instead of 'book a call to learn more'.",
    "should coaches show prices on website", 6,
    "The standard advice — hide prices so prospects 'get on a call first' — optimizes for call volume. What it actually produces is calls with people who were never going to pay your fee, and silence from the budget-aware professionals who would have.",
    [
      { h: "What hidden pricing actually filters", paras: ["Serious buyers research with a shortlist and a budget range. A missing price doesn't make you premium; it makes you uncomparable, so you fall off the list. Meanwhile the purely curious — no budget, no urgency — happily book free calls. You end up 'selling' hardest to the least qualified."] },
      { h: "Three ways to show fees without a corner", paras: [], list: ["Exact price for a productized entry offer (audit, intensive, sprint) — bespoke work quoted after, anchored by it", "A range tied to scope ('Engagements run $3k–$8k depending on X')", "A 'from' anchor + what moves the number up ('from $250/session; packages from $1,800')"] },
      { h: "If you still gate the number", paras: ["At minimum, publish who should NOT book on budget grounds ('If $X is a stretch, my free resources will serve you better right now'). It respects everyone's time — and reads as confidence, not gatekeeping. Then verify the rest of the page with the free scanner: price visibility is one of its 25 checks for a reason."] },
    ],
    [{ q: "Won't competitors undercut me?", a: "They can see your positioning anyway; clients who choose on price alone were going to churn on price alone." },
     { q: "What about high-ticket ($10k+) coaching?", a: "Ranges and application filters are legitimate at true high-ticket with limited capacity. Still anchor: 'Applications open for Q3; engagements from $12k' respects the reader." }])
];

export interface NichePage {
  slug: string; audience: string; title: string; description: string;
  hero: string; pains: string[]; checks: string[]; exampleFix: string;
}

export const NICHES: NichePage[] = [
  { slug: "coaches", audience: "Coaches",
    title: "Landing Page Clarity Audit for Coaches",
    description: "Free clarity score for coaching pages: outcome headline, discovery-call CTA, proof, and pricing transparency — scored in seconds.",
    hero: "Your coaching page has five seconds to answer: what changes, for whom, and how do we start?",
    pains: ["“Transform your life” headlines that could belong to any coach on Earth", "Discovery calls hidden behind 9-field applications", "No price anchor, so only the already-convinced book", "Testimonials that glow but say nothing specific"],
    checks: ["Outcome + audience in the headline", "Low-friction first step (not just “apply”)", "Price or starting-point visible", "FAQ that answers “is the call a sales pitch?”"],
    exampleFix: "Before: “Transform Your Life Today!!!” → After: “I help new managers end Sunday-night dread in 8 weeks — without quitting the job they mostly like.”" },
  { slug: "course-creators", audience: "Course creators",
    title: "Course Sales Page Clarity Audit",
    description: "Score your course sales page before launch: curriculum outcomes, price block, guarantee, FAQ — free instant check.",
    hero: "Buyers skim for outcome, curriculum, proof, price, refund. If any one is missing, launch day leaks.",
    pains: ["Curriculum listed as topics, not capabilities", "Price discoverable only at checkout", "Guarantee buried or absent", "No fit/not-fit block, so refunds do the filtering"],
    checks: ["Module titles written as outcomes", "Deliverables checklist above the buy button", "Guarantee next to the price", "FAQ covering time, access, tech, refund"],
    exampleFix: "Before: “Module 3: Email Marketing” → After: “Module 3: Write the 5 emails that sell while you sleep (swipe templates inside).”" },
  { slug: "consultants", audience: "Consultants",
    title: "Consultant Website Clarity Audit",
    description: "Turn a services brochure into a bookable offer. Free clarity score for consultant websites: niche statement, entry offer, booking friction.",
    hero: "Clients don't buy “services”. They buy a defined first step with a defined outcome.",
    pains: ["Capability lists with no productized entry offer", "No fee anchor anywhere on the site", "“Contact us” as the only next step", "Niche so broad it reads as “available”"],
    checks: ["One-sentence niche statement in the hero", "Fixed-scope entry offer with a price", "Calendar booking in ≤2 questions", "Proof with client type + measurable change"],
    exampleFix: "Before: “Strategy & Operations Consulting” → After: “2-week pricing audit for B2B SaaS under $5M. $2,500 fixed. Findings + roadmap, guaranteed sections or refund.”" },
];
