"""
Victorian Council Meeting Scraper
Main entry point for scraping council meetings
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scrapers.base import scrape_all_councils, SCRAPERS


def main():
    """Main function to run all scrapers"""
    print("🏛️ Victorian Council Meeting Scraper")
    print("=" * 60)
    
    results = scrape_all_councils()
    
    print(f"\n\nTotal documents found: {len(results)}")
    
    # Summary by council
    council_counts = {}
    for result in results:
        council = result.name.split(' - ')[0] if ' - ' in result.name else 'Unknown'
        council_counts[council] = council_counts.get(council, 0) + 1
    
    print("\nDocuments by council:")
    for council, count in sorted(council_counts.items()):
        print(f"  {council}: {count}")


if __name__ == "__main__":
    main()
