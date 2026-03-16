---
name: audit-website
description: >
  Audit any website for SEO, performance, accessibility, security, and content quality issues
  using Python and standard CLI tools. No external CLI binaries required. Returns a structured
  report with a health score (0-100), categorized issues by severity, and actionable fix
  recommendations. Use whenever the user wants to check a site's health, debug SEO problems,
  find broken links, validate meta tags or structured data, review security headers, assess
  accessibility, generate an audit report, or compare site health before and after changes.
  Also trigger on phrases like "audit my site," "check my website," "SEO issues," "site health,"
  "broken links," "page speed," "meta tags," "security headers," "accessibility check," or
  any URL followed by a request to analyze, review, or improve it.
---

# Website Audit Skill

Audit websites for SEO, technical, content, performance, accessibility, and security issues using Python scripts and standard tools already available in the environment. No proprietary CLI binaries needed.

## How It Works

This skill uses a Python-based audit engine (`scripts/audit_engine.py`) that fetches pages via HTTP, parses the HTML, and runs 80+ checks across 10 categories. It produces a structured JSON report that the agent then summarizes for the user.

### Categories Covered

The audit checks fall into these groups:

1. **Core SEO**: title tags, meta descriptions, canonical URLs, Open Graph, robots directives
2. **Technical SEO**: broken links (internal + external), redirect chains, sitemap.xml, robots.txt
3. **Performance**: page size, resource count, image optimization hints, render-blocking resources
4. **Content Quality**: heading hierarchy (H1-H6), word count, duplicate content signals, keyword density
5. **Security**: HTTPS enforcement, security headers (CSP, HSTS, X-Frame-Options, etc.), mixed content
6. **Accessibility**: image alt text, form labels, ARIA landmarks, color contrast (basic), lang attribute
7. **Schema/Structured Data**: JSON-LD presence and validation, required properties per schema type
8. **Links**: internal link structure, orphan pages, external link health, anchor text quality
9. **Mobile**: viewport meta, touch target sizing, responsive signals
10. **Social**: Open Graph completeness, Twitter Card tags

### Running an Audit

**Step 1: Run the audit script**

```bash
python3 /path/to/audit-website/scripts/audit_engine.py "https://example.com" --max-pages 25 --output /tmp/audit_report.json
```

Key options:
- `--max-pages N`: Maximum pages to crawl (default 25, max 100)
- `--output PATH`: Where to save the JSON report
- `--check-external`: Also verify external link health (slower, off by default)
- `--verbose`: Print progress to stderr

**Step 2: Read and interpret the report**

The JSON report structure is documented in `references/REPORT-FORMAT.md`. Read that file to understand the scoring model and issue schema before presenting results.

**Step 3: Present findings to the user**

Summarize the report in this order:
1. Overall health score and grade (A through F)
2. Top issues by severity (errors first, then warnings, then notices)
3. Category breakdown with per-category scores
4. Specific actionable recommendations

### Grading Scale

| Score     | Grade | Meaning                                      |
|-----------|-------|----------------------------------------------|
| 90-100    | A     | Excellent, minor polish only                 |
| 80-89     | B     | Good, a few issues to address                |
| 70-79     | C     | Fair, notable problems impacting quality     |
| 50-69     | D     | Poor, significant issues across categories   |
| Below 50  | F     | Critical, major problems need immediate work |

### Fix Workflow

When the user asks to fix issues (not just audit):

1. Present the audit results and propose a prioritized fix plan
2. Get user confirmation before making any changes
3. Group fixes by type: code changes vs. content changes
4. After applying fixes, re-run the audit to confirm improvements
5. Show before/after score comparison

Always flag issues that require human judgment (e.g., "should this broken external link be removed or replaced?") rather than making assumptions.

### Important Constraints

- Crawl only the domain provided. Do not follow links to external domains during the crawl phase.
- Respect robots.txt when crawling. If the robots.txt disallows a path, skip it and note it in the report.
- Rate-limit requests: wait at least 1 second between fetches to avoid hammering the server.
- For sites behind authentication or paywalls, inform the user that those pages cannot be audited.
- The audit script needs `requests` and `beautifulsoup4`. Install them if not present: `pip install requests beautifulsoup4 --break-system-packages`

### Edge Cases

- **User provides no URL**: Ask which site they want audited.
- **URL missing protocol**: Prepend `https://` and inform the user.
- **Site is unreachable**: Report the connection error clearly and suggest the user verify the URL.
- **Very large site**: Cap at `--max-pages 100` and inform the user that a partial audit was performed. Suggest re-running on specific sections (e.g., `/blog`) for deeper coverage.

## Reference Files

- `references/REPORT-FORMAT.md`: Full JSON report schema, scoring algorithm, and field definitions. Read this before interpreting audit output.
- `scripts/audit_engine.py`: The main audit script. Run it with Python 3.8+.
