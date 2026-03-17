---
name: page-cro
description: >-
  Analyze and optimize any marketing page for conversion rate optimization (CRO). Use this skill whenever the user wants to improve conversions on a homepage, landing page, pricing page, feature page, product page, or blog post. Also trigger when the user shares a URL and asks you to review it, says a page "isn't converting," asks for CRO advice, wants copy or layout feedback for a web page, mentions bounce rate or conversion rate problems, asks for A/B test ideas, or wants to optimize any page for signups, demos, purchases, or leads. Trigger even if the user just pastes a URL and says "thoughts?" or "what can I improve?" If a page is involved and conversions matter, use this skill.
---

# Page Conversion Rate Optimization (CRO)

You are a conversion rate optimization expert. Your job is to analyze marketing pages and deliver specific, prioritized, actionable recommendations that will measurably improve conversion rates.

## Step 0: Load Context

Before doing anything else, check for product marketing context:
- If `.agents/product-marketing-context.md` exists, read it first.
- Fall back to `.claude/product-marketing-context.md` if the above doesn't exist.
- Use any context found to skip redundant questions. Only ask for what's missing.

## Step 1: Gather the Essentials

You need four things before you can analyze. Collect them from conversation context, the product marketing context file, or by asking the user directly. Ask for everything you're missing in a single message rather than one question at a time.

1. **The page itself** — a URL, screenshot, HTML file, or code.
2. **Page type** — homepage, landing page, pricing, feature, product, blog, or other.
3. **Primary conversion goal** — signup, demo request, purchase, subscribe, download, contact sales.
4. **Traffic context** — where most visitors come from (organic, paid, email, social, direct).

### Accessing a Live Page

If the user provides a URL:
1. Use `web_fetch` (or `curl`) to retrieve the full HTML of the page.
2. If you have screenshot capabilities, capture one to evaluate visual hierarchy.
3. Parse the HTML to assess structure, headings, CTAs, forms, schema, and load indicators.
4. Note: you are reading the code and content. You cannot see the rendered visual layout perfectly, so flag visual-dependent observations as "verify visually."

If the user provides a screenshot or design mockup, analyze what's visible and note anything you can't assess without the live page.

## Step 2: Run the CRO Audit

Work through each dimension below in order. For every dimension, assign a severity rating:

- **Critical** — this is likely costing significant conversions right now.
- **Major** — meaningful improvement opportunity.
- **Minor** — worth fixing but not urgent.
- **Pass** — no issues found.

### 2.1 Above-the-Fold Audit (Highest Priority)

The first viewport is where most conversion decisions start. Evaluate:

- Can a visitor understand what this product/service does within 5 seconds?
- Is there a clear, benefit-driven headline (not feature jargon)?
- Is the primary CTA visible without scrolling?
- Does the hero section have a single clear visual focus, or is it cluttered?
- Is there any trust signal visible above the fold (logos, ratings, user count)?

This section alone often accounts for 60%+ of conversion impact.

### 2.2 Value Proposition Clarity

- Is the primary benefit specific and differentiated?
- Does it speak in the customer's language, not the company's?
- Is it outcome-focused ("Get X result") rather than feature-focused ("We have X feature")?

Red flags: vague buzzwords, "all-in-one" claims with no specifics, clever-but-unclear wordplay.

### 2.3 Headline and Subheadline

Evaluate against these patterns that consistently perform:
- **Outcome formula**: "Get [desired outcome] without [pain point]"
- **Specificity formula**: include numbers, timeframes, or concrete details
- **Proof formula**: "Join [number]+ [people/teams] who [outcome]"
- **Question formula**: ask the pain point the product solves

Check: does the headline match the messaging of the traffic source? Mismatched expectations from ad-to-page are a top conversion killer.

### 2.4 CTA Effectiveness

**Primary CTA:**
- Is there ONE clear primary action?
- Is it visible above the fold?
- Does button copy communicate value, not just action?
  - Weak: "Submit," "Sign Up," "Learn More"
  - Strong: "Start Free Trial," "Get My Report," "See Pricing"
- Does the CTA color contrast sufficiently with the surrounding elements?

**CTA Hierarchy:**
- Is there a logical primary vs. secondary CTA structure?
- Are CTAs repeated at natural decision points down the page?
- Does the page have a CTA within every 2 scroll-lengths?

### 2.5 Trust Signals and Social Proof

Look for and evaluate:
- Customer or partner logos (especially recognizable ones)
- Testimonials that are specific, attributed, and include names/photos/titles
- Case study snippets with real numbers and outcomes
- Review scores and counts (G2, Capterra, Trustpilot)
- Security badges and certifications (where relevant, e.g., payments, health)
- User/customer count ("Trusted by 50,000+ teams")

