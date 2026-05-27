#!/usr/bin/env python3
"""
Quality Risk Analysis report quality checker (content accuracy).

Purpose:
  Validate that a generated risk_analysis_report.md follows the content accuracy rubric:
    - Each risk includes inline evidence tags (REQ-###, CODE-###) and confidence level
    - No "invented" metrics are presented as facts without evidence tags
    - CODE evidence is relevant to the risk (not analogical/indirect without disclosure)

Output:
  Writes a machine-readable JSON report: risk_quality_report.json

"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# Risk headers: support both ### and #### (the lean template uses ####).
RISK_HEADER_RE = re.compile(r"^#{3,4}\s+(RISK-\d{3})\s*:\s*(.+?)\s*$")

EVIDENCE_TAG_RE = re.compile(r"\b(REQ|CODE|HIST|OPS)-\d{3}\b")

# Confidence can appear as a standalone bold line OR inline in prose (e.g., "**Confidence: Medium**").
CONFIDENCE_RE = re.compile(r"\*\*Confidence:?\*?\*?\s*(High|Medium|Low)\b", re.IGNORECASE)
CONFIDENCE_INLINE_RE = re.compile(r"\bConfidence:?\s*(High|Medium|Low)\b", re.IGNORECASE)

# "banned unless verified" patterns (rubric calls these out explicitly).
BANNED_METRIC_PATTERNS: List[Tuple[str, re.Pattern]] = [
    ("coverage_percentage", re.compile(r"\b\d{1,3}%\s+coverage\b", re.IGNORECASE)),
    ("cyclomatic_complexity", re.compile(r"\bcyclomatic\s+complexity\b", re.IGNORECASE)),
    ("high_churn_claim", re.compile(r"\bchanges?\s+in\s+last\b", re.IGNORECASE)),
    ("record_count_claim", re.compile(r"\b\d[\d,]*\+\s+records\b", re.IGNORECASE)),
    ("migration_timing_claim", re.compile(r"\b\d+\s*-\s*\d+\s*hours\b|\b\d+\s+hours\b", re.IGNORECASE)),
]

# Hedging language that suggests CODE evidence is being used by analogy.
HEDGING_PATTERNS: List[re.Pattern] = [
    re.compile(r"\bsuggests?\b", re.IGNORECASE),
    re.compile(r"\bpattern of\b", re.IGNORECASE),
    re.compile(r"\bsimilar\s+(to|pattern|issue|bug)\b", re.IGNORECASE),
    re.compile(r"\bby analogy\b", re.IGNORECASE),
    re.compile(r"\bimplies?\b", re.IGNORECASE),
    re.compile(r"\bindicates?\s+that\s+.*\bmay\b", re.IGNORECASE),
    re.compile(r"\bcould\s+similarly\b", re.IGNORECASE),
    re.compile(r"\bthis\s+.*\bfragile\b", re.IGNORECASE),
]


@dataclass
class Finding:
    severity: str  # high|medium|low
    rule: str
    message: str
    risk_id: Optional[str] = None
    line: Optional[int] = None

    def to_dict(self) -> Dict[str, object]:
        out: Dict[str, object] = {"severity": self.severity, "rule": self.rule, "message": self.message}
        if self.risk_id:
            out["risk_id"] = self.risk_id
        if self.line is not None:
            out["line"] = self.line
        return out


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _split_risk_blocks(lines: List[str]) -> List[Tuple[str, str, int, int]]:
    """
    Return list of (risk_id, title, start_line_idx, end_line_idx) in 1-based line numbers.
    """
    blocks: List[Tuple[str, str, int, int]] = []
    starts: List[Tuple[str, str, int]] = []
    for idx, line in enumerate(lines, start=1):
        m = RISK_HEADER_RE.match(line)
        if m:
            starts.append((m.group(1), m.group(2), idx))
    for i, (rid, title, start) in enumerate(starts):
        end = (starts[i + 1][2] - 1) if i + 1 < len(starts) else len(lines)
        blocks.append((rid, title, start, end))
    return blocks


def _extract_block_text(lines: List[str], start: int, end: int) -> str:
    return "\n".join(lines[start - 1 : end])


def _count_evidence_tags(text: str) -> Dict[str, int]:
    counts = {"REQ": 0, "CODE": 0, "HIST": 0, "OPS": 0}
    for m in EVIDENCE_TAG_RE.finditer(text):
        kind = m.group(1)
        counts[kind] = counts.get(kind, 0) + 1
    return counts


def check_report(path: Path) -> Dict[str, object]:
    text = _read_text(path)
    lines = text.splitlines()
    findings: List[Finding] = []

    risk_blocks = _split_risk_blocks(lines)
    if not risk_blocks:
        findings.append(
            Finding(
                severity="high",
                rule="no_risks_detected",
                message="No risk headers found. Expected headings like: '#### RISK-001: ...'",
            )
        )

    # Global checks — look for Key Requirements section (lean format) or
    # Unified Requirements Summary (legacy format).
    has_requirements = ("Key Requirements" in text or "Unified Requirements Summary" in text)
    if not has_requirements:
        findings.append(
            Finding(
                severity="medium",
                rule="missing_requirements_section",
                message="Missing 'Key Requirements' (or 'Unified Requirements Summary') section.",
            )
        )

    # Per-risk checks
    for rid, _title, start, end in risk_blocks:
        block = _extract_block_text(lines, start, end)
        counts = _count_evidence_tags(block)

        # Evidence: at least one REQ tag in the risk block.
        if counts["REQ"] <= 0:
            findings.append(
                Finding(
                    severity="high",
                    rule="risk_missing_req_evidence",
                    message="Risk missing requirements evidence tag (REQ-###).",
                    risk_id=rid,
                    line=start,
                )
            )

        # CODE evidence: medium severity if missing (some risks are requirement-only).
        if counts["CODE"] <= 0:
            findings.append(
                Finding(
                    severity="medium",
                    rule="risk_missing_code_evidence",
                    message="Risk has no code evidence tag (CODE-###). If no code mapping exists, ensure confidence is Low and a spike/question is included.",
                    risk_id=rid,
                    line=start,
                )
            )

        # Confidence: can appear as bold line OR inline in description text.
        block_lines_raw = lines[start - 1 : end]
        has_confidence = any(
            CONFIDENCE_RE.search(l) or CONFIDENCE_INLINE_RE.search(l)
            for l in block_lines_raw
        )
        if not has_confidence:
            findings.append(
                Finding(
                    severity="high",
                    rule="risk_missing_confidence",
                    message="Risk missing confidence level. Include 'Confidence: High|Medium|Low' (inline or as a bold line).",
                    risk_id=rid,
                    line=start,
                )
            )

        # Mitigations: check that at least one exists.
        if "**Mitigations:**" not in block and "**Mitigation" not in block:
            findings.append(
                Finding(
                    severity="medium",
                    rule="risk_missing_mitigations",
                    message="Risk missing mitigations section.",
                    risk_id=rid,
                    line=start,
                )
            )

    # Banned metric claims without evidence tag on same line.
    for idx, line in enumerate(lines, start=1):
        for rule, pat in BANNED_METRIC_PATTERNS:
            if pat.search(line):
                if not EVIDENCE_TAG_RE.search(line):
                    findings.append(
                        Finding(
                            severity="high",
                            rule=f"unverified_metric_{rule}",
                            message="Found a potentially unverified metric claim. Add evidence (HIST/OPS/CODE) or rephrase as hypothesis.",
                            line=idx,
                        )
                    )

    # Evidence relevance: detect hedging language near CODE references.
    # Scans all lines in a risk block (evidence is now inline, not in a separate section).
    for rid, _title, start, end in risk_blocks:
        block_lines = lines[start - 1 : end]
        flagged = False
        for local_idx, bline in enumerate(block_lines):
            if not re.search(r"\bCODE-\d{3}\b|\bPR\s+#\d+\b", bline):
                continue
            for hedging_pat in HEDGING_PATTERNS:
                if hedging_pat.search(bline):
                    findings.append(
                        Finding(
                            severity="medium",
                            rule="evidence_analogical_not_direct",
                            message=(
                                "CODE/PR reference uses hedging language, suggesting analogical "
                                "reasoning. Verify the code directly supports this risk, or "
                                "convert the inference into an assumption."
                            ),
                            risk_id=rid,
                            line=start + local_idx,
                        )
                    )
                    flagged = True
                    break
            if flagged:
                break

    summary = {
        "risks_detected": len(risk_blocks),
        "findings_total": len(findings),
        "high": sum(1 for f in findings if f.severity == "high"),
        "medium": sum(1 for f in findings if f.severity == "medium"),
        "low": sum(1 for f in findings if f.severity == "low"),
    }

    passed = summary["high"] == 0

    return {
        "tool": "qualityforge.risk_report_quality",
        "version": "2",
        "input_path": str(path),
        "passed": passed,
        "summary": summary,
        "findings": [f.to_dict() for f in findings],
    }


def _rewrite_unverified_metric_line(line: str) -> str:
    """
    Convert "banned unless verified" metric statements into non-numeric hypotheses.
    """
    out = line
    out = re.sub(r"\b\d{1,3}%\s+coverage\b", "coverage level (not verified)", out, flags=re.IGNORECASE)
    out = re.sub(r"\bcyclomatic\s+complexity\b", "complexity (not verified)", out, flags=re.IGNORECASE)
    out = re.sub(r"\bchanges?\s+in\s+last\b", "recent changes (not verified)", out, flags=re.IGNORECASE)
    out = re.sub(r"\b\d[\d,]*\+\s+records\b", "large record volume (not verified)", out, flags=re.IGNORECASE)
    out = re.sub(r"\b\d+\s*-\s*\d+\s*hours\b", "multi-hour (not verified)", out, flags=re.IGNORECASE)
    out = re.sub(r"\b\d+\s+hours\b", "multi-hour (not verified)", out, flags=re.IGNORECASE)
    return out


def _self_repair_in_place(report_path: Path, last_result: Dict[str, object]) -> bool:
    """
    Attempt safe, mechanical repairs only (no invented evidence).
    Returns True if the file was modified.
    """
    text = _read_text(report_path)
    lines = text.splitlines()
    changed = False

    # Rewrite unverified metric lines (high severity if present).
    for i, line in enumerate(lines):
        if EVIDENCE_TAG_RE.search(line):
            continue
        if any(pat.search(line) for _rule, pat in BANNED_METRIC_PATTERNS):
            new_line = _rewrite_unverified_metric_line(line)
            if new_line != line:
                lines[i] = new_line
                changed = True

    if changed:
        report_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    return changed


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Quality Risk Analysis report content accuracy.")
    parser.add_argument("report_path", help="Path to risk_analysis_report.md")
    parser.add_argument(
        "--repair",
        action="store_true",
        help="Attempt safe, mechanical self-repair in-place (no invented evidence).",
    )
    parser.add_argument(
        "--max-repair-attempts",
        type=int,
        default=2,
        help="Max self-repair attempts when --repair is set (default: 2).",
    )
    parser.add_argument(
        "--out",
        default=None,
        help="Optional output JSON path. Defaults to risk_quality_report.json next to the input.",
    )
    args = parser.parse_args()

    report_path = Path(args.report_path).expanduser().resolve()
    if not report_path.exists():
        raise FileNotFoundError(f"Report not found: {report_path}")

    out_path = Path(args.out).expanduser().resolve() if args.out else report_path.parent / "risk_quality_report.json"

    result = check_report(report_path)

    if args.repair and not result.get("passed"):
        attempts = 0
        while attempts < max(0, int(args.max_repair_attempts)) and not result.get("passed"):
            attempts += 1
            modified = _self_repair_in_place(report_path, result)
            if not modified:
                break
            result = check_report(report_path)

    out_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    status = "PASS" if result.get("passed") else "FAIL"
    print(status)
    print(f"Report: {report_path}")
    print(f"Output: {out_path}")
    print(f"Findings: {result['summary']['findings_total']} (high: {result['summary']['high']}, medium: {result['summary']['medium']}, low: {result['summary']['low']})")


if __name__ == "__main__":
    main()
