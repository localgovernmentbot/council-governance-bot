"""
Check what's actually working from our original scrapers
"""

import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.scrape_councils import load_councils, scrape_melbourne_council, scrape_generic_council

def test_working_scrapers():
    """Test the scrapers we know were working"""
    
    print("Testing scrapers that were previously working...")
    print("="*60)
    
    # Test Melbourne
    print("\n1. Testing Melbourne scraper...")
    melbourne_docs = scrape_melbourne_council()
    print(f"   Found {len(melbourne_docs)} documents")
    if melbourne_docs:
        for doc in melbourne_docs[:3]:
            print(f"   - {doc['type']}: {doc['title']}")
    
    # Test Darebin with the specific URL we know works
    print("\n2. Testing Darebin with CMS URL...")
    darebin_council = {
        'id': 'darebin',
        'name': 'Darebin City Council',
        'url': 'https://www.darebin.vic.gov.au',
        'meetings_url': 'https://www.darebin.vic.gov.au/About-council/Council-structure-and-performance/Council-and-Committee-Meetings/Council-meetings/Meeting-agendas-and-minutes/2025-Council-meeting-agendas-and-minutes'
    }
    
    darebin_docs = scrape_generic_council(darebin_council)
    print(f"   Found {len(darebin_docs)} documents")
    if darebin_docs:
        for doc in darebin_docs[:3]:
            print(f"   - {doc['type']}: {doc['title']}")
    
    # Show what makes these work
    print("\n\nWhy these work:")
    print("- Melbourne: Uses S3 bucket with direct PDF links")
    print("- Darebin: We're using the specific 2025 page with direct PDF links")
    print("\nThe issue: Most councils don't expose PDFs directly on their main pages")

if __name__ == "__main__":
    test_working_scrapers()
