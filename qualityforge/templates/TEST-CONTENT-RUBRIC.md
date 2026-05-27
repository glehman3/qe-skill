# Test Case Content Rubric (Thorough Accuracy Pass)

This rubric defines how the agent-driven **Thorough** accuracy pass scores test cases produced by `/qforge` (Feature 1: Test Case / Jam Generation). Quick mode is heuristic and CSV-shape oriented; the Thorough pass uses this rubric to evaluate **content quality** semantically.

Score every test case in the jam against each of the six dimensions below on a **1–5 scale**. Cite evidence from the test case row (Test ID, field) and, where applicable, from the source ACs / PRD / PR. Output goes into the `"thorough"` block of `test_jam_quality_report.json` (see `THOROUGH-REPORT-SCHEMA.md`).

---

## Core Principle

**Score what the tester would actually do.** A test case is high-quality when an unfamiliar tester can execute it without guessing, observe the result without interpretation, and trace it back to a specific requirement. If any of those three things require guessing, mark the relevant dimension at `2` or below and add a concrete `recommendation`.

---

## The Six Dimensions

Each test case gets six 1–5 scores plus a per-dimension `note` (one short sentence with evidence). The agent must justify every score `≤ 2` with at least one concrete remediation in the `recommendations` array.

### 1. Clarity (1–5)

How unambiguous are the Pre-conditions, Test Steps, and Expected Results to a tester who has never seen this feature?

| Score | Anchor |
|---|---|
| 5 | Every step references a concrete UI element (button label, field name, URL) and a concrete action; no jargon left undefined |
| 4 | One or two steps lean on shared context but a tester from the same team would have no trouble |
| 3 | Mostly clear but at least one step requires the tester to infer where to click or what to look at |
| 2 | Multiple steps use vague verbs ("verify", "check", "confirm") without naming the target element or value |
| 1 | A new tester cannot follow the steps without asking the author |

### 2. Atomicity (1–5)

Does the test verify **one** behavior, or is it bundled with unrelated checks?

| Score | Anchor |
|---|---|
| 5 | A single behavior with one logical assertion path; failure points to one root cause |
| 4 | One primary behavior plus a closely related sanity assertion |
| 3 | Two related behaviors bundled — failure could be either |
| 2 | Three+ behaviors mixed; would be hard to debug a failure |
| 1 | A multi-feature smoke test masquerading as a focused test case |

When a test scores `≤ 2` here, the recommendation should usually be `split`.

### 3. Verifiability (1–5)

Are the Expected Results observable and objective?

| Score | Anchor |
|---|---|
| 5 | Every expected result names the exact UI text, state change, URL, status code, or stored value |
| 4 | Expected results are objective but rely on one slightly fuzzy phrase ("appears", "is shown") that a tester can still verify visually |
| 3 | At least one expected result is qualitative ("looks correct") but recoverable from context |
| 2 | Most expected results use vague success language without a concrete observation |
| 1 | Expected results say "works as expected" / "behaves correctly" / "no issues" with no observable signal |

### 4. AC Traceability (1–5)

Does the test map cleanly to a specific Acceptance Criterion (or explicitly mark itself as a derived edge case)?

| Score | Anchor |
|---|---|
| 5 | Test name, objective, or steps cite the AC ID; the assertion is the AC's success condition |
| 4 | Cites the AC by paraphrase; mapping is unambiguous |
| 3 | Maps to an AC by inference but no explicit reference; mapping is plausible |
| 2 | Could map to several ACs; need to read the steps carefully to guess |
| 1 | No discernible relationship to any provided AC and not labeled as a derived edge case |

When ACs are not provided in session context, score this dimension `n/a` and surface that in the `notes`.

### 5. Expected-Result Specificity (1–5)

Closely related to Verifiability but focused on the **strength** of the success signal, not just whether it's observable.

| Score | Anchor |
|---|---|
| 5 | Names exact text / value / state / status code / URL / element ID |
| 4 | Names the element or page and the type of change (e.g., "the cart count increases by 1") |
| 3 | Names the element but not the precise change |
| 2 | Says only that something happens ("the page updates") |
| 1 | Indistinguishable from "it works" |

Use this dimension to disambiguate between a test that is technically observable but weak (Verifiability `4`, Specificity `2`) and one that is both observable and strong (`5` / `5`).

### 6. Negative / Boundary / Error-path Coverage (jam-level, 1–5)

This is scored **once per jam**, not per test. Looks across the whole jam for systematic gaps.

| Score | Anchor |
|---|---|
| 5 | Every AC has at least one happy-path AND at least one negative / boundary / error-path test, plus accessibility / permission coverage where relevant |
| 4 | Every AC has happy + at least one negative or boundary; minor gaps in error-path or accessibility |
| 3 | Most ACs have happy + one form of edge coverage; some ACs are happy-path only |
| 2 | Many ACs have only happy-path tests; at most one or two negative tests in the whole jam |
| 1 | All happy path; no negative / boundary / error-path / accessibility coverage |

When this dimension scores `≤ 3`, list each missing scenario type per AC in the `gaps` block of the report.

---

## Confidence on AC↔Test Mappings

For every AC↔test link reported in the `ac_coverage_matrix`, attach a confidence:

- **high** — the test's assertion IS the AC's success condition; named explicitly or unambiguous from steps
- **medium** — the test exercises the same flow as the AC and asserts a related outcome, but doesn't directly assert the AC itself
- **low** — the test touches the same area but the assertion does not verify the AC; treat as a partial signal and flag in `gaps`

Never report a `high` mapping without quoting the AC text and the matching expected result.

---

## What the Thorough Pass Must NOT Do

- **Don't invent ACs.** Use only ACs in session context (PRD / Jira / PR / pasted). If there are none, skip the AC dimensions and say so in the report.
- **Don't reword the user's test cases in place.** All mutations to CSVs happen via the High-severity findings remediation flow with explicit user consent.
- **Don't assign confidence above `medium` to mappings inferred only from test names.**
- **Don't claim coverage for ACs whose test only exercises a sibling flow.** Flag those as `gaps`.

---

## Recommendation Vocabulary

Every finding needs one of:

- `rewrite` — the test should keep its scope but the wording must change (most Clarity / Verifiability / Specificity issues)
- `split` — the test bundles multiple behaviors and should become two or more (most Atomicity issues)
- `merge` — two or more tests cover the same assertion and should collapse
- `regenerate` — the test is structurally broken (missing steps / results / objective) — feed into the High-severity findings remediation flow

---

## Severity Mapping

When merging Thorough findings into the existing `findings` list, use these severities so the High-severity remediation flow picks them up correctly:

- **high**: Verifiability or Expected-Result Specificity scored `1`; Atomicity scored `1`; AC scored `1` AND the AC has no other covering test in the jam
- **medium**: any other dimension scored `2`; AC scored `2`; jam-level Negative/Boundary scored `≤ 2`
- **low**: any dimension scored `3` with a concrete recommendation

Do not emit `high` severity for stylistic preferences — only for content that would actually mislead a tester or leave an AC uncovered.
