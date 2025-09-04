"""
Date formatting helpers for CouncilBot posts.
"""

from datetime import datetime


def format_long_date(date_str: str) -> str:
    """Format 'YYYY-MM-DD' as 'Tuesday, 2 September 2025'.

    Falls back to the input if parsing fails.
    """
    if not date_str:
        return ""
    try:
        # Expect ISO format from scrapers
        dt = datetime.fromisoformat(date_str)
    except Exception:
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
        except Exception:
            return date_str

    # Build without platform-specific %-d/%#d modifiers
    day = dt.day
    return f"{dt.strftime('%A')}, {day} {dt.strftime('%B %Y')}"

