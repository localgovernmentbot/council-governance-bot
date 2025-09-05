"""
Lightweight summarizer and hashtag suggester for CouncilBot.

Extracts 1–3 key bullets from PDF text using heuristics and suggests
1 council hashtag + 1 topical hashtag, keeping posts discoverable
without hashtag spam.
"""

import re
from typing import List, Tuple, Dict, Optional, Tuple
import os
from src.utils.date_format import format_long_date, rewrite_date_in_title


COUNCIL_TAGS = {
    'City of Melbourne': '#Melbourne',
    'Melbourne': '#Melbourne',
    'Darebin City Council': '#Darebin',
    'Darebin': '#Darebin',
    'Hobsons Bay City Council': '#HobsonsBay',
    'Hobsons Bay': '#HobsonsBay',
    'Maribyrnong City Council': '#Maribyrnong',
    'Maribyrnong': '#Maribyrnong',
    'Merri-bek City Council': '#MerriBek',
    'Merri-bek': '#MerriBek',
    'Moonee Valley City Council': '#MooneeValley',
    'Moonee Valley': '#MooneeValley',
    'Port Phillip City Council': '#PortPhillip',
    'Port Phillip': '#PortPhillip',
    'Stonnington City Council': '#Stonnington',
    'Stonnington': '#Stonnington',
    'Yarra City Council': '#Yarra',
    'Yarra': '#Yarra',
}

# Per-council standing item phrases to remove from TOC lines
COUNCIL_STANDING_SKIPS: Dict[str, List[str]] = {
    'Port Phillip City Council': [
        'an engaged and empowered community',
        'a vibrant and thriving community',
        'sustainable', 'well-governed',
    ],
    'Port Phillip': [
        'an engaged and empowered community',
        'a vibrant and thriving community',
        'sustainable', 'well-governed',
    ],
}


TOPIC_KEYWORDS: Dict[str, List[str]] = {
    '#Budget': [r'\bbudget\b', r'financial plan', r'annual budget', r'long[-\s]?term financial', r'capital works'],
    '#Rates': [r'\brates?\b', r'revenue & rating', r'revenue and rating', r'rating strategy'],
    '#Planning': [r'planning scheme', r'amendment\s+C\d+', r'\bpermit\b', r'\bvcat\b'],
    '#Environment': [r'climate', r'sustainab', r'net zero', r'emission', r'tree', r'waste', r'recycling'],
    '#Transport': [r'parking', r'road', r'bike|bicycle|cycling', r'speed', r'tram|bus'],
    '#Tenders': [r'contract', r'procure', r'tender', r'award(ed)?\b'],
    '#Community': [r'community', r'consultation', r'engagement', r'library', r'facility'],
    '#Policy': [r'policy', r'local law', r'governance', r'audit', r'risk', r'ceo employment'],
    '#Housing': [r'housing', r'affordable', r'social housing'],
}


MONEY_RE = re.compile(r'\$\s?\d[\d,]*(\.\d+)?\b|\b\d+(?:\.\d+)?\s*(million|billion)\b', re.I)
AMENDMENT_RE = re.compile(r'amendment\s+C\d+', re.I)

# Safeguard markers: unlikely in released public docs, but filter defensively
CONFIDENTIAL_MARKERS = [
    r'\bconfidential\b', r'\bin camera\b', r'\bclosed session\b', r'\bconfidential information\b',
    r'\blegal advice\b', r'\blegal professional privilege\b', r'\bprivileged\b',
    r'\bceo employment\b', r'\bpersonnel matter\b', r'\bindustrial\b', r'\bsecurity\b',
]
CONFIDENTIAL_RE = re.compile('|'.join(CONFIDENTIAL_MARKERS), re.I)

# Redaction patterns
EMAIL_RE = re.compile(r'[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}', re.I)
PHONE_RE = re.compile(r'(?:\+?61\s?|0)(?:\d\s?){8,10}')


def infer_topics(text: str) -> List[str]:
    """Infer up to two topical hashtags from text."""
    topics: List[str] = []
    t = text.lower()
    for tag, patterns in TOPIC_KEYWORDS.items():
        for p in patterns:
            if re.search(p, t, re.I):
                topics.append(tag)
                break
        if len(topics) >= 2:
            break
    return topics


