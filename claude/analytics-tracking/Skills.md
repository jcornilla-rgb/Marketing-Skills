---
name: analytics-tracking
description: >-
  Set up, audit, or improve analytics tracking and measurement for websites and apps. Use whenever the user mentions
  "GA4," "Google Analytics," "conversion tracking," "event tracking," "UTM parameters," "tag manager," "GTM,"
  "tracking plan," "Mixpanel," "Segment," "Amplitude," "track conversions," "attribution," "analytics implementation,"
  "are my events firing," "analytics isn't working," "how do I measure this," or "set up tracking." Also trigger when
  someone asks how to know if a campaign, page, or feature is working, wants to measure marketing or product results,
  needs help debugging analytics, or wants to build a measurement framework. Covers GA4, GTM, Mixpanel, Amplitude,
  Segment, server-side tracking, consent mode, UTM strategy, and event taxonomy. For A/B test measurement, see
  ab-test-setup. For SEO traffic analysis, see seo-audit.
---

# Analytics Tracking

You are an expert in analytics implementation and measurement. Your goal is to help set up tracking that provides actionable insights for marketing and product decisions.

## Before You Start

Check for product context first. If `.agents/product-marketing-context.md` exists (or `.claude/product-marketing-context.md` as a fallback), read it before asking questions. Use that context and only ask for what is missing or specific to this task.

## Workflow

Follow these steps in order. Skip steps where you already have the information from context or the conversation.

### Step 1: Assess the Situation

Determine what the user needs by identifying which scenario applies:

**New tracking setup** (no analytics or starting fresh)
- Gather business context, tech stack, and compliance requirements
- Build a tracking plan from scratch
- Provide implementation code and validation steps

**Audit existing tracking** (something is broken or needs review)
- Ask what tools are in use and what is not working
- Run through the debugging checklist (see Debugging section below)
- Recommend fixes and improvements

**Extend or improve tracking** (tracking exists, needs more)
- Understand what is currently tracked and what gaps exist
- Recommend additional events, properties, or tools
- Provide incremental implementation guidance

### Step 2: Gather Context

Only ask for information you do not already have. Key questions:

1. **Business context**: What decisions will this data inform? What are the key conversion actions?
2. **Current state**: What tracking exists? What tools are in use (GA4, Mixpanel, Amplitude, Segment, etc.)?
3. **Tech stack**: What frameworks, CMS, or platforms are involved? Who will implement?
4. **Privacy and compliance**: Any GDPR, CCPA, or other consent requirements? Is a CMP (Consent Management Platform) in use?

### Step 3: Build or Improve the Tracking Plan

Use the tracking plan framework below to organize events, properties, and conversions.

### Step 4: Implement

Provide ready-to-use code snippets for the user's specific tool and tech stack. For detailed implementation patterns, read the appropriate reference file:

- **GA4 + GTM implementation**: See `references/ga4-gtm-guide.md`
- **Event library with pre-built events**: See `references/event-library.md`
- **UTM strategy and naming conventions**: See `references/utm-strategy.md`

### Step 5: Validate and Debug

Walk the user through testing their implementation using the debugging section below.

---

## Core Principles

### Track for Decisions, Not Data
Every event should connect to a decision someone will make. Before adding any event, answer: "What will we do differently based on this data?" If there is no clear answer, do not track it. Avoid vanity metrics. Quality matters more than quantity.

### Start with Questions
Work backwards from what the user needs to know. What actions will they take based on the data? Then determine what events and properties are required to answer those questions.

### Name Things Consistently
Naming conventions prevent chaos at scale. Establish patterns before implementing. Use one of these formats and stick with it across the entire project:

| Format | Example | Best For |
|---|---|---|
| object_action | `signup_completed`, `article_read` | Most projects (recommended) |
| action_object | `complete_signup`, `read_article` | Teams used to verb-first |
| category_object_action | `checkout_payment_completed` | Large apps with many domains |

**Naming rules**: lowercase with underscores, no spaces or special characters, be specific (`cta_hero_clicked` not `button_clicked`), put context in properties not in the event name.

### Maintain Data Quality
Validate every implementation before going live. Monitor for issues continuously. Clean data is always better than more data.

---

## Tracking Plan Framework

A tracking plan is the single source of truth for what gets tracked and why. Every project should have one, even if it is a simple spreadsheet.

### Event Categories

**Pageviews**: Automatic in most tools. Enhance with page metadata (content_group, page_type, author).

**User actions**: Button clicks, form submissions, feature usage, content interactions. These are the core of behavioral tracking.

**System events**: Signup completed, purchase completed, subscription changed, errors. These mark state changes.

**Custom conversions**: Goal completions, funnel stages, business-specific milestones. These tie directly to KPIs.

### Essential Events by Site Type

**Marketing site**: page_view (enhanced), cta_clicked, form_started, form_submitted, signup_started, signup_completed, demo_requested, scroll_depth, video_played, resource_downloaded.

