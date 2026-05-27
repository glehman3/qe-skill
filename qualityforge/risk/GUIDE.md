# Quality Risk Analysis Guide

**Quick Start for Identifying Risks Before Implementation**

---

## What is Quality Risk Analysis?

A mode in QualityForge that helps teams discover implementation risks **before writing code**. Instead of finding problems during development or testing, you identify potential issues during the planning phase when you have maximum flexibility.

---

## When to Use

**Good fit:**
- Early planning phase — you have a PRD but haven't started coding
- Architecture review prep — identify discussion points
- Sprint planning — estimating complexity and unknowns
- Spike planning — deciding what research/POCs are needed

**Not ideal for:**
- Features already in development (use code review instead)
- Simple bug fixes or well-understood changes
- Features with no technical documentation yet

---

## Quick Start: 4 Steps

### Step 1: Invoke the Tool

```
/qforge
> Select Option 2: Quality Risk Analysis (BETA)
```

**Optional CLI scaffold:**

```bash
python3 qualityforge/risk/run.py \
  --feature-slug "<feature-slug>" \
  --repo "<org/repo>" \
  --prd-url "<prd-url>"
```

### Step 2: Provide Documentation

**Required:**
- PRD Content (full text — not just a link)
- Repository name (e.g., `org/project`)

**Optional but recommended:**
- PRD URL, Jira ticket, Figma URL, additional context

### Step 3: Review the Report + Quality Gate

The tool generates a lean risk report:

```
test-jams/[date]_[feature]-risk-analysis/
  ├── risk_analysis_report.md     # The report
  ├── risk_summary.md             # Executive summary
  └── risk_quality_report.json    # Quality gate results
```

The quality gate runs automatically. It checks:
- Every risk has REQ evidence + confidence level
- No unverified metrics presented as facts
- No analogical evidence disguised as direct

### Step 4: Export for Sharing

```bash
python3 qualityforge/risk/run.py \
  --feature-slug "<feature-slug>" \
  --repo "<org/repo>" \
  --prd-url "<prd-url>" \
  --export
```

Produces a `.docx` with inlined CSS (tables survive Google Docs import). Upload to Google Drive → Open with Google Docs.

---

## Report Structure

The report is intentionally lean. Here's what's in it and why:

| Section | Purpose |
|---------|---------|
| **Summary** | Metrics table, top 3 concerns, key requirements |
| **Codebase Touch Points** | Which areas are affected + why |
| **Risks** | Grouped by severity, each with inline evidence + mitigations |
| **Open Questions** | Prioritized unknowns (P0 blockers, P1 high, nice-to-have) |
| **Recommended Spikes** | Research needed before implementation |
| **Sources** | Links to PRD, Jira, Figma, repo |

### What's NOT in the report (by design)

- No separate "Unified Requirements Summary" — key reqs are in the Summary
- No per-risk "Affected Areas" / "Category" / "Assumptions" sections — descriptions are self-contained prose
- No "Testing Complexity Assessment" or "Testing Matrix" — that's a separate QualityForge feature
- Low-severity risks are a table row, not a full block

---

## Content Accuracy

Each risk description should embed evidence **inline**:

> The send handler (CODE-001) has no scheduling error handling, but the PRD requires reliable delivery (REQ-003). **Confidence: Medium** — retry infrastructure exists but idempotency not confirmed.

**Confidence levels:**
- **High**: REQ + direct CODE evidence, clear mapping
- **Medium**: REQ exists, CODE evidence is partial
- **Low**: hypothesis — must include a Question or Spike

See [CONTENT-ACCURACY-RUBRIC.md](./CONTENT-ACCURACY-RUBRIC.md) for the full rubric.

**Red flags the quality gate catches:**
- Missing REQ or confidence → blocks pass
- Hedging language on CODE references ("suggests", "similar to") → analogical evidence warning
- Unverified metric claims → blocks pass

---

## Using Reports with Stakeholders

| Audience | Focus on |
|----------|----------|
| **Product Managers** | Summary, open questions, timeline impact |
| **Tech Leads** | Touch points, critical risks, spikes |
| **Engineering Managers** | Resource needs, cross-team deps, timeline |
| **Architects** | Integration risks, scalability, security |

---

## Risk Review Meeting (60 min)

1. **Summary** (5 min) — top 3 concerns
2. **Critical risks** (20 min) — mitigations + owners
3. **Spikes** (10 min) — assign + deadline
4. **Open questions** (10 min) — assign + deadline
5. **Timeline impact** (10 min) — adjust plan
6. **Go/No-Go** (5 min) — proceed, descope, or defer

---

## Re-Assessment

Re-run risk analysis when:
- Spike work completes (new learnings)
- Requirements change significantly
- New risks surface during development

---

## Troubleshooting

**"Too many risks"** — Focus on Critical first. Consider descoping or phasing the feature.

**"Report is too technical for PMs"** — Share only the Summary section and top 3 concerns.

**"Tool missed a risk"** — Provide more detailed PRD content and specific areas of concern. Manually add missing risks.

---

## Related Resources

- [Example Report](../templates/EXAMPLE-RISK-REPORT.md)
- [Content Accuracy Rubric](./CONTENT-ACCURACY-RUBRIC.md)
- [QualityForge README](../README.md)

---

*Quality Risk Analysis Guide v2.0*
*Last Updated: 2026-02-09*