def choose_hashtags(council_name: str, topics: List[str]) -> List[str]:
    """Compose up to 3 hashtags following this pattern:

    - Core: always include #VicCouncils
    - Council/location: include the council tag if known (e.g., #PortPhillip)
    - Third slot: prefer a topical tag if detected; otherwise include a second core tag
      chosen from #LocalGov or #OpenGovAU (default #OpenGovAU). Controlled by env
      CORE_SECOND_TAG.
    """
    tags: List[str] = ['#VicCouncils']
    # Council/location
    council_tag = COUNCIL_TAGS.get(council_name) or COUNCIL_TAGS.get(council_name.split(' (')[0], '')
    if not council_tag:
        # Fallback: derive a tag from the council name (e.g., "City of Ballarat" -> #Ballarat)
        import re
        # Prefer last word token of the name that is alphabetic and > 3 chars
        tokens = [t for t in re.split(r"[^A-Za-z]+", council_name) if t]
        fallback = None
        if tokens:
            # Use the last non-generic token if possible
            generics = {"city", "council", "shire", "rural", "cityof", "of", "cityofmelbourne"}
            for t in reversed(tokens):
                low = t.lower()
                if low not in generics and len(t) >= 4:
                    fallback = t
                    break
            if not fallback:
                fallback = tokens[-1]
        council_tag = f"#{fallback}" if fallback else ""
    if council_tag:
        tags.append(council_tag)

    # Choose topical if available, else second core
    second_core_default = os.environ.get('CORE_SECOND_TAG', '#OpenGovAU')
    second_core = second_core_default if second_core_default in ('#LocalGov', '#OpenGovAU') else '#OpenGovAU'

    if topics:
        top = topics[0]
        # Avoid duplicating a core tag if the topic happens to be one
        if top not in tags and top not in ('#LocalGov', '#OpenGovAU', '#VicCouncils'):
            tags.append(top)
        else:
            # Fallback to second core if topic is a core or duplicate
            if second_core not in tags:
                tags.append(second_core)
    else:
        if second_core not in tags:
            tags.append(second_core)

    return tags[:3]


def refine_toc_lines(council_name: str, lines: List[str]) -> List[str]:
    """Remove standing items and container categories from TOC lines.

    - Applies per-council skip phrases
    - Drops lines whose title part is too short or looks like a category heading
    """
    if not lines:
        return []
    skips = [
        'apologies', 'acknowledgement', 'acknowledgment', 'declarations of', 'conflict of interest',
        'confirmation of minutes', 'adoption of minutes', 'public question', 'petitions', 'presentations',
        'notices of motion', 'general business', 'urgent business', 'confidential', 'meeting closed',
        'reports by councillors', 'sealing schedule'
    ]
    council_skips = [s.lower() for s in COUNCIL_STANDING_SKIPS.get(council_name, [])]
    out = []
    for l in lines:
        low = l.lower()
        if any(k in low for k in skips):
            continue
        if any(k in low for k in council_skips):
            continue
        # Pull title part after the number
        parts = l.split(None, 1)
        title = parts[1] if len(parts) > 1 else l
        title = re.sub(r"^[-–:]+\s*", "", title).strip()
        # Drop very short or obviously category headings (single word, or almost all caps)
        words = [w for w in re.split(r"\s+", title) if w]
        if len(words) < 2:
            continue
        if title.isupper() and len(title) > 8:
            continue
        out.append(l)
    return out


def _clean_line(line: str) -> str:
    line = re.sub(r'\s+', ' ', line).strip()
    # Trim leading numbering like "1.", "1.1", "Item 3 -"
    line = re.sub(r'^(Item\s+\d+\s*[-–:]\s*|\d+(?:\.\d+)*\s*[-–:\)]\s*)', '', line, flags=re.I)
    return line.strip()


def _score_line(line: str) -> int:
    """Compute a heuristic score for a line."""
    low = line.lower()
    score = 0
    verbs = ['adopt', 'endorse', 'approve', 'resolve', 'consider', 'exhibit', 'award', 'amend']
    if any(v in low for v in verbs):
        score += 2
    if MONEY_RE.search(line):
        score += 2
    if AMENDMENT_RE.search(line):
        score += 3
    score += len(infer_topics(line))
    if 'council' in low:
        score += 1
    return score


def _extract_candidates_from_lines(lines: List[str]) -> List[Tuple[int, str]]:
    """Return scored, cleaned candidate lines from a list of lines."""
    candidates: List[Tuple[int, str]] = []
    seen = set()
    for line in lines:
        score = _score_line(line)
        if score > 0:
            cleaned = _clean_line(line)
            if cleaned and cleaned not in seen:
                seen.add(cleaned)
                # Clip individual bullet length early
                cleaned2 = cleaned if len(cleaned) <= 180 else (cleaned[:177] + '...')
                # Redact personal data
                cleaned2 = EMAIL_RE.sub('[redacted email]', cleaned2)
                cleaned2 = PHONE_RE.sub('[redacted phone]', cleaned2)
                # Skip if sensitive markers present
                if CONFIDENTIAL_RE.search(cleaned2):
                    continue
                candidates.append((score, cleaned2))
    # Sort by score desc, then by shorter length
    candidates.sort(key=lambda x: (-x[0], len(x[1])))
    return candidates


