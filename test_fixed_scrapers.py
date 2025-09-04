#!/usr/bin/env python3
"""
Quick test of the fixed scrapers
"""

import sys
sys.path.append('src/scrapers')

from yarra_stonnington_fixed import YarraFixedScraper, StonningtonFixedScraper

print("=" * 60)
print("TESTING FIXED SCRAPERS")
print("=" * 60)

total = 0

# Test Yarra
print("\n1. Yarra City Council:")
print("-" * 40)
try:
    scraper = YarraFixedScraper()
    docs = scraper.scrape()
    print(f"   ✅ Found {len(docs)} documents")
    if docs:
        print(f"   Latest: {docs[0].date} - {docs[0].title[:40]}...")
    total += len(docs)
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test Stonnington  
print("\n2. Stonnington City Council:")
print("-" * 40)
try:
    scraper = StonningtonFixedScraper()
    docs = scraper.scrape()
    print(f"   ✅ Found {len(docs)} documents")
    if docs:
        print(f"   Latest: {docs[0].date} - {docs[0].title[:40]}...")
    total += len(docs)
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
if total > 0:
    print(f"✅ SUCCESS! Fixed scrapers found {total} total documents")
    print("   Run m9_unified_scraper.py to update all results")
else:
    print("⚠️  No documents found - scrapers may need manual debugging")
print("=" * 60)
