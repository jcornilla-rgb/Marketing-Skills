# Audit Report Format Reference

This document describes the JSON structure produced by `scripts/audit_engine.py`.

## Top-Level Structure

```json
{
  "url": "https://example.com",
  "audit_date": "2026-03-17T12:00:00Z",
  "pages_crawled": 25,
  "pages_skipped": 3,
  "crawl_duration_seconds": 45.2,
  "overall_score": 72,
  "grade": "C",
  "category_scores": { ... },
  "issues": [ ... ],
  "summary": { ... }
}
```

## Fields

### `overall_score` (int, 0-100)
Weighted average of all category scores. Weights:

| Category           | Weight |
|--------------------|--------|
| Core SEO           | 20%    |
| Technical SEO      | 15%    |
| Performance        | 10%    |
| Content Quality    | 15%    |
| Security           | 15%    |
| Accessibility      | 10%    |
| Schema             | 5%     |
| Links              | 5%     |
| Mobile             | 3%     |
| Social             | 2%     |

### `grade` (string)
Letter grade derived from `overall_score`:
- A: 90-100
- B: 80-89
- C: 70-79
- D: 50-69
- F: 0-49

### `category_scores` (object)
Per-category scores, each 0-100:

```json
{
  "core_seo": 85,
  "technical_seo": 60,
  "performance": 78,
  "content_quality": 70,
  "security": 90,
  "accessibility": 65,
  "schema": 50,
  "links": 80,
  "mobile": 75,
  "social": 40
}
```

Each category score is calculated as: `100 - (penalty_points)` where penalties are assigned per issue found in that category. Error-level issues penalize more than warnings, which penalize more than notices.

### `issues` (array)
List of all issues found. Each issue:

```json
{
  "id": "seo-001",
  "category": "core_seo",
  "severity": "error",
  "title": "Missing title tag",
  "description": "The page has no <title> element. Search engines use the title tag as the primary heading in search results.",
  "affected_urls": ["https://example.com/about"],
  "recommendation": "Add a unique, descriptive title tag between 30-60 characters to each page.",
  "penalty": 10
}
```

**Severity levels:**
- `error`: Critical issue that significantly impacts the site. Penalty: 5-15 points.
- `warning`: Notable issue that should be addressed. Penalty: 2-5 points.
- `notice`: Minor issue or optimization opportunity. Penalty: 0-2 points.

### `summary` (object)
High-level counts:

```json
{
  "total_issues": 34,
  "errors": 5,
  "warnings": 15,
  "notices": 14,
  "pages_with_issues": 18,
  "clean_pages": 7
}
```

## Scoring Algorithm

1. For each page crawled, run all applicable checks.
2. Each failed check produces an issue with a severity-based penalty.
3. Per-category score = `max(0, 100 - sum(penalties_in_category))`. Penalties are deduplicated: if the same issue affects 10 pages, it counts once for scoring but all affected URLs are listed.
4. Overall score = weighted average of category scores (see weight table above).
5. Grade is derived from the overall score.

## Check IDs

Check IDs follow the pattern `{category_short}-{number}`:
- `seo-001` through `seo-015`: Core SEO checks
- `tech-001` through `tech-012`: Technical SEO checks
- `perf-001` through `perf-008`: Performance checks
- `content-001` through `content-010`: Content quality checks
- `sec-001` through `sec-010`: Security checks
- `a11y-001` through `a11y-010`: Accessibility checks
- `schema-001` through `schema-005`: Structured data checks
- `links-001` through `links-008`: Link checks
- `mobile-001` through `mobile-005`: Mobile checks
- `social-001` through `social-005`: Social/OG checks
