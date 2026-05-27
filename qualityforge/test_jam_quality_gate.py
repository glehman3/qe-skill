#!/usr/bin/env python3
"""
QualityForge - Test Jam Quality Gate

Runs:
  1) CSV structural/format validation (hard fail on errors)
  2) Content findings check (report-only by default)

This provides a single command to run after generating a test jam to ensure:
  - CSVs will not "shift columns" in Excel/Sheets
  - Numbered list requirements are met
  - Formula injection sanitization is applied
  - Execution tracking columns are blank by default
  - Content quality signals are summarized (content findings analyzer)
"""

from __future__ import annotations

import argparse
import json
from utils import now_utc_iso
from pathlib import Path
from typing import Any, Dict, Optional

from test_jam_accuracy import AccuracyAnalyzer, parse_acs_text
from test_jam_csv_validate import validate_csv_file



def main() -> None:
    parser = argparse.ArgumentParser(description="QualityForge Test Jam Quality Gate")
    parser.add_argument("--test-jam", required=True, help="Test jam directory name under test-jams/")
    parser.add_argument(
        "--acs-file",
        default=None,
        help="Optional path to a text file containing Acceptance Criteria (ACs), one per line (e.g., 'AC1: ...')",
    )
    parser.add_argument(
        "--acs-text",
        default=None,
        help="Optional AC text blob (multiline). Prefer --acs-file if long.",
    )
    parser.add_argument(
        "--output",
        default="test_jam_quality_gate_report.json",
        help="Output report filename written into the test jam directory",
    )
    parser.add_argument(
        "--fail-on-findings-high",
        action="store_true",
        help="Fail the quality gate if the content findings analyzer reports any high-severity findings.",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    test_jam_dir = repo_root / "test-jams" / args.test_jam
    if not test_jam_dir.exists():
        raise FileNotFoundError(f"Test jam not found: {test_jam_dir}")

    # 1) CSV validation
    csv_files = sorted(test_jam_dir.glob("testjam_*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No testjam_*.csv files found in {test_jam_dir}")

    csv_issues = []
    for p in csv_files:
        csv_issues.extend(validate_csv_file(p))

    csv_errors = [i for i in csv_issues if i.severity == "error"]
    csv_warnings = [i for i in csv_issues if i.severity == "warning"]

    # 2) Content findings analyzer (quick)
    acs_text = ""
    if args.acs_file:
        acs_text = Path(args.acs_file).read_text(encoding="utf-8")
    elif args.acs_text:
        acs_text = args.acs_text

    acs = parse_acs_text(acs_text) if acs_text.strip() else None

    analyzer = AccuracyAnalyzer(repo_root=repo_root)
    accuracy_report = analyzer.analyze_quick(test_jam_dir=test_jam_dir, acs=acs)

    # Decide pass/fail
    passed = True
    fail_reasons = []
    if csv_errors:
        passed = False
        fail_reasons.append("CSV validation errors")
    if args.fail_on_findings_high and accuracy_report["counts"]["high"] > 0:
        passed = False
        fail_reasons.append("Content findings: high-severity issues detected")

    report: Dict[str, Any] = {
        "generated_at_utc": now_utc_iso(),
        "test_jam_dir": str(test_jam_dir),
        "passed": passed,
        "fail_reasons": fail_reasons,
        "csv_validation": {
            "files_checked": [p.name for p in csv_files],
            "counts": {
                "errors": len(csv_errors),
                "warnings": len(csv_warnings),
                "total": len(csv_issues),
            },
            "issues": [
                {
                    "severity": i.severity,
                    "file": i.file,
                    "row_number": i.row_number,
                    "test_id": i.test_id,
                    "issue": i.issue,
                    "detail": i.detail,
                }
                for i in csv_issues
            ],
        },
        "content_findings": accuracy_report,
    }

    out_path = test_jam_dir / args.output
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print("✅ Test Jam Quality Gate Report Generated")
    print(f"📁 Location: {out_path}")
    print(f"🧾 CSV: {len(csv_errors)} errors, {len(csv_warnings)} warnings")
    print(
        f"🔎 Content Findings: {accuracy_report['counts']['high']} high, {accuracy_report['counts']['medium']} medium, {accuracy_report['counts']['low']} low"
    )
    print(f"🏁 Result: {'PASS' if passed else 'FAIL'}")

    if not passed:
        raise SystemExit(2)


if __name__ == "__main__":
    main()