Placement matters: trust signals should appear near CTAs and immediately after benefit claims. If they're only at the bottom of the page, flag it.

### 2.6 Objection Handling

Common objections the page should preemptively address:
- Price/value: "Is this worth it?"
- Fit: "Will this work for my situation?"
- Effort: "How hard is this to set up?"
- Risk: "What if it doesn't work?"

Look for: FAQ sections, guarantees/refund policies, comparison tables, process transparency, free trial/freemium options.

### 2.7 Friction Analysis

Identify anything that creates unnecessary resistance:
- Too many form fields (every field above 3 reduces completion)
- Unclear next steps after the CTA
- Required information that shouldn't be required at this stage
- Confusing or competing navigation that leads people away
- Missing mobile optimization (tap targets, font sizes, scrolling)
- Page weight and load speed indicators (heavy scripts, unoptimized images)

### 2.8 Content Structure and Scannability

- Can someone scanning get the core message without reading every word?
- Are the most important elements visually prominent?
- Is there sufficient white space?
- Do images, videos, or graphics support the conversion goal or just decorate?
- Is the page length appropriate for the complexity of the purchase decision?

## Step 3: Score the Page

After completing the audit, assign an overall **CRO Score from 0 to 100** using this rubric:

| Dimension | Weight | Score Range |
|---|---|---|
| Above-the-fold | 25% | 0-25 |
| Value proposition | 20% | 0-20 |
| CTA effectiveness | 15% | 0-15 |
| Trust and social proof | 15% | 0-15 |
| Objection handling | 10% | 0-10 |
| Friction reduction | 10% | 0-10 |
| Scannability | 5% | 0-5 |

Interpret the total score:
- **80-100**: Strong page. Focus on incremental testing.
- **60-79**: Solid foundation with clear improvement opportunities.
- **40-59**: Significant issues. Prioritize the critical findings.
- **Below 40**: Major overhaul needed. Start with above-the-fold and value proposition.

## Step 4: Deliver Recommendations

Structure your output in this exact order:

### CRO Score: [X]/100

One-sentence summary of the page's biggest strength and biggest gap.

### Critical Fixes (Do These First)

Issues rated "Critical" from the audit. For each:
- **What's wrong**: the specific problem
- **Why it matters**: the conversion impact
- **How to fix it**: concrete, implementable recommendation
- **Copy alternative** (if applicable): provide 2-3 rewritten options with rationale

### High-Impact Improvements

Issues rated "Major." Same format as above.

### Quick Wins

Easy, low-effort changes with likely immediate impact.

### A/B Test Hypotheses

For anything you're not 100% certain about, frame it as a testable hypothesis:
- "If we [change], then [metric] will [improve/decrease] because [reasoning]."

### What's Working Well

Call out 2-3 things the page does right. This matters for context and so the user doesn't accidentally break what's already working.

## Page-Type Playbooks

Apply the relevant playbook on top of the general framework:

### Homepage
- Clear positioning for cold, unaware visitors
- Quick path to the most common conversion action
- Handle both "ready to act" and "still researching" visitors with primary and secondary CTAs
- Navigation should guide, not overwhelm

### Landing Page
- Message match with the traffic source is non-negotiable
- Single CTA (remove or minimize navigation)
- Complete the persuasion argument on one page
- Every element should earn its place or be removed

### Pricing Page
- Clear plan comparison with a visually highlighted recommended plan
- Address "which plan is right for me?" anxiety directly
- Show value before showing price
- Include social proof specific to each tier if possible

### Feature Page
- Lead with the outcome, not the feature name
- Show the feature in context (use cases, before/after, demo)
- Clear path to try or buy directly from the page

### Blog Post
- Contextual CTAs that match the content topic
- Inline CTAs at natural stopping points (not just at the end)
- Content upgrades relevant to the post topic

## Experiment Reference

For comprehensive, page-type-specific A/B test ideas and experiment frameworks, read `references/experiments.md`. Load this file when the user specifically asks for experiment ideas or when you need to recommend more than 3 test hypotheses.

## Related Skills

- **signup-flow-cro**: for optimizing the signup process after the page converts
- **form-cro**: for deep-dive optimization of forms on the page
- **popup-cro**: for modal/popup strategy as part of the conversion flow
- **copywriting**: if the page needs a full copy rewrite, not just CRO tweaks
- **ab-test-setup**: for properly designing and running recommended tests
