#!/usr/bin/env python3
"""
Test M9 scrapers with fixed Hobsons Bay
"""

import sys
sys.path.append('src/scrapers')

from melbourne_m9 import MelbourneScraper
from darebin_m9 import DarebinScraper
from hobsonsbay_m9_fixed import HobsonsBayScraper

print("M9 Council Bot - Testing Scrapers (with Hobsons Bay fixed)")
print("=" * 60)

scrapers = [
    ("Melbourne", MelbourneScraper),
    ("Darebin", DarebinScraper),
    ("Hobsons Bay", HobsonsBayScraper),
]

total_docs = 0
council_summaries = []

for name, scraper_class in scrapers:
    print(f"\n{name}:")
    try:
        scraper = scraper_class()
        docs = scraper.scrape()
        
        # Count by type
        agendas = [d for d in docs if d.document_type == 'agenda']
        minutes = [d for d in docs if d.document_type == 'minutes']
        
        print(f"  Total: {len(docs)} documents ({len(agendas)} agendas, {len(minutes)} minutes)")
        
        if docs:
            print(f"  Most recent: {docs[0].date} - {docs[0].title}")
            
        total_docs += len(docs)
        council_summaries.append({
            'name': name,
            'total': len(docs),
            'agendas': len(agendas),
            'minutes': len(minutes)
        })
        
    except Exception as e:
        print(f"  Error: {e}")

print(f"\n{'='*60}")
print(f"SUMMARY")
print(f"{'='*60}")
print(f"Total documents: {total_docs}")
print(f"Working councils: {len([c for c in council_summaries if c['total'] > 0])}/3")

# Show breakdown
print(f"\nBy council:")
for council in council_summaries:
    if council['total'] > 0:
        print(f"  {council['name']}: {council['total']} docs ({council['agendas']} agendas, {council['minutes']} minutes)")
