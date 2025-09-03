#!/usr/bin/env python3
"""
Test Selenium-based M9 scrapers for problematic councils
"""

import sys
sys.path.append('src/scrapers')

from m9_selenium import (
    YarraSeleniumScraper, 
    MooneeValleySeleniumScraper,
    PortPhillipSeleniumScraper,
    StonningtonSeleniumScraper
)

print("Testing Selenium-based M9 Scrapers")
print("=" * 60)
print("NOTE: This will open browser windows - please ensure Chrome is installed")
print("Installing required packages: pip install undetected-chromedriver selenium")
print()

scrapers = [
    ("Yarra (403 bypass)", YarraSeleniumScraper),
    ("Moonee Valley (dynamic content)", MooneeValleySeleniumScraper),
    ("Port Phillip (slow site)", PortPhillipSeleniumScraper),
    ("Stonnington (InfoCouncil)", StonningtonSeleniumScraper),
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
print(f"SUMMARY: {working_councils}/4 councils working")
print(f"Total documents from Selenium scrapers: {total_docs}")
