#!/usr/bin/env python3
"""
QualityForge - Test Jam CSV Validator

Purpose:
  Catch (and fail fast on) CSV structural problems that cause Excel/Sheets column shifts,
  such as unquoted commas/newlines leading to misaligned rows.

What it checks:
  - Every `testjam_*.csv` row has the same number of columns as its header
  - No "extra columns" are present (a common symptom of misquoted commas)
  - Execution tracking columns are empty by default (Status/Tester/Date Tested/Actual Results/Notes/Bug ID)

This tool is intentionally conservative: it does not attempt to auto-fix malformed CSVs.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import dataclass
from utils import now_utc_iso
from pathlib import Path
from typing import Dict, List, Optional


FORMULA_PREFIX_CHARS = ("=", "+", "-", "@", "\t", "\r")

EXECUTION_TRACKING_COLUMNS = [
    "Status",
    "Tester",
    "Date Tested",
    "Actual Results",
    "Notes",
    "Bug ID",
]

REQUIRED_CORE_COLUMNS = [
    "Test ID",
    "Category",
    "Test Name",
    "Priority",
    "Type",
    "Component",
    "Objective",
    "Pre-conditions",
    "Test Steps",
    "Expected Results",
]

REQUIRED_NUMBERED_LIST_COLUMNS = [
    "Pre-conditions",
    "Test Steps",
    "Expected Results",
]




@dataclass
class CsvIssue:
    severity: str  # "error" | "warning"
    file: str
    row_number: Optional[int]  # 1-based CSV line number, including header
    test_id: Optional[str]
    issue: str
    detail: str


def load_csv_rows(path: Path) -> Dict[str, object]:
    """
    Returns:
      {
        "header": [...],
        "rows": [[...], ...],
      }
    """
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        rows = list(reader)
    header = rows[0] if rows else []
    data_rows = rows[1:] if len(rows) > 1 else []
    return {"header": header, "rows": data_rows}


def get_test_id(header: List[str], row: List[str]) -> Optional[str]:
    if not header or not row:
        return None
    for key in ("Test ID", "Test Case ID", "Test Id"):
        if key in header:
            idx = header.index(key)
            if idx < len(row):
                v = (row[idx] or "").strip()
                return v or None
    return None


def validate_csv_file(path: Path) -> List[CsvIssue]:
    issues: List[CsvIssue] = []
    blob = load_csv_rows(path)
    header: List[str] = blob["header"]  # type: ignore[assignment]
    rows: List[List[str]] = blob["rows"]  # type: ignore[assignment]

    if not header:
        issues.append(
            CsvIssue(
                severity="error",
                file=path.name,
                row_number=None,
                test_id=None,
                issue="Missing header row",
                detail="CSV appears to be empty or unreadable.",
            )
        )
        return issues

    expected_len = len(header)
    if expected_len == 0:
        issues.append(
            CsvIssue(
                severity="error",
                file=path.name,
                row_number=1,
                test_id=None,
                issue="Empty header",
                detail="Header row has zero columns.",
            )
        )
        return issues

    # Header sanity: duplicates
    if len(set(header)) != len(header):
        issues.append(
            CsvIssue(
                severity="error",
                file=path.name,
                row_number=1,
                test_id=None,
                issue="Duplicate header columns detected",
                detail="CSV header contains duplicate column names; this can break DictReader-based tools and spreadsheets.",
            )
        )

    # Header requirements (core columns + execution tracking columns)
    missing = [c for c in REQUIRED_CORE_COLUMNS if c not in header]
    if missing:
        issues.append(
            CsvIssue(
                severity="error",
                file=path.name,
                row_number=1,
                test_id=None,
                issue="Missing required columns",
                detail=f"Missing required column(s): {', '.join(missing)}",
            )
        )

    # Type column name must be "Type" (and in the 5th position for standard formats)
    if len(header) >= 5 and header[4] != "Type":
        issues.append(
            CsvIssue(
                severity="error",
                file=path.name,
                row_number=1,
                test_id=None,
                issue='Column 5 header is not "Type"',
                detail=f'Expected header[4] to be "Type" but found {header[4]!r}.',
            )
        )

    # Structural row-length validation
    for i, row in enumerate(rows, start=2):  # 1-based line number; header is line 1
        if len(row) != expected_len:
            tid = get_test_id(header, row)
            issues.append(
                CsvIssue(
                    severity="error",
                    file=path.name,
                    row_number=i,
                    test_id=tid,
                    issue="Row column-count mismatch",
                    detail=f"Expected {expected_len} columns (per header), found {len(row)}. This often indicates an unquoted comma or newline in a field.",
                )
            )

    # If structure is broken, deeper checks may be unreliable. Still try, but guard against index issues.
    col_index = {name: idx for idx, name in enumerate(header)}

    # Execution tracking columns should be blank in generated files
    tracking_indices = {c: col_index[c] for c in EXECUTION_TRACKING_COLUMNS if c in col_index}
    if tracking_indices:
        for i, row in enumerate(rows, start=2):
            tid = get_test_id(header, row)
            for col, idx in tracking_indices.items():
                if idx >= len(row):
                    continue
                if (row[idx] or "").strip():
                    issues.append(
                        CsvIssue(
                            severity="warning",
                            file=path.name,
                            row_number=i,
                            test_id=tid,
                            issue="Execution tracking field is non-empty",
                            detail=f"Column '{col}' should be blank in generated CSVs. Found value: {row[idx]!r}",
                        )
                    )
                    break

    # Formula injection sanitization: any cell starting with a formula char should be prefixed with "'"
    for i, row in enumerate(rows, start=2):
        tid = get_test_id(header, row)
        for j, cell in enumerate(row):
            if cell is None:
                continue
            s = str(cell)
            if not s:
                continue
            # If the cell starts with a dangerous character and isn't already escaped, error.
            # (We treat a leading apostrophe as "escaped".)
            if s[0] in FORMULA_PREFIX_CHARS and not s.startswith("'"):
                col_name = header[j] if j < len(header) else f"(col {j + 1})"
                issues.append(
                    CsvIssue(
                        severity="error",
                        file=path.name,
                        row_number=i,
                        test_id=tid,
                        issue="Potential CSV formula injection (unsanitized cell start)",
                        detail=f"Column {col_name!r} starts with {s[0]!r}. Prefix the cell with a single quote to force text interpretation.",
                    )
                )
                # One per row is enough to signal the problem; avoid flooding.
                break

    # Enforce numbered lists (and forbid bullet points) in the required multi-line fields
    bullet_re = re.compile(r"^\s*[-*•+]\s+", re.MULTILINE)
    numbered_re = re.compile(r"^\s*\d+[\.\)]\s+")
    for i, row in enumerate(rows, start=2):
        tid = get_test_id(header, row)
        for col in REQUIRED_NUMBERED_LIST_COLUMNS:
            idx = col_index.get(col)
            if idx is None or idx >= len(row):
                continue
            text = (row[idx] or "").strip()
            if not text:
                continue
            if bullet_re.search(text):
                issues.append(
                    CsvIssue(
                        severity="error",
                        file=path.name,
                        row_number=i,
                        test_id=tid,
                        issue="Bullet points detected (numbered lists required)",
                        detail=f"Column {col!r} contains bullet formatting (-/*/•/+). Use numbered lists (1., 2., 3.) only.",
                    )
                )
                break
            # Each non-empty line should be numbered.
            bad_lines = []
            for line in text.splitlines():
                if not line.strip():
                    continue
                if not numbered_re.match(line.strip()):
                    bad_lines.append(line.strip())
                    if len(bad_lines) >= 3:
                        break
            if bad_lines:
                issues.append(
                    CsvIssue(
                        severity="error",
                        file=path.name,
                        row_number=i,
                        test_id=tid,
                        issue="Non-numbered list formatting detected",
                        detail=f"Column {col!r} must be a numbered list. Example bad line: {bad_lines[0]!r}",
                    )
                )
                break

    return issues


def main() -> None:
    parser = argparse.ArgumentParser(description="QualityForge Test Jam CSV Validator")
    parser.add_argument("--test-jam", required=True, help="Test jam directory name under test-jams/")
    parser.add_argument(
        "--output",
        default="test_jam_csv_validation_report.json",
        help="Output report filename written into the test jam directory",
    )
    parser.add_argument(
        "--fail-on-warnings",
        action="store_true",
        help="Treat warnings as failures (non-zero exit code).",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    test_jam_dir = repo_root / "test-jams" / args.test_jam
    if not test_jam_dir.exists():
        raise FileNotFoundError(f"Test jam not found: {test_jam_dir}")

    csv_files = sorted(test_jam_dir.glob("testjam_*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No testjam_*.csv files found in {test_jam_dir}")

    all_issues: List[CsvIssue] = []
    for p in csv_files:
        all_issues.extend(validate_csv_file(p))

    errors = [i for i in all_issues if i.severity == "error"]
    warnings = [i for i in all_issues if i.severity == "warning"]

    report = {
        "generated_at_utc": now_utc_iso(),
        "test_jam_dir": str(test_jam_dir),
        "files_checked": [p.name for p in csv_files],
        "counts": {
            "errors": len(errors),
            "warnings": len(warnings),
            "total": len(all_issues),
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
            for i in all_issues
        ],
    }

    out_path = test_jam_dir / args.output
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print("✅ Test Jam CSV Validation Report Generated")
    print(f"📁 Location: {out_path}")
    print(f"📄 Files checked: {len(csv_files)}")
    print(f"🧾 Issues: {len(errors)} errors, {len(warnings)} warnings")

    if errors:
        raise SystemExit(2)
    if warnings and args.fail_on_warnings:
        raise SystemExit(3)


if __name__ == "__main__":
    main()