def extract_key_bullets(text: str, limit: int = 3, context: str = '', *, lines: Optional[List[str]] = None) -> List[str]:
    """Extract up to `limit` concise bullets from text or provided lines."""
    if lines is None:
        lines = [l.strip() for l in text.split('\n') if 20 <= len(l.strip()) <= 200]
    candidates = _extract_candidates_from_lines(lines)
    if not candidates:
        sentences = re.split(r'(?<=[.!?])\s+', text)
        for s in sentences:
            s = s.strip()
            if 30 <= len(s) <= 180:
                return [s[:180]]
        return []
    return [c[1] for c in candidates[:limit]]


def extract_high_value_bullets(text: str, min_score: int = 3, fallback_limit: int = 3, *, lines: Optional[List[str]] = None) -> List[str]:
    """Return all bullets with score >= min_score. If none, fall back to top-N.

    Use this to include all high-value items (e.g., budget meetings) in reply threads.
    """
    if lines is None:
        lines = [l.strip() for l in text.split('\n') if 20 <= len(l.strip()) <= 200]
    candidates = _extract_candidates_from_lines(lines)
    if not candidates:
        return []
    hv = [c[1] for c in candidates if c[0] >= min_score]
    if hv:
        return hv
    return [c[1] for c in candidates[:fallback_limit]]


def _title_phrase_from_line(line: str) -> str:
    # Remove leading number token and any leading punctuation
    parts = line.split(None, 1)
    title = parts[1] if len(parts) > 1 else line
    title = re.sub(r"^[-–:]+\s*", "", title).strip()
    # Collapse whitespace
    title = re.sub(r"\s+", " ", title)
    return title


def build_summary_paragraph(council_name: str, text: str, *, lines: Optional[List[str]] = None,
                            min_score: int = 3, max_phrases: int = 6, max_chars: int = 280) -> str:
    """Compose a single paragraph summarizing notable items as short phrases.

    - Uses TOC `lines` if provided (preferred). Falls back to whole-text candidate lines.
    - Selects items with score >= min_score, then converts to concise phrases (title part only).
    - Packs up to `max_phrases` separated by '; ' under `max_chars`.
    """
    if lines is None:
        lines = [l.strip() for l in text.split('\n') if 10 <= len(l.strip()) <= 200]

    # Apply per-council refinement
    lines = refine_toc_lines(council_name, lines)
    if not lines:
        return ""

    candidates = _extract_candidates_from_lines(lines)
    high = [c for c in candidates if c[0] >= min_score]
    if not high:
        high = candidates[:max_phrases]

    # Convert to phrases and trim length (e.g., 8–12 words)
    phrases: List[str] = []
    for _, line in high:
        phrase = _title_phrase_from_line(line)
        words = phrase.split()
        if len(words) > 12:
            phrase = ' '.join(words[:12]) + '…'
        phrases.append(phrase)

    # Build paragraph within max_chars
    base = "Notable items: "
    out = base
    taken = 0
    for ph in phrases[:max_phrases]:
        sep = '' if taken == 0 else '; '
        if len(out) + len(sep) + len(ph) <= max_chars:
            out += sep + ph
            taken += 1
        else:
            break
    return out if taken > 0 else ""


def _meeting_label(meeting_type: Optional[str]) -> str:
    if not meeting_type:
        return 'Meeting'
    mt = meeting_type.lower()
    if mt == 'council':
        return 'Council Meeting'
    if mt == 'delegated':
        return 'Delegated Committee'
    if mt == 'special':
        return 'Special Meeting'
    return meeting_type.title()


def compose_post_text(council_name: str, doc_type: str, title: str, date_str: str, url: str, 
                      topics: List[str], meeting_type: Optional[str] = None) -> str:
    """Compose a BlueSky-ready base post with 2–3 hashtags under 300 chars.

    Includes meeting type per LGA categories (Ordinary Council, Delegated Committee, Special).
    """
    hashtags = choose_hashtags(council_name, topics)

    # Base template
    label = _meeting_label(meeting_type)
    pretty_date = format_long_date(date_str) if date_str else ""
    header = f"{council_name} {label} {doc_type.title()} — {pretty_date}".rstrip(" —")
    footer = f"{url}\n\n{' '.join(hashtags)}"

    # Fit within 300 chars total
    budget = 300 - (len(header) + 2 + len('\n\n') + len(footer))
    # Rewrite any ISO date in the title to long form to match header
    t = rewrite_date_in_title(title.strip(), date_str)
    if len(t) > budget:
        t = t[:max(0, budget - 3)] + '...'

    post = f"{header}\n\n{t}\n\n{footer}"
    return post
