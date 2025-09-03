#!/usr/bin/env python3
"""
Final unified M9 scraper - runs all 9 councils
"""

import sys
sys.path.append('src/scrapers')

# Import working scrapers from existing modules
from melbourne_m9_v2 import MelbourneScraper
from darebin_m9 import DarebinScraper
from hobsonsbay_m9_fixed import HobsonsBayScraper
from m9_adapted import MaribyrnongScraper, MerribekScraper
from moonee_valley_fixed import MooneeValleyFixedScraper
from m9_selenium import YarraSeleniumScraper
from m9_final_three_complete import StonningtonFinalScraper, PortPhillipFinalScraper

print("M9 COUNCIL BOT - FINAL UNIFIED SCRAPER")
print("=" * 60)
print("\nRunning all 9 metropolitan Melbourne councils...\n")

# All 9 M9 councils
scrapers = [
    ("Melbourne", MelbourneScraper),
    ("Darebin", DarebinScraper),
    ("Hobsons Bay", HobsonsBayScraper),
    ("Maribyrnong", MaribyrnongScraper),
    ("Merri-bek", MerribekScraper),
    ("Moonee Valley", MooneeValleyFixedScraper),
    ("Yarra", YarraSeleniumScraper),
    ("Stonnington", StonningtonFinalScraper),
    ("Port Phillip", PortPhillipFinalScraper),
]

all_documents = []
council_stats = []

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
            print(f"  Most recent: {docs[0].date} - {docs[0].title[:50]}...")
            
        all_documents.extend(docs)
        council_stats.append({
            'name': name,
            'total': len(docs),
            'agendas': len(agendas),
            'minutes': len(minutes),
            'working': len(docs) > 0
        })
        
    except Exception as e:
        print(f"  Error: {e}")
        council_stats.append({
            'name': name,
            'total': 0,
            'agendas': 0,
            'minutes': 0,
            'working': False
        })

# Summary
print(f"\n{'='*60}")
print("FINAL SUMMARY:")
print(f"\nWorking councils: {sum(1 for c in council_stats if c['working'])}/9")
print(f"Total documents: {len(all_documents)}")
print(f"Total agendas: {sum(c['agendas'] for c in council_stats)}")
print(f"Total minutes: {sum(c['minutes'] for c in council_stats)}")

print("\nBreakdown by council:")
for stat in sorted(council_stats, key=lambda x: x['total'], reverse=True):
    status = "✓" if stat['working'] else "✗"
    print(f"  {status} {stat['name']:15} - {stat['total']:3} documents")

# Save results
import json
from datetime import datetime

# Convert documents to JSON-serializable format
output_data = {
    'scrape_date': datetime.now().isoformat(),
    'total_councils': len(scrapers),
    'working_councils': sum(1 for c in council_stats if c['working']),
    'total_documents': len(all_documents),
    'council_stats': council_stats,
    'documents': [
        {
            'council_id': doc.council_id,
            'council_name': doc.council_name,
            'document_type': doc.document_type,
            'meeting_type': doc.meeting_type,
            'title': doc.title,
            'date': doc.date,
            'url': doc.url,
            'webpage_url': doc.webpage_url
        }
        for doc in all_documents
    ]
}

# Save to file
with open('m9_scraper_results.json', 'w') as f:
    json.dump(output_data, f, indent=2)

print(f"\nResults saved to m9_scraper_results.json")
print(f"\nSUCCESS: {sum(1 for c in council_stats if c['working'])}/9 councils operational!")
print(f"Total of {len(all_documents)} documents ready for processing.")
