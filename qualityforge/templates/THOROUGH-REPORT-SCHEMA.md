# Thorough Accuracy Report Schema

Defines the JSON shape the **Thorough** accuracy pass writes to `test-jams/{session-name}/test_jam_quality_report.json`. Thorough mode extends — never replaces — the Quick-mode report so downstream tooling (the High-severity findings remediation flow, Step 6 Coverage Map, future dashboards) keeps working.

This schema is the **source of truth**. The agent must conform to it when running the Thorough pass described in [`FEATURE-1-TESTJAM.md`](../../.cursor/skills/qforge/references/FEATURE-1-TESTJAM.md) Step 5.

---

## Top-level shape

The Quick-mode report (written by `qualityforge/test_jam_accuracy.py`) provides these fields and they MUST be preserved verbatim:

```jsonc
{
  "generated_at_utc": "2026-05-07T17:00:00+00:00",
  "mode": "quick",
  "test_jam_dir": "/abs/path/to/test-jams/{session-name}",
  "counts": {
    "test_cases_reviewed": 42,
    "findings_total": 7,
    "high": 2,
    "medium": 3,
    "low": 2,
    "ac_coverage_gaps": 1
  },
  "acs": [ /* parsed AC objects from the analyzer */ ],
  "ac_coverage": { "AC1": ["TC-001", "TC-002"], "AC2": [] },
  "read_warnings": [],
  "findings": [
    {
      "severity": "high",
      "test_id": "TC-005",
      "field": "expected_results",
      "issue": "Missing Expected Results",
      "suggestion": "Add verifiable expected results (UI state, message text, URL change, etc.)."
    }
  ]
}
```

The Thorough pass adds two top-level fields and updates two existing ones:

| Field | Add / Update | Notes |
|---|---|---|
| `mode` | **Update** | Set to `"thorough"` after the merge. The original Quick `mode` value is captured inside `thorough.quick_mode_snapshot` for traceability. |
| `counts` | **Update** | Recompute `findings_total`, `high`, `medium`, `low` to include Thorough findings. Leave `test_cases_reviewed` and `ac_coverage_gaps` (Quick) untouched; Thorough's own AC tally lives in `thorough.ac_coverage_matrix`. |
| `findings` | **Update** | Append Thorough findings to the existing Quick `findings` array. Each Thorough finding MUST include a `source: "thorough"` field. Quick findings retain `source: "quick"` (back-fill if missing). |
| `thorough` | **Add** | New object containing the semantic-pass output. Detailed below. |
| `schema_version` | **Add** | Set to `"1.0"`. |

---

## The `thorough` object

```jsonc
{
  "thorough": {
    "rubric_version": "1.0",
    "rubric_path": "qualityforge/templates/TEST-CONTENT-RUBRIC.md",
    "ran_at_utc": "2026-05-07T17:01:30+00:00",
    "quick_mode_snapshot": {
      "mode": "quick",
      "counts_high": 2,
      "counts_medium": 3,
      "counts_low": 2
    },

    "ac_coverage_matrix": [
      {
        "ac_id": "AC1",
        "ac_text": "User can sign in with email and password",
        "covered_by": [
          {
            "test_id": "TC-001",
            "confidence": "high",
            "reasoning": "Steps 3-5 enter valid credentials and assert dashboard URL — directly verifies AC1's success condition."
          },
          {
            "test_id": "TC-002",
            "confidence": "medium",
            "reasoning": "Exercises the same form but asserts only that the spinner disappears."
          }
        ],
        "status": "covered"
      },
      {
        "ac_id": "AC2",
        "ac_text": "User sees an error for invalid credentials",
        "covered_by": [],
        "status": "uncovered"
      }
    ],

    "scenario_gaps": [
      {
        "ac_id": "AC1",
        "missing_scenarios": ["negative", "boundary"],
        "note": "No test exercises empty-password or expired-account paths."
      },
      {
        "ac_id": null,
        "feature": "Sign-in form",
        "missing_scenarios": ["accessibility"],
        "note": "No test verifies keyboard-only form submission."
      }
    ],

    "per_test_scores": [
      {
        "test_id": "TC-001",
        "scores": {
          "clarity": 4,
          "atomicity": 5,
          "verifiability": 5,
          "ac_traceability": 5,
          "expected_result_specificity": 4
        },
        "notes": {
          "clarity": "Step 2 says 'navigate to the login page' without a URL — minor.",
          "atomicity": "Single behavior, single assertion.",
          "verifiability": "Asserts dashboard URL substring.",
          "ac_traceability": "Cites AC1 by paraphrase in the Objective.",
          "expected_result_specificity": "Names the URL but not the page heading."
        }
      }
    ],

    "jam_level_scores": {
      "negative_boundary_coverage": 2,
      "note": "Only 1 negative test (TC-014) across 8 ACs."
    },

    "counts": {
      "tests_scored": 42,
      "acs_analyzed": 4,
      "acs_covered_high_confidence": 1,
      "acs_covered_medium_confidence": 2,
      "acs_uncovered": 1,
      "scenario_gaps_total": 3
    }
  }
}
```

