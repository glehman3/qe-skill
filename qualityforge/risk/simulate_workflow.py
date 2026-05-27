#!/usr/bin/env python3
"""
Risk Analysis workflow simulation (order-of-operations check).

Goal:
  Validate that our intended workflow can be executed in the right order with the
  expected artifacts:
    1) scaffold output folder + report files
    2) run quality gate -> expected FAIL (because report is incomplete)
    3) write a minimal compliant report
    4) run quality gate -> expected PASS

This is a local simulation only (no MCP calls, no Jira/GitHub/Figma ingestion).
"""

from __future__ import annotations

import argparse
import datetime as _dt
import importlib.util
import json
from pathlib import Path
import sys

def _load_module_from_path(module_name: str, module_path: Path):
    spec = importlib.util.spec_from_file_location(module_name, str(module_path))
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load module spec: {module_name} from {module_path}")
    module = importlib.util.module_from_spec(spec)
    # dataclasses (and other stdlib mechanisms) expect the module to be present in sys.modules.
    sys.modules[module_name] = module
    spec.loader.exec_module(module)  # type: ignore[call-arg]
    return module


MINIMAL_PASSING_REPORT = """\
## Risk Analysis Report: {feature_name}

**Generated:** {date}
**Feature:** {feature_name}
**Jira:** {jira}
**Repository:** {repo}
**PRD:** [{prd_title}]({prd_url})
**Design:** {figma_url}

---

## 🧾 Unified Requirements Summary

### Goals
- Ship a small feature safely. (REQ-001)

### Acceptance Criteria (Key)
- AC1: The system supports the new workflow end-to-end. (REQ-002)

---

## 🎯 Codebase Touch Points

- `{example_file}` — likely entry point for feature logic. (CODE-001)
  - Evidence: CODE-001
  - Confidence: Medium

---

## 🔴 Critical Risks (P0)

### RISK-001: Example risk (simulation)
**Severity:** 🔴 Critical (P0)
**Category:** Technical
**Impact:** Could block delivery if unmitigated.
**Affected Areas:** {example_file}
**Confidence:** Medium

**Description:**
This is a simulated risk used to validate the quality gate and workflow order.

**Evidence (required):**
- REQ-001: PRD requires a new workflow.
- CODE-001: Touch point identified in `{example_file}`.

**Mitigation Strategies (2–3):**
1. Add a small spike to validate the approach in staging.
2. Add targeted tests around the touch point.

**Assumptions (explicit):**
- The touch point is correct; if not, update mapping. (REQ-003)

**Questions (if any):**
- Do we have an owner for validating the touch point? (REQ-004)

---

## 🔗 Source Links

- PRD: {prd_url}
- Jira: {jira}
- Figma: {figma_url}
"""

FIXABLE_FAILING_REPORT = """\
## Risk Analysis Report: {feature_name}

**Generated:** {date}
**Feature:** {feature_name}
**Jira:** {jira}
**Repository:** {repo}
**PRD:** [{prd_title}]({prd_url})

---

## 🧾 Unified Requirements Summary

### Acceptance Criteria (Key)
- REQ-001: The feature must exist. (REQ-001)

---

## 🔴 Critical Risks (P0)

### RISK-001: Example risk (needs repair)
**Severity:** 🔴 Critical (P0)
**Category:** Technical
**Impact:** Demonstrate repair.
**Affected Areas:** {example_file}

**Description:**
We might only have 85% coverage and changes in last 6 months could be high.

**Evidence (required):**
- REQ-001: Requirement exists.
- CODE-001: Touch point exists.

**Mitigation Strategies (2–3):**
1. Do a thing.

---
"""


