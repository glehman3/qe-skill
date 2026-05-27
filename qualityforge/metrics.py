"""Local-first metrics logging with Google Sheets sync.

Logs invocations locally to metrics.log (JSONL format). Optional sync to
Google Sheets must not block the agent: see SYNC_INSTRUCTIONS.

Usage (for AI agent):
    1. Call log_invocation() to write to local log
    2. Do not call user-DAST-Orch sheets_append during /qforge (can hang indefinitely)
    3. Optional: user-google-drive-mcp sheets_append, or CLI export — see SYNC_INSTRUCTIONS

CLI (manual / non-blocking sync):
    python3 qualityforge/metrics.py --export-pending
    python3 qualityforge/metrics.py --mark-synced <timestamp> [<timestamp> ...]
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

METRICS_FILE = Path(__file__).parent / "metrics.log"
SPREADSHEET_ID = "15Px9z6MBG8b5o6dZcRaLO-cnaG61LNcdbbxiAaDu_-o"
SHEET_NAME = "Invocations"


def _ensure_metrics_file() -> None:
    """Create metrics.log if it doesn't exist."""
    if not METRICS_FILE.exists():
        METRICS_FILE.touch()


_ensure_metrics_file()


def _now_utc_iso() -> str:
    """Return current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat()


def _read_metrics() -> list[dict]:
    """Read all metrics entries from local log."""
    if not METRICS_FILE.exists():
        return []
    
    entries = []
    with open(METRICS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return entries


def _write_metrics(entries: list[dict]) -> None:
    """Write all metrics entries to local log (overwrites)."""
    with open(METRICS_FILE, "w", encoding="utf-8") as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")


def _append_metric(entry: dict) -> None:
    """Append a single metrics entry to local log."""
    with open(METRICS_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def log_invocation(
    local_version: str,
    latest_version: Optional[str] = None,
    is_up_to_date: Optional[bool] = None,
    feature_selected: Optional[str] = None,
) -> dict:
    """Log a QualityForge invocation locally.
    
    Args:
        local_version: Current installed version (e.g., "1.0.0")
        latest_version: Latest available version, or None if check failed
        is_up_to_date: True if local >= latest, None if unknown
        feature_selected: Which feature was selected (1-5), optional
    
    Returns:
        dict: The logged entry with synced=False
    """
    entry = {
        "timestamp": _now_utc_iso(),
        "local_version": local_version,
        "latest_version": latest_version or "unknown",
        "is_up_to_date": is_up_to_date if is_up_to_date is not None else "unknown",
        "feature_selected": feature_selected,
        "synced": False,
    }
    _append_metric(entry)
    return entry


def get_pending_entries() -> list[dict]:
    """Get all entries that haven't been synced to Sheets."""
    return [e for e in _read_metrics() if not e.get("synced", False)]


def mark_entries_synced(timestamps: list[str]) -> int:
    """Mark entries as synced by their timestamps.
    
    Args:
        timestamps: List of ISO timestamps to mark as synced
    
    Returns:
        int: Number of entries marked as synced
    """
    entries = _read_metrics()
    count = 0
    timestamp_set = set(timestamps)
    
    for entry in entries:
        if entry.get("timestamp") in timestamp_set and not entry.get("synced"):
            entry["synced"] = True
            count += 1
    
    _write_metrics(entries)
    return count


def get_metrics_summary() -> dict:
    """Get summary of local metrics.
    
    Returns:
        dict with total_invocations, pending_sync, last_invocation
    """
    entries = _read_metrics()
    pending = [e for e in entries if not e.get("synced", False)]
    
    return {
        "total_invocations": len(entries),
        "pending_sync": len(pending),
        "synced": len(entries) - len(pending),
        "last_invocation": entries[-1].get("timestamp") if entries else None,
        "metrics_file": str(METRICS_FILE),
    }


def format_for_sheets(entries: list[dict]) -> list[list[str]]:
    """Format entries as 2D array for Sheets append.
    
    Args:
        entries: List of metric entries
    
    Returns:
        2D array suitable for sheets_append values parameter
    """
    rows = []
    for e in entries:
        rows.append([
            e.get("timestamp", ""),
            e.get("local_version", ""),
            e.get("latest_version", "unknown"),
            str(e.get("is_up_to_date", "unknown")),
            e.get("feature_selected") or "",
        ])
    return rows


# Instructions for AI agent to sync pending entries:
SYNC_INSTRUCTIONS = """
To sync pending metrics to Google Sheets (without hanging the session):

**Do not** call user-DAST-Orch `sheets_append` during /qforge. That MCP tool can block
indefinitely (no client-side timeout while waiting on Google APIs / auth).

Preferred options (pick one):

A) **user-google-drive-mcp** — If enabled in Cursor, call its `sheets_append` with:
   - spreadsheet_id: "15Px9z6MBG8b5o6dZcRaLO-cnaG61LNcdbbxiAaDu_-o"
   - sheet_name: "Invocations"
   - values: from format_for_sheets(get_pending_entries())
   Then mark_entries_synced(...) on success.

B) **Skip MCP in-session** — Leave entries as synced: false. Tell the user they can run:
   python3 qualityforge/metrics.py --export-pending
   Paste rows into the Invocations sheet, then:
   python3 qualityforge/metrics.py --mark-synced <timestamp> ...

The metrics.log file persists all data locally regardless of sync status.
See qualityforge/guides/METRICS-SYNC.md for troubleshooting.
"""


def _main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="QualityForge metrics: local JSONL log and optional Sheets helpers.",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print JSON summary (counts, paths, last invocation).",
    )
    parser.add_argument(
        "--export-pending",
        action="store_true",
        help="Print pending (unsynced) rows as TSV with header, for pasting into Sheets.",
    )
    parser.add_argument(
        "--mark-synced",
        nargs="+",
        metavar="TIMESTAMP",
        help="Mark entries with these exact timestamps as synced (after manual or MCP append).",
    )
    args = parser.parse_args(argv)

    if not any([args.summary, args.export_pending, args.mark_synced]):
        parser.print_help()
        return 0

    if args.summary:
        print(json.dumps(get_metrics_summary(), indent=2))
    if args.export_pending:
        pending = get_pending_entries()
        header = ["timestamp", "local_version", "latest_version", "is_up_to_date", "feature_selected"]
        print("\t".join(header))
        for row in format_for_sheets(pending):
            print("\t".join(row))
        if not pending:
            print("(no pending rows)", file=sys.stderr)
    if args.mark_synced:
        n = mark_entries_synced(list(args.mark_synced))
        print(
            f"Marked {n} of {len(args.mark_synced)} requested timestamp(s) as synced.",
            file=sys.stderr,
        )
        if n < len(args.mark_synced):
            print(
                "Tip: timestamps must match metrics.log exactly (pending, unsynced rows only).",
                file=sys.stderr,
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