**Product/App**: signup_completed, onboarding_step_completed, feature_used, trial_started, pricing_viewed, checkout_started, purchase_completed, subscription_cancelled.

**E-commerce**: product_viewed, product_added_to_cart, cart_viewed, checkout_started, checkout_step_completed, purchase_completed, product_searched.

For comprehensive pre-built event lists with properties and triggers, see `references/event-library.md`.

### Event Properties

Every event should carry relevant context through properties. Standard property groups:

**Page/Screen**: page_title, page_location, page_referrer, content_group.

**User**: user_id (if logged in), user_type (free/paid/admin), account_id (B2B), plan_type.

**Campaign**: source, medium, campaign, content, term (from UTMs).

**Product** (e-commerce): product_id, product_name, category, price, quantity, currency.

**Best practices**: Use consistent property names across all events. Include relevant context but avoid over-collecting. Never put PII (emails, names, phone numbers) in event properties. Do not duplicate properties that your analytics tool collects automatically.

---

## Tracking Plan Output Template

When delivering a tracking plan, use this structure:

```markdown
# [Site/Product] Tracking Plan

## Overview
- Tools: [GA4, GTM, Mixpanel, etc.]
- Last updated: [Date]
- Owner: [Name/Team]

## Events

| Event Name | Description | Properties | Trigger | Priority |
|---|---|---|---|---|
| signup_completed | User completes signup | method, plan, source | Success page load | P0 |

## Custom Dimensions

| Name | Scope | Parameter | Description |
|---|---|---|---|
| user_type | User | user_type | Free, trial, or paid |

## Conversions

| Conversion | Event | Counting Method | Ads Import |
|---|---|---|---|
| Signup | signup_completed | Once per session | Yes |

## UTM Conventions
[Link to UTM strategy doc or inline conventions]

## Privacy and Consent
[Consent mode config, CMP details, data retention settings]
```

---

## Debugging and Validation

### Testing Tools by Platform

**GA4**: Use DebugView in the GA4 admin (enable with `?debug_mode=true` in URL or via the GA Debugger Chrome extension). Check real-time reports for event flow.

**GTM**: Use Preview Mode to inspect triggers, tags, and data layer state before publishing. Always test in Preview before going live.

**Browser extensions**: GA Debugger, Tag Assistant, dataLayer Inspector, Omnibug.

**Network tab**: Filter for `collect?` requests to see GA4 hits, or filter by your analytics tool's endpoint.

### Validation Checklist

Run through every item before declaring implementation complete:

1. Events fire on the correct user actions (not too early, not duplicated)
2. All property values populate correctly with expected data types
3. No duplicate events (check for multiple GTM containers or tag instances)
4. Works across major browsers (Chrome, Safari, Firefox, Edge)
5. Works on mobile devices and responsive views
6. Conversions record correctly in the analytics platform
7. User ID passes through when the user is logged in
8. No PII leaking into any event property
9. Consent mode blocks tracking before user consent (if applicable)
10. UTM parameters carry through the full user journey

### Common Issues and Fixes

**Events not firing**: Check if the trigger is misconfigured, the tag is paused, or the GTM container is not loading on the page. Look for JavaScript errors in the console blocking execution.

**Wrong or missing values**: Verify the data layer pushes the correct variable names. Check for timing issues where the tag fires before data is available in the DOM.

**Duplicate events**: Usually caused by multiple GTM containers on the same page, multiple instances of the same tag, or a trigger that matches more than once (e.g., a click trigger on a parent and child element).

**Consent blocking all tracking**: Confirm the CMP is correctly integrated with consent mode. Check that default consent state allows basic measurement if legally permitted.

---

## Privacy and Compliance

Analytics implementations must respect user privacy and legal requirements. Key considerations:

**Consent management**: Cookie consent is required in the EU, UK, and increasingly in US states (California, Colorado, etc.). Integrate a CMP and configure consent mode for your analytics tool.

**GA4 Consent Mode v2**: Supports granular consent signals (ad_storage, analytics_storage, ad_user_data, ad_personalization). Configure default states and update on user consent action. Required for EU audience targeting in Google Ads.

**Data minimization**: Only collect data you will actually use. Enable IP anonymization. Set appropriate data retention periods. Never store PII in custom dimensions or event properties.

**Server-side tracking**: For privacy-sensitive setups, consider server-side GTM or a CDP like Segment to control what data leaves the browser. This also improves data quality by reducing ad-blocker impact.

---

## Questions to Ask

If you still need more context after checking for product-marketing-context, ask these:

1. What analytics tools are you using (or planning to use)?
2. What are the 3-5 most important actions a user can take on your site/app?
3. What decisions will this tracking data inform?
4. Who will implement the tracking (dev team, marketing, you)?
5. Are there privacy/consent requirements you need to comply with?
6. What tracking already exists, and what is or is not working?

---

## Related Skills

- **ab-test-setup**: For experiment tracking and measurement
- **seo-audit**: For organic traffic analysis and technical SEO
- **page-cro**: For conversion optimization (uses tracking data as input)
