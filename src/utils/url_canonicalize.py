"""
URL canonicalization helpers for CouncilBot.

Currently normalizes InfoCouncil redirect links so that
"/RedirectToDoc.aspx?URL=Open/....PDF" hashes the same as
"/Open/....PDF" on the same host.
"""

from urllib.parse import urlparse, parse_qs, urlunparse


def canonicalize_doc_url(url: str) -> str:
    """Return a canonical URL for hashing/deduplication.

    - For InfoCouncil, convert RedirectToDoc.aspx?URL=Open/... to /Open/... on same host
    - Drop fragments and query for direct Open/ links
    - Keep scheme + host stable
    - Leave case as-is to avoid 404s on case-sensitive servers
    """
    try:
        p = urlparse(url)
        path = p.path or ""
        query = p.query or ""

        if path.lower().endswith("/redirecttodoc.aspx"):
            q = parse_qs(query)
            inner = None
            for k in ("URL", "url", "u"):
                if k in q and q[k]:
                    inner = q[k][0]
                    break
            if inner:
                if inner.startswith("/"):
                    new_path = inner
                else:
                    new_path = "/" + inner
                # Build without query/fragment
                return urlunparse((p.scheme or "https", p.netloc, new_path, "", "", ""))

        # For direct Open/... links, strip query/fragment
        if "/open/" in path.lower():
            return urlunparse((p.scheme or "https", p.netloc, path, "", "", ""))

        # Default: strip fragment only
        return urlunparse((p.scheme or "https", p.netloc, path, p.params, query, ""))
    except Exception:
        return url