### Field-by-field rules

- **`rubric_version`**: bump when `TEST-CONTENT-RUBRIC.md` is revised in a way that changes scoring anchors. Currently `"1.0"`.
- **`ac_coverage_matrix[].status`**: `"covered"` when at least one entry in `covered_by` has confidence `high` or `medium`; `"weakly_covered"` when only `low` confidence entries exist; `"uncovered"` when `covered_by` is empty.
- **`scenario_gaps[].missing_scenarios`**: subset of `["negative", "boundary", "error_path", "accessibility", "permission"]`. Use `null` for `ac_id` when the gap is feature-level rather than AC-level (and provide `feature` instead).
- **`per_test_scores[].scores`**: every key must be present, integer 1–5, **except** `ac_traceability` which may be the string `"n/a"` when no ACs were provided in session context.
- **`per_test_scores[].notes`**: free-form one-sentence justification per dimension. Required for any score `≤ 2` and for any score reported as `"n/a"`.
- **`jam_level_scores`**: only `negative_boundary_coverage` for now (1–5 per the rubric); reserved for future jam-level dimensions.

---

## How Thorough findings merge into `findings`

Each Thorough finding is appended to the existing `findings` array using the same shape as Quick findings, plus three required extras:

```jsonc
{
  "severity": "high",
  "test_id": "TC-007",
  "field": "expected_results",
  "issue": "Expected results say only 'works as expected' — not verifiable.",
  "suggestion": "Replace with the exact toast text and the resulting URL.",

  "source": "thorough",
  "rubric_dimension": "verifiability",
  "recommendation": "rewrite"
}
```

Required extra fields when `source == "thorough"`:

| Field | Allowed values |
|---|---|
| `source` | `"thorough"` |
| `rubric_dimension` | `"clarity"` \| `"atomicity"` \| `"verifiability"` \| `"ac_traceability"` \| `"expected_result_specificity"` \| `"negative_boundary_coverage"` |
| `recommendation` | `"rewrite"` \| `"split"` \| `"merge"` \| `"regenerate"` |

For findings that come from the AC coverage matrix (an AC with status `"uncovered"`), use:

```jsonc
{
  "severity": "high",
  "test_id": "(test jam)",
  "field": "coverage",
  "issue": "AC2 has no covering test (semantic pass).",
  "suggestion": "Add a negative-path test that asserts the error message text for invalid credentials.",
  "source": "thorough",
  "rubric_dimension": "ac_traceability",
  "recommendation": "regenerate"
}
```

This shape ensures the High-severity findings remediation flow's `high_severity_test_ids(report)` helper (in `qualityforge/test_jam_accuracy.py`) keeps returning the right Test IDs after the Thorough pass.

---

## Severity rules (must match the rubric)

| Condition | Severity |
|---|---|
| `verifiability` or `expected_result_specificity` scored `1` | `high` |
| `atomicity` scored `1` | `high` |
| `ac_traceability` scored `1` AND that AC has no other covering test | `high` |
| Any AC has `status: "uncovered"` | `high` |
| Any other dimension scored `2`; `ac_traceability` scored `2`; `negative_boundary_coverage` scored `≤ 2` | `medium` |
| Any dimension scored `3` with a concrete `recommendation` | `low` |

Stylistic preferences must NOT be `high`.

---

## Validation checklist (run before writing the file)

1. Quick fields preserved verbatim (`generated_at_utc`, `test_jam_dir`, `acs`, `ac_coverage`, `read_warnings`).
2. `mode == "thorough"` and `schema_version == "1.0"`.
3. `counts.high|medium|low|findings_total` recomputed across the merged `findings` array.
4. Every Quick finding has `source: "quick"`; every Thorough finding has `source: "thorough"` plus `rubric_dimension` and `recommendation`.
5. Every entry in `thorough.per_test_scores[].scores` is an integer 1–5 (or `"n/a"` only for `ac_traceability`).
6. Every score `≤ 2` has a matching `notes` entry.
7. Every `ac_coverage_matrix` entry's `status` matches the rule above (covered / weakly_covered / uncovered).
8. `thorough.counts` totals match the matrix and gaps content.
9. JSON parses (`python3 -c "import json; json.load(open(...))"`).

If any check fails, fix and re-emit before surfacing the report to the user.
