"""
Test our council scrapers
"""

import sys
sys.path.append('src')

from council_scrapers import scrape_all_councils, SCRAPERS

def test_scrapers():
    print("Testing Council Scrapers")
    print("=" * 60)
    
    # Show registered scrapers
    print(f"\nRegistered scrapers: {list(SCRAPERS.keys())}")
    
    # Run all scrapers
    results = scrape_all_councils()
    
    # Summary by council
    council_counts = {}
    for result in results:
        # Determine council from webpage URL
        if 'melbourne.vic.gov.au' in result.webpage_url:
            council = 'Melbourne'
        elif 'darebin.vic.gov.au' in result.webpage_url:
            council = 'Darebin'
        else:
            council = 'Unknown'
        
        council_counts[council] = council_counts.get(council, 0) + 1
    
    print("\n\nSummary by Council:")
    for council, count in council_counts.items():
        print(f"  {council}: {count} documents")
    
    # Show newest documents
    print("\n\nNewest Documents (by date):")
    sorted_results = sorted([r for r in results if r.date], 
                          key=lambda x: x.date, 
                          reverse=True)
    
    for result in sorted_results[:10]:
        print(f"\n{result.date} - {result.name}")
        print(f"  Download: {result.download_url[:80]}...")

if __name__ == "__main__":
    test_scrapers()
