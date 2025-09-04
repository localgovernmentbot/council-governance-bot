"""
Date formatting helpers for CouncilBot posts.
"""

from datetime import datetime
import re


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


def rewrite_date_in_title(title: str, date_str: str) -> str:
    """Replace 'YYYY-MM-DD' in title with long date form.

    If date_str is provided and appears in the title, it is replaced.
    Otherwise, the first ISO date in the title is detected and replaced.
    """
    if not title:
        return title
    try:
        target = None
        # Prefer the explicit date_str if it looks like YYYY-MM-DD
        if date_str and re.fullmatch(r"\d{4}-\d{2}-\d{2}", date_str):
            target = date_str
        else:
            m = re.search(r"\b\d{4}-\d{2}-\d{2}\b", title)
            if m:
                target = m.group(0)
        if not target:
            return title
        pretty = format_long_date(target)
        return title.replace(target, pretty)
    except Exception:
        return title
