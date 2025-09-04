#!/usr/bin/env python3
"""
Test Yarra and Stonnington scrapers to debug why they return 0 documents
"""

import sys
import os
sys.path.append('src/scrapers')

from m9_selenium import YarraSeleniumScraper
from m9_final_three_complete import YarraFinalScraper, StonningtonFinalScraper

print("=" * 60)
print("DEBUGGING YARRA AND STONNINGTON SCRAPERS")
print("=" * 60)

# Test 1: Try the Selenium-based Yarra scraper
print("\n1. Testing YarraSeleniumScraper (uses Selenium)...")
print("-" * 40)
try:
    scraper = YarraSeleniumScraper()
    docs = scraper.scrape()
    print(f"   Results: {len(docs)} documents found")
    if docs:
        print(f"   Latest: {docs[0].date} - {docs[0].title[:50]}")
        print(f"   URL: {docs[0].url}")
except Exception as e:
    print(f"   ERROR: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Try the non-Selenium Yarra scraper
print("\n2. Testing YarraFinalScraper (pattern-based)...")
print("-" * 40)
try:
    scraper = YarraFinalScraper()
    docs = scraper.scrape()
    print(f"   Results: {len(docs)} documents found")
    if docs:
        print(f"   Latest: {docs[0].date} - {docs[0].title[:50]}")
        print(f"   URL: {docs[0].url}")
except Exception as e:
    print(f"   ERROR: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Try Stonnington scraper
print("\n3. Testing StonningtonFinalScraper...")
print("-" * 40)
try:
    # Set environment variable for testing
    os.environ['STON_WEEKS'] = '8'  # Test last 2 months
    
    scraper = StonningtonFinalScraper()
    docs = scraper.scrape()
    print(f"   Results: {len(docs)} documents found")
    if docs:
        print(f"   Latest: {docs[0].date} - {docs[0].title[:50]}")
        print(f"   URL: {docs[0].url}")
        # Show first few URLs to verify pattern
        print("\n   Sample URLs found:")
        for doc in docs[:3]:
            print(f"     - {doc.url}")
except Exception as e:
    print(f"   ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("DEBUGGING COMPLETE")
print("=" * 60)
