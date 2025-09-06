#!/usr/bin/env python3
"""
Generate a coverage report for CouncilBot over a relaxed ±30 day window.

Reads m9_scraper_results.json, aggregates per-council counts, highlights
councils with zero items, and writes coverage_summary.json. If available,
uses src/registry/councils.json to include councils configured in the
registry + the built-in M9 councils.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

RESULTS = Path('m9_scraper_results.json')
REGISTRY = Path('src/registry/councils.json')

WINDOW_DAYS = 30


def load_results():
    if not RESULTS.exists():
        raise SystemExit('m9_scraper_results.json not found. Run scraper first.')
    return json.loads(RESULTS.read_text())


def load_registry_names():
    names = set()
    if REGISTRY.exists():
        try:
            reg = json.loads(REGISTRY.read_text())
            for row in reg:
                n = (row.get('name') or '').strip()
                if n:
                    names.add(n)
        except Exception:
            pass
    # Add common M9 council names to ensure they are represented
    names.update({
        'City of Melbourne',
        'Port Phillip City Council',
        'Hobsons Bay City Council',
        'Maribyrnong City Council',
        'Merri-bek City Council',
        'Moonee Valley City Council',
        'Yarra City Council',
        'Stonnington City Council',
        'Darebin City Council',
    })
    return sorted(names)


def within_window(doc_date: str) -> bool:
    try:
        d = datetime.fromisoformat(doc_date)
    except Exception:
        return False
    now = datetime.now()
    return (now - timedelta(days=WINDOW_DAYS)) <= d <= (now + timedelta(days=WINDOW_DAYS))


def main():
    data = load_results()
    all_docs = data.get('documents', [])
    councils = load_registry_names()

    # Build counts within ±WINDOW_DAYS for both agendas and minutes
    counts = {}
    for c in councils:
        counts[c] = {"agendas": 0, "minutes": 0, "total": 0}

    for doc in all_docs:
        cname = doc.get('council_name') or ''
        if not cname:
            continue
        if not within_window(doc.get('date', '')):
            continue
        dtype = (doc.get('document_type') or '').lower()
        if cname not in counts:
            counts[cname] = {"agendas": 0, "minutes": 0, "total": 0}
        if dtype == 'agenda':
            counts[cname]['agendas'] += 1
        elif dtype == 'minutes':
            counts[cname]['minutes'] += 1
        counts[cname]['total'] += 1

    zero_councils = [c for c, v in counts.items() if v['total'] == 0]
    active_councils = [
        {"name": c, **counts[c]} for c in counts if counts[c]['total'] > 0
    ]
    active_councils.sort(key=lambda x: x['total'], reverse=True)

    summary = {
        'window_days': WINDOW_DAYS,
        'generated_at': datetime.now().isoformat(),
        'active_count': len(active_councils),
        'zero_count': len(zero_councils),
        'active_councils': active_councils,
        'zero_councils': sorted(zero_councils),
    }
    Path('coverage_summary.json').write_text(json.dumps(summary, indent=2))

    # Human-readable summary to stdout
    print('Coverage Report (±{} days)'.format(WINDOW_DAYS))
    print('Active councils: {}  Zero councils: {}'.format(summary['active_count'], summary['zero_count']))
    print('\nTop active councils:')
    for row in active_councils[:15]:
        print('- {}: {} total ({} agendas, {} minutes)'.format(row['name'], row['total'], row['agendas'], row['minutes']))
    if zero_councils:
        print('\nCouncils with zero items in window ({}):'.format(len(zero_councils)))
        for c in zero_councils:
            print('-', c)


if __name__ == '__main__':
    main()

