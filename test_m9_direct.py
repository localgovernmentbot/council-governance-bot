#!/usr/bin/env python3
"""
Test M9 scrapers directly
"""

import sys
sys.path.append('src/scrapers')

from melbourne_m9 import MelbourneScraper
from darebin_m9 import DarebinScraper

print("M9 Council Bot - Testing Scrapers")
print("=" * 60)

# Test Melbourne
print("\nTesting Melbourne...")
try:
    melb = MelbourneScraper()
    melb_docs = melb.scrape()
    print(f"Melbourne: Found {len(melb_docs)} documents")
    
    if melb_docs:
        print(f"  Most recent: {melb_docs[0].date} - {melb_docs[0].title}")
except Exception as e:
    print(f"Melbourne error: {e}")

# Test Darebin
print("\nTesting Darebin...")
try:
    dare = DarebinScraper()
    dare_docs = dare.scrape()
    print(f"Darebin: Found {len(dare_docs)} documents")
    
    if dare_docs:
        print(f"  Most recent: {dare_docs[0].date} - {dare_docs[0].title}")
except Exception as e:
    print(f"Darebin error: {e}")

# Summary
try:
    total = len(melb_docs) + len(dare_docs)
    print(f"\nTotal documents: {total}")
except:
    print("\nCould not calculate total")
