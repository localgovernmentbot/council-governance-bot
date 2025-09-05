"""
Helpers for InfoCouncil hosts (*/infocouncil.biz) to discover files.

Strategy:
- Try fetching a month directory listing at /Open/YYYY/MM/ (some hosts serve a
  minimal HTML page with links even if not a full index).
- Also try the RedirectToDoc.aspx with URL=Open/YYYY/MM/ as some deployments
  expose a listing via that path.
- Parse any .PDF links found and return absolute URLs.
"""

from __future__ import annotations

import re
from typing import List, Tuple


def discover_month_files(base: str, year: int, month: int, session, headers) -> List[str]:
    """Return a list of absolute PDF URLs under Open/YYYY/MM for an InfoCouncil host.

    base: like https://darebin.infocouncil.biz
    """
    mm = f"{month:02d}"
    y_m = f"{year}/{mm}"
    candidates = [
        f"{base}/Open/{y_m}/",
        f"{base}/RedirectToDoc.aspx?URL=Open/{y_m}/",
    ]
    pdfs: List[str] = []
    for url in candidates:
        try:
            r = session.get(url, headers=headers, timeout=10, allow_redirects=True)
            if r.status_code != 200:
                continue
            # Find .pdf links in the body (case-insensitive)
            for m in re.finditer(r'href=[\"\']([^\"\']+\.pdf)\b', r.text, flags=re.I):
                href = m.group(1)
                if href.startswith('http'):
                    pdfs.append(href)
                else:
                    # Build absolute from base
                    if href.startswith('/'):
                        pdfs.append(base + href)
                    else:
                        pdfs.append(f"{base}/Open/{y_m}/{href}")
        except Exception:
            continue
    # Dedupe, preserve order
    seen = set()
    out = []
    for u in pdfs:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out

def parse_infocouncil_filename(url: str) -> Tuple[str|None, str|None]:
    """Return (doc_type, iso_date) from an InfoCouncil URL if possible.

    Recognizes patterns with DDMMYYYY and AGN/MIN markers.
    """
    low = url.lower()
    m = re.search(r'(\d{2})(\d{2})(\d{4})', low)
    if not m:
        return None, None
    dd, mm, yyyy = m.group(1), m.group(2), m.group(3)
    try:
        iso = f"{yyyy}-{mm}-{dd}"
    except Exception:
        iso = None
    doc_type = 'agenda' if 'agn' in low else ('minutes' if 'min' in low else None)
    return doc_type, iso

