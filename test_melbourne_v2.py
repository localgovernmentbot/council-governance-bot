#!/usr/bin/env python3
"""
Test Melbourne scraper v2
"""

import sys
sys.path.append('src/scrapers')

from melbourne_m9_v2 import MelbourneScraper

print("Testing Melbourne scraper v2 (handles AUG25 format)...")
print("=" * 60)

scraper = MelbourneScraper()
docs = scraper.scrape()

print(f"\nFound {len(docs)} documents")

# Count by type
agendas = [d for d in docs if d.document_type == 'agenda']
minutes = [d for d in docs if d.document_type == 'minutes']

print(f"  Agendas: {len(agendas)}")
print(f"  Minutes: {len(minutes)}")

# Show meeting types
council = [d for d in docs if d.meeting_type == 'council']
delegated = [d for d in docs if d.meeting_type == 'delegated']

print(f"\nMeeting types:")
print(f"  Council: {len(council)}")
print(f"  Delegated (FMC): {len(delegated)}")

# Show recent documents
if docs:
    print(f"\nRecent documents:")
    for doc in docs[:5]:
        print(f"\n  Date: {doc.date}")
        print(f"  Title: {doc.title}")
        print(f"  Type: {doc.document_type} ({doc.meeting_type})")
