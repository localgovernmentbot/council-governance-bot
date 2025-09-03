#!/usr/bin/env python3
"""
Preview BlueSky posts (base + 1–3 reply bullets) without publishing.

Reads m9_scraper_results.json, downloads PDFs to extract text for a few
recent/next documents per council, composes base posts and bullet replies,
and prints a rotation schedule for the next 24 hours (1 post/hour).

Usage:
  python3 scripts/preview_posts.py [--per-council 2] [--window-days 14]

Notes:
  - Uses a small per-council cap to keep preview fast.
  - Requires network access for PDF fetch. Timeouts kept moderate.
"""

import argparse
import json
import os
from datetime import datetime, timedelta
from collections import defaultdict, deque
from typing import List, Dict

import sys
from pathlib import Path
# Ensure project root on path when running from repo
ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from src.processors.pdf_extractor import PDFExtractor
from src.processors.summarize import (
    infer_topics,
    compose_post_text,
    build_summary_paragraph,
)


def load_results(path: str) -> Dict:
    if not os.path.exists(path):
        raise SystemExit(f"Missing {path}. Run m9_unified_scraper.py first.")
    with open(path, 'r') as f:
        return json.load(f)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--results', default='m9_scraper_results.json')
    p.add_argument('--per-council', type=int, default=2, help='Max docs per council in preview')
    p.add_argument('--window-days', type=int, default=14, help='Days window around today')
    p.add_argument('--include-minutes', action='store_true', help='Include minutes in addition to agendas')
    p.add_argument('--include-agendas', action='store_true', help='Include agendas in addition to minutes')
    p.add_argument('--fast', action='store_true', help='Skip PDF downloads (summary from titles only)')
    return p.parse_args()


def filter_docs(docs: List[Dict], include_minutes: bool, include_agendas: bool, window_days: int) -> List[Dict]:
    today = datetime.now().date()
    start = today - timedelta(days=window_days)
    end = today + timedelta(days=window_days)

    def want(d):
        dt = datetime.fromisoformat(d['date']).date() if d.get('date') else None
        if not dt or not (start <= dt <= end):
            return False
        if d['document_type'] == 'minutes' and not include_minutes:
            return False
        if d['document_type'] == 'agenda' and not include_agendas:
            return False
        return True

    return [d for d in docs if want(d)]


def pick_per_council(docs: List[Dict], per_council: int) -> List[Dict]:
    buckets = defaultdict(list)
    for d in sorted(docs, key=lambda x: x.get('date', ''), reverse=True):
        buckets[d['council_name']].append(d)
    picked = []
    for name, arr in buckets.items():
        picked.extend(arr[:per_council])
    return picked


def round_robin_schedule(items: List[Dict]) -> List[Dict]:
    # Group by council and interleave
    groups = defaultdict(deque)
    for d in items:
        name = d.get('council_name') or d.get('council')
        groups[name].append(d)
    queue = deque(sorted(groups.keys()))
    ordered = []
    while queue:
        council = queue.popleft()
        if groups[council]:
            ordered.append(groups[council].popleft())
            queue.append(council) if groups[council] else None
    # Assign times 1/h from now
    start = datetime.now()
    out = []
    for i, d in enumerate(ordered[:24]):
        d2 = dict(d)
        d2['_scheduled_for'] = (start + timedelta(hours=i)).isoformat(timespec='minutes')
        out.append(d2)
    return out


def main():
    args = parse_args()
    data = load_results(args.results)
    docs = data.get('documents', [])

    # If user didn't specify, include both types by default
    include_minutes = args.include_minutes or (not args.include_agendas)
    include_agendas = args.include_agendas or (not args.include_minutes)

    filtered = filter_docs(docs, include_minutes, include_agendas, args.window_days)
    selected = pick_per_council(filtered, args.per_council)

    extractor = PDFExtractor()

    # Build previews
    previews = []
    for d in selected:
        council = d['council_name']
        url = d['url']
        date_str = d.get('date', '')
        doc_type = d['document_type']
        title = d['title']

        # Download and extract bullets
        if args.fast:
            pdf = None
            text = ''
            toc_lines = []
        else:
            pdf = extractor.download_pdf(url)
            text = extractor.extract_text_from_pdf(pdf) if pdf else ''
            # Prefer table-of-contents/agenda lines to avoid boilerplate
            toc_lines = extractor.extract_toc_lines(text) if text else []
            # Per-council refinement of TOC
        from src.processors.summarize import refine_toc_lines
        toc_lines = refine_toc_lines(council, toc_lines)

        topics = infer_topics("\n".join(toc_lines) or text or title)
        base = compose_post_text(
            council_name=council,
            doc_type=doc_type,
            title=title,
            date_str=date_str,
            url=url,
            topics=topics,
            meeting_type=d.get('meeting_type'),
        )
        # Build a concise summary paragraph of notable items
        summary = build_summary_paragraph(council, text or title, lines=toc_lines or None, min_score=3)

        previews.append({
            'council': council,
            'type': doc_type,
            'date': date_str,
            'title': title,
            'url': url,
            'base_post': base,
            'summary': summary,
        })

    # Schedule and print
    scheduled = round_robin_schedule(previews)

    print("Previewing next posts (no publishing):")
    print("=" * 60)
    for p in scheduled:
        print(f"\n[{p['_scheduled_for']}] {p['council']} — {p['type'].title()} ({p['date']})")
        print("- Base post:")
        print(p['base_post'])
        if p['summary']:
            print("- Thread summary:")
            print(p['summary'])
        else:
            print("- Thread summary: (none)")

    print("\nDone. This is a dry-run preview.\n")


if __name__ == '__main__':
    main()
