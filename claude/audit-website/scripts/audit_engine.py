#!/usr/bin/env python3
"""
audit_engine.py - Website audit tool for SEO, performance, accessibility, security, and content quality.

Usage:
    python3 audit_engine.py "https://example.com" [options]

Options:
    --max-pages N        Maximum pages to crawl (default: 25, max: 100)
    --output PATH        Save JSON report to file (default: stdout)
    --check-external     Also check external link health
    --verbose            Print progress to stderr
"""

import argparse
import json
import re
import sys
import time
import hashlib
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse, urlunparse
from collections import defaultdict

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("ERROR: Missing dependencies. Install with:", file=sys.stderr)
    print("  pip install requests beautifulsoup4 --break-system-packages", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def normalize_url(url):
    """Normalize a URL for deduplication."""
    parsed = urlparse(url)
    path = parsed.path.rstrip("/") or "/"
    return urlunparse((parsed.scheme, parsed.netloc, path, "", "", ""))


def is_same_domain(url, base_domain):
    """Check if a URL belongs to the same domain."""
    try:
        return urlparse(url).netloc == base_domain
    except Exception:
        return False


def fetch_page(url, session, timeout=15):
    """Fetch a page and return (response, error_string_or_None)."""
    try:
        resp = session.get(url, timeout=timeout, allow_redirects=True)
        return resp, None
    except requests.exceptions.Timeout:
        return None, "timeout"
    except requests.exceptions.ConnectionError:
        return None, "connection_error"
    except requests.exceptions.TooManyRedirects:
        return None, "too_many_redirects"
    except Exception as e:
        return None, str(e)


def fetch_robots_txt(base_url, session):
    """Fetch and parse robots.txt, return set of disallowed paths."""
    robots_url = urljoin(base_url, "/robots.txt")
    resp, err = fetch_page(robots_url, session, timeout=10)
    disallowed = set()
    if resp and resp.status_code == 200:
        for line in resp.text.splitlines():
            line = line.strip()
            if line.lower().startswith("disallow:"):
                path = line.split(":", 1)[1].strip()
                if path:
                    disallowed.add(path)
    return disallowed


def is_disallowed(url, disallowed_paths):
    """Check if a URL path is disallowed by robots.txt."""
    path = urlparse(url).path
    for dp in disallowed_paths:
        if path.startswith(dp):
            return True
    return False


# ---------------------------------------------------------------------------
# Check functions - each returns a list of issue dicts
# ---------------------------------------------------------------------------

def check_core_seo(url, soup, resp):
    """Core SEO checks: title, meta description, canonical, OG, robots."""
    issues = []

    # Title tag
    title_tag = soup.find("title")
    if not title_tag or not title_tag.get_text(strip=True):
        issues.append({
            "id": "seo-001", "category": "core_seo", "severity": "error",
            "title": "Missing title tag",
            "description": "Page has no <title> element. Search engines rely on this as the primary heading in results.",
            "recommendation": "Add a unique, descriptive title tag (30-60 characters).",
            "penalty": 10
        })
    else:
        title_text = title_tag.get_text(strip=True)
        if len(title_text) > 70:
            issues.append({
                "id": "seo-002", "category": "core_seo", "severity": "warning",
                "title": "Title tag too long",
                "description": f"Title is {len(title_text)} characters. Google typically truncates titles beyond ~60 characters.",
                "recommendation": "Shorten to 50-60 characters while keeping it descriptive.",
                "penalty": 3
            })
        elif len(title_text) < 20:
            issues.append({
                "id": "seo-003", "category": "core_seo", "severity": "warning",
                "title": "Title tag too short",
                "description": f"Title is only {len(title_text)} characters. Short titles miss keyword opportunities.",
                "recommendation": "Expand to 30-60 characters with relevant keywords.",
                "penalty": 3
            })

    # Meta description
    meta_desc = soup.find("meta", attrs={"name": re.compile(r"^description$", re.I)})
    if not meta_desc or not meta_desc.get("content", "").strip():
        issues.append({
            "id": "seo-004", "category": "core_seo", "severity": "error",
            "title": "Missing meta description",
            "description": "No meta description found. Search engines may auto-generate a snippet, which is often suboptimal.",
            "recommendation": "Add a compelling meta description (120-160 characters) summarizing the page content.",
            "penalty": 8
        })
    else:
        desc_len = len(meta_desc["content"].strip())
        if desc_len > 170:
            issues.append({
                "id": "seo-005", "category": "core_seo", "severity": "notice",
                "title": "Meta description may be truncated",
                "description": f"Meta description is {desc_len} characters. Google typically shows ~155-160 characters.",
                "recommendation": "Trim to 120-160 characters for full visibility in search results.",
                "penalty": 1
            })

    # Canonical URL
    canonical = soup.find("link", rel="canonical")
    if not canonical or not canonical.get("href", "").strip():
        issues.append({
            "id": "seo-006", "category": "core_seo", "severity": "warning",
            "title": "Missing canonical URL",
            "description": "No canonical link element found. This can cause duplicate content issues.",
            "recommendation": "Add <link rel='canonical' href='...'> pointing to the preferred URL for this page.",
            "penalty": 5
        })

    # Open Graph basic tags
    og_title = soup.find("meta", property="og:title")
    og_desc = soup.find("meta", property="og:description")
    og_image = soup.find("meta", property="og:image")
    missing_og = []
    if not og_title:
        missing_og.append("og:title")
    if not og_desc:
        missing_og.append("og:description")
    if not og_image:
        missing_og.append("og:image")
    if missing_og:
        issues.append({
            "id": "seo-007", "category": "core_seo", "severity": "warning",
            "title": "Incomplete Open Graph tags",
            "description": f"Missing Open Graph tags: {', '.join(missing_og)}. Social shares will lack rich previews.",
            "recommendation": "Add the missing OG tags so the page displays properly when shared on social media.",
            "penalty": 3
        })

    # Robots meta
    robots_meta = soup.find("meta", attrs={"name": re.compile(r"^robots$", re.I)})
    if robots_meta:
        content = robots_meta.get("content", "").lower()
        if "noindex" in content:
            issues.append({
                "id": "seo-008", "category": "core_seo", "severity": "notice",
                "title": "Page set to noindex",
                "description": "This page has a noindex robots directive. It will not appear in search results.",
                "recommendation": "Verify this is intentional. Remove noindex if the page should be indexed.",
                "penalty": 0
            })

    # Viewport meta
    viewport = soup.find("meta", attrs={"name": "viewport"})
    if not viewport:
        issues.append({
            "id": "mobile-001", "category": "mobile", "severity": "error",
            "title": "Missing viewport meta tag",
            "description": "No viewport meta tag found. The page will not render correctly on mobile devices.",
            "recommendation": "Add <meta name='viewport' content='width=device-width, initial-scale=1'>.",
            "penalty": 10
        })

    return issues


def check_headings(url, soup):
    """Content quality: heading structure."""
    issues = []
    h1s = soup.find_all("h1")

    if len(h1s) == 0:
        issues.append({
            "id": "content-001", "category": "content_quality", "severity": "error",
            "title": "Missing H1 heading",
            "description": "The page has no H1 heading. H1 is a strong relevance signal for search engines.",
            "recommendation": "Add exactly one H1 heading that describes the page's primary topic.",
            "penalty": 8
        })
    elif len(h1s) > 1:
        issues.append({
            "id": "content-002", "category": "content_quality", "severity": "warning",
            "title": "Multiple H1 headings",
            "description": f"Found {len(h1s)} H1 tags. While not strictly invalid, best practice is one H1 per page.",
            "recommendation": "Consolidate into a single H1 and use H2-H6 for subsections.",
            "penalty": 3
        })

    # Check heading hierarchy (no skipped levels)
    all_headings = soup.find_all(re.compile(r"^h[1-6]$"))
    prev_level = 0
    for h in all_headings:
        level = int(h.name[1])
        if level > prev_level + 1 and prev_level != 0:
            issues.append({
                "id": "content-003", "category": "content_quality", "severity": "warning",
                "title": "Skipped heading level",
                "description": f"Heading jumped from H{prev_level} to H{level}. Skipping levels hurts accessibility and SEO.",
                "recommendation": f"Use H{prev_level + 1} instead of H{level}, or add the intermediate heading levels.",
                "penalty": 2
            })
            break  # Report once per page
        prev_level = level

    return issues


def check_images(url, soup):
    """Accessibility and SEO: image alt text."""
    issues = []
    images = soup.find_all("img")
    missing_alt = []
    empty_alt_decorative = 0

    for img in images:
        src = img.get("src", "")
        alt = img.get("alt")
        if alt is None:
            missing_alt.append(src[:80])
        elif alt.strip() == "":
            empty_alt_decorative += 1

    if missing_alt:
        issues.append({
            "id": "a11y-001", "category": "accessibility", "severity": "error",
            "title": "Images missing alt attribute",
            "description": f"{len(missing_alt)} image(s) have no alt attribute. Screen readers cannot describe these images.",
            "recommendation": "Add descriptive alt text to each image, or alt='' for purely decorative images.",
            "penalty": min(10, len(missing_alt) * 2)
        })

    return issues


def check_links_on_page(url, soup, base_domain):
    """Collect internal and external links from a page."""
    internal_links = set()
    external_links = set()

    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if href.startswith("#") or href.startswith("mailto:") or href.startswith("tel:") or href.startswith("javascript:"):
            continue
        absolute = urljoin(url, href)
        if is_same_domain(absolute, base_domain):
            internal_links.add(normalize_url(absolute))
        else:
            external_links.add(absolute)

    return internal_links, external_links


def check_security(url, resp):
    """Security header checks."""
    issues = []
    headers = resp.headers

    # HTTPS
    if not url.startswith("https://"):
        issues.append({
            "id": "sec-001", "category": "security", "severity": "error",
            "title": "Not using HTTPS",
            "description": "The page is served over HTTP. Data is transmitted unencrypted.",
            "recommendation": "Migrate to HTTPS and set up redirects from HTTP to HTTPS.",
            "penalty": 15
        })

    # HSTS
    if "strict-transport-security" not in (k.lower() for k in headers):
        issues.append({
            "id": "sec-002", "category": "security", "severity": "warning",
            "title": "Missing HSTS header",
            "description": "No Strict-Transport-Security header. Browsers may still attempt HTTP connections.",
            "recommendation": "Add Strict-Transport-Security: max-age=31536000; includeSubDomains",
            "penalty": 4
        })

    # X-Content-Type-Options
    if "x-content-type-options" not in (k.lower() for k in headers):
        issues.append({
            "id": "sec-003", "category": "security", "severity": "warning",
            "title": "Missing X-Content-Type-Options header",
            "description": "Without this header, browsers may MIME-sniff responses, enabling certain attacks.",
            "recommendation": "Add X-Content-Type-Options: nosniff",
            "penalty": 3
        })

    # X-Frame-Options
    xfo = headers.get("x-frame-options", "").lower()
    csp = headers.get("content-security-policy", "").lower()
    if not xfo and "frame-ancestors" not in csp:
        issues.append({
            "id": "sec-004", "category": "security", "severity": "warning",
            "title": "Missing clickjacking protection",
            "description": "No X-Frame-Options or CSP frame-ancestors directive. The page could be embedded in a malicious iframe.",
            "recommendation": "Add X-Frame-Options: DENY (or SAMEORIGIN) or use CSP frame-ancestors.",
            "penalty": 3
        })

    # Content-Security-Policy
    if "content-security-policy" not in (k.lower() for k in headers):
        issues.append({
            "id": "sec-005", "category": "security", "severity": "notice",
            "title": "No Content-Security-Policy header",
            "description": "CSP helps mitigate XSS and data injection attacks.",
            "recommendation": "Implement a Content-Security-Policy header appropriate for your site.",
            "penalty": 2
        })

    return issues


def check_performance(url, resp, soup):
    """Basic performance checks."""
    issues = []

    # Page size
    content_length = len(resp.content)
    if content_length > 3_000_000:
        issues.append({
            "id": "perf-001", "category": "performance", "severity": "error",
            "title": "Page size exceeds 3MB",
            "description": f"Total HTML response is {content_length / 1_000_000:.1f}MB. Large pages load slowly, especially on mobile.",
            "recommendation": "Reduce page size by optimizing images, minifying CSS/JS, and lazy-loading below-the-fold content.",
            "penalty": 8
        })
    elif content_length > 1_000_000:
        issues.append({
            "id": "perf-002", "category": "performance", "severity": "warning",
            "title": "Page size exceeds 1MB",
            "description": f"Total HTML response is {content_length / 1_000_000:.1f}MB.",
            "recommendation": "Consider optimizing assets and reducing page weight.",
            "penalty": 4
        })

    # Inline styles and scripts (rough count)
    inline_styles = soup.find_all("style")
    inline_scripts = soup.find_all("script", src=False)
    large_inline = [s for s in inline_styles + inline_scripts if s.string and len(s.string) > 5000]
    if large_inline:
        issues.append({
            "id": "perf-003", "category": "performance", "severity": "notice",
            "title": "Large inline styles or scripts",
            "description": f"Found {len(large_inline)} inline style/script block(s) over 5KB. These cannot be cached separately.",
            "recommendation": "Move large inline code to external files for better caching.",
            "penalty": 2
        })

    return issues


def check_schema(url, soup):
    """JSON-LD structured data checks."""
    issues = []
    ld_scripts = soup.find_all("script", type="application/ld+json")

    if not ld_scripts:
        issues.append({
            "id": "schema-001", "category": "schema", "severity": "warning",
            "title": "No JSON-LD structured data found",
            "description": "The page has no JSON-LD schema markup. Structured data enables rich results in search.",
            "recommendation": "Add JSON-LD for the most relevant schema type (Organization, Product, Article, FAQPage, etc.).",
            "penalty": 5
        })
    else:
        for script in ld_scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and "@type" not in data and "@graph" not in data:
                    issues.append({
                        "id": "schema-002", "category": "schema", "severity": "warning",
                        "title": "JSON-LD missing @type",
                        "description": "A JSON-LD block exists but has no @type property.",
                        "recommendation": "Add an @type field (e.g., 'Organization', 'Article') to the JSON-LD.",
                        "penalty": 3
                    })
            except (json.JSONDecodeError, TypeError):
                issues.append({
                    "id": "schema-003", "category": "schema", "severity": "error",
                    "title": "Invalid JSON-LD",
                    "description": "A JSON-LD script block contains invalid JSON.",
                    "recommendation": "Fix the JSON syntax in the structured data block.",
                    "penalty": 5
                })

    return issues


def check_social(url, soup):
    """Twitter Card and social meta checks."""
    issues = []
    tc_card = soup.find("meta", attrs={"name": "twitter:card"})
    tc_title = soup.find("meta", attrs={"name": "twitter:title"})

    if not tc_card:
        issues.append({
            "id": "social-001", "category": "social", "severity": "notice",
            "title": "Missing Twitter Card meta tag",
            "description": "No twitter:card meta tag found. Tweets linking to this page will not show rich previews.",
            "recommendation": "Add <meta name='twitter:card' content='summary_large_image'> and related twitter: tags.",
            "penalty": 2
        })

    return issues


def check_lang_attribute(url, soup):
    """Accessibility: html lang attribute."""
    issues = []
    html_tag = soup.find("html")
    if html_tag and not html_tag.get("lang"):
        issues.append({
            "id": "a11y-002", "category": "accessibility", "severity": "warning",
            "title": "Missing lang attribute on <html>",
            "description": "The <html> element has no lang attribute. Screen readers need this to select the correct pronunciation.",
            "recommendation": "Add lang='en' (or the appropriate language code) to the <html> tag.",
            "penalty": 4
        })
    return issues


# ---------------------------------------------------------------------------
# Crawl + Audit orchestration
# ---------------------------------------------------------------------------

def crawl_and_audit(start_url, max_pages=25, check_external=False, verbose=False):
    """Crawl a site and run all audit checks. Returns the report dict."""
    parsed_start = urlparse(start_url)
    base_domain = parsed_start.netloc
    base_url = f"{parsed_start.scheme}://{parsed_start.netloc}"

    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (compatible; AuditBot/1.0; +website-audit-skill)"
    })

    if verbose:
        print(f"[*] Starting audit of {start_url}", file=sys.stderr)
        print(f"[*] Max pages: {max_pages}", file=sys.stderr)

    # Fetch robots.txt
    disallowed = fetch_robots_txt(base_url, session)
    if verbose and disallowed:
        print(f"[*] robots.txt disallows {len(disallowed)} path(s)", file=sys.stderr)

    # BFS crawl
    to_visit = [normalize_url(start_url)]
    visited = set()
    all_issues = []
    page_data = []
    external_links_all = set()
    broken_internal = []
    skipped = 0
    start_time = time.time()

    while to_visit and len(visited) < max_pages:
        current_url = to_visit.pop(0)
        if current_url in visited:
            continue

        if is_disallowed(current_url, disallowed):
            skipped += 1
            if verbose:
                print(f"[*] Skipped (robots.txt): {current_url}", file=sys.stderr)
            continue

        visited.add(current_url)
        if verbose:
            print(f"[{len(visited)}/{max_pages}] Crawling: {current_url}", file=sys.stderr)

        resp, err = fetch_page(current_url, session)
        if err or resp is None:
            broken_internal.append({"url": current_url, "error": err})
            continue
        if resp.status_code >= 400:
            broken_internal.append({"url": current_url, "status": resp.status_code})
            continue

        content_type = resp.headers.get("content-type", "")
        if "text/html" not in content_type:
            continue

        soup = BeautifulSoup(resp.text, "html.parser")

        # Run checks
        page_issues = []
        page_issues.extend(check_core_seo(current_url, soup, resp))
        page_issues.extend(check_headings(current_url, soup))
        page_issues.extend(check_images(current_url, soup))
        page_issues.extend(check_security(current_url, resp))
        page_issues.extend(check_performance(current_url, resp, soup))
        page_issues.extend(check_schema(current_url, soup))
        page_issues.extend(check_social(current_url, soup))
        page_issues.extend(check_lang_attribute(current_url, soup))

        for issue in page_issues:
            issue["affected_urls"] = [current_url]

        all_issues.extend(page_issues)

        # Discover links
        internal, external = check_links_on_page(current_url, soup, base_domain)
        external_links_all.update(external)
        for link in internal:
            if link not in visited:
                to_visit.append(link)

        # Rate limit
        time.sleep(1.0)

    elapsed = time.time() - start_time

    # Check external links if requested
    broken_external = []
    if check_external and external_links_all:
        if verbose:
            print(f"[*] Checking {len(external_links_all)} external links...", file=sys.stderr)
        for ext_url in list(external_links_all)[:200]:  # Cap at 200
            try:
                r = session.head(ext_url, timeout=10, allow_redirects=True)
                if r.status_code >= 400:
                    broken_external.append({"url": ext_url, "status": r.status_code})
            except Exception:
                broken_external.append({"url": ext_url, "error": "unreachable"})

    if broken_internal:
        all_issues.append({
            "id": "links-001", "category": "links", "severity": "error",
            "title": "Broken internal links",
            "description": f"Found {len(broken_internal)} broken internal link(s).",
            "affected_urls": [b.get("url", "") for b in broken_internal],
            "recommendation": "Fix or remove the broken internal links.",
            "penalty": min(15, len(broken_internal) * 3)
        })

    if broken_external:
        all_issues.append({
            "id": "links-002", "category": "links", "severity": "warning",
            "title": "Broken external links",
            "description": f"Found {len(broken_external)} broken external link(s).",
            "affected_urls": [b.get("url", "") for b in broken_external],
            "recommendation": "Update or remove broken external links.",
            "penalty": min(10, len(broken_external) * 2)
        })

    # Deduplicate issues (merge same ID across pages)
    merged = {}
    for issue in all_issues:
        iid = issue["id"]
        if iid in merged:
            existing_urls = merged[iid].get("affected_urls", [])
            new_urls = issue.get("affected_urls", [])
            merged[iid]["affected_urls"] = list(set(existing_urls + new_urls))
        else:
            merged[iid] = issue
    all_issues = list(merged.values())

    # Calculate scores
    category_penalties = defaultdict(int)
    for issue in all_issues:
        cat = issue.get("category", "other")
        category_penalties[cat] += issue.get("penalty", 0)

    categories = [
        "core_seo", "technical_seo", "performance", "content_quality",
        "security", "accessibility", "schema", "links", "mobile", "social"
    ]
    weights = {
        "core_seo": 0.20, "technical_seo": 0.15, "performance": 0.10,
        "content_quality": 0.15, "security": 0.15, "accessibility": 0.10,
        "schema": 0.05, "links": 0.05, "mobile": 0.03, "social": 0.02
    }

    category_scores = {}
    for cat in categories:
        category_scores[cat] = max(0, 100 - category_penalties.get(cat, 0))

    overall = sum(category_scores[c] * weights[c] for c in categories)
    overall = round(overall)

    if overall >= 90:
        grade = "A"
    elif overall >= 80:
        grade = "B"
    elif overall >= 70:
        grade = "C"
    elif overall >= 50:
        grade = "D"
    else:
        grade = "F"

    errors = sum(1 for i in all_issues if i["severity"] == "error")
    warnings = sum(1 for i in all_issues if i["severity"] == "warning")
    notices = sum(1 for i in all_issues if i["severity"] == "notice")

    report = {
        "url": start_url,
        "audit_date": datetime.now(timezone.utc).isoformat(),
        "pages_crawled": len(visited),
        "pages_skipped": skipped,
        "crawl_duration_seconds": round(elapsed, 1),
        "overall_score": overall,
        "grade": grade,
        "category_scores": category_scores,
        "issues": sorted(all_issues, key=lambda x: {"error": 0, "warning": 1, "notice": 2}.get(x["severity"], 3)),
        "summary": {
            "total_issues": len(all_issues),
            "errors": errors,
            "warnings": warnings,
            "notices": notices,
            "external_links_found": len(external_links_all),
            "broken_external_checked": len(broken_external) if check_external else "not_checked"
        }
    }

    return report


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Audit a website for SEO, performance, accessibility, security, and content issues.")
    parser.add_argument("url", help="URL to audit (must include https:// or http://)")
    parser.add_argument("--max-pages", type=int, default=25, help="Maximum pages to crawl (default: 25, max: 100)")
    parser.add_argument("--output", help="Save JSON report to this path (default: stdout)")
    parser.add_argument("--check-external", action="store_true", help="Also check external link health")
    parser.add_argument("--verbose", action="store_true", help="Print progress to stderr")

    args = parser.parse_args()

    # Validate URL
    url = args.url.strip()
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url
        if args.verbose:
            print(f"[*] No protocol specified, using: {url}", file=sys.stderr)

    max_pages = min(args.max_pages, 100)

    report = crawl_and_audit(url, max_pages=max_pages, check_external=args.check_external, verbose=args.verbose)

    output_json = json.dumps(report, indent=2, ensure_ascii=False)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_json)
        if args.verbose:
            print(f"[*] Report saved to {args.output}", file=sys.stderr)
    else:
        print(output_json)


if __name__ == "__main__":
    main()
