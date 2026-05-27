## Quality Risk Analysis Content Accuracy Rubric (BETA)

This rubric defines how Quality Risk Analysis content must be generated so reports are **accurate, evidence-based, and actionable** — not just well-formatted.

---

## Core Principle

**Do not claim facts you cannot support.** If you cannot support a statement with evidence from inputs (PRD/Jira/Figma) or codebase inspection (GitHub MCP), label it as a **hypothesis** and convert it into a **question** or a **recommended spike**.

---

## Evidence Types

Use inline evidence tags directly in risk descriptions:

- **REQ-###**: Requirements evidence (PRD, Jira, Figma)
- **CODE-###**: Codebase evidence (GitHub MCP search/file contents)
- **HIST-###**: History/ownership evidence — **only when verified** (commit/churn data you actually retrieved)
- **OPS-###**: Operational evidence (Bugsnag/monitoring) — **only when verified**

If you cannot cite a real source, do **not** present it as fact.

### Direct vs. Analogical Evidence

Evidence must be **direct** — it references the same component, service, or code path the risk describes.

**Direct (preferred):**
> "The send handler (CODE-001) has no error handling for scheduling failures"
> — the code reference IS the component the risk is about.

**Analogical (flag and disclose):**
> "A similar redirect bug was fixed in the sending domain card (CODE-003), suggesting this flow may have the same issue"
> — the code reference is about a DIFFERENT component used to infer risk elsewhere.

**Rules:**
1. Never present analogical evidence as direct.
2. Analogical evidence alone cannot support High or Medium confidence — must be Low with a Question or Spike.
3. Hedging language ("suggests", "pattern of", "similar to", "implies", "could similarly", "fragile") is a red flag — the quality gate will flag it.

---

## What the Quality Gate Checks

Each risk block must include:

| Requirement | Severity if Missing |
|---|---|
| At least one `REQ-###` tag | High (blocks pass) |
| Confidence level (High / Medium / Low) | High (blocks pass) |
| Mitigations section | Medium |
| At least one `CODE-###` tag | Medium |
| No banned metrics without evidence | High (blocks pass) |
| No hedging language on CODE/PR references | Medium |

### Confidence Levels

- **High**: REQ + direct CODE evidence; mapping is clear
- **Medium**: REQ exists; CODE evidence is partial or indirect
- **Low**: hypothesis or analogical evidence only; must include a Question or Spike to raise confidence

### Banned Claims (unless verified)

Do **not** invent:
- Exact churn counts ("45 changes in 6 months")
- Test coverage percentages
- Cyclomatic complexity numbers
- Exact dependent service counts
- Precise migration timings / record counts

You may say "likely" and convert it into a **verification step** unless you actually verified it.

---

## Severity Guidance

Assign severity based on Impact x Likelihood:

- **Impact**: P0 (outage/data loss/security) → P3 (minor, easy mitigation)
- **Likelihood**: High (critical paths, many dependencies, ambiguous reqs) → Low (isolated, well-understood)

If you can't justify severity in 1-2 sentences, mark confidence as **Low** and add a question.

---

## Output Quality Gates

Before the report is "done":
- Every risk has **inline evidence + confidence**
- Every mitigation is **actionable**
- Unknowns are captured as **Questions** and/or **Spikes**
- No unverified metrics are presented as facts
