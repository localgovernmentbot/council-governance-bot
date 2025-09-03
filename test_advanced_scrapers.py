#!/usr/bin/env python3
"""
Test advanced M9 scrapers for the 3 problematic councils
Using GitHub-proven solutions
"""

import sys
sys.path.append('src/scrapers')

# First install SeleniumBase if needed
print("Installing SeleniumBase...")
import subprocess
subprocess.run([sys.executable, '-m', 'pip', 'install', 'seleniumbase', 'cloudscraper'], capture_output=True)

from m9_advanced import YarraAdvancedScraper, PortPhillipAdvancedScraper, StonningtonAdvancedScraper

print("\nTesting Advanced M9 Scrapers")
print("=" * 60)
print("Using proven GitHub solutions:")
print("- Yarra: SeleniumBase with stealth mode")
print("- Port Phillip: Extended timeouts + retry logic")  
print("- Stonnington: Multiple approaches + InfoCouncil")
print()

scrapers = [
    ("Yarra (SeleniumBase)", YarraAdvancedScraper),
    ("Port Phillip (Patience)", PortPhillipAdvancedScraper),
    ("Stonnington (Multi-approach)", StonningtonAdvancedScraper),
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
print(f"SUMMARY: {working_councils}/3 advanced scrapers working")
print(f"Total documents from advanced methods: {total_docs}")

if working_councils > 0:
    print("\nCombined with our 6 existing councils, we now have:")
    print(f"- Total councils: {6 + working_councils}/9")
    print(f"- Total documents: {318 + total_docs}")
