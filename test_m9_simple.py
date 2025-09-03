#!/usr/bin/env python3
"""
Simple test of M9 scrapers
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Now try imports
try:
    from src.scrapers.m9.melbourne import MelbourneScraper
    from src.scrapers.m9.darebin import DarebinScraper
    
    print("M9 Council Bot - Testing Scrapers")
    print("=" * 60)
    
    # Test Melbourne
    print("\nTesting Melbourne...")
    melb = MelbourneScraper()
    melb_docs = melb.scrape()
    print(f"Melbourne: Found {len(melb_docs)} documents")
    
    # Test Darebin
    print("\nTesting Darebin...")
    dare = DarebinScraper()
    dare_docs = dare.scrape()
    print(f"Darebin: Found {len(dare_docs)} documents")
    
    # Show totals
    total = len(melb_docs) + len(dare_docs)
    print(f"\nTotal documents: {total}")
    
    # Show sample
    if melb_docs:
        print("\nSample Melbourne document:")
        doc = melb_docs[0]
        print(f"  Title: {doc.title}")
        print(f"  Date: {doc.date}")
        print(f"  Type: {doc.document_type}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
