from datetime import datetime, timezone
from typing import Optional


def format_relative_date(dt: Optional[datetime], now: Optional[datetime] = None) -> Optional[str]:
    """Format a datetime as a relative years/months string plus a YYYY-MM-DD date.

    Examples:
      - "2 years and 3 months ago at 2023-08-15"
      - "3 months ago at 2025-09-10"
      - "less than a month ago at 2025-11-25"

    Returns None if `dt` is falsy.
    """
    if not dt:
        return None

    # Ensure timezone-aware in UTC
    try:
        joined_dt = dt
        if joined_dt.tzinfo is None:
            joined_dt = joined_dt.replace(tzinfo=timezone.utc)
        else:
            joined_dt = joined_dt.astimezone(timezone.utc)
    except Exception:
        joined_dt = dt

    if now is None:
        now = datetime.now(timezone.utc)

    years = now.year - joined_dt.year
    months = now.month - joined_dt.month

    # If the current day hasn't reached the joined day, subtract one month
    if now.day < joined_dt.day:
        months -= 1

    if months < 0:
        years -= 1
        months += 12

    parts = []
    if years > 0:
        parts.append(f"{years} year{'s' if years != 1 else ''}")
    if months > 0:
        parts.append(f"{months} month{'s' if months != 1 else ''}")

    if parts:
        rel = ' and '.join(parts) + ' ago.'
    else:
        rel = 'less than a month ago.'

    formatted_date = joined_dt.strftime("%Y-%m-%d")
    return f"{rel}\nat {formatted_date}"
