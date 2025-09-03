#!/usr/bin/env python3
"""
Test pattern-based scrapers for the final 3 councils
"""

import sys
sys.path.append('src/scrapers')

from m9_pattern_scrapers import YarraPatternScraper, PortPhillipYearScraper, StonningtonInfoCouncilScraper

print("Testing Pattern-Based M9 Scrapers")
print("=" * 60)
print("Using discovered URL patterns:")
print("- Yarra: YIMBY's approach (upcoming meetings div)")
print("- Port Phillip: Year-based pages (2024/2025)")  
print("- Stonnington: InfoCouncil year directories")
print()

scrapers = [
    ("Yarra (YIMBY pattern)", YarraPatternScraper),
    ("Port Phillip (Year pages)", PortPhillipYearScraper),
    ("Stonnington (InfoCouncil years)", StonningtonInfoCouncilScraper),
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
            
            # Show a few more examples
            for doc in docs[1:4]:
                print(f"  - {doc.date} - {doc.document_type} - {doc.title[:50]}...")
        
        total_docs += len(docs)
            
    except Exception as e:
        print(f"  Error: {e}")
        import traceback
        traceback.print_exc()

print(f"\n{'='*60}")
print(f"PATTERN SCRAPERS: {working_councils}/3 working")
print(f"Total documents: {total_docs}")

if total_docs > 0:
    print("\nFINAL M9 COUNCIL BOT STATUS:")
    print(f"- Working councils: {6 + working_councils}/9")
    print(f"- Total documents: {318 + total_docs}")
    print(f"- Success rate: {(6 + working_councils)/9*100:.0f}%")
