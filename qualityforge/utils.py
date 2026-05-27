"""Shared utilities for Quality Engineering Suite scripts."""

from datetime import datetime, timezone


def now_utc_iso() -> str:
    """Return current UTC timestamp in ISO format.
    
    Returns:
        str: ISO 8601 formatted UTC timestamp, or empty string on error.
    """
    try:
        return datetime.now(timezone.utc).isoformat()
    except Exception:
        return ""
