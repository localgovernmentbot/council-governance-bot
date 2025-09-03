#!/usr/bin/env python3
"""
Test remaining M9 scrapers
"""

import sys
sys.path.append('src/scrapers')

from m9_remaining import MooneeValleyScraper, YarraScraper, PortPhillipScraper, StonningtonScraper

print("Testing Remaining M9 Scrapers")
print("=" * 60)

scrapers = [
    ("Moonee Valley", MooneeValleyScraper),
    ("Yarra", YarraScraper),
    ("Port Phillip", PortPhillipScraper),
    ("Stonnington", StonningtonScraper),
]

total_docs = 0

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
            
    except Exception as e:
        print(f"  Error: {e}")
        import traceback
        traceback.print_exc()

print(f"\n{'='*60}")
print(f"Total from these 4 councils: {total_docs} documents")
