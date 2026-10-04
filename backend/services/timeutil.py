"""
AirVision AI — Timestamp helpers
=================================
Every timestamp the API emits is **ISO-8601 in UTC with an explicit `Z`**.

Why this matters: the backend previously sent naive strings like
``"2026-10-03 04:26:02"``. A browser parses that as *local* time, so a server
running in UTC and a user in IST (UTC+5:30) disagreed by 5½ hours — fresh data
looked 5½ hours old and the dashboard raised a false
"Live data is temporarily unavailable" staleness warning.

`utc_iso()` removes the ambiguity: `2026-10-03T04:26:02Z` is parsed correctly
by `new Date(...)` in every timezone.
"""

import time
from datetime import datetime, timezone

ISO_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


def utc_iso(epoch_seconds: float = None) -> str:
    """Current (or given) time as an ISO-8601 UTC string, e.g. 2026-10-03T04:26:02Z."""
    if epoch_seconds is None:
        epoch_seconds = time.time()
    return time.strftime(ISO_FORMAT, time.gmtime(epoch_seconds))


def to_utc_iso(dt: datetime) -> str:
    """Convert a datetime (naive = assumed local) to an ISO-8601 UTC string."""
    if dt.tzinfo is None:
        dt = dt.astimezone()
    return dt.astimezone(timezone.utc).strftime(ISO_FORMAT)


def epoch_now() -> float:
    return time.time()
