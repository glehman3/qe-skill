#!/usr/bin/env python3
"""
Generate Jira ticket drafts from a completed test jam CSV export.

This tool:
  - Scans a completed test jam CSV
  - Filters rows with FAIL results
  - Dedupes by Test ID (default)
  - Outputs Jira-ready title + description blocks (no auto-creation)
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import dataclass, asdict
from utils import now_utc_iso
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


DEFAULT_FAIL_TOKENS = ("fail", "failed", "failure")
URL_RE = re.compile(r"https?://[^\s)]+", re.IGNORECASE)
ARTIFACT_HINTS = (
    "screenshot",
    "screen shot",
    "image",
    "png",
    "jpg",
    "jpeg",
    "gif",
    "drive.google.com",
    "docs.google.com",
    "video",
    "loom",
)



def load_csv_rows(path: Path) -> Tuple[List[str], List[Dict[str, str]]]:
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        header = list(reader.fieldnames) if reader.fieldnames else []
        rows = [normalize_row(row) for row in reader]
    return header, rows


def normalize_row(row: Dict[str, Optional[str]]) -> Dict[str, str]:
    normalized: Dict[str, str] = {}
    for key, value in row.items():
        k = (key or "").strip()
        v = (value or "").strip()
        normalized[k] = v
    return normalized


def find_column(header: Iterable[str], candidates: Iterable[Optional[str]]) -> Optional[str]:
    header_set = {h.strip() for h in header}
    for candidate in candidates:
        if candidate and candidate in header_set:
            return candidate
    return None


def get_value(row: Dict[str, str], header: Iterable[str], candidates: Iterable[Optional[str]]) -> str:
    column = find_column(header, candidates)
    if not column:
        return ""
    return (row.get(column) or "").strip()


def is_fail(value: str, fail_tokens: Tuple[str, ...] = DEFAULT_FAIL_TOKENS) -> bool:
    v = (value or "").strip().lower()
    if not v:
        return False
    return any(token in v for token in fail_tokens)


def split_csv_list(value: str) -> List[str]:
    if not value:
        return []
    return [v.strip() for v in value.split(",") if v.strip()]


def extract_artifacts(*texts: str) -> Tuple[bool, List[str]]:
    links: List[str] = []
    hint_found = False
    for text in texts:
        if not text:
            continue
        for match in URL_RE.findall(text):
            if match not in links:
                links.append(match)
        lowered = text.lower()
        if any(hint in lowered for hint in ARTIFACT_HINTS):
            hint_found = True
    return (hint_found or bool(links)), links


def format_section(title: str, content: str, fallback: str = "Not provided in CSV.") -> str:
    body = content.strip() if content.strip() else fallback
    return f"h3. {title}\n{body}\n"


@dataclass
class DraftTicket:
    title: str
    description: str
    test_id: str
    # Jira creation parameters (stored for JSON output)
    project_key: str = ""
    epic_key: str = ""
    labels: List[str] = None  # type: ignore
    priority: str = ""
    issue_type: str = ""
    
    def __post_init__(self) -> None:
        if self.labels is None:
            self.labels = []
    
    def to_atlassian_jira_args(self) -> Dict[str, Any]:
        """Return arguments for Atlassian MCP createJiraIssue.
        
        Note: cloudId must be added by the agent when calling the MCP.
        """
        args: Dict[str, Any] = {
            "projectKey": self.project_key,
            "summary": self.title,
            "description": self.description,
            "issueTypeName": self.issue_type or "Story",  # Renamed from issueType
        }
        additional_fields: Dict[str, Any] = {}
        if self.labels:
            additional_fields["labels"] = self.labels
        if self.priority:
            additional_fields["priority"] = {"name": self.priority}
        if additional_fields:
            args["additional_fields"] = additional_fields
        # Note: epicLink often requires manual linking due to Jira API limitations
        return args

    def to_jira_args(self) -> Dict[str, Any]:
        """Deprecated: Use to_atlassian_jira_args() instead."""
        return self.to_atlassian_jira_args()


def build_description(
    test_id: str,
    test_name: str,
    conditions: str,
    steps: str,
    expected: str,
    actual: str,
    evidence: str,
    artifacts_present: bool,
    artifact_links: List[str],
    feature_flags: List[str],
    experiment_command: str,
    environment: str,
    project_key: str,
    epic_key: str,
    labels: List[str],
    priority: str,
    issue_type: str,
) -> str:
    blocks: List[str] = []
    blocks.append(format_section("Test Case ID", test_id or "Unknown"))
    blocks.append(format_section("Description", test_name or "Test case failed during completed test jam."))
    blocks.append(format_section("Conditions", conditions))
    blocks.append(format_section("Steps to Test", steps))
    blocks.append(format_section("Expected Results", expected))

    if actual.strip():
        blocks.append(format_section("Actual Results", actual, fallback=""))

    if evidence.strip():
        blocks.append(format_section("Testing Evidence", evidence, fallback=""))

    if artifacts_present:
        links_line = f"Links: {', '.join(artifact_links)}" if artifact_links else "Links: Not provided"
        blocks.append(
            "h3. Artifacts\n"
            "Artifacts referenced in test jam: Yes\n"
            f"{links_line}\n"
            "Note: Attach screenshots/artifacts to Jira manually.\n"
        )

    flags_block = "None provided"
    if feature_flags:
        flags_block = "\n".join([f"- {flag}" for flag in feature_flags])

    blocks.append(
        "h3. Requirements\n"
        "*Feature Flags:*\n"
        f"{flags_block}\n\n"
        "*Console Command for Experiments:*\n"
        f"{format_code_block(experiment_command)}\n"
        f"\n*Environment:* {environment or 'Not specified'}\n"
    )

    metadata_lines = []
    if project_key:
        metadata_lines.append(f"*Project:* {project_key}")
    if epic_key:
        metadata_lines.append(f"*Epic:* {epic_key}")
    if labels:
        metadata_lines.append(f"*Labels:* {', '.join(labels)}")
    if priority:
        metadata_lines.append(f"*Priority:* {priority}")
    if issue_type:
        metadata_lines.append(f"*Issue Type:* {issue_type}")

    if metadata_lines:
        blocks.append("h3. Metadata\n" + "\n".join(metadata_lines) + "\n")

    return "\n".join(blocks).strip() + "\n"


def format_code_block(command: str) -> str:
    if not command.strip():
        return "Not provided"
    return "{code}" + command.strip() + "{code}"


def build_ticket_drafts(
    header: List[str],
    rows: List[Dict[str, str]],
    dedupe_by: str,
    include_with_bug_id: bool,
    feature_flags: List[str],
    experiment_command: str,
    environment: str,
    project_key: str,
    epic_key: str,
    labels: List[str],
    priority: str,
    issue_type: str,
    result_column: Optional[str] = None,
    fail_tokens: Tuple[str, ...] = DEFAULT_FAIL_TOKENS,
) -> Tuple[List[DraftTicket], Dict[str, int]]:
    seen: set = set()
    drafts: List[DraftTicket] = []
    stats = {
        "rows_total": len(rows),
        "rows_failed": 0,
        "rows_skipped_bug_id": 0,
        "rows_skipped_duplicate": 0,
        "rows_missing_title": 0,
    }

    # Determine result column - user-specified or fallback to common names
    result_candidates = [result_column] if result_column else []
    result_candidates.extend(["Results", "Status", "Outcome", "Test Result", "Result"])

    for row in rows:
        result_value = get_value(row, header, result_candidates)
        if not is_fail(result_value, fail_tokens):
            continue
        stats["rows_failed"] += 1

        bug_id = get_value(row, header, ["Bug ID", "Bug", "BugId", "BugID"])
        if bug_id and not include_with_bug_id:
            stats["rows_skipped_bug_id"] += 1
            continue

        test_id = get_value(row, header, ["Test ID", "Test Case ID", "Test Id"])
        test_name = get_value(row, header, ["Test Name", "Title", "Name"])

        dedupe_key = test_id.strip() if dedupe_by == "test_id" else test_name.strip()
        if not dedupe_key:
            dedupe_key = test_name or test_id or ""
        dedupe_key_norm = dedupe_key.strip().lower()
        if dedupe_key_norm in seen and dedupe_key_norm:
            stats["rows_skipped_duplicate"] += 1
            continue
        if dedupe_key_norm:
            seen.add(dedupe_key_norm)

        if not test_name and not test_id:
            stats["rows_missing_title"] += 1
            continue

        conditions = get_value(row, header, ["Conditions", "Pre-conditions", "Preconditions"])
        steps = get_value(row, header, ["Steps to Test", "Test Steps", "Steps"])
        expected = get_value(row, header, ["Expected Results", "Expected"])
        actual = get_value(row, header, ["Actual Results", "Actual Result"])
        evidence = get_value(row, header, ["Testing Evidence", "Notes", "Evidence"])

        artifacts_present, artifact_links = extract_artifacts(actual, evidence, conditions, steps, expected)

        description = build_description(
            test_id=test_id,
            test_name=test_name,
            conditions=conditions,
            steps=steps,
            expected=expected,
            actual=actual,
            evidence=evidence,
            artifacts_present=artifacts_present,
            artifact_links=artifact_links,
            feature_flags=feature_flags,
            experiment_command=experiment_command,
            environment=environment,
            project_key=project_key,
            epic_key=epic_key,
            labels=labels,
            priority=priority,
            issue_type=issue_type,
        )

        title = test_name.strip() if test_name else (test_id or "Test case failure")
        drafts.append(DraftTicket(
            title=title,
            description=description,
            test_id=test_id,
            project_key=project_key,
            epic_key=epic_key,
            labels=labels.copy(),
            priority=priority,
            issue_type=issue_type,
        ))

    return drafts, stats


def normalize_labels(values: List[str]) -> List[str]:
    normalized: List[str] = []
    for value in values:
        normalized.extend(split_csv_list(value))
    return normalized


def write_markdown(
    output_path: Path,
    csv_path: Path,
    drafts: List[DraftTicket],
    stats: Dict[str, int],
) -> None:
    header_lines = [
        "# Jira Ticket Drafts - Completed Test Jam",
        "",
        f"- Source CSV: {csv_path}",
        f"- Generated: {now_utc_iso()}",
        "",
        "## Summary",
        f"- Total rows: {stats.get('rows_total', 0)}",
        f"- Failed rows: {stats.get('rows_failed', 0)}",
        f"- Skipped (Bug ID present): {stats.get('rows_skipped_bug_id', 0)}",
        f"- Skipped (Duplicate): {stats.get('rows_skipped_duplicate', 0)}",
        f"- Skipped (Missing title): {stats.get('rows_missing_title', 0)}",
        f"- Draft tickets: {len(drafts)}",
        "",
        "## Drafts",
        "",
    ]

    sections: List[str] = []
    for idx, draft in enumerate(drafts, start=1):
        sections.append(f"### Ticket {idx}")
        sections.append("")
        sections.append("Title:")
        sections.append("```")
        sections.append(draft.title)
        sections.append("```")
        sections.append("")
        sections.append("Description:")
        sections.append("```")
        sections.append(draft.description.rstrip())
        sections.append("```")
        sections.append("")

    output_path.write_text("\n".join(header_lines + sections).strip() + "\n", encoding="utf-8")


def write_json(
    output_path: Path,
    csv_path: Path,
    drafts: List[DraftTicket],
    stats: Dict[str, int],
    epic_key: str,
) -> None:
    """Write JSON output for programmatic consumption by agent."""
    data = {
        "source_csv": str(csv_path),
        "generated_at": now_utc_iso(),
        "stats": stats,
        "epic_key": epic_key,
        "draft_count": len(drafts),
        "drafts": [
            {
                "index": idx,
                "test_id": draft.test_id,
                "title": draft.title,
                "description": draft.description,
                "jira_args": draft.to_jira_args(),
            }
            for idx, draft in enumerate(drafts, start=1)
        ],
    }
    output_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate Jira ticket drafts from a completed test jam CSV export."
    )
    parser.add_argument("--csv", required=True, help="Path to completed test jam CSV export")
    parser.add_argument(
        "--output",
        default=None,
        help="Output markdown path (default: jira_ticket_drafts.md next to the CSV)",
    )
    parser.add_argument("--project-key", default="", help="Jira project key (e.g., HELIX)")
    parser.add_argument("--epic", dest="epic_key", default="", help="Epic key (e.g., HELIX-10332)")
    parser.add_argument("--label", action="append", default=[], help="Label to apply (repeatable)")
    parser.add_argument("--priority", default="P3", help="Priority label (default: P3)")
    parser.add_argument("--issue-type", default="Story", help="Issue type (default: Story)")
    parser.add_argument("--environment", default="Production", help="Environment label")
    parser.add_argument(
        "--feature-flags",
        default="",
        help="Comma-separated feature flags (included in description)",
    )
    parser.add_argument(
        "--experiment-command",
        default="",
        help="Console command for experiments (included in description)",
    )
    parser.add_argument(
        "--dedupe-by",
        choices=["test_id", "test_name"],
        default="test_id",
        help="Deduplicate failing rows by test_id (default) or test_name",
    )
    parser.add_argument(
        "--include-with-bug-id",
        action="store_true",
        help="Include rows that already have a Bug ID set",
    )
    parser.add_argument(
        "--result-column",
        default=None,
        help="Column name indicating pass/fail (default: auto-detect from Results, Status, Outcome)",
    )
    parser.add_argument(
        "--fail-values",
        default="fail,failed,failure",
        help="Comma-separated values indicating failure (default: fail,failed,failure)",
    )
    parser.add_argument(
        "--list-columns",
        action="store_true",
        help="List CSV columns and exit (useful for discovering column names)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON (jira_ticket_drafts.json) instead of/alongside markdown for agent consumption",
    )

    args = parser.parse_args()

    csv_path = Path(args.csv).expanduser().resolve()
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    header, rows = load_csv_rows(csv_path)

    # List columns mode - useful for discovering column names
    if args.list_columns:
        print(f"📋 CSV Columns in {csv_path.name}:")
        for i, col in enumerate(header, start=1):
            print(f"  {i}. {col}")
        print(f"\nTotal columns: {len(header)}")
        print(f"Total rows: {len(rows)}")
        return

    labels = normalize_labels(args.label)
    feature_flags = split_csv_list(args.feature_flags)
    fail_tokens = tuple(v.strip().lower() for v in args.fail_values.split(",") if v.strip())

    output_path = (
        Path(args.output).expanduser().resolve()
        if args.output
        else csv_path.parent / "jira_ticket_drafts.md"
    )

    drafts, stats = build_ticket_drafts(
        header=header,
        rows=rows,
        dedupe_by=args.dedupe_by,
        include_with_bug_id=args.include_with_bug_id,
        feature_flags=feature_flags,
        experiment_command=args.experiment_command,
        environment=args.environment,
        project_key=args.project_key,
        epic_key=args.epic_key,
        labels=labels,
        priority=args.priority,
        issue_type=args.issue_type,
        result_column=args.result_column,
        fail_tokens=fail_tokens,
    )

    write_markdown(output_path, csv_path, drafts, stats)
    print(f"✅ Jira drafts (markdown): {output_path}")
    
    # Also write JSON if requested
    if args.json:
        json_path = output_path.with_suffix(".json")
        write_json(json_path, csv_path, drafts, stats, args.epic_key)
        print(f"✅ Jira drafts (JSON): {json_path}")
    
    print(f"✅ Draft tickets: {len(drafts)}")


if __name__ == "__main__":
    main()
