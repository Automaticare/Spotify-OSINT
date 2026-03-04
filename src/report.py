"""Track addition time analysis — detects when a playlist owner is most active."""

import logging
from datetime import timezone, timedelta

logger = logging.getLogger(__name__)

_TZ_ISTANBUL = timezone(timedelta(hours=3))

_TIME_SLOTS = {
    "gece": (0, 6),       # 00:00–05:59
    "sabah": (6, 12),     # 06:00–11:59
    "öğleden sonra": (12, 18),  # 12:00–17:59
    "akşam": (18, 24),    # 18:00–23:59
}


def analyze_time_patterns(tracks: list[dict]) -> dict | None:
    """Analyze detected_at timestamps and return structured time patterns.

    Returns None if there are no tracks to analyze.
    """
    if not tracks:
        return None

    hours = []
    for t in tracks:
        dt = t["detected_at"]
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        local = dt.astimezone(_TZ_ISTANBUL)
        hours.append(local.hour)

    # Hour frequency (0–23)
    hour_counts = [0] * 24
    for h in hours:
        hour_counts[h] += 1

    # Time slot distribution
    slot_counts = {}
    for slot_name, (start, end) in _TIME_SLOTS.items():
        slot_counts[slot_name] = sum(hour_counts[start:end])

    # Peak hour
    peak_hour = max(range(24), key=lambda h: hour_counts[h])

    # Most active slot
    most_active_slot = max(slot_counts, key=slot_counts.get)

    return {
        "total_tracks": len(tracks),
        "hour_counts": hour_counts,
        "slot_counts": slot_counts,
        "peak_hour": peak_hour,
        "most_active_slot": most_active_slot,
    }