def _write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Simulate Risk Analysis workflow order-of-operations.")
    parser.add_argument("--feature-slug", default="workflow-simulation", help="Used in output folder name.")
    parser.add_argument("--repo", default="nova-corp/helix-api", help="Repo placeholder.")
    parser.add_argument("--prd-url", default="https://example.com/prd", help="PRD placeholder.")
    parser.add_argument("--prd-title", default="Example PRD", help="PRD title placeholder.")
    parser.add_argument("--jira", default="TESTING-1518", help="Jira placeholder.")
    parser.add_argument("--figma-url", default="https://figma.com/file/example", help="Figma placeholder.")
    parser.add_argument("--out-root", default="test-jams", help="Root output directory (default: test-jams).")
    parser.add_argument("--keep", action="store_true", help="Keep output folder (default: keep).")
    parser.add_argument(
        "--exercise-repair",
        action="store_true",
        help="Exercise the checker self-repair loop on a fixable failing report (missing Confidence + unverified metrics).",
    )
    args = parser.parse_args()

    date = _dt.date.today().isoformat()
    out_root = Path(args.out_root).expanduser().resolve()
    template_path = (Path(__file__).resolve().parents[1] / "templates" / "RISK-REPORT-TEMPLATE.md").resolve()

    # Load local modules by path so this simulation works even if `qualityforge/` is not a Python package.
    risk_quality_mod = _load_module_from_path(
        "qualityforge_risk_report_quality",
        (Path(__file__).resolve().parent / "risk_report_quality.py").resolve(),
    )
    risk_run_mod = _load_module_from_path(
        "qualityforge_risk_run",
        (Path(__file__).resolve().parent / "run.py").resolve(),
    )

    check_report = getattr(risk_quality_mod, "check_report")
    scaffold = getattr(risk_run_mod, "scaffold")
    self_repair = getattr(risk_quality_mod, "_self_repair_in_place", None)

    print("🧪 Risk Analysis Workflow Simulation")
    print(f"1) Scaffold report folder + files (date={date})")

    session_dir = scaffold(
        out_root=out_root,
        date=date,
        feature_slug=args.feature_slug,
        feature_name=args.feature_slug,
        repo=args.repo,
        prd_url=args.prd_url,
        prd_title=args.prd_title,
        jira=args.jira,
        figma_url=args.figma_url,
        template_path=template_path,
        overwrite=True,
    )

    report_path = session_dir / "risk_analysis_report.md"
    out_json = session_dir / "risk_quality_report.json"

    if args.exercise_repair:
        if self_repair is None:
            raise RuntimeError("Self-repair function not available in risk_report_quality.py")

        print("2) Write a fixable failing report (missing Confidence + unverified metrics)")
        failing = FIXABLE_FAILING_REPORT.format(
            feature_name=args.feature_slug,
            date=date,
            jira=args.jira,
            repo=args.repo,
            prd_title=args.prd_title,
            prd_url=args.prd_url,
            example_file="app/example/entrypoint.ts",
        )
        _write_text(report_path, failing.rstrip() + "\n")

        print("3) Run quality gate → expect FAIL")
        first = check_report(report_path)
        _write_text(out_json, json.dumps(first, indent=2, sort_keys=True) + "\n")
        print(f"   - passed={first['passed']} (high={first['summary']['high']}, medium={first['summary']['medium']}, low={first['summary']['low']})")

        print("4) Self-repair loop (max 2 attempts) → expect PASS")
        attempts = 0
        result = first
        while attempts < 2 and not result.get("passed"):
            attempts += 1
            modified = self_repair(report_path, result)
            result = check_report(report_path)
            if not modified:
                break
        _write_text(out_json, json.dumps(result, indent=2, sort_keys=True) + "\n")
        print(f"   - passed={result['passed']} (high={result['summary']['high']}, medium={result['summary']['medium']}, low={result['summary']['low']})")
    else:
        print("2) Run quality gate on scaffolded (mostly-empty) report → expect FAIL")
        first = check_report(report_path)
        _write_text(out_json, json.dumps(first, indent=2, sort_keys=True) + "\n")
        print(
            f"   - passed={first['passed']} (high={first['summary']['high']}, medium={first['summary']['medium']}, low={first['summary']['low']})"
        )

        print("3) Write minimal compliant report content")
        minimal = MINIMAL_PASSING_REPORT.format(
            feature_name=args.feature_slug,
            date=date,
            jira=args.jira,
            repo=args.repo,
            prd_title=args.prd_title,
            prd_url=args.prd_url,
            figma_url=args.figma_url,
            example_file="app/example/entrypoint.ts",
        )
        _write_text(report_path, minimal.rstrip() + "\n")

        print("4) Run quality gate again → expect PASS")
        second = check_report(report_path)
        _write_text(out_json, json.dumps(second, indent=2, sort_keys=True) + "\n")
        print(f"   - passed={second['passed']} (high={second['summary']['high']}, medium={second['summary']['medium']}, low={second['summary']['low']})")

    print("✅ Simulation complete")
    print(f"📁 Folder: {session_dir}")
    print(f"📝 Report: {report_path}")
    print(f"🧾 Quality: {out_json}")

    if not args.keep:
        # In practice we keep by default for inspection; this is here if you want cleanup later.
        pass


if __name__ == "__main__":
    main()


