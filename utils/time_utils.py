"""Time utility functions."""

from datetime import datetime, timezone


def now_utc_iso():
    """Get current UTC time in ISO format.
    
    Returns:
        str: Current UTC timestamp in ISO 8601 format
    """
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
