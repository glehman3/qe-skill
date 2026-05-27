#!/usr/bin/env python3
"""
QualityForge - Test Jam Accuracy Analyzer (Feature 1 - Accuracy Pass)

Purpose:
  Generate a machine-readable content-quality report for a test jam's CSV test cases.

Why this exists:
  The existing "quality contract" focuses on formatting/safety (numbered lists, CSV injection prevention).
  This tool focuses on *content validity signals*:
    - Completeness (preconditions/steps/results present and verifiable)
    - Specificity (avoid vague "works as expected" outcomes)
    - Consistency (basic contradiction heuristics)
    - Optional AC coverage mapping (heuristic; requires AC text input)

Output:
  test-jams/{session}/test_jam_quality_report.json

Notes:
  - This tool is intentionally conservative and heuristic-based.
  - It will not invent product behavior.
  - It is designed to keep the workflow fast: Quick mode should run in seconds.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import dataclass
from utils import now_utc_iso
from pathlib import Path
from typing import Dict, List, Optional, Tuple


@dataclass
class Finding:
    severity: str  # "high" | "medium" | "low"
    test_id: str
    field: str  # "pre_conditions" | "test_steps" | "expected_results" | "metadata" | "coverage"
    issue: str
    suggestion: str


VAGUE_PATTERNS = [
    r"\bworks as expected\b",
    r"\bexpected behavior\b",
    r"\bproperly\b",
    r"\bcorrectly\b",
    r"\bsuccessfully\b",
    r"\bno issues\b",
    r"\bshould work\b",
    r"\bverify it works\b",
    r"\bconfirm it works\b",
]

VAGUE_VERBS = [
    "verify",
    "check",
    "confirm",
    "ensure",
    "validate",
]



def tokenize(text: str) -> List[str]:
    text = (text or "").lower()
    text = re.sub(r"[^a-z0-9\s-]", " ", text)
    tokens = [t for t in text.split() if len(t) >= 3]
    # light stopwording
    stop = {"the", "and", "then", "with", "that", "this", "from", "when", "into", "for", "user", "page"}
    return [t for t in tokens if t not in stop]


def extract_numbered_items(text: str) -> List[str]:
    """
    Extract numbered-list items from multi-line fields.
    Supports:
      1. item
      2) item
    """
    if not text or not text.strip():
        return []
    items: List[str] = []
    for line in text.splitlines():
        m = re.match(r"^\s*\d+[\.\)]\s*(.+?)\s*$", line.strip())
        if m:
            items.append(m.group(1).strip())
        elif line.strip():
            # If it's not numbered, still count it as an item (but mark as unstructured)
            items.append(line.strip())
    return items


def detect_vagueness(text: str) -> bool:
    t = (text or "").lower()
    for pat in VAGUE_PATTERNS:
        if re.search(pat, t, re.IGNORECASE):
            return True
    return False


def has_concrete_noun_phrase(step: str) -> bool:
    """
    Simple heuristic: does the step mention a concrete UI artifact?
    This is intentionally broad: button/link/modal/table/etc.
    """
    s = (step or "").lower()
    concrete_markers = [
        "button",
        "link",
        "modal",
        "dialog",
        "page",
        "screen",
        "table",
        "row",
        "column",
        "field",
        "input",
        "dropdown",
        "checkbox",
        "toggle",
        "banner",
        "toast",
        "error",
        "warning",
        "message",
        "header",
        "footer",
        "tab",
        "menu",
        "navigation",
        "url",
        "/",
    ]
    return any(m in s for m in concrete_markers)


def parse_acs_text(acs_text: str) -> List[Dict[str, str]]:
    """
    Parse ACs from pasted text. Supports lines like:
      AC1: ...
      AC-2 - ...
      AC 3 ...
    """
    if not acs_text or not acs_text.strip():
        return []

    acs: List[Dict[str, str]] = []
    for raw in acs_text.splitlines():
        line = raw.strip()
        if not line:
            continue
        m = re.match(r"^(AC[\s-]*\d+)\s*[:\-]\s*(.+)$", line, re.IGNORECASE)
        if not m:
            # fallback: if the line starts with AC<number>
            m2 = re.match(r"^(AC[\s-]*\d+)\s+(.+)$", line, re.IGNORECASE)
            if not m2:
                continue
            ac_id = re.sub(r"\s+", "", m2.group(1).upper())
            acs.append({"ac_id": ac_id, "text": m2.group(2).strip()})
            continue
        ac_id = re.sub(r"\s+", "", m.group(1).upper())
        acs.append({"ac_id": ac_id, "text": m.group(2).strip()})
    return acs


def score_ac_match(ac_text: str, test_blob: str) -> float:
    """
    Very lightweight similarity: token overlap ratio.
    """
    ac_tokens = set(tokenize(ac_text))
    tc_tokens = set(tokenize(test_blob))
    if not ac_tokens or not tc_tokens:
        return 0.0
    overlap = len(ac_tokens.intersection(tc_tokens))
    return overlap / max(1, len(ac_tokens))


class AccuracyAnalyzer:
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root

    def resolve_test_jam_dir(self, name: str) -> Path:
        return self.repo_root / "test-jams" / name

    def load_test_cases(self, test_jam_dir: Path) -> Tuple[List[Dict[str, str]], List[str]]:
        """
        Load test cases from CSV files within a test jam directory.

        Preference:
          - If the master CSV `testjam_all_test_cases.csv` exists, analyze ONLY that file.
            (Participant CSVs intentionally share the same Test IDs and would otherwise
            create false "duplicate ID" findings.)
          - Otherwise, fall back to analyzing all `testjam_*.csv` files found.

        Returns: (rows, warnings)
        """
        warnings: List[str] = []
        master = test_jam_dir / "testjam_all_test_cases.csv"
        if master.exists():
            csv_files = [master]
        else:
            csv_files = list(test_jam_dir.glob("testjam_*.csv"))
        if not csv_files:
            raise FileNotFoundError(f"No testjam_*.csv files found in {test_jam_dir}")

        rows: List[Dict[str, str]] = []
        for path in csv_files:
            try:
                with open(path, "r", encoding="utf-8-sig", newline="") as f:
                    reader = csv.DictReader(f)
                    for r in reader:
                        # Only consider rows that look like test cases
                        tid = (r.get("Test Case ID") or r.get("Test ID") or r.get("Test Id") or "").strip()
                        if not tid:
                            continue
                        rows.append(r)
            except Exception as e:
                warnings.append(f"Failed to read {path.name}: {e}")
        return rows, warnings

    def analyze_quick(
        self,
        test_jam_dir: Path,
        acs: Optional[List[Dict[str, str]]] = None,
    ) -> Dict:
        rows, read_warnings = self.load_test_cases(test_jam_dir)

        findings: List[Finding] = []
        test_ids_seen: set[str] = set()

        for r in rows:
            test_id = (r.get("Test Case ID") or r.get("Test ID") or r.get("Test Id") or "").strip()
            if not test_id:
                continue
            if test_id in test_ids_seen:
                findings.append(
                    Finding(
                        severity="medium",
                        test_id=test_id,
                        field="metadata",
                        issue="Duplicate Test ID detected",
                        suggestion="Ensure Test IDs are unique across the test jam.",
                    )
                )
            test_ids_seen.add(test_id)

            pre = (r.get("Pre-conditions") or r.get("Preconditions") or "").strip()
            steps = (r.get("Test Steps") or "").strip()
            results = (r.get("Expected Results") or "").strip()
            name = (r.get("Test Name") or r.get("Test Scenario") or "").strip()
            objective = (r.get("Objective") or "").strip()

            # Completeness
            if not steps:
                findings.append(
                    Finding(
                        severity="high",
                        test_id=test_id,
                        field="test_steps",
                        issue="Missing Test Steps",
                        suggestion="Add numbered steps that a tester can execute unambiguously.",
                    )
                )
            if not results:
                findings.append(
                    Finding(
                        severity="high",
                        test_id=test_id,
                        field="expected_results",
                        issue="Missing Expected Results",
                        suggestion="Add verifiable expected results (UI state, message text, URL change, etc.).",
                    )
                )

            # Specificity/vagueness
            if detect_vagueness(results):
                findings.append(
                    Finding(
                        severity="medium",
                        test_id=test_id,
                        field="expected_results",
                        issue="Vague expected results (e.g., 'works as expected')",
                        suggestion="Rewrite as verifiable outcomes (what appears/changes, what text, what state).",
                    )
                )

            step_items = extract_numbered_items(steps)
            for item in step_items:
                if any(item.lower().startswith(v) for v in VAGUE_VERBS) and not has_concrete_noun_phrase(item):
                    findings.append(
                        Finding(
                            severity="low",
                            test_id=test_id,
                            field="test_steps",
                            issue=f"Vague step '{item[:60] + ('…' if len(item) > 60 else '')}'",
                            suggestion="Reference a concrete UI element and the action (click/fill/navigate) explicitly.",
                        )
                    )
                    break

            # Light consistency: auth hint mismatch
            if "logged out" in pre.lower() and "login" not in steps.lower() and "sign in" not in steps.lower():
                # This is a weak heuristic; mark low.
                findings.append(
                    Finding(
                        severity="low",
                        test_id=test_id,
                        field="pre_conditions",
                        issue="Pre-conditions mention 'logged out' but steps don’t include login/navigation",
                        suggestion="Confirm starting state and ensure steps include required navigation/auth actions.",
                    )
                )

            # Light completeness: name/objective
            if not name:
                findings.append(
                    Finding(
                        severity="low",
                        test_id=test_id,
                        field="metadata",
                        issue="Missing Test Name",
                        suggestion="Provide a concise, specific test name that reflects the scenario under test.",
                    )
                )
            if not objective:
                findings.append(
                    Finding(
                        severity="low",
                        test_id=test_id,
                        field="metadata",
                        issue="Missing Objective",
                        suggestion="Add a one-line objective (what risk/behavior this test validates).",
                    )
                )

        # AC Coverage (heuristic)
        coverage: Dict[str, List[str]] = {}
        coverage_missing: List[str] = []
        if acs:
            for ac in acs:
                ac_id = ac["ac_id"]
                best: List[Tuple[str, float]] = []
                for r in rows:
                    test_id = (r.get("Test Case ID") or r.get("Test ID") or r.get("Test Id") or "").strip()
                    if not test_id:
                        continue
                    blob = " ".join(
                        [
                            (r.get("Test Name") or ""),
                            (r.get("Objective") or ""),
                            (r.get("Pre-conditions") or r.get("Preconditions") or ""),
                            (r.get("Test Steps") or ""),
                            (r.get("Expected Results") or ""),
                        ]
                    )
                    score = score_ac_match(ac["text"], blob)
                    if score >= 0.18:  # heuristic threshold
                        best.append((test_id, score))
                best.sort(key=lambda x: x[1], reverse=True)
                coverage[ac_id] = [tid for tid, _ in best[:10]]
                if not coverage[ac_id]:
                    coverage_missing.append(ac_id)
                    findings.append(
                        Finding(
                            severity="high",
                            test_id="(test jam)",
                            field="coverage",
                            issue=f"Missing coverage for {ac_id}",
                            suggestion="Add at least one test case explicitly covering this AC.",
                        )
                    )

        # Summarize findings
        def count(sev: str) -> int:
            return sum(1 for f in findings if f.severity == sev)

        report = {
            "generated_at_utc": now_utc_iso(),
            "mode": "quick",
            "test_jam_dir": str(test_jam_dir),
            "counts": {
                "test_cases_reviewed": len(test_ids_seen),
                "findings_total": len(findings),
                "high": count("high"),
                "medium": count("medium"),
                "low": count("low"),
                "ac_coverage_gaps": len(coverage_missing),
            },
            "acs": acs or [],
            "ac_coverage": coverage,
            "read_warnings": read_warnings,
            "findings": [
                {
                    "severity": f.severity,
                    "test_id": f.test_id,
                    "field": f.field,
                    "issue": f.issue,
                    "suggestion": f.suggestion,
                }
                for f in findings
            ],
        }
        return report

    def write_report(self, test_jam_dir: Path, report: Dict) -> Path:
        out_path = test_jam_dir / "test_jam_quality_report.json"
        out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return out_path


def high_severity_test_ids(report: Dict) -> List[str]:
    """Return unique Test IDs that have at least one high-severity finding.

    Used by the /qforge skill's "high-severity findings remediation" step to
    drive targeted regeneration of just the flagged rows. Order is preserved
    so the agent can stream-regenerate in a stable sequence.
    """
    seen: set = set()
    out: List[str] = []
    for finding in report.get("findings", []) or []:
        if finding.get("severity") != "high":
            continue
        test_id = finding.get("test_id")
        if not test_id or test_id in seen:
            continue
        seen.add(test_id)
        out.append(test_id)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="QualityForge Test Jam Accuracy Analyzer (Feature 1)")
    parser.add_argument("--test-jam", required=True, help="Test jam directory name under test-jams/")
    parser.add_argument(
        "--mode",
        choices=["quick"],
        default="quick",
        help=(
            "Accuracy pass mode. Only 'quick' is supported by this CLI; "
            "the deeper 'Thorough' pass is orchestrated by /qforge at the skill layer "
            "(Quick heuristics + agent-driven semantic analysis)."
        ),
    )
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

    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    analyzer = AccuracyAnalyzer(repo_root=repo_root)
    test_jam_dir = analyzer.resolve_test_jam_dir(args.test_jam)
    if not test_jam_dir.exists():
        raise FileNotFoundError(f"Test jam not found: {test_jam_dir}")

    acs_text = ""
    if args.acs_file:
        acs_text = Path(args.acs_file).read_text(encoding="utf-8")
    elif args.acs_text:
        acs_text = args.acs_text

    acs = parse_acs_text(acs_text) if acs_text.strip() else None

    report = analyzer.analyze_quick(test_jam_dir=test_jam_dir, acs=acs)
    out_path = analyzer.write_report(test_jam_dir, report)

    print("✅ Test Jam Content Findings Report Generated")
    print(f"📁 Location: {out_path}")
    print(f"📊 Reviewed: {report['counts']['test_cases_reviewed']} test cases")
    print(
        f"🔎 Content Findings: {report['counts']['high']} high, {report['counts']['medium']} medium, {report['counts']['low']} low"
    )
    if report["counts"]["ac_coverage_gaps"] > 0:
        print(f"⚠️  AC coverage gaps: {report['counts']['ac_coverage_gaps']}")


if __name__ == "__main__":
    main()


