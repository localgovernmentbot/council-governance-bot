#!/usr/bin/env python3
"""
Test all M9 scrapers with fixed versions
"""

import sys
sys.path.append('src/scrapers')

from melbourne_m9_fixed import MelbourneScraper
from darebin_m9 import DarebinScraper
from hobsonsbay_m9_fixed import HobsonsBayScraper

print("M9 Council Bot - Testing All Fixed Scrapers")
print("=" * 60)

scrapers = [
    ("Melbourne", MelbourneScraper),
    ("Darebin", DarebinScraper),
    ("Hobsons Bay", HobsonsBayScraper),
]

total_docs = 0
working_councils = 0

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
            working_councils += 1
            
        total_docs += len(docs)
        
    except Exception as e:
        print(f"  Error: {e}")
        import traceback
        traceback.print_exc()

print(f"\n{'='*60}")
print(f"SUMMARY: {working_councils}/3 councils working")
print(f"Total documents: {total_docs}")
