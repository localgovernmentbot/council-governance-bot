#!/usr/bin/env python3
"""
Test adapted M9 scrapers
"""

import sys
sys.path.append('src/scrapers')

from m9_adapted import MaribyrnongScraper, MerribekScraper

print("Testing Adapted M9 Scrapers from YIMBY")
print("=" * 60)

scrapers = [
    ("Maribyrnong", MaribyrnongScraper),
    ("Merri-bek", MerribekScraper),
]

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
            
    except Exception as e:
        print(f"  Error: {e}")
        import traceback
        traceback.print_exc()
