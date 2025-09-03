#!/usr/bin/env python3
"""
Test all M9 scrapers including Hobsons Bay
"""

import sys
sys.path.append('src/scrapers')

from melbourne_m9 import MelbourneScraper
from darebin_m9 import DarebinScraper
from hobsonsbay_m9 import HobsonsBayScraper

print("M9 Council Bot - Testing Priority Scrapers")
print("=" * 60)

scrapers = [
    ("Melbourne", MelbourneScraper),
    ("Darebin", DarebinScraper),
    ("Hobsons Bay (Priority)", HobsonsBayScraper),
]

total_docs = 0

for name, scraper_class in scrapers:
    print(f"\nTesting {name}...")
    try:
        scraper = scraper_class()
        docs = scraper.scrape()
        print(f"{name}: Found {len(docs)} documents")
        
        if docs:
            print(f"  Most recent: {docs[0].date} - {docs[0].title}")
            
        total_docs += len(docs)
        
    except Exception as e:
        print(f"{name} error: {e}")
        import traceback
        traceback.print_exc()

print(f"\n{'='*60}")
print(f"Total documents across tested councils: {total_docs}")
